"""Bounded launcher for explicitly listed independent campaigns; no merging or Git writes."""
# JSON manifests are data, never shell command strings.
import json
# Per-child environment copies keep numerical thread limits local.
import os
# Paths scope each graph/config/campaign to this checkout.
from pathlib import Path
# IDs follow the same narrow namespace as the single-campaign controller.
import re
# Each selected campaign runs the ordinary controller CLI in its own process.
import subprocess
# The currently synced Python interpreter is reused without hidden installations.
import sys
# A short poll keeps Ctrl-C and owned child completion responsive.
import time
# Campaign creation freezes identical trusted inputs before the child takes its own lock.
from evolution_controller import Campaign,create_campaign
# The same config parser enforces all per-campaign caps and publication policy.
from evolution_common import configuration
# Process cleanup is PID/start-tick scoped, never a name-matched broad kill.
from portfolio_external import process_tick,stop_process_group
# Structured launch/stop/exit receipts stay inside each campaign's logs/ directory.
from run_bm import atomic_json


def batch_entries(root,path):
    """Validate an explicit JSON batch before any initialization; return resolved jobs.

    root/path Paths. Accept version=1 and campaigns with instance/campaign_id,
    optional config and overrides. Duplicate/existing IDs or invalid inputs fail
    without launching anything. Example two selected different graphs, jobs=2.
    """
    # Both a relative filename and an explicit absolute manifest path are ordinary local inputs.
    path=path if path.is_absolute() else root/path
    # A manifest cannot contain hidden command fields or silently ignored options.
    manifest=json.loads(path.read_text())
    # Keep one small versioned schema instead of accepting arbitrary launcher instructions.
    if set(manifest)!={'version','campaigns'} or manifest['version']!=1 or not isinstance(manifest['campaigns'],list) or not manifest['campaigns']:
        raise ValueError('batch requires version=1 and a nonempty campaigns list')
    # Names are unique across the entire request, even while jobs wait in the queue.
    seen=set()
    # Preserve the explicitly requested input order for bounded scheduling.
    jobs=[]
    # Validate every job before creating the first campaign directory.
    for entry in manifest['campaigns']:
        # New batches deliberately do not silently resume or overwrite old campaigns.
        if not isinstance(entry,dict) or not {'instance','campaign_id'}<=set(entry) or set(entry)-{'instance','campaign_id','config','overrides'}:
            raise ValueError('batch entry needs instance/campaign_id and optional config/overrides only')
        # Reject path-like IDs before any child or log directory exists.
        name=entry['campaign_id']
        # The controller and launcher must agree on the exact immutable namespace.
        if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',name) or '..' in name or name in seen:
            raise ValueError('invalid or duplicate batch campaign ID')
        # Existing evidence requires the explicit single-campaign resume command.
        if (root/'evolve/campaigns'/name).exists():
            raise ValueError('campaign already exists; resume it explicitly: '+name)
        # Record identity before considering the next entry.
        seen.add(name)
        # Each job resolves the standard default file unless the user explicitly selects another.
        config_path=root/entry.get('config','evolve/configs/default.json')
        # Overrides are saved as part of this campaign's initial immutable configuration.
        overrides=entry.get('overrides',{})
        # Lists or strings cannot masquerade as unrecorded configuration controls.
        if not isinstance(overrides,dict):
            raise ValueError('batch overrides must be an object')
        # No model, authentication or source version is invented by the launcher.
        config=configuration({**json.loads(config_path.read_text()),**overrides})
        # Validate every data-root boundary before any earlier entry could start.
        if any(not (root/config[key]).resolve().is_relative_to(root.resolve()) for key in ('instances','references','baseline_solutions','public_solutions')):
            # A late invalid config must not produce a partially launched batch.
            raise ValueError('batch data path escapes checkout')
        # Check graph selection before launching any earlier manifest entry.
        instance=Path(entry['instance'])
        # Basenames are resolved exactly as in the single-campaign CLI.
        selected=(root/instance).resolve() if (root/instance).is_file() else (root/config['instances']/instance.name).resolve()
        # A batch is not permission to read arbitrary graphs outside the declared directory.
        if selected.parent!=(root/config['instances']).resolve() or not selected.is_file():
            raise ValueError('batch instance must be in the configured public directory')
        # Keep exact user-selected graph/config boundaries for later creation.
        jobs.append({'campaign_id':name,'instance':selected,'config':config})
    # No mutation has occurred during preflight.
    return jobs


def run_batch(root,path,jobs=2):
    """Run at most jobs ordinary controllers together; return per-campaign outcomes.

    Only the explicit manifest graphs are searched. Ctrl-C requests durable stops
    for this launcher's own children and cleans only those owned PID incarnations.
    Logs/results stay per campaign; root solutions, branches and index are untouched.
    """
    # A user must deliberately opt into wider concurrency than the default two controllers.
    if type(jobs) is not int or not 1<=jobs<=32:
        raise ValueError('jobs must be an integer from 1 to 32')
    # Complete manifest validation precedes every filesystem/process mutation.
    queue=batch_entries(root,path)
    # These handles belong only to controllers actually launched by this invocation.
    active=[]
    # Completion means orchestration finished, not that all graph targets were reached.
    outcomes=[]
    # Interruption retains started campaign IDs; unstarted manifest entries remain untouched.
    interrupted=False
    try:
        # A small bounded pool does not launch a background agent per candidate.
        while queue or active:
            # Initialize only when a slot is available, preserving cumulative active-time accounting.
            while queue and len(active)<jobs:
                # User order is stable and all identities were prevalidated.
                entry=queue.pop(0)
                # Creation owns only this ID's lock, never a repository-wide campaign mutex.
                campaign=create_campaign(root,entry['instance'],entry['config'],entry['campaign_id'])
                # Console logs are private alongside raw Codex and numerical logs.
                log=campaign.path/'logs'
                # No competing controller owns these fresh exclusively reserved output paths.
                log.mkdir(parents=True,exist_ok=True)
                # The ordinary resume CLI handles ownership/recovery without resetting initialization costs.
                argv=[sys.executable,str(root/'evolve_search.py'),'resume','--campaign-id',entry['campaign_id'],'--preserve-stop-request']
                # Thread caps prevent simultaneous NumPy jobs from each claiming the entire host.
                environment=os.environ.copy()
                # Two-rank native methods retain their own MPI launch semantics.
                environment.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
                # Files avoid blocking PIPE buffers and interleaved multi-campaign console output.
                with (log/'controller.stdout').open('xb') as stdout,(log/'controller.stderr').open('xb') as stderr:
                    # New sessions allow scoped cleanup without signaling this terminal's unrelated jobs.
                    process=subprocess.Popen(argv,cwd=root,stdout=stdout,stderr=stderr,env=environment,start_new_session=True)
                # Start ticks distinguish an owned process from any future PID reuse.
                item={'campaign':campaign,'process':process,'tick':process_tick(process.pid),'started_at':time.time()}
                # Keep the handle before any receipt write so exceptions still clean this child.
                active.append(item)
                # This filename is not a numerical active_process registration that recovery would reap.
                atomic_json(log/'launcher.json',{'argv':argv,'pid':process.pid,'tick':item['tick'],'started_at':item['started_at']})
            # Only completed children release capacity for queued work.
            for item in active[:]:
                # Polling does not consume another solver or model slot.
                code=item['process'].poll()
                # Still-running controllers keep independent per-campaign budgets and locks.
                if code is None:
                    continue
                # Read the child's final durable state, never infer a cut from process success alone.
                result=Campaign(root,item['campaign'].path).status()
                # Exit code and target status are different recorded facts.
                outcome={'campaign_id':result['campaign_id'],'exit_code':code,'status':result['status'],
                         'target_met':result['archive']['metrics']['target_met'],'cut':result['archive']['metrics']['cut'],
                         'started_at':item['started_at'],'ended_at':time.time()}
                # No shared batch log or solution merge is performed.
                atomic_json(item['campaign'].path/'logs/launcher_result.json',outcome)
                # The final CLI response also exposes each independent outcome.
                outcomes.append(outcome)
                # Releasing only this completed process cannot affect any other terminal's controller.
                active.remove(item)
            # Short polls remain responsive without a busy loop.
            time.sleep(.1)
    # Do not start queued graphs after the user interrupts the batch.
    except KeyboardInterrupt:
        # Final response explicitly distinguishes a stopped batch from completed search.
        interrupted=True
    finally:
        # Exceptions and Ctrl-C stop only processes actually created by this launcher.
        for item in active:
            # A durable campaign stop allows its ordinary checkpoint/owned-worker cleanup path.
            atomic_json(item['campaign'].path/'stop.json',{'requested_at':time.time(),'reason':'batch launcher stopped'})
        # Use one bounded collective grace period, not a full timeout for every child serially.
        deadline=time.monotonic()+15
        # Normal controllers observe stop requests during their short process polls/reservations.
        for item in active:
            # A child that ignores orderly stop is still confined to its owned incarnation/tree.
            try:
                item['process'].wait(timeout=max(.1,deadline-time.monotonic()))
            # Cleanup is exact PID/start-tick ownership, never a global process-name match.
            except subprocess.TimeoutExpired:
                # Reuse the project's tested descendant-aware cleanup implementation.
                stop_process_group(item['process'].pid,item['tick'])
                # Reap the launched controller after signaling its owned descendants.
                item['process'].wait(timeout=5)
        # Interrupted children also retain individual exit/status receipts and visible IDs.
        for item in active:
            # Read only after the exact child has exited or been reaped.
            result=Campaign(root,item['campaign'].path).status()
            # Forced cleanup can leave an interrupted reservation for ordinary explicit resume recovery.
            outcome={'campaign_id':result['campaign_id'],'exit_code':item['process'].returncode,
                     'status':result['status'],'target_met':result['archive']['metrics']['target_met'],
                     'cut':result['archive']['metrics']['cut'],'started_at':item['started_at'],'ended_at':time.time()}
            # Each record belongs only to this controller's private launch log.
            atomic_json(item['campaign'].path/'logs/launcher_result.json',outcome)
            # No started campaign disappears from the interrupted batch's summary.
            outcomes.append(outcome)
    # A normal budget stop may leave targets unmet even though the launcher finished correctly.
    return {'status':'batch_interrupted' if interrupted else 'batch_complete','campaigns':outcomes,
            'all_targets_met':bool(outcomes) and all(row['target_met'] for row in outcomes) and not interrupted,
            'all_processes_succeeded':bool(outcomes) and all(row['exit_code']==0 for row in outcomes) and not interrupted,
            'unstarted_campaigns':[entry['campaign_id'] for entry in queue],'max_concurrent_campaigns':jobs,
            'commit_policy':'manual','public_solutions_updated':False}
