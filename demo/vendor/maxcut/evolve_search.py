"""Launch, inspect, resume, stop or explicitly test ONE persistent graph campaign."""
# Conventional argparse keeps campaign operations explicit instead of a service/dashboard.
import argparse
# JSON configs/status/receipts are portable and preserve full precision.
import json
# Environment guard prevents recursive controllers from model/numerical subprocesses.
import os
# Local executable discovery uses the standard library without dynamic import tricks.
import shutil
# Paths bind the actual checkout or an explicitly isolated fixture repository.
from pathlib import Path
# Temporary scratch diagnostics do not modify official inputs/solutions.
import tempfile
# Native Git/CLI diagnostics use fixed argv without shell interpolation.
import subprocess
# Timing reports real read-only planning/doctor overhead.
import time
# NumPy reproduces official mean-within-rung/mean-across-rungs projections.
import numpy as np
# The unchanged professor scorer supplies actual current solution quality.
import evaluate
# Original graph/assignment loading independently verifies current incumbents.
from bm_solver import load_graph
# Existing finite atomic JSON is reused for stop/config revision records.
from run_bm import atomic_json,file_sha256,load_assignment
# Current feature discovery is read-only and reflects actual installed dependencies.
from solver_portfolio import list_solvers
# Framework contracts/limits remain immutable during a campaign.
from evolution_common import CampaignError,CampaignLock,configuration,identity,metrics,owned_process,protected_manifest,verify_manifest
# Real graph eligibility never guesses warm support or topology from method names.
from evolution_candidates import initial_configurations,eligibility
# Actual Codex probes make no model call unless explicit smoke is requested.
from evolution_codex import inspect_codex
# Plain controller manages one named graph/branch, never the whole ladder automatically.
from evolution_controller import Campaign,create_campaign

# All default paths are relative to the actual validated checkout.
ROOT=Path(__file__).resolve().parent

# Read-only planning makes screening scope/cost and baseline accounting reviewable before launch.
def plan(root,instance,config):
    """Return one-graph compatibility/target/full-ladder projection; no writes/solvers/model calls.

    Args root/instance Paths or name and resolved config. Example plan for a
    1000-node public graph. Scoring uses actual official folders, never a partial
    folder called a full ladder score. Bad reference/inputs fail explicitly.
    """
    # Planning respects the same repository data boundary as actual campaign initialization.
    for key in ('instances','references','baseline_solutions','public_solutions'):
        # Existing symlink parents are resolved before inspecting any unrelated file.
        if not (root/config[key]).resolve().is_relative_to(root.resolve()):
            # Read-only planning must not silently broaden declared input scope either.
            raise ValueError('configured data path escapes checkout: '+key)
    # Short names resolve only within the configured public-instance folder.
    instances=(root/config['instances']).resolve()
    # An explicit relative input path remains constrained to that exact directory.
    target=(root/instance).resolve() if (root/instance).is_file() else (instances/Path(instance).name).resolve()
    # Read-only inspection cannot silently start another graph or accept an unrelated file.
    if target.parent!=instances or not target.is_file():
        # Scratch tests provide an explicit separate fixture root.
        raise ValueError('instance must be one configured public input')
    # Original graph features drive actual eligibility guards.
    graph=load_graph(target)
    # Actual references establish the default target deficit and exact/nonexact metadata.
    refs=json.loads((root/config['references']).read_text())
    # Both configured complete folders are scored by the unchanged official aggregation.
    reports=[evaluate.score_folder(root/config[key],instances,root/config['references']) for key in ('baseline_solutions','public_solutions')]
    # Project the declared per-graph best valid current selection without writing an assembled folder.
    selected={}
    # Missing/invalid other files remain their actual failed zero-score records.
    for name in reports[0]['instances']:
        # Best actual current cut determines selected input, not reference score rounding.
        choices=[report['instances'][name] for report in reports if report['instances'][name]['cut'] is not None]
        # No labels/score are synthesized when both actual sources fail.
        selected[name]=max(choices,key=lambda item:item['cut']) if choices else reports[0]['instances'][name]
    # Reproduce official mean-within-rung semantics for a read-only projection only.
    rungs={r:float(np.mean([item['score'] for item in selected.values() if item['rung']==r])) for r in sorted({item['rung'] for item in selected.values()})}
    # Obtain actual target labels using the same declared source selection.
    choices=[]
    # Each actual incumbent is provenance-checked before its quality is displayed.
    for key in ('baseline_solutions','public_solutions'):
        # Invalid/missing target files may use only the explicitly labeled trivial fallback.
        try:
            # No output assignment is written during planning.
            signs,value,info=load_assignment(root/config[key]/target.name,graph,file_sha256(target))
            # Source choice is deterministic on exact quality ties.
            choices.append((value,str(root/config[key]/target.name),signs))
        # Preserve bad starting-state visibility rather than invent successful source bytes.
        except (OSError,ValueError,TypeError):
            # A later initialized campaign records each actual source hash/failure.
            pass
    # All-plus is a feasible fallback ONLY for the explicitly selected target.
    current=max(choices,key=lambda item:(item[0],item[1]))[2] if choices else np.ones(graph.node_count,dtype=np.int8)
    # Independent exact-vs-official threshold diagnosis is not rounded away.
    current_metrics=metrics(target,current,refs[target.name],config['target_score'])
    # Each actual installed entry gets a concrete compatibility or exclusion record.
    eligible,excluded=[],{}
    # Discovery doesn't launch native solvers or import heavyweight optional models.
    for backend,features in list_solvers().items():
        # Explicit screening subsets are transparent; default screens all compatible entries.
        if config['screen_solvers'] is not None and backend not in config['screen_solvers']:
            # A fixture/user filter is not evidence of measured incompatibility.
            excluded[backend]='excluded by explicit screen_solvers setting'
            # No work estimate includes the excluded entry.
            continue
        # Absent native/source entries have no fabricated config or performance measurement.
        if not features['available']:
            # Record actual current installation reason.
            excluded[backend]=features['availability_reason']
            # QuBowl is not mapped to generic SCIP.
            continue
        for settings in initial_configurations(root,backend,config):
            compatible,reason=eligibility(graph,backend,settings,config)
            if compatible:
                eligible.append({'backend':backend,'features':features,'config':settings,'performance':'unmeasured on target until campaign screening'})
            else:
                excluded[backend+':'+identity(settings)[:8]]=reason
    # Default caps can stop long before twenty ordinary rounds; this estimate makes that explicit.
    screening=len(eligible)*config['screen_trial_seconds']
    # A maximal ordinary batch compares parents+children twice at the same end-to-end cap.
    ordinary=config['repeats']*(config['survivors']+config['children_per_round'])*config['trial_seconds']
    # Mutation regression checks and model calls also consume overall wall/solver exposure.
    checks=config['children_per_round']*config['validation_seconds']
    # Code/config/native prerequisites have an inspectable content identity before any campaign starts.
    source_manifest=protected_manifest(root)
    # Record real checkout identity without creating a branch, commit or public solver result.
    starting_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    # Return a read-only report; initialization will create actual assembled scoring receipts later.
    return {'starting_head':starting_head,'source_identity':identity(source_manifest),'source_manifest':source_manifest,'instance':str(target),'graph_sha256':file_sha256(target),'current_target':current_metrics,
            'target_initial_fallback':not bool(choices),'read_only_projected_assembled_ladder_score':float(np.mean(list(rungs.values()))) if rungs else 0.,
            'rungs':rungs,'failed_other_assignments':[name for name,item in selected.items() if item['status']!='ok'],
            'eligible':eligible,'excluded':excluded,'screening_solver_seconds_upper_bound':screening,
            'ordinary_round_numerical_seconds_upper_bound':ordinary,'ordinary_round_check_seconds_upper_bound':checks,
            'max_wall_seconds':config['max_wall_seconds'],'max_solver_call_slots_including_checks':config['max_solver_trials'],
            'note':'First reached cap wins. Default limits need not fund all rounds; no public optimization or model call was launched.'}

# Doctor separates host/owned-process diagnostics from an explicitly requested real model smoke.
def doctor(root,config):
    """Return actual CLI/portfolio/git/sandbox/cleanup health; no LLM call.

    Example evolve_search.py doctor. Creates only a temporary two-second local
    sleeping-process diagnostic; reports blocked Snap/runtime access precisely.
    """
    # Current runtime capabilities include real native paths/constraints.
    portfolio=list_solvers()
    # Local version/help probing does not invoke a model or read authentication secrets.
    codex=inspect_codex(config['codex_executable'])
    # Git identity and current branch are read-only diagnostic inputs.
    git={}
    # Commit feasibility distinguishes identity from a promise about all future hooks/permissions.
    for key,argv in {'head':['git','rev-parse','HEAD'],'branch':['git','branch','--show-current'],'author':['git','var','GIT_AUTHOR_IDENT'],'committer':['git','var','GIT_COMMITTER_IDENT']}.items():
        # Native commands use exact argv and bounded read-only execution.
        completed=subprocess.run(argv,cwd=root,capture_output=True,text=True,timeout=5)
        # Actual stderr/exit code makes missing config actionable.
        git[key]={'value':completed.stdout.strip(),'exit_code':completed.returncode,'error':completed.stderr.strip()}
    # A filesystem sandbox probe makes no numerical/model call.
    bubblewrap=shutil.which('bwrap')
    # Raw capture/reaping are checked in a fresh scratch directory, not public solutions.
    with tempfile.TemporaryDirectory(prefix='maxcut-evolution-doctor-') as temporary:
        # These diagnostic outputs are local and disposable, not campaign evidence.
        directory=Path(temporary)
        # A short owned sleeping process exercises timeout and actual descendant-aware cleanup.
        import sys
        # It prints no secrets or user data and receives no model-generated shell arguments.
        cleanup=owned_process([sys.executable,'-c',"import sys,time; print('capture-ok',flush=True); print('stderr-ok',file=sys.stderr,flush=True); time.sleep(10)"],directory,.5,directory/'stdout',directory/'stderr')
        # Verify exact raw capture independently of observed timeout cleanup.
        raw_capture=(directory/'stdout').read_bytes()==b'capture-ok\n' and (directory/'stderr').read_bytes()==b'stderr-ok\n'
        # Read-only root binding plus a writable selected scratch directory is the actual execution boundary.
        sandbox=subprocess.run([bubblewrap,'--ro-bind','/','/','--bind',str(directory),str(directory),'/bin/true'],capture_output=True,text=True,timeout=5) if bubblewrap else None
    # Returned status does not conflate a successful local probe with live Codex authentication.
    return {'codex':codex,'live_codex_called':False,'portfolio':portfolio,'git':git,
            'bubblewrap':{'path':bubblewrap,'passed':sandbox is not None and sandbox.returncode==0,'error':sandbox.stderr if sandbox else 'not installed'},
            'owned_timeout_cleanup':cleanup,'raw_capture_passed':raw_capture,'free_disk_bytes':shutil.disk_usage(root).free,'commit_note':'actual round commits are checked by the controller; this doctor does not stage or commit user files'}

# Explicit launch/status/resume/stop paths keep accidental public campaign starts out of diagnostics.
def main(argv=None):
    """Parse real CLI, run one action, print finite JSON and return status exit code.

    Example doctor, plan --instance name, run/resume/status/stop --campaign-id ID.
    test --provider codex is the explicit bounded scratch integration; fixture-test
    is unmistakably labeled. No tags, remote pushes or automatic second graph.
    """
    # Recursion prevention applies to all mutating controller actions below.
    parser=argparse.ArgumentParser(description=__doc__)
    # Subcommands make read-only inspection distinct from an actual user-launched campaign.
    commands=parser.add_subparsers(dest='command',required=True)
    # Shared config input is a plain versioned JSON file.
    for name in ('doctor','plan','run'):
        # Each command has only the arguments it genuinely uses.
        child=commands.add_parser(name)
        # Default file is checked in with this framework rather than a hidden settings grid.
        child.add_argument('--config',type=Path,default=ROOT/'evolve/configs/default.json')
        # Both planning and execution require an explicit single selected graph.
        if name in ('plan','run'):
            # Basenames are resolved only in instances/public.
            child.add_argument('--instance',required=True,type=Path)
        # Only run creates a fresh campaign namespace/branch.
        if name=='run':
            # Collision rejection requires the user to choose a new ID or explicit resume.
            child.add_argument('--campaign-id',required=True)
            # New-run budgets can be overridden without inventing another config file.
            for key,kind in (('max-wall-seconds',float),('max-rounds',int),('max-codex-calls',int),('max-solver-trials',int)):
                # Explicit values become the initial immutable resolved configuration.
                child.add_argument('--'+key,type=kind)
    # A batch is only the explicitly listed campaigns, with bounded concurrent controllers.
    child=commands.add_parser('batch')
    # A JSON manifest makes graph/ID choices reviewable before any campaign starts.
    child.add_argument('--campaigns',type=Path,required=True)
    # Two workers is a useful bounded initial parallel setting, not all host CPUs.
    child.add_argument('--jobs',type=int,default=2)
    # Status/resume/stop refer only to existing exact campaign IDs.
    for name in ('status','resume','stop'):
        # No implicit latest campaign lookup can affect the wrong target.
        child=commands.add_parser(name)
        # Exact identity is mandatory for durable operations.
        child.add_argument('--campaign-id',required=True)
        # Resume budget/config changes are explicit and become new immutable revisions.
        if name=='resume':
            # An optional override file can change implemented settings without hiding prior expenditure.
            child.add_argument('--config',type=Path)
            # Batch startup must not erase a stop posted between process creation and lock acquisition.
            child.add_argument('--preserve-stop-request',action='store_true')
            # Common cumulative cap overrides are convenient without rewriting full JSON.
            for key,kind in (('max-wall-seconds',float),('max-rounds',int),('max-codex-calls',int),('max-solver-trials',int)):
                # None means unchanged, never reset to engineering defaults.
                child.add_argument('--'+key,type=kind)
    # One explicit bounded scratch check is distinct from a public-graph campaign.
    child=commands.add_parser('test')
    # Scratch results need a fresh output destination for review/reproduction.
    child.add_argument('--output',type=Path,required=True)
    # Test provider is never the implicit production campaign fallback.
    child.add_argument('--provider',choices=['fixture-test','codex'],default='fixture-test')
    # CLI tests invoke the same parser as a normal shell run.
    args=parser.parse_args(argv)
    # User/data/model errors preserve actual files and produce an honest nonzero result.
    try:
        # No controller/model recursion can be launched from a numerical or Codex child.
        if args.command in ('run','resume','test','batch') and (os.environ.get('MAXCUT_EVOLUTION_CODEX_CHILD') or os.environ.get('MAXCUT_EVOLUTION_WORKER')):
            # Explicit guard, not a model promise, stops nested use of this framework.
            raise CampaignError('integrity_error','recursive evolutionary invocation refused')
        # Doctor and plan never optimize or ask a model for variants.
        if args.command in ('doctor','plan','run'):
            # Resolve declared file bytes once, then validate every implemented key/range.
            config=configuration(json.loads(args.config.read_text()))
            # Convenient flags affect only a fresh run, never silently reset a saved campaign.
            if args.command=='run':
                # Each override is checked by the same strict parser as a custom JSON config.
                updates={key:getattr(args,key) for key in ('max_wall_seconds','max_rounds','max_codex_calls','max_solver_trials') if getattr(args,key) is not None}
                # Save exactly the budget actually used when the campaign is created.
                config=configuration({**config,**updates})
        # Actual diagnostics include available CLI version/flags, no live model request.
        if args.command=='doctor':
            # Real environment failures remain visible in the JSON report.
            result=doctor(ROOT,config)
        # Planning is read-only scope/cost/deficit inspection.
        elif args.command=='plan':
            # No campaign branch, file, solver trial or model call is created.
            result=plan(ROOT,args.instance,config)
        # Run creates exactly one fresh campaign and then carries its bounded rounds forward.
        elif args.command=='run':
            # The user explicitly authorizes this chosen graph campaign via run.
            campaign=create_campaign(ROOT,args.instance,config,args.campaign_id)
            # Target success or honest budget/block checkpoint terminates this same graph only.
            result=campaign.run()
        # A stop request must not wait for the campaign's own mutation lock.
        elif args.command=='stop':
            # Validate ID/path through the real campaign loader before writing its stop flag.
            campaign=Campaign(ROOT,ROOT/'evolve/campaigns'/args.campaign_id)
            # This atomic request is consumed only by explicit resume.
            atomic_json(campaign.path/'stop.json',{'requested_at':time.time(),'campaign_id':args.campaign_id})
            # A running bounded process sees this flag within its next short poll.
            result={'campaign_id':args.campaign_id,'stop_requested':True,'status_command':f'uv run python evolve_search.py status --campaign-id {args.campaign_id}'}
        # Read-only state inspection does not reexecute interrupted trials.
        elif args.command=='status':
            # Existing atomic checkpoint is the sole current operational truth.
            result=Campaign(ROOT,ROOT/'evolve/campaigns'/args.campaign_id).status()
        # Resume preserves graph, references, source snapshot, counters and all prior trial IDs.
        elif args.command=='resume':
            # Validate/read an existing namespace before a lock could create any missing directory.
            selected_campaign=Campaign(ROOT,ROOT/'evolve/campaigns'/args.campaign_id)
            # Refuse legacy mutation before even creating a new-style lock file in its old directory.
            if selected_campaign.record.get('execution_mode')!='isolated':
                # Historical checkpoints, manifests and directory inventories remain unchanged.
                raise CampaignError('legacy_campaign','Use a fresh isolated campaign ID; historical campaign is preserved read-only.')
            # Configuration revisions and stop-flag consumption may not race an active controller.
            with CampaignLock(ROOT,selected_campaign.path):
                # Load exact campaign, never create a new namespace to hide old resource use.
                campaign=Campaign(ROOT,ROOT/'evolve/campaigns'/args.campaign_id)
                # Legacy branch/commit runs remain unchanged forensic evidence, not silently migrated.
                if campaign.record.get('execution_mode')!='isolated':
                    # Fail before changing old checkpoints, stop flags or source identities.
                    raise CampaignError('legacy_campaign','Use a fresh isolated campaign ID; historical campaign is preserved read-only.')
                # Reject a changed framework before editing old config/checkpoint/reservation bytes.
                try:
                    # Existing recovery still owns publication/process reconciliation in a matching checkout.
                    verify_manifest(ROOT,campaign.record['protected_manifest'])
                # Source updates must never silently rewrite the campaign's frozen implementation identity.
                except CampaignError as error:
                    # Explain the supported version boundary without migrating or charging old work.
                    raise CampaignError('integrity_error',str(error)+'; no checkpoint/config changes applied. '
                                        'Restore the recorded checkout to resume this campaign; use a fresh campaign ID '
                                        'to run an updated framework. See docs/evolution/ADMISSION_FIXES.md.') from error
                # Only explicitly supplied changes alter limits/behavior.
                updates=json.loads(args.config.read_text()) if args.config else {}
                # Convenient cap flags override corresponding keys without resetting any other controls.
                for key in ('max_wall_seconds','max_rounds','max_codex_calls','max_solver_trials'):
                    # None preserves the already recorded cumulative cap.
                    if getattr(args,key) is not None:
                        # Every changed value is persisted in a new config revision below.
                        updates[key]=getattr(args,key)
                # Resume can increase limits but never silently change graph/reference/frozen baseline roots/provider.
                forbidden={'instances','references','baseline_solutions','public_solutions','provider','campaign_seed','version'}
                # Changing pinned identity requires a separate fresh campaign instead of a misleading resume.
                if any(key in updates and updates[key]!=campaign.config[key] for key in forbidden):
                    # Preserve all past evidence and existing graph accounting.
                    raise ValueError('resume cannot change pinned inputs/provider/campaign seed/config version')
                # Configuration validation includes unsupported parallelism/certification/unknown keys.
                resolved=configuration({**campaign.config,**updates})
                # A changed configuration has an immutable new identity, never overwrites revision zero.
                if resolved!=campaign.config:
                    # No spent counters are reset or discounted here.
                    campaign.state['config_revision']+=1
                    # Persist exact actual updated settings in a numbered revision file.
                    atomic_json(campaign.path/'config-revisions'/f'{campaign.state["config_revision"]:04d}.json',resolved)
                    # Controller uses the same updated object it records.
                    campaign.config=resolved
                    # State checkpoint points at the exact current revision.
                    campaign.state['config']=resolved
                # Explicit resume revokes the previous durable stop request.
                if not args.preserve_stop_request:
                    # An explicit user resume revokes stop; a batch startup preserves a concurrent request.
                    (campaign.path/'stop.json').unlink(missing_ok=True)
                # Active overhead/config changes are charged before continuing old pending work.
                campaign.checkpoint()
            # Recovery and later rounds obey remaining cumulative budgets.
            result=campaign.run()
        # Batch execution uses the same isolated create/resume paths, never an agent swarm.
        elif args.command=='batch':
            # Import only when the user explicitly requests multiple selected campaigns.
            from evolution_batch import run_batch
            # All manifest identities/configs are prevalidated before the first worker launch.
            result=run_batch(ROOT,args.campaigns,args.jobs)
        # Explicit test workflow constructs only a fresh isolated repository with a tiny scratch graph.
        else:
            # This helper never copies/optimizes public original graphs or publishes their assignments.
            from scripts.run_evolution_smoke import run_smoke
            # The same production bridge/controller/commit path is exercised by the requested provider.
            result=run_smoke(ROOT,args.output.resolve(),args.provider)
        # Full precision finite JSON avoids six-digit score-based decisions.
        print(json.dumps(result,indent=2,allow_nan=False))
        # Unsuccessful/blocked target search remains visibly non-successful to shell automation.
        return 0 if result.get('status','') in ('target_already_met','target_reached') or args.command in ('doctor','plan','status','stop') or result.get('passed') or args.command=='batch' and result['all_targets_met'] and result['all_processes_succeeded'] else 2
    # Actual operational errors retain concrete reasons without speculative authentication fixes.
    except (CampaignError,OSError,ValueError,TypeError,KeyError,subprocess.SubprocessError) as error:
        # No failed action is silently reported as a successful campaign.
        print(json.dumps({'status':getattr(error,'state','integrity_error'),'reason':str(error)},indent=2))
        # Inputs/missing CLI/model failures are actionable nonzero exits.
        return 2

# Importing CLI code starts no model, numerical trial or campaign mutation.
if __name__=='__main__':
    # Shell exit code matches actual target/inspection/test outcomes.
    raise SystemExit(main())
