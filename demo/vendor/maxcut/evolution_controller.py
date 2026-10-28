"""Independent resumable campaigns, cumulative budgets, verified selection and private evidence."""
# Fractions order exact represented cut values without score clipping/epsilon ties.
from fractions import Fraction
# JSON is the explicit immutable/durable state protocol.
import json
# Stage and allocation limits require finite numeric checks.
import math
# Runtime environment guards reject recursive controllers from model/numerical children.
import os
# Paths identify a single selected campaign/round rather than search the whole ladder.
from pathlib import Path
# Stable identifiers reject traversal/shell-like campaign names.
import re
# Evidence copies preserve original incumbent/source/transcript bytes.
import shutil
# Medians describe repeated actual candidate witnesses, not archive-inherited scores.
import statistics
# Git operations use argv and explicit path lists only.
import subprocess
# Monotone timing charges active execution across process/checkpoint boundaries.
import time
# Original graph/sign loading and F are protected validated primitives.
from bm_solver import load_graph,validate_signs
# Actual backend capabilities determine starts, seeds and runtime-only restrictions.
from solver_portfolio import FEATURES,list_solvers
# Existing atomic finite JSON and SHA helpers are reused.
from run_bm import atomic_json,file_sha256,load_assignment,metadata_path
# Shared policy/state errors and protected hashes are not candidate-editable.
from evolution_common import SCORING_TIMING_POLICY as POLICY,CampaignError,CampaignLock,configuration,identity,immutable_json,metrics,protected_manifest,verify_manifest
from portfolio_external import OwnedCleanupError, process_live
# Candidate content identity, snapshots and guard checks remain explicit functions.
from evolution_candidates import initial_configurations,artifact,eligibility,load_artifact,save_artifact,snapshot
# Real Codex and explicit fixture provider use one independently validated protocol.
from evolution_codex import request_plan
# Numerical execution/archive/publication always operate through protected verification.
from evolution_evaluation import archive_witness,assembled_score,freeze_inputs,launch_trial,verify_context
# Existing descendant cleanup is also used when resuming an interrupted invocation.
from portfolio_external import process_tick,stop_process_group

# Stop/status strings are evidence categories, never implicit success aliases.
SUCCESS={'target_already_met','target_reached'}
# Source-root relative paths are fixed by the actual checkout, not an installed package name.
ROOT=Path(__file__).resolve().parent

# Exact deterministic seeds are shared across compatible parent/child comparisons.
def trial_seed(graph_hash,campaign_seed,round_id,repeat,backend):
    """Return effective reproducible integer seed, no mutation.

    Example BiqBin always returns 2020. Other seeds derive from graph/round/
    repeat/comparison role, never candidate order or ID. MQLib uses 16 bits.
    """
    # Actual hardcoded native RNG behavior overrides requested independent repetitions.
    if backend in ('biqbin','madam'):
        # This fixed seed is recorded rather than misrepresented as an independent rerun.
        return 2020
    # Deterministic/retention-only computations collapse identical repetitions.
    slot=0 if backend in ('exhaustive','planar_matching','toroidal_bound') else repeat
    # A common comparison role supplies identical random starts for compatible candidates.
    value=int(identity([graph_hash,campaign_seed,round_id,slot,'comparison'])[:12],16)%(2**31-1)
    # Actual MQLib seed range is 0..65535.
    return value%65536 if backend=='mqlib' else value

# Selection consumes only each artifact's own eligible verified observations.
def select_survivors(observations,count,diversity=False):
    """Return ranked IDs/metrics from valid search witnesses, no mutation.

    Best exact cut, median comparable cut, completion-time upper bound, ID break
    ties. Example an unselected candidate's archive improvement is independent.
    Requested diversity retains best-ranked plus a different backend when possible.
    """
    # Failures/fallbacks remain in raw records but cannot borrow archive fitness.
    groups={}
    # Cached identical executions are deduplicated, not additional independent samples.
    seen=set()
    # Each observation belongs to exactly one immutable artifact.
    for item in observations:
        # Invalid/nonsearch/duplicate execution outcomes do not enter the ranking sample.
        if not item.get('eligible_for_selection') or item.get('execution_id') in seen:
            # Raw failure/fallback counts are still available in round summaries.
            continue
        # Track exact execution identity rather than merely a trial filename.
        seen.add(item['execution_id'])
        # Candidate-specific measurements never take a later archive's cut.
        groups.setdefault(item['artifact_id'],[]).append(item)
    # Ranking metrics explicitly state their timing scope.
    ranking=[]
    # All valid repeats enter candidate aggregation; failed repeats remain visible separately.
    for candidate_id,items in groups.items():
        # Fractions avoid six-decimal rounding and artificial epsilon ties.
        values=[Fraction(item['metrics']['exact_cut']) for item in items]
        # Best witness is the campaign's primary candidate-quality objective.
        best=max(values)
        # Median is meaningful only over the comparable actual witnessed repeats recorded here.
        median=statistics.median(values)
        # Time-to-best is measured at return, an upper bound on the unobserved first-hit time.
        elapsed=0.0
        # Earliest completion of a best-cut trial is a reproducible timing tie-break.
        time_to_best=None
        # Evaluation order is explicit and timings remain end-to-end observations.
        for item in [entry for entry in observations if entry['artifact_id']==candidate_id and not entry.get('cached')]:
            # Include earlier actual trial costs for this candidate in the measurement scope.
            elapsed+=item.get('evaluation_elapsed_seconds',item['process']['elapsed_seconds'])
            # Record the first completion that established this candidate's eventual best.
            if item.get('eligible_for_selection') and Fraction(item['metrics']['exact_cut'])==best and time_to_best is None:
                # No unobserved inside-solver first-hit timestamp is invented.
                time_to_best=elapsed
        # A round containing only reused executions retains their original measured timing bound.
        if time_to_best is None:
            # Cache hits are not timed as fresh numerical samples.
            time_to_best=sum(item.get('evaluation_elapsed_seconds',item['process']['elapsed_seconds']) for item in items)
        # Portable metrics preserve fractions as exact strings and numeric public summaries separately.
        ranking.append({'id':candidate_id,'best_exact_cut':str(best),'median_exact_cut':str(median),
                        'time_to_best_seconds_upper_bound':time_to_best,'backend':items[0]['backend'],'samples':len(items)})
    # Deterministic IDs resolve exact numerical/timing ties.
    ranking.sort(key=lambda item:(-Fraction(item['best_exact_cut']),-Fraction(item['median_exact_cut']),item['time_to_best_seconds_upper_bound'],item['id']))
    # The default survivors are distinct immutable artifacts.
    chosen=ranking[:count]
    # Diversity is a predeclared round policy, never a retroactive result preference.
    if diversity and count>1 and ranking:
        # Preserve the best-ranked artifact under all diversity outcomes.
        other=next((item for item in ranking[1:] if item['backend']!=ranking[0]['backend']),None)
        # Replace only the last slot if a genuinely different mechanism is available.
        if other is not None and other not in chosen:
            # Different backend here is a conservative explicit mechanism definition.
            chosen=ranking[:count-1]+[other]
    # Return actual IDs and full ranking so selection reasoning is independently reviewable.
    return [item['id'] for item in chosen],ranking

# Controller state is plain JSON; functions rather than inheritance manage the round machine.
class Campaign:
    """Own one campaign's cumulative budgets and state; no solver work at construction.

    root/campaign Paths; use create/resume then run. Example Campaign(root,path).
    All exceptions checkpoint honestly; ordinary model decisions need no per-round approval.
    """
    # Existing state/context are reloaded before any recovery or new execution.
    def __init__(self,root,path):
        """Load explicit campaign Paths; return object, no writes; missing/corrupt state fails."""
        # Resolve root once to keep sandbox/evidence paths stable.
        self.root=root.resolve()
        # The selected campaign path is never a basename search across other graphs.
        self.path=path.resolve()
        # A load/status/stop request cannot escape the campaign namespace through ../ or symlinks.
        if not self.path.is_relative_to(self.root) or self.path.parent!=(self.root/'evolve/campaigns').resolve() or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',self.path.name) or '..' in self.path.name:
            # Read-only status and writable stop share the same path boundary.
            raise ValueError('invalid campaign path or identifier')
        # Campaign config/source/context have immutable identities.
        self.record=json.loads((self.path/'campaign.json').read_text())
        # The directory and stored campaign identity must describe the same namespace.
        if self.record['id']!=self.path.name:
            # Never redirect a saved campaign to another one's raw logs or public solution.
            raise CampaignError('integrity_error','campaign directory/identity mismatch')
        # The latest atomic checkpoint preserves all cumulative counters.
        self.state=json.loads((self.path/'state.json').read_text())
        # Current resolved configuration is the latest explicitly recorded revision.
        self.config=self.state['config']
        # Reference and frozen other assignments cannot evolve.
        self.context=json.loads((self.path/'context.json').read_text())
        # Active elapsed time starts now; paused/downtime is not silently reset into new resources.
        self.tick=time.monotonic()
    # Every durable checkpoint charges actual active controller/verification/closure time.
    def checkpoint(self):
        """Atomically save state and charge elapsed active time; return None.

        No expenditure counter resets. Example after a trial or model call.
        """
        # Time since the last checkpoint includes numerical/model and housekeeping work once.
        now=time.monotonic()
        # Accumulate rather than overwrite prior sessions' consumed resources.
        self.state['spent_wall_seconds']+=now-self.tick
        # The next measurement interval begins after this charge.
        self.tick=now
        # Finite atomic JSON protects the latest best-pointer/counters on interruption.
        atomic_json(self.path/'state.json',self.state)
    # Reserving completion work prevents a solver from consuming the whole remaining campaign wall budget.
    def available_seconds(self):
        """Return remaining launch allowance after active time and finalization reserve; no writes."""
        # An in-flight reservation is held across crash recovery, not a fresh allowance on resume.
        held=self.state['reservation']['seconds'] if self.state.get('reservation') else 0
        # First reached global wall limit prevents new work, preserving bounded finalization overhead.
        return max(0,self.config['max_wall_seconds']-self.state['spent_wall_seconds']-(time.monotonic()-self.tick)-held-self.config['finalize_reserve_seconds'])
    # Calls and solver/test work are reserved durably before launch to prevent duplicate hidden expenditure.
    def reserve(self,kind,seconds,directory,slots=0):
        """Reserve one operation and cumulative solver/Codex quota; return clipped seconds.

        kind trial/check/codex; directory uniquely identifies execution. Example
        a two-stage trial reserves two solver-call slots, not two full time budgets.
        """
        # A durable stop request takes precedence over launching more work.
        if (self.path/'stop.json').exists():
            # Stop is resumable and never classified as target success.
            raise CampaignError('interrupted','durable stop requested')
        # No action can overlap a previous un-reconciled execution reservation.
        if self.state.get('reservation'):
            # This catches controller/recovery logic inconsistencies before resource reuse.
            raise CampaignError('integrity_error','pending execution reservation requires recovery')
        # Tests/nested stages count toward the same global solver-call cap.
        if self.config['max_solver_trials'] is not None and self.state['counters']['solver_calls_reserved']+slots>self.config['max_solver_trials']:
            # Unlaunched work is explicitly excluded, not run on a fresh hidden budget.
            raise CampaignError('solver_budget_exhausted','solver/check call quota exhausted')
        # Real Codex corrections use the same finite call budget as initial proposals.
        if kind=='codex' and self.config['provider']=='codex' and self.state['counters']['codex_calls']>=self.config['max_codex_calls']:
            # No random/mock substitution occurs when the account/call quota is unavailable.
            raise CampaignError('llm_budget_exhausted','Codex call quota exhausted')
        # Test-provider calls are separately counted but obey the same call ceiling.
        if kind=='codex' and self.config['provider']=='fixture-test' and self.state['counters']['fixture_calls']>=self.config['max_codex_calls']:
            # A mock-only test cannot appear to have unlimited live LLM service.
            raise CampaignError('llm_budget_exhausted','fixture-test call quota exhausted')
        # Reserve bounded time for this operation, not more than the remaining campaign allowance.
        allowance=min(seconds,self.available_seconds())
        # Compared candidates must receive the same declared allowance, never a shorter last-child budget.
        if kind=='trial' and allowance<seconds:
            # Preserve an incomplete/censored batch rather than bias selection with unequal budgets.
            raise CampaignError('wall_budget_exhausted','insufficient remaining time for a full comparable trial')
        # An exhausted wall budget wins before any subprocess is launched.
        if allowance<=0:
            # Keep a durable deficit/checkpoint rather than promise target attainment.
            raise CampaignError('wall_budget_exhausted','active campaign wall allowance exhausted')
        # Work reservation is a conservative upper bound if the controller crashes mid-call.
        self.state['counters']['solver_calls_reserved']+=slots
        # Codex/provider usage counters remain distinct.
        if kind=='codex':
            # Requested correction calls are billed even if output is invalid or startup fails.
            key='codex_calls' if self.config['provider']=='codex' else 'fixture_calls'
            # A call is never reset on resume.
            self.state['counters'][key]+=1
        # Serial reservations contain exact paths for process/result reconciliation.
        self.state['reservation']={'kind':kind,'seconds':allowance,'directory':str(directory),'solver_call_slots':slots}
        # Durable accounting precedes process creation.
        self.checkpoint()
        # Caller uses only this clipped actual allowance.
        return allowance
    # Completed work clears only its reservation, without resetting cumulative counters.
    def finish_operation(self):
        """Clear active reservation, charge elapsed time and checkpoint; no return value."""
        # A subsequent resume need not conservatively charge this already-measured operation again.
        self.state['reservation']=None
        # Actual active time is charged once here.
        self.checkpoint()
    # Immutable context/sources and mutable archive identity are independently checked.
    def integrity(self):
        """Check original source/inputs/base/archive bytes; no mutation, raises integrity_error."""
        # Candidate attempts may not evolve controller, objective, official input or portfolio code.
        verify_manifest(self.root,self.record['protected_manifest'])
        # Frozen full-ladder reference and other assignments must retain their original bytes.
        verify_context(self.path,self.context)
        # Candidate imports must resolve to exactly the saved base prerequisites.
        verify_manifest(self.path/'base',json.loads((self.path/'base_manifest.json').read_text()))
        # The latest archive pointer must always refer to reloadable validated content.
        archive=self.state['archive']
        # A corrupted archive cannot be used as a future common incumbent.
        if file_sha256(archive['path'])!=archive['sha256']:
            # Stop rather than silently fall back to a weaker old public file.
            raise CampaignError('integrity_error','archive assignment bytes corrupted')
        # Graph/sign membership and exact objective are recomputed from actual stored labels.
        signs,value,info=load_assignment(Path(archive['path']),load_graph(self.context['instance']),self.context['graph_sha256'])
        # Recorded metrics cannot replace the original assignment's mathematical quality.
        actual=metrics(self.context['instance'],signs,self.context['reference'],self.config['target_score'])
        # Exact cut identity detects fabricated archive quality even if float totals round alike.
        if actual['exact_cut']!=archive['metrics']['exact_cut']:
            # No parent/trial can inherit unverified quality.
            raise CampaignError('integrity_error','archive exact objective mismatch')
    # Round closure is a durable receipt, independent of user-managed Git history.
    def finalize_round(self,round_id):
        """Verify a closed round and save its receipt; return manifest SHA, no Git calls.

        Paths/candidates must match the immutable manifest. Repeating closure after
        interruption is idempotent. Example round zero closes without a commit.
        """
        # No modified or incomplete evidence may authorize the next round.
        directory=self.path/'rounds'/f'{round_id:04d}'
        # The manifest freezes measured outcomes before checkpoint advancement.
        manifest=json.loads((directory/'round_manifest.json').read_text())
        # Keep every referenced file inside this round and independently check its bytes.
        for name,digest in manifest['files'].items():
            # Path traversal and changes to closed evidence are consistency failures.
            if not (directory/name).resolve().is_relative_to(directory.resolve()) or file_sha256(directory/name)!=digest:
                # Preserve damaged evidence for review without executing anything else.
                raise CampaignError('integrity_error','closed round manifest mismatch: '+name)
        # Source/config/lineage remain independently content-addressed.
        for candidate_id in manifest['candidates']:
            # A changed candidate cannot be blessed by an intact numerical receipt.
            load_artifact(self.path,candidate_id)
        # The manifest hash replaces the former automatically created Git commit ID.
        digest=file_sha256(directory/'round_manifest.json')
        # Immutable closure can be replayed after an interrupt without duplicating numerical work.
        immutable_json(directory/'closure_receipt.json',{'round_id':round_id,'manifest_sha256':digest,
                                                       'commit':None,'commit_policy':'manual'})
        # Return only a verified identity for the checkpoint's closed-round list.
        return digest
    # Private result copies are derived from the validated immutable archive.
    def export_best(self):
        """Atomically refresh this campaign's result/sidecar from its archive; no public writes.

        Outputs results/solutions/<target>, best.json and scores from the recorded
        frozen context. An interrupted derived copy is repairable from the archive.
        Example a target improvement is visible here before its round closes.
        """
        # Only this campaign owns these writable generated output paths.
        destination=self.path/'results/solutions'/self.context['instance_name']
        # Archive bytes must still match their independently checked content identity.
        archive=self.state['archive']
        # Never export unverified metadata or a changed assignment file.
        if file_sha256(archive['path'])!=archive['sha256']:
            # Preserve the existing private result on an archive integrity failure.
            raise CampaignError('integrity_error','archive changed before private export')
        # Validate original graph, order and signs again before replacing the derived copy.
        load_assignment(Path(archive['path']),load_graph(self.context['instance']),self.context['graph_sha256'])
        # The private export and metadata are never inputs to a different live campaign.
        destination.parent.mkdir(parents=True,exist_ok=True)
        # Same-directory replacement never exposes truncated label files.
        temporary=destination.with_name('.'+destination.name+'.tmp')
        # Copy exact canonical archive bytes rather than re-rounding coordinates.
        temporary.write_bytes(Path(archive['path']).read_bytes())
        # The caller holds this campaign's lock; no other controller can replace this temporary.
        temporary.replace(destination)
        # Recoverable metadata is derived exclusively from the known immutable archive/graph.
        graph=load_graph(self.context['instance'])
        # Readers can verify graph and assignment hashes independently of best.json.
        atomic_json(metadata_path(destination),{'instance_sha256':self.context['graph_sha256'],
                    'assignment_sha256':archive['sha256'],'node_count':graph.node_count,
                    'edge_count':len(graph.edges),'node_order':'original input node order'})
        # Machine-readable summary explicitly describes private, unmerged results.
        atomic_json(self.path/'results/best.json',{'instance':self.context['instance_name'],'archive':archive,
                    'assignment':str(destination),'publication':'private; explicit consolidation required'})
    # Recovery never reexecutes an ambiguous prior trial under its old execution ID.
    def recover(self):
        """Reconcile owned processes/reservations/closure receipts; no duplicate numerical work.

        Ambiguous killed calls are conservatively charged their reserved allowance.
        Completed observations are recovered by schedule/paths below. Only verified
        own start ticks are signaled; existing evidence is never deleted/overwritten.
        """
        # Original input/reference/source identity must hold before recovery writes private state.
        self.integrity()
        # Any active recorded numerical/model jobs belong to this one locked campaign.
        roots=[self.path]
        # Registrations are private to these paths, never name-matched OS process scans.
        for root in roots:
            # Missing LLM logs are normal before the first mutation round.
            if not root.exists():
                # There is no process to recover in this absent namespace.
                continue
            # Every registration includes a kernel incarnation ID.
            for registration in root.rglob('active_process.json'):
                # Process completion can remove its registration during a read.
                try:
                    # Only this explicit saved argv/session is eligible for cleanup.
                    process=json.loads(registration.read_text())
                # An already-cleared registration needs no signal.
                except FileNotFoundError:
                    # Continue with other own-run records.
                    continue
                # A previous failed cleanup retains descendants even after root exit.
                if any(process_live(pid,tick) for pid,tick in process.get('cleanup_survivors',[])):
                    raise CampaignError('cleanup_failed','previously owned descendants are still live; see '+str(registration))
                # Existing cleanup verifies PID/start ticks and descendant ownership.
                stop_process_group(process['pid'],process['tick'])
                # Keep a durable cleanup receipt without reusing the active registration filename.
                atomic_json(registration.with_name('recovered_process.json'),process)
                # No active owner remains after the locked recovery action.
                registration.unlink(missing_ok=True)
        # A crash must not reset an in-flight call's reserved resource exposure.
        if self.state.get('reservation'):
            # Without a measured finish, charge its full bounded allowance conservatively.
            self.state['spent_wall_seconds']+=self.state['reservation']['seconds']
            # Preserve the exact abandoned operation in cumulative recovery history.
            self.state.setdefault('recovered_reservations',[]).append(self.state['reservation'])
            # Trial schedule reconciliation checks for actual completed files before marking interruption.
            self.state['reservation']=None
        # A pending round can have a prepared immutable closure after interruption.
        pending=self.state.get('pending_round')
        # A campaign may have no open round at a normal budget stop.
        if pending is not None:
            # The round has one fixed path and common incumbent.
            directory=self.path/'rounds'/f'{pending:04d}'
            # A closed manifest must be revalidated before any new work is scheduled.
            if (directory/'round_manifest.json').exists():
                # Restore the closed round's terminal diagnosis even if an interrupt/closure error replaced runtime status.
                closed=json.loads((directory/'round_manifest.json').read_text())
                # A recovered target or proof/numerical warning must not launch another mutation.
                if closed['status'] in SUCCESS|{'numerical_review_required','target_unreachable_with_evidence'}:
                    # Immutable manifest records the last completed mathematical decision.
                    self.state['status']=closed['status']
                # Idempotent receipt validation avoids repeating a closed round after a crash.
                digest=self.finalize_round(pending)
                # The closure receipt is separate from the manifest it identifies.
                self.record_closed(pending,digest)
        # All resource/publication reconciliation becomes durable before continuing.
        self.checkpoint()
    # Each fixed round incumbent is immutable even when later observations improve the archive.
    def open_round(self,round_id):
        """Create/reload unique round state, freeze assignment, return dict; only owned writes."""
        # The next round cannot bypass a prepared/unclosed predecessor.
        if self.state.get('pending_round') not in (None,round_id):
            # Preserve both IDs for explicit consistency review.
            raise CampaignError('integrity_error','another round is still pending')
        # Round IDs are durable write-ahead identifiers.
        directory=self.path/'rounds'/f'{round_id:04d}'
        # Resume reuses metadata, never overwrites the previous frozen incumbent.
        if (directory/'round_state.json').exists():
            # Recorded phase/schedule determine exactly which work remains.
            return json.loads((directory/'round_state.json').read_text())
        # Exclusive directory creation rejects stale output collisions.
        directory.mkdir(parents=True,exist_ok=False)
        # Archive labels are validated by integrity() before copying.
        shutil.copyfile(self.state['archive']['path'],directory/'frozen_incumbent.txt')
        # All comparisons use this exact common state, never mid-round archive updates.
        record={'round_id':round_id,'phase':'screening' if round_id==0 else 'planning','frozen_sha256':file_sha256(directory/'frozen_incumbent.txt'),
                'frozen_metrics':self.state['archive']['metrics'],'parents':self.state['parents'][:],'children':[],
                'schedule':[],'observations':[],'rejections':[],'diversity_slot':False,'started_archive_sha256':self.state['archive']['sha256']}
        # The pending pointer is checkpointed before numerical/model work begins.
        self.state['pending_round']=round_id
        # Persist immutable initial round input separately from evolving phase metadata.
        immutable_json(directory/'frozen_manifest.json',{'sha256':record['frozen_sha256'],'archive':self.state['archive'],'graph_sha256':self.context['graph_sha256']})
        # Dynamic round state is atomic and recoverable across each phase.
        atomic_json(directory/'round_state.json',record)
        # Durable write-ahead pointer prevents a second round from starting after a crash.
        self.checkpoint()
        # Return an owned plain dictionary used by the serial state machine.
        return record
    # Small helper persists a phase transition before its next external action.
    def save_round(self,record):
        """Atomically save current round dict and campaign state; no numerical work."""
        # Round path derives only from its validated integer ID.
        directory=self.path/'rounds'/f'{record["round_id"]:04d}'
        # Dynamic observations/schedule are preserved before round finalization.
        atomic_json(directory/'round_state.json',record)
        # Active overhead/time and current archive become durable together.
        self.checkpoint()
    # Ranking artifacts and assignment harvesting are deliberately different operations.
    def harvest(self,observation,round_record,directory,deadline=None):
        """Verify/score/harvest any admitted valid witness; no parent-selection side effect.

        Every improvement has provenance, even when its artifact later loses ranking.
        Target success does not imply a mathematical certificate.
        """
        # Invalid/failing candidates cannot contribute guessed labels.
        if not observation.get('valid') or not observation.get('result') or observation['result'].get('failed'):
            # Failed results remain in round observations and raw logs.
            return
        # Independent target metrics always use the campaign's actual requested score.
        signs=observation['result']['assignment']
        # Original/exact scoring is protected from candidate source edits.
        actual=metrics(self.context['instance'],signs,self.context['reference'],self.config['target_score'])
        # Candidate fitness never takes a later archive's value.
        observation['metrics']=actual
        # A fresh receipt uses this candidate's labels with the unchanged frozen alternatives.
        if not observation.get('ladder_score_path'):
            receipt_dir = directory / ('score-' + str(len(list(directory.glob('score-*')))))
            receipt_dir.mkdir()
            recovery = deadline is None
            reserved_here = False
            try:
                if recovery:
                    # Recovery is a separately charged, bounded verification operation,
                    # never another search or a new fair timing sample.
                    if self.state.get('reservation'):
                        raise CampaignError('integrity_error', 'reconcile old reservation before verification recovery')
                    seconds = self.reserve('verification', POLICY['recovery_verification_seconds'], receipt_dir)
                    reserved_here = True
                    observation['eligible_for_selection'] = False
                    observation['verification_recovery'] = True
                else:
                    seconds = max(0, deadline - time.monotonic())
                observation['timing_policy'] = POLICY
                if seconds <= 0:
                    atomic_json(receipt_dir / 'score_process.json', {'process_started': False, 'timed_out': True,
                                'allowance_seconds': 0, 'failure': {'state': 'verification_timeout', 'reason': 'aggregate trial deadline exhausted before scorer launch'}})
                    raise CampaignError('verification_timeout', 'aggregate trial deadline exhausted before scorer launch')
                receipt = assembled_score(self.path, self.context, observation['result']['assignment'], receipt_dir, seconds)
                if receipt['instances'][self.context['instance_name']]['score'] != actual['score']:
                    raise CampaignError('integrity_error', 'official assembled score disagreement')
                observation['ladder_score_path'] = str(receipt_dir / 'ladder_score.json')
            finally:
                if reserved_here:
                    self.finish_operation()
        # Any strict exact improvement is saved regardless of eventual survivor membership.
        if Fraction(actual['exact_cut'])>Fraction(self.state['archive']['metrics']['exact_cut']):
            # Content-addressed archive never overwrites an earlier best witness.
            self.state['archive']=archive_witness(self.path,self.context,signs,
                {'kind':'candidate_search' if observation['eligible_for_selection'] else 'operational_nonsearch_witness',
                 'artifact_id':observation['artifact_id'],'execution_id':observation['execution_id'],'round_id':round_record['round_id']},self.config['target_score'])
            # Archive durability precedes optional public publication.
            self.checkpoint()
            # Verified best labels become available privately without waiting for the round to finish.
            self.export_best()
        # Native/global bounds have distinct graph/scaling/source/proof assumptions.
        for stage in observation['result'].get('stages',[]):
            # Only protected builtin adapter output can carry an upper bound.
            result=stage['result']
            # A missing bound remains null, not a relaxed heuristic surrogate.
            upper=result.get('upper_bound')
            # Preserve only computed original-unit bounds with their actual evidence.
            if upper is not None:
                # Every bound is scoped to this immutable original graph hash.
                bound={'upper_bound':upper,'graph_sha256':self.context['graph_sha256'],'backend':stage['backend'],
                       'implementation':result.get('implementation'),'upstream':result.get('upstream'),'integer_scale':result.get('integer_scale'),
                       'proof_status':result['optimality_status'],'evidence':result.get('optimality_evidence'),'execution_id':observation['execution_id']}
                # Never discard an existing tighter computed bound.
                if self.state.get('best_bound') is None or upper<self.state['best_bound']['upper_bound']:
                    # Solver-reported evidence is not upgraded to a separately checked certificate.
                    self.state['best_bound']=bound
        # Raw candidate quality, archive quality and exact threshold review remain distinct.
        if actual['numerical_review']:
            # Keep diagnostic fractions and official scores rather than apply an arbitrary epsilon.
            self.state['status']='numerical_review_required'
        # Stop scheduling promptly on a verified actual target witness.
        elif actual['target_met']:
            # A native success claim alone cannot reach this branch without verified labels and official scoring.
            self.state['status']='target_reached'
        # A credible bound below the requested target needs a consistency/unreachability diagnostic.
        elif self.state.get('best_bound') and self.state['best_bound']['upper_bound']<actual['target_cut']:
            # A completed solver-reported optimum below a higher requested target is explicitly unsuccessful target search.
            bound=self.state['best_bound']
            # Equality with this actual witness avoids declaring unreachable from a loose/unverified heuristic value.
            if bound['proof_status']=='solver_reported_optimal' and bound['upper_bound']==actual['cut']:
                # Reference/units/graph identity have all been checked above.
                self.state['status']='target_unreachable_with_evidence'
            # A merely numerical bound conflict is not silently treated as a proof.
            else:
                # Record assumptions for human numerical review instead of lowering the target.
                self.state['status']='numerical_review_required'
        # Verified observation and archive state survive interruption before survivor selection.
        atomic_json(directory/'verified_observation.json',observation)
        # No public file has changed yet; round closing prepares an explicit CAS promotion.
        self.checkpoint()
    # Model input contains actual measurements and immutable lineage, not an arbitrary fixed random sampler.
    def model_context(self,record):
        """Return bounded prompt context; read-only, includes source/config and remaining budgets."""
        # Parents are actual surviving immutable artifacts, not a narrative list of algorithms.
        parents=[load_artifact(self.path,candidate_id) for candidate_id in record['parents']]
        # Only a small graph summary is sent by default.
        graph=load_graph(self.context['instance'])
        # Full edges are useful only for deliberately tiny worked examples.
        summary={'nodes':graph.node_count,'edges':len(graph.edges),'negative_edges':sum(w<0 for i,j,w in graph.edges),
                 'total_weight':sum(w for i,j,w in graph.edges)}
        # Large public graphs are never serialized edge-by-edge into the model prompt.
        if graph.node_count<=8:
            # These actual fixture edges support a mathematically checkable tiny hypothesis.
            summary['tiny_edges']=graph.edges
        # Latest completed round results, failures and mutations guide the next justified action.
        previous=[]
        # Limit prompt volume while raw complete histories remain locally inspectable.
        for path in sorted((self.path/'rounds').glob('*/selection.json'))[-3:]:
            # These are deterministic measured summaries, not model assertions.
            previous.append(json.loads(path.read_text()))
        # Novelty needs the entire immutable population history, not only the latest survivors.
        known=[]
        # Stable ordering makes the complete catalogue auditable in every captured prompt.
        for path in sorted((self.path/'candidates').glob('*/artifact.json')):
            # Verify identities before exposing them as known strategies to the model.
            candidate=load_artifact(self.path,path.parent.name)
            # Config/policy/stages are complete resolved objects, so omitted defaults do not hide duplicates.
            known.append({'id':candidate['id'],'backend':candidate['content']['backend'],
                          'config':candidate['content']['config'],'policy':candidate['content']['policy'],
                          'stages':candidate['content']['stages'],
                          'semantic_source_sha256':identity(candidate['content']['semantic_source']),
                          'source_sha256':candidate['source_sha256'],
                          'has_source':bool(candidate['source']),
                          'creation_round':candidate['creation_round'],'category':candidate['category']})
        # Earlier source-version evidence guides proposals without pretending that
        # old timings are comparable to fresh screening under this numerical base.
        prior=None
        if self.record.get('continuation_of'):
            old=json.loads((self.path/'continuation/parent_state.json').read_text())
            prior={'campaign_id':self.record['continuation_of']['campaign_id'],
                   'status':old['status'],'reason':old.get('reason'),'archive_metrics':old['archive']['metrics'],
                   'closed_ordinary_rounds':self.state.get('prior_completed_ordinary_rounds',0),
                   'counters':old['counters'],'note':'historical source version; not comparable timing samples'}
        # Return explicit known source identities and scheduling constraints.
        return {'prior_source_summary':prior,'verification_timing_policy':POLICY,'round_id':record['round_id'],'graph_sha256':self.context['graph_sha256'],'graph_summary':summary,
                'reference':self.context['reference'],'initial_metrics':self.context['initial_metrics'],
                'frozen_incumbent':record['frozen_metrics'],'frozen_assignment_sha256':record['frozen_sha256'],
                'parents':parents,'known_candidates':known,'previous_round_measurements':previous,'capabilities':self.record['capabilities'],
                'excluded':self.record['excluded'],'remaining_wall_seconds':self.available_seconds(),
                'remaining_solver_calls':None if self.config['max_solver_trials'] is None else self.config['max_solver_trials']-self.state['counters']['solver_calls_reserved'],
                'remaining_codex_calls':self.config['max_codex_calls']-self.state['counters']['codex_calls'],
                'trial_seconds':self.config['trial_seconds'],'repeats':self.config['repeats'],'children_per_round':self.config['children_per_round'],
                'stagnation_completed_rounds':self.state['stagnation'],'lift_backend_guards':self.config['lift_backend_guards'],
                'editable_scope':['isolated variant.py numerical hooks','explicit backend configuration','declared perturbation/refinement policy'],
                'forbidden_scope':['objective/validation/proof/status','controller/selection/logging/commit','official inputs/scorer','parent/core sources']}
    # Semantic admission protects lineage, novelty, scheduling and resource scope independently of JSON schema.
    def admit_plan(self,plan,record):
        """Validate and save proposed inherited variants; return child IDs/order, or ValueError.

        No candidate is selected/published from the model narrative. Complete source
        bytes/config/lineage are durable before bounded correctness checks.
        """
        # A decision must address this precise frozen graph and round.
        if plan['round_id']!=record['round_id'] or plan['graph_sha256']!=self.context['graph_sha256']:
            # Stale graph/round decisions are never relabeled as current proposals.
            raise ValueError('proposal round/graph identity mismatch')
        # Resource/scheduling bounds are checked before creating any numerical trial.
        schedule=plan['evaluation_plan']
        # A stop-only decision schedules no computation and has no positive trial budget.
        if plan['stop_reason']=='plateau':
            # Reject hidden work in a purported stop, but accept the zero-work response seen in practice.
            if plan['children'] or schedule['seconds']!=0 or schedule['repeats']!=0 or schedule['order'] not in ([],record['parents']):
                # The bounded correction can remove work without inventing positive stop allowances.
                raise ValueError('plateau stop requires no children and a zero-work evaluation plan')
            # Retain the exact decision with no candidate or numerical reservation.
            immutable_json(self.path/'rounds'/f'{record["round_id"]:04d}'/'plan.json',plan)
            # The caller handles the honest unsuccessful plateau transition.
            return record
        # Fair comparisons use one declared common budget/repeat policy for every parent/child.
        if not 0<schedule['seconds']<=self.config['trial_seconds'] or not 1<=schedule['repeats']<=self.config['repeats'] or len(plan['children'])>self.config['children_per_round']:
            # Recombination cannot expand the aggregate per-candidate allowance.
            raise ValueError('model evaluation schedule exceeds declared campaign limits')
        # Diversity must be justified before measurements can favor any artifact.
        if plan['diversity_slot'] and not plan['diversification_reason'].strip():
            # No retroactive unrecorded diversity exception exists.
            raise ValueError('diversity slot needs prior rationale')
        # Every continuing ordinary round must have real inherited variant proposals.
        if not plan['children'] and plan['stop_reason']=='continue':
            # Seed-only portfolio repetitions are not silently labeled algorithm evolution.
            raise ValueError('continuing round needs a novel inherited variant')
        # Plateau rounds must explain an actual diversification action or stop honestly.
        if self.state['stagnation']>=self.config['stagnation_rounds'] and plan['stop_reason']=='continue' and not plan['diversification_reason'].strip():
            # More seeds alone cannot substitute for a justified inherited strategy change.
            raise ValueError('stagnation requires an explicit diversification rationale or plateau stop')
        # Validate all child metadata before publishing the first artifact.
        prepared=[]
        # Duplicate handles are retained as evidence but never counted as novel offspring.
        duplicates=[]
        # Candidate proposal IDs differ from content-derived immutable artifact IDs.
        proposal_ids=set()
        # Every child inherits actual current population members only.
        for child in plan['children']:
            # Safe short proposal names are local schema handles, never filesystem paths.
            if child['proposal_id'] not in ('child1','child2','child3') or child['proposal_id'] in proposal_ids:
                # Duplicate or path-like IDs cannot create new evidence namespaces.
                raise ValueError('invalid/duplicate child proposal ID')
            # Track exact unique within-plan names.
            proposal_ids.add(child['proposal_id'])
            # Real lineage requires one/two distinct parents in this round's population.
            if len(set(child['parent_ids']))!=len(child['parent_ids']) or any(parent not in record['parents'] for parent in child['parent_ids']):
                # A model cannot claim a nonexistent or stale parent artifact.
                raise ValueError('child parent is not in current population')
            # Recombination has two actual parents and must retain both sources in lineage.
            if (child['category']=='recombination')!=(len(child['parent_ids'])==2):
                # A two-parent record is not merely a renamed parameter mutation.
                raise ValueError('recombination category/parent count mismatch')
            # Parent bytes/configuration are verified before inheritance.
            parent=load_artifact(self.path,child['parent_ids'][0])
            # A backend switch is explicit rather than an invented local algorithm name.
            backend=child['backend']
            # Unknown backend names cannot bypass capability filtering.
            if backend not in FEATURES or backend=='qubowl':
                # Missing QuBowl remains excluded, never substituted.
                raise ValueError('unknown/unavailable child backend')
            # Parameter inheritance starts from the actual parent's resolved configuration.
            old=parent['content']['config'] if backend==parent['content']['backend'] else json.loads((self.root/'configs/portfolio'/f'{backend}.json').read_text())
            # All inner JSON blobs are ordinary data; never evaluate them as code.
            changes=json.loads(child['config_json'])
            # The explicit policy object is full replacement, while {} means inherit.
            policy=json.loads(child['policy_json'])
            # A single stage is [], a recombination/sequence is an explicit bounded list.
            stages=json.loads(child['stages_json'])
            # Invalid nested data cannot masquerade as parsed schema strings.
            if not isinstance(changes,dict) or not isinstance(policy,dict) or not isinstance(stages,list):
                # One correction attempt can repair this concrete rejected shape.
                raise ValueError('child nested JSON must be config/policy objects and stage array')
            # Actual differences determine parameter mutation claims.
            new={**old,**changes}
            # Changed-key disclosure is independently recomputed rather than accepted from prose.
            changed=sorted(key for key in set(old)|set(new) if old.get(key)!=new.get(key))
            # Invented or omitted changed keys are not reproducible mutation evidence.
            if sorted(child['changed_keys'])!=changed:
                # A false backend-parameter report is rejected before evaluation.
                raise ValueError('changed_keys does not match actual inherited config changes')
            # Backend-switch provenance must match a real backend change.
            if (backend!=parent['content']['backend'])!=(child['category']=='backend_switch') and child['category']!='recombination':
                # Configuration changes cannot be falsely called a new backend, or vice versa.
                raise ValueError('backend-switch category mismatch')
            # Source path is a fixed safe relative filename, not a patch into controller/protected files.
            if child['source_path'] not in ('','variant.py') or bool(child['source_code'])!=(child['source_path']=='variant.py'):
                # Full source snapshots avoid patch prerequisites escaping the declared namespace.
                raise ValueError('source path must be empty or exactly variant.py with complete source')
            # Empty source inherits parent code except an explicit backend switch.
            source=child['source_code'] or (parent['source'] if backend==parent['content']['backend'] else '')
            # Inherit the full actual policy, not merely a filename or new random seed.
            policy=policy or (parent['content']['policy'] if backend==parent['content']['backend'] else {'representation':'none'})
            # Mutation categories describe actual changed content, not merely a model label.
            source_changed=source!=parent['source']
            # Distinguish executable policy changes from inherited state and parameter-only edits.
            policy_changed=policy!=parent['content']['policy']
            # Parameter provenance cannot hide new code or a new perturbation strategy.
            if child['category']=='parameter' and (source_changed or policy_changed or stages or not changed):
                # A semantic correction can choose the appropriate honest category.
                raise ValueError('parameter mutation must change config only')
            # State-policy proposals change initialization while algorithm-policy proposals may change code or scheduling.
            if child['category']=='state_policy' and (source_changed or not policy_changed):
                # Numerical perturbation alone is recorded separately from algorithm implementation mutation.
                raise ValueError('state_policy must change policy without changing source')
            # Native/retention capabilities cannot be wished into a warm-start interface.
            if policy.get('representation','none')!='none' and FEATURES[backend]['warm_start']=='unsupported':
                # Passing a worse state to an unsupported native backend would silently ignore strategy.
                raise ValueError('state perturbation requires actual supported warm-start/refinement')
            # Recombination/stages split one candidate budget, never multiply full budgets.
            if stages:
                # The simple initial controller supports at most two transparent numerical stages.
                if len(stages)>2 or any(set(stage)!={'backend','config','fraction'} or stage['backend'] not in FEATURES or stage['backend']=='qubowl' or not isinstance(stage['config'],dict) or not isinstance(stage['fraction'],(int,float)) or not math.isfinite(stage['fraction']) or stage['fraction']<=0 for stage in stages) or sum(stage['fraction'] for stage in stages)>1:
                    # No unbounded nested pipeline or changed aggregate budget is admitted.
                    raise ValueError('invalid multistage aggregate fractions/scope')
                # Full stages use actual default parameter names and topology/size compatibility.
                for stage in stages:
                    # Fill omitted defaults so semantic identity is independent of sparse JSON spelling.
                    defaults=json.loads((self.root/'configs/portfolio'/f'{stage["backend"]}.json').read_text())
                    # Canonical complete stage config is saved in the immutable child artifact.
                    stage['config']={**defaults,**stage['config']}
            # Validate actual selected graph compatibility for every proposed stage.
            for stage in stages or [{'backend':backend,'config':new}]:
                # Never lift guards or run an unsupported topology implicitly.
                compatible,reason=eligibility(load_graph(self.context['instance']),stage['backend'],stage['config'],self.config)
                # Incompatible children remain rejected proposals with a concrete reason.
                if not compatible:
                    # One Codex correction may choose an admissible alternative.
                    raise ValueError('child incompatible: '+reason)
                # Any explicit resource-guard increase must also carry a separately reviewable estimate.
                defaults=json.loads((self.root/'configs/portfolio'/f'{stage["backend"]}.json').read_text())
                # Campaign opt-in alone does not explain a specific increased allocation.
                if any(key in stage['config'] and key in defaults and stage['config'][key]>defaults[key] for key in ('max_nodes','max_defects','max_expanded_nodes')) and not child['resource_estimate'].strip():
                    # Numeric-memory estimates are stated as proposals, not measured feasibility.
                    raise ValueError('guard increase lacks explicit resource estimate')
            # Required independent checks are enforced even if the model omits them.
            if not {'signed_examples','ownership'}<=set(child['required_checks']):
                # Every child must preserve the signed objective and caller ownership contract.
                raise ValueError('signed_examples and ownership checks required')
            # Small complete source/config content determines immutable novelty.
            proposed=artifact(self.record['base_identity'],backend,new,policy,stages,source)
            # Existing and within-plan duplicates do not create fictional novel children.
            if (self.path/'candidates'/proposed['id']).exists() or any(item[1]['id']==proposed['id'] for item in prepared):
                # One duplicate must not discard independent valid novel children in the same batch.
                duplicates.append({'proposal_id':child['proposal_id'],'artifact_id':proposed['id'],
                                   'reason':'duplicate semantic candidate identity; skipped without solver/check calls'})
                # Do not save, validate numerically or schedule this repeated strategy again.
                continue
            # Save only after every proposal passes schema, lineage, scope, resource and schedule checks.
            prepared.append((child,proposed))
        # All current parents and proposed children must enter the declared comparison schedule exactly once.
        expected=set(record['parents'])|proposal_ids
        # Missing/extra/repeated evaluation IDs cannot silently favor an offspring.
        if set(schedule['order'])!=expected or len(schedule['order'])!=len(expected):
            # A successful child can still stop remaining work, but the predeclared plan must be fair.
            raise ValueError('evaluation order must contain each parent and child exactly once')
        # An entirely repeated plan still needs the one bounded correction, never fabricated novelty.
        if not prepared and plan['stop_reason']=='continue':
            # Identify each collision so a correction can replace the actual repeated strategies.
            collisions=', '.join(item['proposal_id']+' matches '+item['artifact_id'] for item in duplicates)
            # No artifacts or numerical reservations have been created by this rejected plan.
            raise ValueError('no novel children: duplicate semantic candidate identities: '+collisions+
                             '; replace them using known_candidates, or report plateau')
        # Only now publish independent immutable source/config snapshots.
        mapping={}
        # Each new artifact includes actual lineage and explicit mutation category/hypothesis.
        for child,proposed in prepared:
            # No child ever edits its parent's file or the frozen portfolio.
            candidate_id=save_artifact(self.path,proposed,child['parent_ids'],record['round_id'],child['category'],child['hypothesis'])
            # Proposal handles map to real content IDs for subsequent execution.
            mapping[child['proposal_id']]=candidate_id
        # Persist declared policy BEFORE any measured results are available.
        record['diversity_slot']=plan['diversity_slot']
        # New artifacts start as pending bounded correctness admission.
        record['children']=[{'id':mapping[child['proposal_id']],'admitted':False,'proposal':child} for child,proposed in prepared]
        # Original raw plan and explicit skipped handles explain the effective reduced batch.
        record['duplicate_proposals']=duplicates
        # Fair evaluation plan is immutable while phase state continues durably.
        record['evaluation_plan']={'order':[mapping.get(item,item) for item in schedule['order']
                                            if item in mapping or item in record['parents']],
                                   'seconds':schedule['seconds'],'repeats':schedule['repeats']}
        # Exact structured model decision remains separate from raw transcript bytes.
        immutable_json(self.path/'rounds'/f'{record["round_id"]:04d}'/'plan.json',plan)
        # Caller executes the required deterministic correctness checks next.
        return record
    # Screening and ordinary comparisons use stable complete schedule records before trial execution.
    def build_schedule(self,record,ids,seconds,repeats):
        """Populate durable unique trial IDs and effective seeds; no solver work.

        Same frozen input/budget across each parent/child repeat. Deterministic
        duplicate keys are cached at execution, never billed as independent samples.
        """
        # A recovered schedule is never silently regenerated with new seeds/order.
        if record['schedule']:
            # Existing unlaunched entries continue under their original declared conditions.
            return
        # An explicitly censored comparison keeps old trial directories; never reuse an ID.
        trial_root=self.path/'rounds'/f'{record["round_id"]:04d}'/'trials'
        first_id=1+max((int(path.name[1:]) for path in trial_root.glob('t*') if path.name[1:].isdigit()),default=-1)
        # The explicit model/screen order is stable and recorded.
        for repeat in range(repeats):
            # Every artifact gets the same repeat seed role when compatible.
            for candidate_id in ids:
                # Backend seed constraints come from actual immutable artifact identity.
                candidate=load_artifact(self.path,candidate_id)
                # Stable execution IDs prevent accidental reruns after interruption.
                trial_id=f't{first_id+len(record["schedule"]):04d}'
                # Each scheduled entry starts unlaunched, not failed/cached.
                record['schedule'].append({'id':trial_id,'artifact_id':candidate_id,'repeat':repeat,'seconds':seconds,
                    'seed':trial_seed(self.context['graph_sha256'],self.config['campaign_seed'],record['round_id'],repeat,candidate['content']['backend']),
                    'status':'unlaunched'})
        # Persist schedule before the first process can start.
        self.save_round(record)
    # A single candidate trial has one total budget even when its strategy has two stages.
    def evaluate_schedule(self,record):
        """Execute/reconcile serial scheduled trials, harvest all witnesses, stop early on target.

        No stale parent metrics are reused when frozen input changes. A cached
        record requires exact source, input, seed, budget and state-use identity.
        """
        # Every comparison sees the immutable round-start assignment.
        directory=self.path/'rounds'/f'{record["round_id"]:04d}'
        # Verify frozen bytes before loading actual labels.
        if file_sha256(directory/'frozen_incumbent.txt')!=record['frozen_sha256']:
            # Archive improvements cannot alter this round's comparison baseline.
            raise CampaignError('integrity_error','frozen round incumbent changed')
        # Copying into the request prevents workers owning controller arrays.
        frozen,cut,info=load_assignment(directory/'frozen_incumbent.txt',load_graph(self.context['instance']),self.context['graph_sha256'])
        # Continue only unlaunched/reconcilable entries; completed work is never repeated.
        for entry in record['schedule']:
            # Any already witnessed target has priority over ordinary selection completeness.
            if self.state['status'] in SUCCESS|{'numerical_review_required','target_unreachable_with_evidence'}:
                # Untested entries are censored, never called failed or included in ranking samples.
                if entry['status']=='unlaunched':
                    # Evidence explicitly distinguishes early-success comparison censoring.
                    entry['status']='censored_after_stop'
                # No further solver is scheduled in this serial implementation.
                continue
            # Recovered completed/cached trials already have their own immutable measurements.
            if entry['status'] in ('completed','cached','failed','interrupted'):
                # No duplicate execution under the same ID occurs.
                continue
            # Backend/source identity is rechecked immediately before execution.
            candidate=load_artifact(self.path,entry['artifact_id'])
            # Existing resource caps use actual backend units; screening can have an explicit shorter work cap.
            caps={**self.config['work_caps'],**(self.config['screen_work_caps'] if record['round_id']==0 else {})}
            # Fresh unsupported-start candidates cannot depend on archive labels; warm/retention ones do.
            uses_state=any(FEATURES[stage['backend']]['warm_start']!='unsupported' for stage in candidate['content']['stages']) if candidate['content']['stages'] else FEATURES[candidate['content']['backend']]['warm_start']!='unsupported'
            # Stage composition/source/policy lives in the artifact content identity.
            conditions={'artifact':candidate['content_hash'],'graph':self.context['graph_sha256'],'seconds':entry['seconds'],'seed':entry['seed'],
                        'timing_policy_sha256':identity(POLICY),'frozen':record['frozen_sha256'] if uses_state else None,'work_caps':caps,'stagnation':self.state['stagnation'] if candidate['content']['policy'].get('adaptive') else None}
            # Exact same conditions can reference real earlier evidence instead of claim new samples.
            key=identity(conditions)
            # Every unique execution has a fresh directory; prepared IDs are reconciled below.
            trial_dir=directory/'trials'/entry['id']
            # An interrupted process may have completed observation serialization before checkpointing.
            if entry['status']=='prepared':
                # Recover actual saved outcome where available; never rerun the old execution ID.
                if (trial_dir/'verified_observation.json').exists():
                    # This already includes actual ladder/metrics/provenance.
                    observation=json.loads((trial_dir/'verified_observation.json').read_text())
                    if 'evaluation_elapsed_seconds' not in observation:
                        observation['eligible_for_selection']=False
                        observation['verification_recovery']=True
                # A completed worker observation may still need scoring/archive harvesting.
                elif (trial_dir/'observation.json').exists():
                    # Independently revalidate during harvest and current integrity checks.
                    observation=json.loads((trial_dir/'observation.json').read_text())
                    # Add the stable execution identity if crash preceded this annotation.
                    observation.update(execution_id=f'{self.record["id"]}/{record["round_id"]:04d}/{entry["id"]}',backend=candidate['content']['backend'])
                    # Useful unselected witnesses are not lost in the checkpoint/closure window.
                    self.harvest(observation,record,trial_dir)
                # No serialized outcome means ambiguous interrupted work is explicitly not retried.
                else:
                    # A later round/retry gets a fresh ID and cannot fabricate missing evidence.
                    entry['status']='interrupted'
                    # Remaining unlaunched trials may resume under the same frozen comparison batch.
                    self.save_round(record)
                    # Continue without duplicate work.
                    continue
            # Exact cache hits do not reserve/bill new solver work.
            elif key in self.state['cache']:
                # Current state conditions were included above for every warm path.
                observation=json.loads(Path(self.state['cache'][key]).read_text())
                # Cache metadata distinguishes reuse from a new independent repeat.
                observation={**observation,'cache_source':self.state['cache'][key],'cached':True}
                # A cache hit retains original execution ID so selection deduplicates it.
                trial_dir.mkdir(parents=True,exist_ok=False)
                # Durable reuse receipt contains the full exact condition key.
                immutable_json(trial_dir/'cached_observation.json',{'conditions':conditions,'observation':observation})
                # Its immutable target witness still receives archive/target checks if needed.
                self.harvest(observation,record,trial_dir)
                # No duplicate native trial is billed as another independent sample.
                entry['status']='cached'
            # New actual numerical execution receives one bounded aggregate reservation.
            else:
                # Nested recombination stages consume solver-call slots, not multiplied full seconds.
                slots=max(1,len(candidate['content']['stages']))
                # Reserve before the unique execution path/status becomes prepared.
                allowance=self.reserve('trial',entry['seconds'],trial_dir,slots)
                # Prepared status is durable before any worker subprocess exists.
                entry['status']='prepared'
                # A clipped budget changes cache conditions and is recorded as a real different condition.
                conditions['seconds']=allowance
                # The effective key can never claim an unclipped full-budget evaluation.
                key=identity(conditions)
                # Checkpoint the exact execution ID before process launch.
                self.save_round(record)
                # All parent/child work uses the same frozen state even if archive improved mid-round.
                started=time.monotonic()
                # Read-only filesystem/source checks prevent research changes outside scope.
                self.integrity()
                # Numerical work leaves reserved room for independent official scoring/output.
                remaining=max(0,started+allowance-time.monotonic())
                verification_reserve=min(POLICY['verification_reserve_seconds'],max(POLICY['minimum_verification_reserve_seconds'],allowance*.5))
                numerical_seconds=min(allowance*POLICY['worker_fraction'],max(0,remaining-verification_reserve))
                immutable_json(directory/('timing-'+entry['id']+'.json'),{'policy':POLICY,'aggregate_seconds':allowance,'numerical_seconds':numerical_seconds,'reserved_verification_seconds':verification_reserve})
                if numerical_seconds<=0:
                    raise CampaignError('verification_timeout','no numerical allowance remains after reserving verification')
                observation=launch_trial(self.path,self.context,entry['artifact_id'],frozen.tolist(),entry['seed'],numerical_seconds,caps,trial_dir,
                                         stagnation=self.state['stagnation'],stop_path=self.path/'stop.json')
                # This stable execution identity prevents duplicate independent-repeat credit.
                observation.update(execution_id=f'{self.record["id"]}/{record["round_id"]:04d}/{entry["id"]}',backend=candidate['content']['backend'],conditions=conditions)
                # Protected files and the actual frozen archive are verified after numerical execution.
                self.integrity()
                # Every valid admitted candidate can improve the archive, selected or not.
                self.harvest(observation,record,trial_dir,deadline=started+allowance)
                # End-to-end observation includes numerical setup, verification and official receipt.
                observation['evaluation_elapsed_seconds']=time.monotonic()-started
                # A native/local stop request must close honestly instead of schedule another trial.
                if observation['process']['stopped']:
                    # Target witness, if any, still takes precedence over operational interruption.
                    if self.state['status'] not in SUCCESS:
                        # No successful target is fabricated from an interrupted run.
                        self.state['status']='interrupted'
                # Independent scoring overrun cannot be hidden behind a nominal solver time.
                observation['allocated_end_to_end_seconds']=allowance
                # Overruns are visible and cannot establish a fair completed comparison.
                if observation['evaluation_elapsed_seconds']>allowance:
                    # The witness can remain archived, but no stronger timing/budget claim is made.
                    observation['eligible_for_selection']=False
                    # Preserve exact actual elapsed, not a clipped reported duration.
                    observation['verification_budget_overrun']=True
                # Save complete verified observation before releasing the execution reservation.
                atomic_json(trial_dir/'verified_observation.json',observation)
                # Actual cumulative trial count is distinct from solver/check call-slot reservations.
                self.state['counters']['candidate_trials']+=1
                # Only completed real observations can populate an exact-condition cache.
                self.state['cache'][key]=str(trial_dir/'verified_observation.json')
                # Measured completion clears this crash-reservation hold and charges elapsed time once.
                self.finish_operation()
            # Each execution/reuse is recorded once in this round's deterministic outcome table.
            if not any(item['execution_id']==observation['execution_id'] and item.get('scheduled_id')==entry['id'] for item in record['observations']):
                # Cache copies keep original execution identity but their own schedule provenance.
                record['observations'].append({**observation,'scheduled_id':entry['id']})
            # Completed serialization precedes marking the durable schedule slot complete.
            if entry['status']!='cached':
                # Invalid outcomes remain explicit failures, not silently dropped repeats.
                entry['status']='completed' if observation['valid'] else 'failed'
            # Current archive and schedule cannot be lost between trials.
            self.save_round(record)
            # Durable stop prevents launching an additional entry in this serial loop.
            if self.state['status']=='interrupted':
                # Resume can continue remaining unlaunched schedule entries later.
                raise CampaignError('interrupted','orderly stop during numerical execution')
        # Early-success/censored entries become durable before finalization.
        self.save_round(record)

    def mutation_round(self,record):
        """Obtain bounded real plan/correction, admit/check children and prepare comparisons.

        Invalid output gets at most one correction per explicit run/resume action;
        cumulative call usage remains charged. Never substitutes random children.
        """
        # Planning does not run again after a valid plan/source snapshot was saved.
        if record['phase']=='planning':
            # One novel single-stage child needs eight checks and at least one trial per competitor.
            minimum=8+sum(max(1,len(load_artifact(self.path,parent)['content']['stages'])) for parent in record['parents'])+1
            # Avoid calling Codex for proposals that cannot receive a valid paired comparison.
            if self.config['max_solver_trials'] is not None and self.config['max_solver_trials']-self.state['counters']['solver_calls_reserved']<minimum:
                # Remaining slots stay unspent; cumulative limits can be raised explicitly on resume.
                raise CampaignError('solver_budget_exhausted','insufficient solver/check slots for one novel child and paired evaluation')
            # Prior measured outcomes and complete parent code enter the real model prompt.
            context=self.model_context(record)
            # One correction attempt is allowed for malformed/invalid proposals.
            correction=None
            # Both attempts consume the same finite global call quota.
            for attempt in range(2):
                # Every call/correction receives a fresh durable transcript path.
                index=self.state['counters']['codex_calls']+self.state['counters']['fixture_calls']
                # Logs are outside numerical output but scoped to this campaign/round.
                directory=self.path/'logs/codex'/f'round-{record["round_id"]:04d}-call-{index:04d}'
                # A bounded model call is reserved before actual process launch.
                allowance=self.reserve('codex',self.config['codex_call_timeout_seconds'],directory)
                # Explicit provider call count selects only deterministic test fixture records.
                fixture_index=self.state['counters']['fixture_calls']-1
                # Real production bridge captures raw stdin/JSONL/stderr and final schema output.
                plan,receipt=request_plan(self.config,context,directory,allowance,fixture_index,correction,self.path/'stop.json')
                # Usage remains recorded even when the model output is invalid.
                self.state.setdefault('codex_receipts',[]).append(str(directory/'receipt.json'))
                # Finished calls cannot be charged a second full timeout after recovery.
                self.finish_operation()
                # Actual interruption is an honest resumable state, not a correction opportunity.
                if receipt['process'].get('stopped'):
                    # No more Codex calls are issued after a durable stop request.
                    raise CampaignError('interrupted','Codex call stopped by user')
                # Missing/failed CLI access is not repaired with a fake fixture response.
                if plan is None and (receipt['process']['exit_code']!=0 or receipt['process']['timed_out']):
                    # Preserve all raw output and exact failed access/timeout reason.
                    raise CampaignError('awaiting_codex','; '.join(receipt.get('runtime_diagnostic',[])) or receipt.get('rejection','Codex failed'))
                # Semantic admission has no privileged trust in model text.
                try:
                    # Malformed JSON is a concrete correction reason with raw bytes already saved.
                    if plan is None:
                        # Continue only through the explicit bounded correction path.
                        raise ValueError(receipt.get('rejection','malformed proposal'))
                    # Validate actual lineage, hashes, scope, novelty and budget scheduling.
                    record=self.admit_plan(plan,record)
                    # A model-explained plateau is a blocked checkpoint, never successful target attainment.
                    if plan['stop_reason']=='plateau':
                        # Preserve the valid structured stop reason and prior measured deficit.
                        self.save_round(record)
                        # No blind identical-seed replay continues indefinitely.
                        raise CampaignError('awaiting_codex','Codex reports no novel justified continuation: plateau')
                    # Admission phase is write-ahead before correctness checks.
                    record['phase']='admitting'
                    # Parent/child source snapshots are durable now.
                    self.save_round(record)
                    # One valid plan needs no extra summary call; next round receives measured results.
                    break
                # Invalid proposals remain durable separate rejected artifacts.
                except (ValueError,TypeError,SyntaxError,KeyError) as error:
                    # Correction uses the exact concrete failure, not silently altered model JSON.
                    correction=f'{type(error).__name__}: {error}'
                    # Record source/config rejection before possibly asking once more.
                    record['rejections'].append({'call':str(directory),'reason':correction})
                    # The rejected plan remains in raw/final files for audit.
                    self.save_round(record)
                    # Failure after one bounded correction becomes a resumable awaiting state.
                    if attempt==1:
                        # No mock/random proposal is substituted.
                        raise CampaignError('awaiting_codex','proposal and one correction rejected: '+correction)
        # Correctness tests are separately budgeted actual numerical work, not proof from model narrative.
        if record['phase']=='admitting':
            # All admitted children must pass before becoming comparison candidates.
            for child in record['children']:
                # Recovered completed admission checks are not rerun as new evidence.
                if child.get('check_path'):
                    # The recorded outcome determines actual admission status.
                    continue
                # Stage count multiplies call slots but never the total check-time budget.
                candidate=load_artifact(self.path,child['id'])
                # Eight required tiny examples exercise objective/ownership/scope.
                slots=8*max(1,len(candidate['content']['stages']))
                # A retry after an interrupted check owns a new explicit directory.
                checks=self.path/'rounds'/f'{record["round_id"]:04d}'/'checks'
                # Fresh attempt index prevents stale check files being treated as new success.
                index=len(list(checks.glob(child['id']+'-*'))) if checks.exists() else 0
                # Immutable artifact ID plus attempt index defines a unique admission execution.
                directory=checks/(child['id']+'-'+str(index))
                # Reserve validation cost in the same global wall/solver-call budgets.
                seconds=self.reserve('check',self.config['validation_seconds'],directory,slots)
                # Tiny checks use the same actual artifact, seed protocol and declared work caps.
                result=launch_trial(self.path,self.context,child['id'],json.loads(json.dumps([1,-1])),self.config['campaign_seed'],seconds,
                                    self.config['work_caps'],directory,check=True,stop_path=self.path/'stop.json')
                # Raw results never upgrade model code on a partial validation failure.
                child['admitted']=result['valid']
                # Persist exact real check path and outcome.
                child['check_path']=str(directory/'observation.json')
                # Validation work is counted independently from target trial successes.
                self.state['counters']['validation_batches']+=1
                # Clear the operation hold only after its durable actual result.
                self.finish_operation()
                # All original immutable source/input/assignment checks still apply after code execution.
                self.integrity()
                # A rejected child cannot win by retaining the warm archive.
                if not child['admitted']:
                    # Keep its complete code, raw stderr and independent failure evidence.
                    record['rejections'].append({'artifact_id':child['id'],'reason':'bounded signed/ownership validation failed'})
                # A crash now can reuse this check record without reexecuting its old ID.
                self.save_round(record)
            # Continuing without any valid novel child is not algorithm evolution.
            if not any(child['admitted'] for child in record['children']):
                # Close this rejected-children round with an honest deficit/blocked state.
                raise CampaignError('awaiting_codex','no proposed novel child passed admission')
            # Only actual parent artifacts and admitted children can enter comparisons.
            admitted=set(record['parents'])|{child['id'] for child in record['children'] if child['admitted']}
            # Rejected proposals are retained but explicitly not scheduled as valid competitors.
            order=[item for item in record['evaluation_plan']['order'] if item in admitted]
            # Write the common-budget schedule before measuring any candidate.
            self.build_schedule(record,order,record['evaluation_plan']['seconds'],record['evaluation_plan']['repeats'])
            # Comparison phase is durable for interruption/resume.
            record['phase']='evaluating'
            # No archive changes can alter its already frozen incumbent.
            self.save_round(record)
        # Ordinary numerical comparisons use actual new measurements for parents and children alike.
        if record['phase']=='evaluating':
            # Early target success censors all remaining work through the same serial schedule.
            self.evaluate_schedule(record)
    # A closed round is durably verified before any successor round can begin.
    def close_round(self,record,reason=None):
        """Freeze selection/private log/manifest and close once without Git or public writes.

        Closed/rejected/interrupted rounds retain hypotheses, variants, transcripts,
        scores, censoring and proof status. Partial interrupted batches can instead
        remain open for resume when no blocking close is requested by the caller.
        """
        # Round namespace is fixed by its write-ahead integer ID.
        directory=self.path/'rounds'/f'{record["round_id"]:04d}'
        # Once a manifest exists, only closure reconciliation is permitted.
        if not (directory/'round_manifest.json').exists():
            # Selection uses real measurements even if new children were rejected.
            survivors,ranking=select_survivors(record['observations'],self.config['survivors'],record['diversity_slot'])
            # Preserve population when no complete ranking is available at early target success or blocking admission.
            if survivors:
                # State is not chosen from archive provenance alone.
                self.state['parents']=survivors
            # A successful/censored batch is explicitly not a complete statistical comparison.
            selection={'round_id':record['round_id'],'survivors':survivors,'ranking':ranking,'policy':'best exact cut, median comparable cut, completion-time upper bound, artifact ID',
                       'diversity_slot_predeclared':record['diversity_slot'],'comparison_complete':all(entry['status'] in ('completed','cached','failed') for entry in record['schedule']),
                       'rejections':record['rejections'],'duplicate_proposals':record.get('duplicate_proposals',[]),
                       'schedule':record['schedule'],'archive':self.state['archive'],'stop_status':self.state['status'],'reason':reason}
            # Model explanations never replace this deterministic selection receipt.
            immutable_json(directory/'selection.json',selection)
            # Stagnation counts completed ordinary rounds without a strict archive improvement.
            improved=self.state['archive']['sha256']!=record['started_archive_sha256']
            # Reset follows actual verified archive progress, not a new seed or narrative claim.
            if record['round_id']>0:
                # No hidden budget enlargement accompanies stagnation/diversification.
                self.state['stagnation']=0 if improved else self.state['stagnation']+1
            # Human-readable summary labels partial evidence and target/proof separately.
            text=f'# Campaign {self.record["id"]}, round {record["round_id"]:04d}\n\nStatus: {self.state["status"]}. Reason: {reason or "round completed"}.\n\nFrozen cut: {record["frozen_metrics"]["cut"]}; archive cut: {self.state["archive"]["metrics"]["cut"]}; target score: {self.config["target_score"]}; actual score: {self.state["archive"]["metrics"]["score"]}.\n\nParents: {record["parents"]}. Proposed children: {[child["id"] for child in record["children"]]}. Survivors: {survivors}.\n\nFailures/rejections: {record["rejections"]}. Schedule/censored trials, actual raw logs, score receipts and immutable source/config artifacts are linked by selection.json and round_state.json. Candidate fitness and harvested archive are separate.\n'
            # Skipped duplicates remain explicit in both human and machine-readable round evidence.
            text+=f'\nSkipped duplicate proposals (not new candidates or numerical work): {record.get("duplicate_proposals",[])}\n'
            # Summary is a separate narrative, never called an unedited raw transcript.
            (directory/'summary.md').write_text(text)
            # Global round log uses unique markers for idempotent recovery.
            log=self.path/'logs/rounds.md'
            # Each campaign owns its narrative independently of other writers.
            log.parent.mkdir(parents=True,exist_ok=True)
            # A fresh repository has no prior evolution log yet.
            content=log.read_text() if log.exists() else '# Evolution round log\n\n'
            # One exact marker prevents duplicate log entries after interruption.
            marker=f'<!-- {self.record["id"]}/{record["round_id"]:04d} -->'
            # Append once while holding only this campaign's mutation lock.
            if marker not in content:
                # Relative links preserve reviewability inside Git history.
                log.write_text(content+marker+'\n'+text.replace('# Campaign','## Campaign',1)+'\n[Round evidence]('+os.path.relpath(directory,log.parent)+'/round_manifest.json)\n\n')
            # A closed manifest pins actual variant/config/log/trial receipts without its own future commit hash.
            record['phase']='closed_prepared'
            # Closure preparation state is durable before verifying its receipt.
            self.save_round(record)
            # Manifest excludes its own hash and ephemeral active-process records.
            files={str(path.relative_to(directory)):file_sha256(path) for path in directory.rglob('*') if path.is_file() and path.name not in ('round_manifest.json','active_process.json')}
            # Exact source/config artifacts and initial prerequisites are separately content-addressed and retained.
            immutable_json(directory/'round_manifest.json',{'campaign':self.record['id'],'round_id':record['round_id'],'files':files,
                'candidates':record['parents']+[child['id'] for child in record['children']],'base_identity':self.record['base_identity'],
                'raw_codex_receipts':self.state.get('codex_receipts',[]),'archive':self.state['archive'],'status':self.state['status']})
        # The next round starts only after manifest/closure receipt verification.
        digest=self.finalize_round(record['round_id'])
        # Closure identity is recorded after its immutable manifest is complete.
        self.record_closed(record['round_id'],digest)
    # Closure reconciliation is idempotent across controller interruptions.
    def record_closed(self,round_id,digest):
        """Record manifest/pending/next-round pointers once; no numerical work or Git calls."""
        # Duplicate receipt recovery never increments the ordinary round count twice.
        if not any(item['round_id']==round_id for item in self.state['closed_rounds']):
            # Manifest identities are durable subsequent-checkpoint receipts.
            self.state['closed_rounds'].append({'round_id':round_id,'manifest_sha256':digest,'commit':None})
        # This round can no longer schedule a trial or another closure.
        self.state['pending_round']=None
        # Ordinary round cap counts mutation rounds, separate from mandatory screening round zero.
        self.state['next_round']=round_id+1
        # Archive remains independently reloadable after every completed round.
        self.checkpoint()
    # One user launch carries all ordinary rounds forward without per-round approval.
    def run(self):
        """Recover and execute this one-graph campaign until target/limit/block/interruption.

        Returns status dict. Every closed round has a private immutable receipt;
        no automatic Git/public writes or implicit second graph search.
        """
        # Historical branch/commit campaigns are preserved without implicit source/path migration.
        if self.record.get('execution_mode')!='isolated':
            # Never enter an old auto-committing loop through the new no-commit controller.
            raise CampaignError('legacy_campaign','Historical campaign is read-only; start a fresh isolated campaign from consolidated solutions.')
        # Each independent controller locks only its own checkpoint/artifacts.
        with CampaignLock(self.root,self.path):
            # Reload under ownership so two sequential resume requests cannot use stale checkpoints.
            self.__init__(self.root,self.path)
            # Exception handling must preserve the best pointer and all accumulated counters.
            record=None
            # User interrupts and ordinary blockers become durable machine-readable states.
            try:
                # Resume first reconciles ambiguous work and private closure receipts.
                self.recover()
                # Derived private results can be reconstructed after an interrupted export.
                self.export_best()
                # An already verified target needs no new solver or Codex work.
                if self.state['status'] in SUCCESS and self.state['pending_round'] is None:
                    # Return actual persisted success rather than make pointless mutations.
                    return self.status()
                # A diagnostic requiring human numerical review must not silently resume ordinary search.
                if self.state['status'] in {'numerical_review_required','target_unreachable_with_evidence'} and self.state['pending_round'] is None:
                    # A fresh campaign/configuration is required after resolving the recorded contradiction.
                    return self.status()
                # A consumed stop flag is removed only by explicit resume, not automatically in this loop.
                self.state['status']='running'
                # A resumed run should not display a stale exhausted/interrupted reason while executing.
                self.state['reason']=None
                # Continue only one immutable graph; outer loop iterates rounds, not instances.
                while True:
                    # Source/ref/archive invariants are checked at every state transition.
                    self.integrity()
                    # A pending round resumes its own write-ahead identifier/frozen state.
                    round_id=self.state['pending_round'] if self.state['pending_round'] is not None else self.state['next_round']
                    # First reached ordinary round limit prevents further model/numerical work.
                    if self.config['max_rounds'] is not None and round_id>self.config['max_rounds']:
                        # Screening remains round zero even with max_rounds=0.
                        raise CampaignError('round_budget_exhausted','ordinary round limit reached')
                    # Stop and wall/call/trial checks precede every external operation through reserve().
                    if self.available_seconds()<=0:
                        # No solver is launched using checkpoint/finalization time.
                        raise CampaignError('wall_budget_exhausted','active campaign time exhausted')
                    # Write-ahead round inputs are created before target/screen/mutation actions.
                    record=self.open_round(round_id)
                    # Initial target achievement exits with a durable private initialization receipt.
                    if self.state['archive']['metrics']['target_met']:
                        # No model call, candidate mutation or solver screening is required.
                        self.state['status']='target_already_met' if round_id==0 else 'target_reached'
                    # A near-threshold official/exact mismatch is not rounded into a success.
                    elif round_id==0 and self.state['archive']['metrics']['numerical_review']:
                        # Save exact diagnosis and stop without changing the reference.
                        self.state['status']='numerical_review_required'
                    # Initialization screens every eligible entry once under short comparable budgets.
                    elif round_id==0:
                        # Initial baseline artifacts remain available even when not selected as survivors.
                        self.build_schedule(record,self.record['initial_candidates'],self.config['screen_trial_seconds'],1)
                        # Screening harvests improvements and can stop promptly before any LLM call.
                        self.evaluate_schedule(record)
                        # No verified search witness means no legitimate ranking/population for mutation.
                        if not select_survivors(record['observations'],self.config['survivors'])[0] and self.state['status'] not in SUCCESS|{'numerical_review_required','target_unreachable_with_evidence'}:
                            # An incumbent-only hard fallback is not credited as a successful search implementation.
                            self.state['status']='no_eligible_candidate'
                    # Ordinary mutation requires an actual surviving population, with BM still an available restart artifact.
                    else:
                        # No unavailable QuBowl or rejected-source artifact can be an invented parent.
                        if not record['parents']:
                            # User can review screening failures/constraints in the private receipt.
                            raise CampaignError('no_eligible_candidate','no verified eligible parent population')
                        # Real Codex proposes, controller checks, numerical code measures.
                        self.mutation_round(record)
                    # All closed rounds retain screening/target/rejection evidence without a Git requirement.
                    self.close_round(record)
                    # A verified target or explicit unsuccessful diagnostic/blocked state stops this campaign.
                    if self.state['status']!='running':
                        # Remaining public problems are never automatically started.
                        return self.status()
                    # Subsequent model context references actual just-measured outcomes.
                    record=None
            # Keyboard interrupt is resumable and not a fake completed batch.
            except KeyboardInterrupt:
                # Owned subprocess helpers already stop/reap their exact descendants.
                self.state['status']='interrupted'
                # A partially evaluated batch retains its schedule/frozen input for continuation.
                self.state['reason']='SIGINT; resume preserves completed execution IDs'
            # Expected stops/errors remain concrete durable outcomes.
            except CampaignError as error:
                # No failure state aliases target success.
                self.state['status']=error.state
                # Preserve actual consistency/quota/model/git failure reason.
                self.state['reason']=str(error)
                # Rejected children/model failures close a durable private round with raw evidence.
                if record is not None and error.state in ('awaiting_codex','no_eligible_candidate','llm_budget_exhausted','solver_budget_exhausted','wall_budget_exhausted','round_budget_exhausted'):
                    # A round with already completed numerical/model work is worth preserving as a graded receipt.
                    try:
                        # A closure failure blocks later rounds without discarding the verified archive.
                        self.close_round(record,str(error))
                    # Do not retry failed closure indefinitely.
                    except CampaignError as closing_error:
                        # The prepared manifest and measurements remain available for resume.
                        self.state.update(status=closing_error.state,reason=str(closing_error))
            except OwnedCleanupError as error:
                # A cleanup failure blocks further launches and retains the ownership receipt.
                self.state.update(status='cleanup_failed',reason=str(error))
            # Corrupted metadata, failed I/O or uncaught backend protocol errors are blocking integrity issues.
            except (OSError,ValueError,TypeError,KeyError,subprocess.SubprocessError) as error:
                # Preserve all raw evidence and the last valid archive pointer.
                self.state.update(status='integrity_error',reason=f'{type(error).__name__}: {error}')
            # Checkpoint never invents an unobserved best assignment or resets past costs.
            finally:
                # A live reservation is conservatively reconciled on resume if the controller was interrupted.
                self.checkpoint()
            # Every unsuccessful stop includes a command to resume this exact campaign.
            return self.status()
    # Status does not run solvers or call Codex.
    def status(self):
        """Return current campaign/target/ladder/counter/commit status, read-only JSON data."""
        # Full ladder score of the latest archive may be found in its actual trial receipt.
        receipt_records=[*(self.path/'rounds').glob('*/round_state.json'),*(self.path/'source-revisions').glob('*/before/rounds/*/round_state.json')]
        receipts=[item.get('ladder_score_path') for path in receipt_records for item in json.loads(path.read_text()).get('observations',[]) if item.get('ladder_score_path') and item.get('metrics',{}).get('exact_cut')==self.state['archive']['metrics']['exact_cut']]
        # Missing receipt remains explicit, never replaced by a partial-folder score.
        overall=json.loads(Path(receipts[-1]).read_text())['overall'] if receipts else self.context['initial_ladder_overall']
        # Only runtime status, not a formatted six-digit table, determines success.
        return {'timing_runtime_version':self.record.get('timing_policy',{}).get('version',1),'source_revision':self.record.get('source_revision',0),'campaign_id':self.record['id'],'instance':self.context['instance_name'],'status':self.state['status'],'reason':self.state.get('reason'),
                'execution_mode':self.record.get('execution_mode','legacy_branch_campaign'),
                'results_directory':str(self.path/'results'),'logs_directory':str(self.path/'logs'),
                'commit_policy':'manual' if self.record.get('execution_mode')=='isolated' else 'historical_automatic',
                'public_solutions_updated':self.record.get('execution_mode')!='isolated' and self.state.get('public_sha256')!=self.context.get('public_initial_sha256'),
                'archive':self.state['archive'],'deficit_cut':self.state['archive']['metrics']['target_cut']-self.state['archive']['metrics']['cut'],
                'assembled_ladder_score_target_only_reevaluation':overall,'target_proof_separate':True,
                'counters':self.state['counters'],'spent_wall_seconds':self.state['spent_wall_seconds'],'closed_rounds':self.state['closed_rounds'],
                'pending_round':self.state['pending_round'],'best_bound':self.state.get('best_bound'),
                'resume_command':f'uv run python evolve_search.py resume --campaign-id {self.record["id"]}'}

# Initialization is itself durable input evidence, never an automatic public campaign started by planning.
def create_campaign(root,instance,config,campaign_id):
    """Create one fresh private campaign, return Campaign; no search or Git mutation yet.

    Explicit root/instance/config/id inputs. Freezes actual source/refs/solutions,
    records real HEAD ancestry and compatible/excluded entries. Never overwrites
    an existing campaign, user files, tags or remote refs.
    """
    # Initialization is active campaign work, including source hashing and full-ladder verification.
    initialized_at=time.monotonic()
    # Child model/numerical environments must never recursively launch this controller.
    if os.environ.get('MAXCUT_EVOLUTION_CODEX_CHILD') or os.environ.get('MAXCUT_EVOLUTION_WORKER'):
        # Self-recursion would evade the configured call/resource caps.
        raise CampaignError('integrity_error','recursive campaign creation refused')
    # Safe campaign IDs become paths/trailers without shell interpretation.
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',campaign_id) or '..' in campaign_id:
        # No arbitrary filesystem path can be chosen via an identifier.
        raise ValueError('campaign ID must be a short safe unique basename')
    # Resolve actual root, retaining all subsequent user work instead of resetting a historical baseline.
    root=root.resolve()
    # Default validation ensures every accepted option has implemented semantics.
    config=configuration(config)
    # Symlinks must not redirect configured input/output data outside the selected checkout.
    for key in ('instances','references','baseline_solutions','public_solutions'):
        # Resolve existing parents even if the eventual output directory is not created yet.
        if not (root/config[key]).resolve().is_relative_to(root):
            # Refuse before creating campaign files or reading unrelated assignments.
            raise ValueError('configured data path escapes checkout: '+key)
    # Fresh paths are required for both numerical state and raw Codex streams.
    path=root/'evolve/campaigns'/campaign_id
    # Framework/log symlinks cannot turn a valid campaign identifier into an external write.
    if not path.resolve().is_relative_to(root):
        # No campaign or log directory is created outside this repository.
        raise ValueError('campaign/log path escapes checkout')
    # Atomically reserving a new ID prevents competing initializers from sharing partial state.
    try:
        # Exclusive mkdir, rather than a separate exists check, closes same-ID initialization races.
        path.mkdir(parents=True,exist_ok=False)
    # Preserve existing/partial evidence and require explicit resume or another ID.
    except FileExistsError as error:
        # This remains the same actionable user error as the original single-campaign interface.
        raise ValueError('campaign directory exists; use resume or a fresh ID') from error
    # Only this new campaign is locked during snapshotting; other campaigns continue normally.
    with CampaignLock(root,path):
        # Git identity is optional read-only provenance; no branches/index/commits are modified.
        try:
            # A checkout without Git metadata can still own isolated campaign evidence.
            head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
        # Missing Git or an unversioned directory is explicitly recorded, not fabricated.
        except (OSError,subprocess.SubprocessError):
            # Source manifests, rather than a branch requirement, establish actual implementation identity.
            head=None
        # Copy all actual source/config prerequisites before deriving candidate identities.
        base_identity=snapshot(root,path)
        # Freeze references/full actual assignments and the one selected graph context.
        context=freeze_inputs(root,path,config,instance)
        # Independent graph features drive capability-aware screening exclusions.
        graph=load_graph(context['instance'])
        # Real discovered features are saved once and rechecked on resumed evaluations.
        capabilities=list_solvers()
        # Compatible baseline artifacts and excluded reasons remain distinct.
        initial,excluded=[],{}
        # Every installed entry is inspected, without running another graph.
        for backend,features in capabilities.items():
            # An explicit fixture/user screening subset is transparent; default None screens all compatible entries.
            if config['screen_solvers'] is not None and backend not in config['screen_solvers']:
                # This is declared configuration, not a hidden claim that an unscreened method was measured.
                excluded[backend]='excluded by explicit screen_solvers setting'
                # No candidate work is reserved for the excluded backend.
                continue
            # Unavailable entries need no nonexistent default config file or native invocation.
            if not features['available']:
                # Preserve the actual current absence reason.
                excluded[backend]=features['availability_reason']
                # No mock QuBowl candidate is created.
                continue
            for settings in initial_configurations(root,backend,config):
                compatible,reason=eligibility(graph,backend,settings,config)
                if not compatible:
                    excluded[backend+':'+identity(settings)[:8]]=reason
                    continue
                candidate=artifact(base_identity,backend,settings,{'representation':'none'},[])
                initial.append(save_artifact(path,candidate,[],0,'existing_portfolio','explicit initial configuration; target performance unmeasured'))
        # Preserve BM as an available restart artifact even when explicitly omitted from fixture screening.
        bm=json.loads((root/'configs/portfolio/bm.json').read_text())
        # Saving it does not force BM into the selected parent population.
        bm_candidate=artifact(base_identity,'bm',bm,{'representation':'none'},[])
        # Content identity can already exist among screened candidates.
        if not (path/'candidates'/bm_candidate['id']).exists():
            # This available restart option has no fictitious target performance measurement.
            save_artifact(path,bm_candidate,[],0,'available_restart','preserved baseline BM restart option, not forced survivor')
        # Track actual baseline ancestry when available without forcing a reset.
        ancestor=bool(head) and subprocess.run(['git','merge-base','--is-ancestor','a19c758',head],cwd=root,capture_output=True).returncode==0
        # Immutable startup record includes actual dirty-source hashes and all exclusions.
        record={'version':2,'timing_policy':POLICY,'source_revision':0,'execution_mode':'isolated','id':campaign_id,'starting_head':head,'branch':None,'descends_from_a19c758':ancestor,
                'base_identity':base_identity,'protected_manifest':protected_manifest(root),'initial_candidates':initial,
                'baseline_bm_restart':bm_candidate['id'],'capabilities':capabilities,'excluded':excluded,'provider':config['provider']}
        # Starting config revision never changes in place on resume.
        immutable_json(path/'config-revisions/0000.json',config)
        # Context/source/candidate identities are durable before a single model/solver call.
        immutable_json(path/'campaign.json',record)
        # Archive initialization always uses actual validated existing labels or the explicit trivial fallback.
        signs,value,info=load_assignment(Path(context['initial_assignment']),graph,context['graph_sha256'])
        # Archive and candidate population begin as separate objects.
        archive=archive_witness(path,context,signs,{'kind':context['initial_origin']},config['target_score'])
        # Counters persist across sessions; reserved calls conservatively account for crashes.
        state={'status':'initialized','config':config,'config_revision':0,'archive':archive,'parents':[],'next_round':0,'pending_round':None,
               'closed_rounds':[],'spent_wall_seconds':time.monotonic()-initialized_at,'reservation':None,'stagnation':0,'cache':{},'best_bound':None,
               'public_sha256':context['public_initial_sha256'],'counters':{'solver_calls_reserved':0,'candidate_trials':0,'validation_batches':0,'codex_calls':0,'fixture_calls':0}}
        # Initial finite atomic checkpoint is sufficient to resume before screening starts.
        atomic_json(path/'state.json',state)
        # Even initialization has a private readable result, without touching root solutions/.
        initialized=Campaign(root,path)
        # All subsequent improvement exports use this same original-order assignment location.
        initialized.export_best()
        # Include initialization/export overhead in the campaign's cumulative active time.
        initialized.checkpoint()
    # The run method acquires only this campaign's lock independently.
    return Campaign(root,path)
