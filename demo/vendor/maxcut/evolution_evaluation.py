"""Frozen ladder receipts, sandboxed trials, monotone archive and recoverable publication."""
# Lossless copies preserve campaign-start assignment bytes and raw scoring receipts.
import shutil
# JSON is structured evidence, never a source of trusted objective values.
import json
# Exact fractions support threshold/gap checks without rounding-to-six-decimals selection.
from fractions import Fraction
# Paths bind one target graph and an explicitly selected fresh scoring tree.
from pathlib import Path
# The isolated interpreter runs unchanged evaluate.py and run_solver.py snapshots.
import sys
# Process environment is copied, never permanently modified for another experiment.
import os
# Timing includes setup, sandbox, all stages and verification.
import time
# NumPy owns original-order sign copies.
import numpy as np
# The professor's scorer and graph/sign functions remain unchanged.
import evaluate
# Original graph representation is authoritative for every returned witness.
from bm_solver import cut_value,load_graph,validate_signs,write_assignment
# Existing SHA/atomic helpers and provenance-aware assignment loading are retained.
from run_bm import atomic_json,file_sha256,load_assignment,metadata_path
# Content identity, official/exact metrics and owned process cleanup are protected infrastructure.
from evolution_common import SCORING_TIMING_POLICY as POLICY,CampaignError,assignment_bytes,identity,immutable_json,metrics,owned_process
# Immutable artifact verification prevents source/config replacement after admission.
from evolution_candidates import load_artifact

# Campaign-start input selection is explicit and frozen for every later assembled receipt.
def freeze_inputs(root,campaign,config,instance):
    """Freeze refs/selected assignments; return immutable one-target context.

    Args Paths root/campaign and selected public instance, resolved config. Prefer
    best valid bytes among configured retained set and root public destination;
    missing/invalid OTHER graphs remain visible failures. Example trap fixture.
    Writes only campaign/frozen and initial receipt, never public assignments.
    """
    # Resolve actual public input/reference directories inside this repository.
    instances=(root/config['instances']).resolve()
    # References are copied and hashed, never altered by search.
    references=(root/config['references']).resolve()
    # An explicit name is interpreted only inside the configured public-instance folder.
    selected=Path(instance)
    # Relative full paths and short names are both accepted without searching a second graph.
    target=(root/selected).resolve() if (root/selected).is_file() else (instances/selected.name).resolve()
    # A campaign must refer to exactly one of the configured original public files.
    if target.parent!=instances or not target.is_file() or not target.is_relative_to(root):
        # Scratch/live tests use an explicit separate fixture repository with the same interface.
        raise ValueError('select one instance inside the configured instances directory')
    # Preserve the full reference metadata including exact/nonexact status and source.
    refs=json.loads(references.read_text())
    # Missing target references cannot be repaired by an invented normalization.
    if target.name not in refs:
        # A campaign cannot establish its requested score without the actual mapping.
        raise ValueError('selected graph missing reference')
    # A dedicated frozen tree keeps all other assignments immutable within comparisons.
    frozen=campaign/'frozen'
    # Exclusive creation prevents reuse of a partial earlier input snapshot.
    (frozen/'solutions').mkdir(parents=True,exist_ok=False)
    # Byte-exact full reference mapping is part of recoverable evidence.
    shutil.copyfile(references,frozen/'references.json')
    # Selected original assignments and their source choices are independently auditable.
    selections={}
    # Public original-byte hashes protect all graphs, even if only one is optimized.
    graph_hashes={}
    # Read and hash the complete current source set; never run a solver for another graph.
    for path in sorted(instances.glob('*.txt')):
        # Graph order/size is interpreted by the unchanged loader.
        graph=load_graph(path)
        # Every instance byte identity survives across resume and scoring.
        graph_hashes[path.name]=file_sha256(path)
        # Valid candidates are actual existing assignment files, not synthetic success outputs.
        choices=[]
        # Both roots are declared config values, not a repository-wide best-of-experiments search.
        sources={str((root/config['baseline_solutions']/path.name).resolve()),str((root/config['public_solutions']/path.name).resolve())}
        # Individual assignment symlinks must also remain within the configured repository boundary.
        if any(not Path(source).is_relative_to(root) for source in sources):
            # No unrelated numeric file is read as an assignment or copied into committed evidence.
            raise ValueError('assignment source escapes checkout')
        # Deterministic source ordering makes equal-quality initial selection reproducible.
        for source in sorted(sources):
            # The original assignment loader verifies any existing graph/SHA sidecar.
            try:
                # No new assignment is written while inspecting current solutions.
                signs,value,info=load_assignment(Path(source),graph,graph_hashes[path.name])
                # Quality is independently recomputed, never copied from a previous JSON history.
                choices.append((value,source,signs,info))
            # Invalid/missing files remain visible in source records below.
            except (OSError,ValueError,TypeError):
                # No successful substitute is synthesized for a different graph.
                pass
        # Preserve raw source existence/hashes even for rejected/missing assignments.
        source_records=[{'path':source,'sha256':file_sha256(source) if Path(source).is_file() else None} for source in sorted(sources)]
        # Use an actual existing valid witness if any source provides one.
        if choices:
            # Strict higher cut wins; source spelling only breaks exact quality ties.
            value,source,signs,info=max(choices,key=lambda item:(item[0],item[1]))
            # Frozen scoring folders reuse these exact bytes for all nontarget graphs.
            shutil.copyfile(source,frozen/'solutions'/path.name)
            # Sidecars are not needed by the official scorer; provenance is explicitly captured here.
            selections[path.name]={'selected_source':source,'sha256':file_sha256(frozen/'solutions'/path.name),'cut':value,'status':'ok','sources':source_records}
        # A bad source remains bad/missing instead of becoming a fabricated valid assignment.
        else:
            # Preserve invalid raw bytes if available, so evaluate.py reports its actual invalid behavior.
            existing=next((source for source in sorted(sources) if Path(source).is_file()),None)
            # Missing others stay absent; their official score remains zero.
            if existing is not None:
                # This copy is evidence of an invalid starting file, never a validation claim.
                shutil.copyfile(existing,frozen/'solutions'/path.name)
            # Explicit failure metadata makes the complete-ladder limitations visible.
            selections[path.name]={'selected_source':existing,'sha256':file_sha256(frozen/'solutions'/path.name) if existing else None,'cut':None,'status':'invalid_or_missing','sources':source_records}
    # Target archive initialization may use a validated trivial fallback, unlike unrelated graph accounting.
    graph=load_graph(target)
    # Try the selected actual target file first.
    try:
        # Frozen bytes have no stale sidecar and are checked against original graph/order.
        initial,value,info=load_assignment(frozen/'solutions'/target.name,graph,graph_hashes[target.name])
        # This is the actual existing target incumbent, not a numerical candidate result.
        origin='existing_selected_target_solution'
    # A missing/corrupt selected target is explicitly allowed a trivial initialization.
    except (OSError,ValueError,TypeError):
        # All equal signs are always feasible, with original cut zero.
        initial=np.ones(graph.node_count,dtype=np.int8)
        # No search credit is assigned to the fallback.
        origin='validated_all_plus_initial_fallback'
    # Validate denominator and exact/official target comparison before any solver/model work.
    initial_metrics=metrics(target,initial,refs[target.name],config['target_score'])
    # The original public destination may differ from the latest retained initial folder.
    destination=root/config['public_solutions']/target.name
    # Complete initial ladder accounting remains the unchanged official function's output.
    baseline=evaluate.score_folder(frozen/'solutions',instances,frozen/'references.json')
    # This receipt reports actual invalid/missing other assignments without clipping or imputation.
    atomic_json(campaign/'initial_ladder_score.json',baseline)
    # A target-only initial fallback has its own assembled score, separate from the actual incomplete starting folder.
    initial_assembled=frozen/'initial_assembled_solutions'
    # Other missing/invalid files remain exactly as frozen, with no successful imputation.
    shutil.copytree(frozen/'solutions',initial_assembled)
    # Only the explicitly declared target initialization supplies new feasible labels.
    write_assignment(initial_assembled/target.name,initial,graph)
    # Official aggregation reports the exact initialized archive's assembled ladder quality.
    archive_baseline=evaluate.score_folder(initial_assembled,instances,frozen/'references.json')
    # Preserve both distinct receipts instead of describing a missing initial target as an archive witness.
    atomic_json(campaign/'initial_archive_ladder_score.json',archive_baseline)
    # Canonical initial labels seed the archive even when original text used '+1'.
    (frozen/'initial_assignment.txt').write_bytes(assignment_bytes(initial))
    # Publication CAS is scoped to only the selected original destination and its metadata.
    context={'root':str(root),'instance':str(target),'instance_name':target.name,'instances':str(instances),'graph_sha256':graph_hashes[target.name],
             'graph_hashes':graph_hashes,'references_original':str(references),'references_sha256':file_sha256(references),
             'references':str(frozen/'references.json'),'reference':refs[target.name],'selections':selections,
             'initial_assignment':str(frozen/'initial_assignment.txt'),'initial_origin':origin,'initial_metrics':initial_metrics,
             'original_starting_ladder_overall':baseline['overall'],'initial_ladder_overall':archive_baseline['overall'],'public_destination':str(destination),
             'public_initial_sha256':file_sha256(destination) if destination.exists() else None,
             'public_metadata_initial_sha256':file_sha256(metadata_path(destination)) if metadata_path(destination).exists() else None}
    # Context itself is immutable across all rounds/resume operations.
    immutable_json(campaign/'context.json',context)
    # No public graph besides this named target can ever enter numerical evaluation.
    return context

# Inputs, frozen alternatives and source graph bytes remain fixed throughout the campaign.
def verify_context(campaign,context):
    """Raise integrity_error if graph/ref/frozen-label bytes changed; no writes or solvers.

    Example verify_context before every promotion/trial and after recovery.
    """
    # Reference identity must survive in both original and copied mapping.
    if file_sha256(context['references_original'])!=context['references_sha256'] or file_sha256(context['references'])!=context['references_sha256']:
        # A shifted reference would change both the target and displayed quality.
        raise CampaignError('integrity_error','reference identity changed')
    # Check every public graph because complete scoring receipts use the full ladder.
    for name,digest in context['graph_hashes'].items():
        # No candidate may alter a different graph to inflate assembled overall.
        if file_sha256(Path(context['instances'])/name)!=digest:
            # Preserve the changed file and stop rather than silently reset user work.
            raise CampaignError('integrity_error','public graph identity changed: '+name)
    # Frozen campaign-start assignment bytes cannot follow later archive improvements.
    for name,selection in context['selections'].items():
        # Missing labels remain absent, and invalid copies remain the same invalid bytes.
        path=campaign/'frozen/solutions'/name
        # Changed or newly synthesized others invalidate assembled ladder claims.
        if (file_sha256(path) if path.exists() else None)!=selection['sha256']:
            # The raw receipt remains available for diagnosis.
            raise CampaignError('integrity_error','frozen ladder assignment changed: '+name)

# Every variant's ladder receipt uses that variant's own verified target labels.
def assembled_score(campaign, context, signs, directory, seconds=POLICY['recovery_verification_seconds']):
    """Bound preparation+process+JSON verification; retain outcome on every failure."""
    started = time.monotonic()
    deadline = started + seconds
    argv = [sys.executable, str(campaign / 'base/evaluate.py'), '--solutions',
            str(directory / 'assembled_solutions'), '--instances', context['instances'],
            '--refs', context['references'], '--json', str(directory / 'ladder_score.json')]
    request = {'argv': argv, 'allowance_seconds': seconds, 'target': context['instance_name'],
               'policy_version': POLICY['version'], 'started_at': time.time()}
    immutable_json(directory / 'score_request.json', request)
    outcome = {'process_started': False, 'exit_code': None, 'timed_out': False, 'stopped': False}
    receipt = None
    failure = None
    try:
        if (campaign / 'stop.json').exists():
            outcome['stopped'] = True
            raise CampaignError('interrupted', 'stop requested before official scoring')
        folder = directory / 'assembled_solutions'
        shutil.copytree(campaign / 'frozen/solutions', folder)
        write_assignment(folder / context['instance_name'], signs, load_graph(context['instance']))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            outcome['timed_out'] = True
            raise CampaignError('verification_timeout', 'official scoring preparation exhausted its verification allowance')
        outcome = {**owned_process(argv, campaign, remaining, directory / 'score.stdout',
                    directory / 'score.stderr', stop_path=campaign / 'stop.json',
                    registration=directory / 'active_process.json'), 'process_started': True}
        if outcome['stopped']:
            raise CampaignError('interrupted', 'official scoring stopped by user')
        if outcome['timed_out']:
            raise CampaignError('verification_timeout', 'official scorer exceeded its verification allowance')
        if outcome['exit_code'] != 0:
            raise CampaignError('verification_failed', 'official scorer exited with code ' + str(outcome['exit_code']))
        receipt = json.loads((directory / 'ladder_score.json').read_text())
        target = receipt['instances'][context['instance_name']]
        if target['status'] != 'ok':
            raise CampaignError('integrity_error', 'official scorer rejected the target assignment: ' + target['status'])
        if time.monotonic() > deadline:
            outcome['timed_out'] = True
            raise CampaignError('verification_timeout', 'official scoring output parsing exceeded its allowance')
    except BaseException as error:
        cleanup_receipt = directory / 'score.stderr.cleanup.json'
        if cleanup_receipt.exists():
            # owned_process failed after launch and retained exact ownership evidence.
            outcome.update(process_started=True, cleanup_failure_path=str(cleanup_receipt))
        failure = {'state': getattr(error, 'state', 'interrupted' if isinstance(error, KeyboardInterrupt) else 'verification_failed'),
                   'type': type(error).__name__, 'reason': str(error)}
    finally:
        outcome.update(total_elapsed_seconds=time.monotonic() - started,
                       allowance_seconds=seconds, argv=argv, failure=failure)
        atomic_json(directory / 'score_process.json', outcome)
    if failure:
        raise CampaignError(failure['state'], failure['reason'] + '; see ' + str(directory / 'score_process.json'))
    immutable_json(directory / 'ladder_receipt.json', {
        'label': 'assembled ladder score, target-only reevaluation', 'target': context['instance_name'],
        'frozen_other_assignments': {name: value['sha256'] for name, value in context['selections'].items() if name != context['instance_name']},
        'argv': argv, 'timing': outcome, 'overall': receipt['overall'], 'timing_policy': POLICY,
        'not_evidence_of_other_graph_solver_runs': True})
    return receipt

# The controller owns the only writable directory; research source and repository stay read-only.
def launch_trial(campaign,context,candidate_id,frozen,seed,seconds,work_caps,directory,stagnation=0,check=False,stop_path=None):
    """Run one sandboxed aggregate candidate/check process; return its real observation.

    Fresh directory, original frozen signs/hash and explicit seed/budget are inputs.
    Example paired parent/child calls share frozen bytes. Bubblewrap unavailable
    means blocked integrity, never unsandboxed candidate-code execution.
    """
    # Validate immutable source/config before the numerical worker can import it.
    record=load_artifact(campaign,candidate_id)
    # A unique attempt ID is embodied by an exclusively reserved path.
    directory.mkdir(parents=True,exist_ok=False)
    # Only this scratch work directory is writable inside the numerical sandbox.
    work=directory/'work'
    # File-based request/result avoids fragile stdout parsing.
    work.mkdir()
    # Serial native backends need writable temporary MPI/cache files in their owned scope.
    (work/'tmp').mkdir()
    # Every work unit and common incumbent is preserved verbatim in the request.
    request={'campaign':str(campaign),'artifact_id':candidate_id,'instance':context['instance'],'graph_sha256':context['graph_sha256'],
             'initial_assignment':list(frozen),'frozen_assignment_sha256':identity(list(frozen)),'seed':seed,'seconds':max(0,seconds*.9),
             'work_caps':work_caps,'stagnation':stagnation,'check':check,'work':str(work)}
    # Exact immutable request identity also defines safe replay/cache conditions.
    immutable_json(directory/'request.json',request)
    # Missing filesystem isolation is not permission to execute arbitrary mutation code unprotected.
    bubblewrap=shutil.which('bwrap')
    # Require the tested filesystem sandbox for both baseline and research workers.
    if bubblewrap is None:
        # Doctor reports the actionable host prerequisite.
        raise CampaignError('integrity_error','Bubblewrap is required for read-only candidate execution')
    # The whole filesystem is read-only except one owned numerical output directory.
    argv=[bubblewrap,'--die-with-parent','--ro-bind','/','/','--bind',str(work),str(work),'--chdir',str(work),
          sys.executable,str(campaign/'base/evolution_worker.py'),str(directory/'request.json')]
    # Record actual argv/environment-relevant scope without leaking authentication contents.
    immutable_json(directory/'command.json',argv)
    # Environment is copied; no global thread/cache policy is changed.
    environment=os.environ.copy()
    # Native MPI and optional libraries write only into the declared scratch directory.
    environment.update(TMPDIR=str(work/'tmp'),XDG_CACHE_HOME=str(work/'tmp'),PYTHONDONTWRITEBYTECODE='1',MAXCUT_EVOLUTION_WORKER='1')
    # Fixed total parent timeout covers all subprocesses and every refinement stage.
    outcome=owned_process(argv,work,seconds,directory/'worker.stdout',directory/'worker.stderr',environment=environment,
                          registration=directory/'active_process.json',stop_path=stop_path)
    # Recover only a genuinely serialized worker result; do not borrow the archive and call it a result.
    result=json.loads((work/'result.json').read_text()) if (work/'result.json').exists() else None
    # Explicit failure/censorship and no-assignment outcomes are not silently omitted from rankings.
    observation={'artifact_id':candidate_id,'process':outcome,'result':result,'valid':False,'eligible_for_selection':False,
                 'frozen_assignment_sha256':request['frozen_assignment_sha256'],'effective_seed':seed}
    # Admission checks have a separate documented meaning from target improvement trials.
    if check:
        # A timed-out or failed correctness run cannot admit code based on a partial success list.
        observation['valid']=outcome['exit_code']==0 and bool(result and result.get('passed'))
    # Only actual returned target witnesses can be independently scored and harvested.
    elif result and not result.get('failed'):
        # Raw graph/artifact/frozen-state identities must match this precise execution request.
        if result['graph_sha256']!=context['graph_sha256'] or result['artifact_id']!=candidate_id or result['frozen_assignment_sha256']!=request['frozen_assignment_sha256']:
            # Never repair a mismatched candidate identity by relabeling its output.
            raise CampaignError('integrity_error','worker graph/artifact/frozen identity mismatch')
        # Existing original evaluator verifies the numerical assignment.
        graph=load_graph(context['instance'])
        # Invalid signs/order cannot be promoted or ranked.
        signs=validate_signs(result['assignment'],graph.node_count)
        # Exact direct evaluator agreement is mandatory, independently of native reported performance.
        if result['cut']!=cut_value(graph,signs):
            # False objectives stop the experiment rather than become competitive values.
            raise CampaignError('integrity_error','false candidate cut')
        # A valid candidate witness remains useful even when not eligible to win selection.
        observation['valid']=True
        # Only actual native/local work counts as comparative search evidence.
        observation['eligible_for_selection']=bool(result['search_witness']) and outcome['exit_code']==0
        # Full-precision target metrics remain independent of proof/status and artifact fitness.
        observation['metrics']=metrics(context['instance'],signs,context['reference'],request.get('target_score',1))
    # Reload candidate identity to detect outside edits during execution too.
    load_artifact(campaign,candidate_id)
    # Raw output/request plus this verified observation are durable evidence.
    atomic_json(directory/'observation.json',observation)
    # The controller adds official complete-folder scoring and cumulative budget receipts.
    return observation

# Archive content files are immutable while the best pointer changes monotonically.
def archive_witness(campaign,context,signs,provenance,target_score):
    """Save validated content-addressed assignment; return metadata, no public writes.

    Example both selected and unselected admitted candidates can contribute cut 10.
    Caller compares exact cut fractions before moving the archive best pointer.
    """
    # Original graph fixes node ordering and direct objective.
    graph=load_graph(context['instance'])
    # Own signs before serialization to prevent mutation after validation.
    checked=validate_signs(signs,graph.node_count)
    # Raw canonical bytes have a stable source-independent assignment identity.
    data=assignment_bytes(checked)
    # A SHA of exact assignment bytes identifies recovery backups and improvements.
    import hashlib
    # This is a byte hash, not a floating cut hash.
    digest=hashlib.sha256(data).hexdigest()
    # New archive entries never replace earlier content.
    path=campaign/'archive'/(digest+'.txt')
    # Only this campaign's private archive parent is created.
    path.parent.mkdir(exist_ok=True)
    # Reuse identical labels without fabricating a new solution discovery.
    if path.exists() and path.read_bytes()!=data:
        # An impossible digest collision/corruption is a consistency blocker.
        raise CampaignError('integrity_error','archive content hash collision')
    # Existing identical content is already durable; otherwise publish only canonical valid bytes.
    if not path.exists():
        # All signs were validated before any archive write.
        path.write_bytes(data)
    # Recompute official/exact metrics from the reloaded stored labels.
    reloaded,value,info=load_assignment(path,graph,context['graph_sha256'])
    # Provenance is separate for repeated discovery of the same content.
    return {'sha256':digest,'path':str(path),'metrics':metrics(context['instance'],reloaded,context['reference'],target_score),'provenance':provenance}

# Public publication is a write-ahead compare-and-swap, not a last-writer-wins output.
def publish(campaign,context,archive,round_dir,state,recovery=False):
    """Prepare/reconcile atomic strict improvement of only the target and its sidecar.

    Inputs explicit validated archive/state/context. Writes backup, WAL, temporary
    sibling then public destination; never writes another graph. Example recovery
    after file replace reconstructs the sidecar from the known new content hash.
    """
    # Publication must preserve graph/ref/frozen-set identity.
    verify_context(campaign,context)
    # Only the campaign's declared destination can change.
    destination=Path(context['public_destination'])
    # Recheck resolved public scope at publication time in case a directory symlink changed mid-campaign.
    if not destination.resolve().is_relative_to(Path(context['root']).resolve()):
        # Unknown external output scope is a consistency error, never a destination to overwrite.
        raise CampaignError('integrity_error','public destination escapes checkout')
    # A persisted promotion describes exactly one intended old->new transition.
    wal=round_dir/'promotion.json'
    # Recovery reads the prepared transition rather than synthesizing a new one from current filenames.
    if wal.exists():
        # Identity fields are immutable once publication is prepared.
        intent=json.loads(wal.read_text())
        # Archive source must still contain the intended validated bytes.
        archive_path=Path(intent['new_path'])
        # Unknown content is never installed during recovery.
        if file_sha256(archive_path)!=intent['new_sha256']:
            # Preserve both versions for diagnosis.
            raise CampaignError('integrity_error','prepared archive bytes corrupted')
    # A new strict improvement needs independent current-destination checks.
    else:
        # Current destination is checked against the campaign's expected publication history.
        current=file_sha256(destination) if destination.exists() else None
        # External edits are user work, not a stale file to overwrite.
        if current!=state['public_sha256']:
            # Stop before preparing or publishing any replacement.
            raise CampaignError('integrity_error','public destination changed outside campaign')
        # A current valid better/tied assignment must never be degraded.
        if destination.exists():
            # Existing sidecars are verified before deciding on a strict improvement.
            old,old_cut,info=load_assignment(destination,load_graph(context['instance']),context['graph_sha256'])
            # Compare exact finite-decimal cut values, not six-digit scores or a guessed epsilon.
            previous=metrics(context['instance'],old,context['reference'],archive['metrics']['target_score'])
            # Equality leaves bytes/inode/sidecar unchanged.
            if Fraction(archive['metrics']['exact_cut'])<=Fraction(previous['exact_cut']):
                # Retention is explicit evidence, not a claimed publication.
                return {'status':'not_a_strict_public_improvement','sha256':current}
        # Archive source is independently reloaded and matched before intent publication.
        archive_path=Path(archive['path'])
        # Current public bytes are preserved by content hash before replacement.
        backup=campaign/'public_backups'
        # Backups belong only to this campaign.
        backup.mkdir(exist_ok=True)
        # Missing original destinations need no invented backup.
        if destination.exists():
            # Copy exact old text, preserving even alternate '+1' formatting.
            shutil.copyfile(destination,backup/(current+'.txt'))
        # Record the only legal old/new hashes before any public mutation.
        intent={'destination':str(destination),'old_sha256':current,'new_sha256':archive['sha256'],'new_path':str(archive_path),
                'graph_sha256':context['graph_sha256'],'old_metadata_sha256':file_sha256(metadata_path(destination)) if metadata_path(destination).exists() else None}
        # Immutable WAL supports crashes before/after atomic file replacement.
        immutable_json(wal,intent)
    # A persisted intent cannot redirect recovery to a different graph, destination or archive namespace.
    if intent['destination']!=str(destination) or intent['graph_sha256']!=context['graph_sha256'] or archive_path.parent.resolve()!=(campaign/'archive').resolve() or file_sha256(archive_path)!=intent['new_sha256']:
        # Preserve evidence rather than trusting stale or edited WAL metadata.
        raise CampaignError('integrity_error','promotion identity mismatch')
    # Recompute actual assignment quality before either new publication or recovery.
    labels,value,info=load_assignment(archive_path,load_graph(context['instance']),context['graph_sha256'])
    # A sidecar edit is user work too, even when solution bytes are unchanged.
    current_metadata=file_sha256(metadata_path(destination)) if metadata_path(destination).exists() else None
    # The canonical new sidecar is the only additional allowed metadata state after a partial publication.
    graph=load_graph(context['instance'])
    # This exact metadata is shared by both the CAS comparison and eventual atomic sidecar replacement.
    new_metadata={'instance_sha256':context['graph_sha256'],'assignment_sha256':intent['new_sha256'],
                  'node_count':graph.node_count,'edge_count':len(graph.edges),'node_order':'original input node order'}
    # If solution replacement happened before a crash, the sidecar may be either old or already finalized.
    installed_new=file_sha256(destination)==intent['new_sha256'] if destination.exists() else False
    # Compare structured known-new metadata without requiring a particular JSON whitespace format.
    known_new_metadata=installed_new and metadata_path(destination).exists() and json.loads(metadata_path(destination).read_text())==new_metadata
    # A changed unknown sidecar blocks publication and recovery rather than being silently overwritten.
    if current_metadata!=intent['old_metadata_sha256'] and not known_new_metadata:
        # The caller can investigate the conflicting user change without losing it.
        raise CampaignError('integrity_error','public metadata CAS conflict')
    # Reconciliation permits only the known old or already-published new state.
    current=file_sha256(destination) if destination.exists() else None
    # A new unrelated public file is never overwritten on retry.
    if current not in (intent['old_sha256'],intent['new_sha256']):
        # Both archive and public bytes remain available for manual consistency review.
        raise CampaignError('integrity_error','promotion CAS conflict')
    # The destination directory is explicitly selected and graph-scoped.
    destination.parent.mkdir(parents=True,exist_ok=True)
    # An already-installed assignment after a crash must not be replaced again.
    if current!=intent['new_sha256']:
        # A same-directory staging file makes replace atomic on the target filesystem.
        temporary=destination.with_name('.'+destination.name+'.evolution.tmp')
        # Never consume an unrelated stale temporary file as a candidate witness.
        if temporary.exists() and file_sha256(temporary)!=intent['new_sha256']:
            # A collision is an explicit consistency blocker.
            raise CampaignError('integrity_error','promotion temporary collision')
        # Source bytes already passed graph/sign/official validation before the WAL.
        temporary.write_bytes(archive_path.read_bytes())
        # Revalidate actual staged bytes independently before replacing the public file.
        labels,value,info=load_assignment(temporary,load_graph(context['instance']),context['graph_sha256'])
        # A final compare-and-swap inspection catches user edits during staging.
        if (file_sha256(destination) if destination.exists() else None)!=intent['old_sha256']:
            # The original destination wins the race; no overwrite occurs.
            raise CampaignError('integrity_error','public destination changed during staging')
        # Atomic replacement publishes only a complete validated original-format assignment.
        temporary.replace(destination)
    # Sidecar recovery is allowed only for the known prepared old/new transition.
    graph=load_graph(context['instance'])
    # Same standard metadata format keeps existing loaders functional after publication.
    atomic_json(metadata_path(destination),{'instance_sha256':context['graph_sha256'],'assignment_sha256':intent['new_sha256'],
                'node_count':graph.node_count,'edge_count':len(graph.edges),'node_order':'original input node order'})
    # Final reloading verifies both assignment and reconstructed sidecar.
    labels,value,info=load_assignment(destination,graph,context['graph_sha256'])
    # Durable receipt distinguishes idempotent recovery from new numerical improvement.
    receipt={'status':'published','sha256':file_sha256(destination),'recovered':recovery}
    # Atomic receipt can be reconciled with a later round commit by content hash.
    if not (round_dir/'promotion_receipt.json').exists():
        # A recovery must not rewrite a receipt already pinned by a closed round manifest.
        atomic_json(round_dir/'promotion_receipt.json',receipt)
    # Existing receipt content must name this precise published assignment.
    elif json.loads((round_dir/'promotion_receipt.json').read_text())['sha256']!=intent['new_sha256']:
        # A conflicting historical receipt cannot be silently repaired.
        raise CampaignError('integrity_error','promotion receipt hash conflict')
    # Controller checkpoint tracks the new expected public destination identity.
    state['public_sha256']=intent['new_sha256']
    # No other public assignment was opened for writing.
    return receipt
