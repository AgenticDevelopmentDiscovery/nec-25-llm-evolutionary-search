"""Persistent identities, official/exact target math, locks and bounded owned processes."""
# File locks serialize all campaigns sharing one repository.
import fcntl
# Fractions diagnose threshold differences without a success epsilon.
from fractions import Fraction
# Hashes identify graph, assignment, source and configuration bytes.
import hashlib
# JSON is finite canonical metadata, never executable configuration.
import json
# Signals/environment identify only owned child process incarnations.
import os
# Ordinary paths keep all campaign state explicit and reviewable.
from pathlib import Path
# Process calls always use argv, never model-generated shell text.
import subprocess
# Nonblocking pipes preserve raw CLI streams even when a confined launcher rejects inherited regular files.
import selectors
# The trusted subreaper uses this exact interpreter for source-pinned process supervision.
import sys
# Temporary sibling files allow atomic publication.
import tempfile
# Monotone timing measures active work; UTC wall timestamps describe records.
import time
# NumPy is the existing sign-vector dependency.
import numpy as np
# The unchanged official scorer remains authoritative for user-visible scores.
import evaluate
# Shared graph/sign validation independently checks all witnesses.
from bm_solver import cut_value, load_graph, validate_signs
# Existing cleanup follows verified descendants across MPI process groups.
from portfolio_external import OwnedCleanupError, process_tick, stop_process_group
# Reuse the established finite JSON writer and original assignment loader.
from run_bm import atomic_json, file_sha256, load_assignment, metadata_path

SCORING_TIMING_POLICY = {'version': 3, 'worker_fraction': 1.0, 'maximum_verification_seconds': None,
          'verification_reserve_seconds': 30.0, 'recovery_verification_seconds': 60.0,
          'minimum_verification_reserve_seconds': 1.0,
          'trial_seconds_scope': 'aggregate including numerical work, verification and setup',
          'recovered_verification_eligible_for_selection': False}

# Versioned engineering defaults are not measured optimal solver settings.
DEFAULTS={'version':1,'target_score':1.0,'campaign_seed':1,'max_rounds':20,'max_wall_seconds':7200,
          'max_codex_calls':25,'codex_call_timeout_seconds':180,'max_solver_trials':500,
          'screen_trial_seconds':120,'trial_seconds':30,'repeats':2,'survivors':3,'children_per_round':3,
          'stagnation_rounds':3,'parallel_trials':1,'auto_commit':False,'auto_publish_improvements':False,
          'certification_after_target':False,'lift_backend_guards':False,'finalize_reserve_seconds':5,
          'validation_seconds':30,'baseline_solutions':'experiments/bm_real_pilot_s1_s2/solutions',
          'public_solutions':'solutions','instances':'instances/public','references':'references/public.json',
          'screen_solvers':None,'screen_work_caps':{},'work_caps':{'bm':8},'candidate_configs':{},'candidate_variants':{'mqlib':[{'heuristic':'PALUBECKIS2004bMST1'},{'heuristic':'FESTA2002GVNSPR','max_nodes':10000},{'heuristic':'MERZ2002KOPT','max_nodes':10000}]},
          'codex_executable':'codex','codex_model':None,'codex_reasoning':None,'codex_profile':None,
          'provider':'codex','fixture_decisions':[]}

# Failures are explicit controller states, not claims of optimization success.
class CampaignError(Exception):
    """Carry resumable state/reason; e.g. CampaignError('integrity_error','hash changed').

    Args state/reason strings; no side effects. Exception message is reason.
    Used for contract, ownership and persistence failures rather than fake results.
    """
    # An explicit state lets the CLI preserve evidence before stopping.
    def __init__(self,state,reason):
        """Store state/reason; return None, no files; example state='awaiting_codex'."""
        # Preserve ordinary exception behavior and exact reason text.
        super().__init__(reason)
        # Machine-readable status is distinct from the human explanation.
        self.state=state

# Byte identity is shared by artifact deduplication and trial conditions.
def identity(value):
    """Return canonical finite JSON SHA256; no mutation; example identity({'x':1})."""
    # Sorted keys and compact separators remove filename/order-only novelty.
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

# Immutable artifact writes reject collisions with different bytes.
def immutable_json(path,value):
    """Write once or verify identical JSON; Path/dict -> None; differing data raises integrity_error.

    Example immutable_json(Path('artifact.json'), {'id':'a'}); no old file is overwritten.
    """
    # A replay must verify original identity rather than replace earlier evidence.
    if path.exists():
        # JSON key ordering is immaterial but content equality is mandatory.
        if json.loads(path.read_text())!=value:
            # Preserve both the old file and its collision diagnostic.
            raise CampaignError('integrity_error',f'immutable artifact collision: {path}')
        # Identical publication is a safe idempotent recovery operation.
        return
    # Missing parents belong to this explicit artifact tree.
    path.parent.mkdir(parents=True,exist_ok=True)
    # Existing finite atomic writing avoids partially visible metadata.
    atomic_json(path,value)

# Config changes on resume must remain explicit recorded revisions.
def configuration(overrides=None):
    """Return validated defaults+overrides dict; no mutation; e.g. {'max_rounds':2}.

    Reject ignored keys, nonfinite/negative limits, unsafe paths and unsupported parallelism.
    """
    # Start with owned nested values, not a shallow mutable global dictionary.
    config=json.loads(json.dumps(DEFAULTS))
    # Unknown options must never appear to have been enforced.
    if set(overrides or {})-set(config):
        # Report the actual unexpected keys.
        raise ValueError('unknown campaign configuration keys: '+str(set(overrides)-set(config)))
    # User overrides are ordinary JSON data with no execution hooks.
    config.update(overrides or {})
    # Integer work/call counts cannot be silently coerced from booleans or fractions.
    for key in ('version','campaign_seed','max_rounds','max_codex_calls','max_solver_trials','repeats','survivors','children_per_round','stagnation_rounds','parallel_trials'):
        # Version two can make rounds/solver counts time-limited instead of count-limited.
        # Other quotas, particularly paid model calls, always remain finite.
        if key in ('max_rounds','max_solver_trials') and config['version']==2 and config[key] is None:
            continue
        # Zero limits are legitimate no-work stops, except structural counts below.
        if type(config[key]) is not int or config[key]<0:
            # Fail before any campaign folder is reserved.
            raise ValueError(f'{key} must be a nonnegative integer')
    # The requested initial implementation is serial and uses up to three survivors/children.
    if config['version'] not in (1,2) or config['parallel_trials']!=1 or not 1<=config['repeats']<=10 or not 1<=config['survivors']<=3 or not 1<=config['children_per_round']<=3 or config['stagnation_rounds']<1:
        # Unsupported scheduling cannot be hidden behind accepted config values.
        raise ValueError('unsupported version/counts; serial trials, 1..3 children/survivors required')
    # All elapsed allowances use finite nonnegative seconds.
    for key in ('target_score','max_wall_seconds','codex_call_timeout_seconds','screen_trial_seconds','trial_seconds','finalize_reserve_seconds','validation_seconds'):
        # Scores below one would weaken the user's declared default goal.
        if isinstance(config[key],bool) or not isinstance(config[key],(int,float)) or not np.isfinite(config[key]) or config[key]<0:
            # No NaN budget can bypass an exhaustion comparison.
            raise ValueError(f'invalid {key}')
    # Certification is outside this target-search controller; no silent continued search after success.
    if config['target_score']<1 or config['certification_after_target']:
        # A separate explicit certification implementation is needed before enabling it.
        raise ValueError('target_score must be >=1; certification_after_target is not implemented')
    # Behavioral toggles must be actual JSON booleans.
    for key in ('auto_commit','auto_publish_improvements','lift_backend_guards'):
        # A truthy string is not an explicit opt-in.
        if type(config[key]) is not bool:
            # Stop before policy changes affect outputs.
            raise ValueError(key+' must be bool')
    # Campaigns own private evidence only; Git and public consolidation require explicit user actions.
    if config['auto_commit'] or config['auto_publish_improvements']:
        # Older custom configs must be updated, not silently allowed to mutate shared resources.
        raise ValueError('auto_commit and auto_publish_improvements must be false; commit manually and consolidate explicitly')
    # The test provider is unmistakably separate from production Codex calls.
    if config['provider'] not in ('codex','fixture-test'):
        # No automatic fallback to a random or mock mutator exists.
        raise ValueError('provider must be codex or explicitly fixture-test')
    # A relative data path must not escape the selected repository.
    for key in ('instances','references','baseline_solutions','public_solutions'):
        # Symlinks are resolved and checked again against the repository at initialization.
        if Path(config[key]).is_absolute() or '..' in Path(config[key]).parts:
            # Prevent campaign publication into unrelated user data.
            raise ValueError('campaign data paths must remain inside the repository')
    # Backend option maps must be real mappings before they control resource reservations.
    for key in ('work_caps','screen_work_caps','candidate_configs'):
        # Lists/strings cannot act as partially ignored per-backend settings.
        if not isinstance(config[key],dict):
            # Fail before any source snapshot, branch or solver call.
            raise ValueError(key+' must be an object')
    # Only discovered backend names may carry explicit configuration or unit caps.
    from solver_portfolio import list_solvers
    # Discovery checks availability without performing optimization.
    names=set(list_solvers())
    # Validate bounded numerical work in each backend's actual integer work units.
    for key in ('work_caps','screen_work_caps'):
        # Zero work may intentionally exercise fallback behavior but cannot masquerade as search.
        if any(name not in names or type(value) is not int or value<0 for name,value in config[key].items()):
            # Unknown names and fractional work caps would otherwise be silently unused.
            raise ValueError(key+' needs known backends and nonnegative integer units')
    # Candidate overrides must be objects keyed by actual installed interface names.
    if any(name not in names or not isinstance(value,dict) for name,value in config['candidate_configs'].items()):
        # Real backend option names are independently checked at eligibility/admission.
        raise ValueError('candidate_configs needs known backends and object values')
    variants=config['candidate_variants']
    if not isinstance(variants,dict) or any(name not in names or not isinstance(items,list) or len(items)>8 or any(not isinstance(item,dict) for item in items) for name,items in variants.items()):
        raise ValueError('candidate_variants needs known backends and at most eight configuration objects each')
    # A deliberate screening subset is explicit, unique and never interpreted as a string.
    if config['screen_solvers'] is not None and (not isinstance(config['screen_solvers'],list) or any(name not in names for name in config['screen_solvers']) or len(set(config['screen_solvers']))!=len(config['screen_solvers'])):
        # Default None still screens all compatible discovered entries.
        raise ValueError('screen_solvers must be null or unique known backend names')
    # Fixture decisions are test data, not an implicit live-provider fallback.
    if not isinstance(config['fixture_decisions'],list):
        # Malformed fixture input gets no model/solver resource reservation.
        raise ValueError('fixture_decisions must be an array')
    # CLI values remain single argv elements and inherit defaults unless explicitly set.
    for key in ('codex_executable','codex_model','codex_reasoning','codex_profile'):
        # A null executable has no valid meaning, while null overrides mean inherited defaults.
        if (key=='codex_executable' or config[key] is not None) and (not isinstance(config[key],str) or not config[key].strip()):
            # No invented model/profile or authentication is substituted.
            raise ValueError('invalid '+key)
    # Canonical finite serialization checks nested numeric values too.
    identity(config)
    # Return a fresh complete resolved config for durable campaign receipts.
    return config

# Owned process execution is reused for Codex, validation, trials, doctor and git.
def owned_process(argv,cwd,seconds,stdout,stderr,stdin=None,environment=None,registration=None,stop_path=None):
    """Run bounded argv with raw streams and optional stop polling; return exit/elapsed/timeout.

    Paths cwd/stdout/stderr are explicit; optional bytes stdin and env copy.
    Example owned_process(['python','-V'],root,2,out,err). Records/reaps exact
    owned PID/descendants on timeout, interruption or stop; no shell strings.
    """
    # Actual elapsed time includes startup, stream draining and descendant cleanup.
    started=time.monotonic()
    # Parent-owned files preserve raw bytes while children see ordinary anonymous pipes.
    with stdout.open('wb') as out, stderr.open('wb') as err:
        # Pipes also avoid confined CLI launchers losing access to inherited regular stdin files.
        launcher=[sys.executable,str(Path(__file__).with_name('evolution_reaper.py')),*argv]
        # A live dedicated subreaper retains orphan ownership even if the main launcher exits immediately.
        child=subprocess.Popen(launcher,cwd=cwd,stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=environment,start_new_session=True)
        # Incarnation identity is recorded before polling/reaping can erase it.
        tick=process_tick(child.pid)
        # A saved PID/start tick supports recovery after controller interruption.
        if registration is not None:
            # Atomic publication prevents truncated active records.
            atomic_json(registration,{'pid':child.pid,'tick':tick,'argv':launcher,'command_argv':argv})
        # One nonblocking selector drains both streams without memory growth or PIPE deadlocks.
        selector=selectors.DefaultSelector()
        # Every captured stream is copied byte-for-byte by the trusted parent process.
        for stream,target in ((child.stdout,out),(child.stderr,err)):
            # Nonblocking reads allow a hard deadline even if a child holds a pipe open.
            os.set_blocking(stream.fileno(),False)
            # Targets are already-open parent-owned raw log streams.
            selector.register(stream,selectors.EVENT_READ,target)
        # Large prompts are written incrementally instead of blocking before timeout checks.
        pending=memoryview(stdin) if stdin is not None else None
        # A write-ready stdin is part of the same bounded event loop.
        if child.stdin is not None:
            # Nonblocking mode prevents a stalled model startup from blocking prompt delivery.
            os.set_blocking(child.stdin.fileno(),False)
            # None distinguishes input writes from raw output targets.
            selector.register(child.stdin,selectors.EVENT_WRITE,None)
        # Exit semantics distinguish a requested stop from an elapsed deadline.
        timeout,stopped=False,False
        # Stream EOF normally arrives with process completion; a short drain guard is conservative.
        exited_at=None
        cleanup_failure=None
        def terminate_owned():
            # Cleanup remains bounded and may target only this recorded incarnation.
            stop_process_group(child.pid,tick)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired as error:
                raise OwnedCleanupError([(child.pid,tick)]) from error
        # All descriptors/processes are cleaned on normal exit, timeout and SIGINT.
        try:
            # Continue until both output pipes reached EOF and the child has exited.
            while selector.get_map() or child.poll() is None:
                # A durable stop can interrupt a long Codex/native call within one short poll.
                stopped=stop_path is not None and stop_path.exists()
                # Timeout/stop cleanup follows only the exact owned root/descendant tree.
                if child.poll() is None and (stopped or time.monotonic()-started>=seconds):
                    # This is an observed operational timeout rather than guessed native success.
                    timeout=not stopped
                    # Existing ancestry/start-tick safeguards also stop separate MPI/Codex child groups.
                    terminate_owned()
                # Record the actual observed exit for bounded post-exit draining.
                if child.poll() is not None and exited_at is None:
                    # No unobserved model runtime is invented from stream timestamps.
                    exited_at=time.monotonic()
                # A stray inherited pipe cannot keep the controller waiting indefinitely after exit.
                if exited_at is not None and time.monotonic()-exited_at>.25:
                    # Remaining bytes are captured on the final available nonblocking reads below until this guard.
                    break
                # Short select waits handle stdout, stderr and input without unbounded sleeps.
                for event,mask in selector.select(timeout=.03):
                    # Every registered descriptor belongs to this launched process only.
                    stream=event.fileobj
                    # Input is delivered exactly as the already-persisted raw prompt bytes.
                    if event.data is None:
                        # The child can exit before consuming its entire prompt.
                        try:
                            # PIPE writes are bounded chunks and preserve argument-free stdin content.
                            count=os.write(stream.fileno(),pending[:65536]) if len(pending) else 0
                            # Consume only bytes actually accepted by the OS pipe.
                            pending=pending[count:]
                        # A closed input is an honest child startup/exit condition, not a reason to hang.
                        except BlockingIOError:
                            # A readiness race leaves all undelivered prompt bytes pending.
                            continue
                        # A genuinely closed child input needs no more prompt bytes.
                        except BrokenPipeError:
                            # Nothing further can be delivered to that process.
                            pending=pending[:0]
                        # Closing stdin after the prompt signals EOF to codex exec '-'.
                        if not len(pending):
                            # Stop monitoring only this completed input descriptor.
                            selector.unregister(stream)
                            # The output pipes remain independently monitored.
                            stream.close()
                    # stdout/stderr are raw public output streams with distinct targets.
                    else:
                        # Nonblocking output reads may race an event notification.
                        try:
                            # No decoding/newline rewriting changes transcript bytes.
                            data=os.read(stream.fileno(),65536)
                        # A temporary empty readiness race is not stream EOF.
                        except BlockingIOError:
                            # Continue the same bounded event loop.
                            continue
                        # Data is written by the unconstrained parent rather than a confined child's inherited file FD.
                        if data:
                            # Preserve stdout/stderr separation and exact original bytes.
                            event.data.write(data)
                        # A real EOF removes just that stream from the selector.
                        else:
                            # The pipe is no longer capable of producing data.
                            selector.unregister(stream)
                            # Close only the owned descriptor.
                            stream.close()
        # Exceptions and SIGINT must not leave a launched job running behind a checkpoint.
        except BaseException as error:
            # Do not repeat a failed cleanup or erase the surviving descendants' identities.
            if isinstance(error,OwnedCleanupError):
                cleanup_failure=error
            else:
                try:
                    terminate_owned()
                except OwnedCleanupError as failure:
                    cleanup_failure=failure
            if cleanup_failure is not None:
                # A descendant failure need not prevent reaping the launched root.
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if (child.pid,tick) not in cleanup_failure.survivors:
                        cleanup_failure.survivors.append((child.pid,tick))
                receipt={'pid':child.pid,'tick':tick,'argv':launcher,'command_argv':argv,
                         'cleanup_survivors':cleanup_failure.survivors,
                         'state':'cleanup_failed','reason':str(cleanup_failure)}
                atomic_json(stderr.with_name(stderr.name+'.cleanup.json'),receipt)
                if registration is not None:
                    atomic_json(registration,receipt)
                if cleanup_failure is error:
                    raise
                raise cleanup_failure from error
            # The controller records the actual failed/interrupted state.
            raise
        # File/selector ownership is scoped to this one explicit call.
        finally:
            # Close only still-open registered process streams.
            for key in list(selector.get_map().values()):
                # Remove the descriptor before its file object closes.
                selector.unregister(key.fileobj)
                # Closing a nonblocking descriptor cannot wait on another reader thread.
                key.fileobj.close()
            # Release the OS selector resources.
            selector.close()
            # Active registration must not outlive the completed/reaped call.
            if registration is not None and cleanup_failure is None and child.poll() is not None:
                # Missing files are ordinary process-completion/recovery races.
                registration.unlink(missing_ok=True)
    # These are real exit/timing flags, not transformed native/LLM quality claims.
    return {'launcher_argv':launcher,'exit_code':child.returncode,'elapsed_seconds':time.monotonic()-started,'timed_out':timeout,'stopped':stopped}


# Kernel file locking is authoritative; metadata alone never proves a live lock.
class RepositoryLock:
    """Exclusive flock released by close/crash; root Path input, context manager output.

    Example with RepositoryLock(root): run one campaign. Writes only the shared
    evolve/repository.lock; another owner fails without killing its process.
    """
    # Lock ownership is scoped to the enclosing controller action.
    def __init__(self,root):
        """Store root Path; no mutation yet; example RepositoryLock(Path.cwd())."""
        # Hold the selected repository's mutation-lock path explicitly.
        self.path=root/'evolve/repository.lock'
        # A symlinked framework directory cannot redirect mutation into unrelated filesystem data.
        if not self.path.resolve().is_relative_to(root.resolve()):
            # Refuse before creating/opening the lock or any external path.
            raise CampaignError('integrity_error','repository lock path escapes checkout')
    # flock prevents a second campaign from racing archive promotion or git.
    def __enter__(self):
        """Acquire exclusive nonblocking flock; return self; busy raises integrity_error."""
        # This infrastructure directory belongs only to the framework.
        self.path.parent.mkdir(parents=True,exist_ok=True)
        # Reopening stale metadata does not steal a live kernel lock.
        self.stream=self.path.open('a+')
        # Failure preserves the other campaign's lock and all files.
        try:
            # Nonblocking acquisition avoids an invisible second controller waiting indefinitely.
            fcntl.flock(self.stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # A live owner is a consistency blocker, not a stale PID to terminate.
        except BlockingIOError as error:
            # Release this unsuccessful descriptor only.
            self.stream.close()
            # Report an actionable concurrency error.
            raise CampaignError('integrity_error','another controller holds '+str(self.path)+' lock') from error
        # Context-manager ownership is explicit.
        return self
    # Normal exit and exceptions release only this descriptor's lock.
    def __exit__(self,*args):
        """Release owned flock/descriptor; None return propagates errors, no other side effects."""
        # Unlock does not modify another process's PID or files.
        fcntl.flock(self.stream,fcntl.LOCK_UN)
        # Closing also releases the kernel lock after ordinary completion.
        self.stream.close()


# Independent campaigns synchronize only their own state, not the entire checkout.
class CampaignLock(RepositoryLock):
    """Own one exact campaign directory's kernel lock; different IDs may run together.

    root/campaign Paths are scoped to root/evolve/campaigns. Example two different
    campaign locks coexist; a second owner of the same lock fails nonblocking.
    No Git/branch changes and no process is signaled by lock acquisition.
    """
    # Reuse flock ownership/cleanup while keeping the pathname inside one campaign.
    def __init__(self,root,campaign):
        """Validate paths and select campaign.lock; no writes until entering the lock."""
        # Resolve symlinks before permitting a writable lock file.
        root=root.resolve()
        # Only a direct child of this repository's campaign namespace is eligible.
        if campaign.resolve().parent!=(root/'evolve/campaigns').resolve() or not campaign.resolve().is_relative_to(root):
            # Never create a lock outside this checkout through a stale or malicious path.
            raise ValueError('campaign lock escapes namespace')
        # Kernel flock distinguishes active owners from stale lock metadata/files.
        self.path=campaign/'campaign.lock'
        # An individual lock-file symlink cannot redirect the synchronization boundary.
        if self.path.is_symlink():
            # Preserve the unexpected file for review instead of following it.
            raise ValueError('campaign lock must not be a symlink')

# Graph scoring uses the unchanged official summation and an independent exact diagnostic.
def metrics(instance,signs,reference,target):
    """Return original cut, official score and exact threshold diagnosis; no files/mutation.

    instance Path, signs +/-1, reference record and target>=1. Example trap
    F=8,W=14,ref=10 -> score 1/3. Degenerate denominator raises integrity_error.
    """
    # The official loader fixes edge counting and its actual floating summation order.
    n,i,j,w=evaluate.load_instance(instance)
    # Validate original order/length before indexing.
    checked=validate_signs(signs,n)
    # Official W/2 is used verbatim for user-visible normalized score.
    half=float(w.sum()/2)
    # References are immutable campaign input, not a tunable target denominator.
    denominator=reference['ref']-half
    # Degenerate or reversed normalization is not repaired by changing signs.
    if not np.isfinite(denominator) or denominator<=0:
        # The reference mapping must be reviewed before search.
        raise CampaignError('integrity_error','reference denominator must be finite and positive')
    # The authoritative displayed/target comparison is full precision, without clipping.
    value=evaluate.cut_value(i,j,w,checked)
    # This matches unchanged evaluate.score_folder for a valid witness.
    score=(value-half)/denominator
    # Exact finite-decimal summation diagnoses comparisons near a threshold.
    weights=[Fraction(str(float(weight))) for weight in w]
    # Each edge contributes its original weight once when endpoints differ.
    exact_cut=sum((weight for a,b,weight in zip(i,j,weights) if checked[a]!=checked[b]),Fraction(0))
    # Exact W and the exact represented reference define a separate diagnostic target.
    exact_half=sum(weights,Fraction(0))/2
    # No arbitrary epsilon changes target attainment.
    exact_target=exact_half+Fraction(str(target))*(Fraction(str(reference['ref']))-exact_half)
    # Official and exact comparisons must agree before automatic success.
    disagreement=(score>=target)!=(exact_cut>=exact_target)
    # Preserve exact fractions, proof-independent success and numerical discrepancy evidence.
    return {'cut':float(value),'score':float(score),'target_score':target,'target_cut':half+target*denominator,
            'exact_cut':str(exact_cut),'exact_target_cut':str(exact_target),'numerical_review':disagreement,
            'target_met':score>=target and not disagreement,'proof_status':'unproven'}

# Canonical assignment bytes are independent of backend/filename spelling.
def assignment_bytes(signs):
    """Return one sign per line as bytes, no mutation; e.g. [1,-1] -> b'1\n-1\n'."""
    # Original node order is preserved; no complementary canonicalization changes provenance.
    return ''.join(f'{int(value)}\n' for value in signs).encode()

# Before/after manifests protect objective, controller, official data and immutable portfolio code.
def protected_manifest(root):
    """Return path->SHA for fixed source/config/official input files; read-only, graph-linear I/O.

    Example protected_manifest(root) excludes evolving artifacts and public solutions,
    which have separate frozen/CAS checks. Source symlinks are never candidates.
    """
    # Controller and numerical core Python files are protected throughout the campaign.
    paths=[*root.glob('*.py'),root/'README.md',root/'problem.md',root/'pyproject.toml',root/'uv.lock']
    # Official graph/ref bytes and validated portfolio settings cannot evolve.
    for directory in ('instances/public','references','configs/portfolio'):
        # Recursive file discovery excludes directories and caches.
        paths.extend(path for path in (root/directory).rglob('*') if path.is_file())
    # Upstream Python primitives, build identities and actual native executables are also immutable prerequisites.
    for name in ('external/sources.json','external/TESB/tSB.py','external/MaxCutPlanarAndToroidal/toroid_lp_lib.py'):
        # Each selected file is small and directly used by an installed adapter.
        paths.append(root/name)
    # Native code can change behavior without changing a project-owned wrapper hash.
    from portfolio_external import BINARIES
    # Record actual executable bytes where these optional builds exist.
    paths.extend(root/name for name in BINARIES.values())
    # Missing optional fixture documentation is not invented.
    return {str(path.relative_to(root)):file_sha256(path) for path in paths if path.is_file()}

# A mismatch is a blocking consistency error; never restore over user changes silently.
def verify_manifest(root,manifest):
    """Raise integrity_error for altered/missing protected bytes; no mutation; example saved baseline."""
    # Only known recorded paths are compared, never arbitrary model-selected files.
    changed=[name for name,digest in manifest.items() if not (root/name).is_file() or file_sha256(root/name)!=digest]
    # A failed check prevents candidate selection and publication.
    if changed:
        # Retain user edits and expose exact conflicting paths.
        raise CampaignError('integrity_error','protected files changed: '+', '.join(changed))
