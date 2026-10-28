"""Trusted bounded numerical worker over frozen sources and isolated research hooks."""
# JSON requests/results carry only explicit finite configuration and witnesses.
import json
# Research modules load from a recorded file, never a mutable global import name.
import importlib.util
# Temporary native outputs stay inside the trial's writable work directory.
import os
# Explicit Paths identify frozen prerequisites, not user-selected shell code.
from pathlib import Path
# The legacy runner executes as its original CLI for ordinary portfolio stages.
import subprocess
# The same isolated Python interpreter runs every trusted numerical stage.
import sys
# Monotone deadlines include perturbation, all stages and local checking.
import time
# Tracebacks preserve actual failed candidate/code behavior.
import traceback
# Numerical state arrays always own copied memory.
import numpy as np
# Validated original kernels stay unchanged.
from bm_solver import angles_from_signs,cut_value,graph_digest,load_graph,solve_from_angles,validate_signs,write_assignment
# Prepared selection/perturbation primitives retain original coordinate semantics.
from portfolio_perturbations import perturb_binary,perturb_selected_angles,select_subset,adaptive_strength
# Shared dispatcher supports bounded correctness fixtures without a separate optimization implementation.
from solver_portfolio import FEATURES,solve
# Research source identity is checked before imports and before return.
from evolution_candidates import load_artifact
# Finite atomic metadata and actual file hashes are reused rather than reimplemented.
from evolution_common import identity
# Atomic metadata and original file hashes are protected evidence helpers.
from run_bm import atomic_json,file_sha256

# The original required examples test validity/sign conventions without demanding heuristic optimality.
CASES=[(2,[(0,1,2)]),(2,[(0,1,-2)]),(3,[(0,1,1),(1,2,1),(0,2,1)]),
       (4,[(0,1,1),(1,2,1),(2,3,1),(0,3,1)]),(3,[(0,1,5),(1,2,3),(0,2,1)]),
       (3,[(0,1,4),(1,2,3),(0,2,-2)]),(3,[(0,1,4),(1,2,-3),(0,2,-2)]),
       (4,[(0,1,3),(2,3,3),(0,2,2),(0,3,2),(1,2,2),(1,3,2)])]

def admission_cases(record):
    """Select eight signed validity/ownership fixtures within every stage's domain.

    Toroidal methods require actual odd/even periodic grids. Their unsupported
    topology rejection is separately tested, never confused with invalid output.
    General methods keep all eight original signed fixtures and the trap.
    """
    backends=[stage['backend'] for stage in record['content']['stages']] or [record['content']['backend']]
    if not any(backend.startswith('toroidal') for backend in backends):
        return [('signed_'+str(i),n,edges) for i,(n,edges) in enumerate(CASES)]
    fixtures=[]
    for sample in range(8):
        side=3 if sample<4 else 4
        edges=[]
        for row in range(side):
            for col in range(side):
                node=row*side+col
                for neighbor in (row*side+(col+1)%side,((row+1)%side)*side+col):
                    weight=1 if (node+neighbor+sample)%3 else -1
                    if sample%4==1: weight=-weight
                    if sample%4==2 and (node+neighbor)%5==0: weight=0
                    edges.append((node,neighbor,weight))
        fixtures.append(('signed_torus_'+str(side)+'_'+str(sample),side*side,edges))
    return fixtures

# Hook imports are restricted statically and run inside a read-only-root numerical sandbox.
def module_for(campaign,record):
    """Return isolated module or None; args Path/verified artifact, no parent mutation.

    Example a choose_nodes hook is loaded from candidates/<id>/variant.py only.
    Import failures remain real trial/admission failures, never silently ignored.
    """
    # Plain portfolio candidates need no dynamic module.
    if not record['source']:
        # No generic mutation code is substituted for missing source.
        return None
    # A content-derived path fixes exactly which source may be imported.
    path=campaign/'candidates'/record['id']/'variant.py'
    # Module namespace is fresh for this worker and independent of its parent's imports.
    spec=importlib.util.spec_from_file_location('evolution_research_variant',path)
    # Create the namespace before executing the already-validated source.
    module=importlib.util.module_from_spec(spec)
    # The outer sandbox prevents source files/controller/public solutions being written by code.
    spec.loader.exec_module(module)
    # No module is installed globally for another candidate.
    return module

# Perturbations operate on declared representations and copied state only.
def prepare(graph,initial,policy,rng,module,stagnation,work):
    """Return (copied signs, optional angles, evidence); graph fixed, no caller mutation.

    policy declares binary/angles, selected nodes, radians/count and optional
    replayable adaptive strength. Example trap fixed nodes=[1] changes cut 8->7.
    Writes actual pre-state and selected IDs inside the owned trial work tree.
    """
    # Original round state is independently copied before any research hook sees it.
    signs=validate_signs(initial,graph.node_count)
    # A second copy permits an ownership assertion after a custom selector returns.
    before=signs.copy()
    # Every possible hook must leave the graph fixed.
    graph_hash=identity([graph.node_count,graph.edges,graph.neighbors])
    # Default policy is an explicit no-perturbation competitor.
    representation=policy.get('representation','none')
    # Counts never require selecting nonexistent coordinates.
    count=min(graph.node_count,policy.get('count',0))
    # Strength is radians for angles; binary perturbation strength is node count.
    strength=policy.get('strength',0.35)
    # A deterministic controller rule is part of the immutable candidate policy.
    if policy.get('adaptive'):
        # All adaptive parameters are explicit and identical on replay.
        parameters=policy['adaptive']
        # Reset/start at its declared minimum; stagnation is a recorded round input.
        strength,counter=parameters.get('minimum',.05),0
        # Replay exactly the observed number of completed nonimproving rounds.
        for observation in range(stagnation):
            # The prepared pure helper applies threshold/multiplier/cap without hidden RNG calls.
            strength,counter=adaptive_strength(strength,counter,False,**parameters)
    # Node selection can be the actual model-authored inherited algorithmic hook.
    if module is not None and hasattr(module,'choose_nodes') and representation!='none':
        # Copying prevents the selector from owning the frozen archive's memory.
        selector_input=signs.copy()
        # The hook gets a caller-owned working copy and must leave even that input unchanged.
        nodes=list(module.choose_nodes(graph,selector_input,rng,dict(policy)))
        # Explicit ownership checks reject hidden state mutation rather than mask it with later copying.
        if not np.array_equal(selector_input,signs):
            # A selector chooses IDs; it is not an undocumented in-place perturbation.
            raise ValueError('choose_nodes mutated its input signs')
    # Fixed original IDs are a declared controlled perturbation policy, not LLM spin-by-spin decisions.
    elif 'nodes' in policy:
        # List copying keeps artifact metadata immutable.
        nodes=list(policy['nodes'])
    # Existing prepared primitives implement uniform/connected/violated/mixed selection.
    else:
        # No state draw occurs for a zero-count/no-op policy.
        nodes=select_subset(graph,signs,count if representation!='none' else 0,rng,policy.get('rule','uniform')).tolist()
    # Duplicate/out-of-order invalid IDs must not be silently wrapped by NumPy.
    if len(set(nodes))!=len(nodes) or any(type(node) is not int or not 0<=node<graph.node_count for node in nodes) or len(nodes)!=count and representation!='none':
        # Invalid perturbations fail admission/evaluation before search.
        raise ValueError('selected original nodes invalid or inconsistent with declared count')
    # No undocumented selection is permitted under an explicitly disabled perturbation.
    if representation=='none' and nodes:
        # A disabled strategy cannot hide a pre-perturbation.
        raise ValueError('disabled perturbation selected nodes')
    # Angles are separate continuous coordinates, never a replica-axis reinterpretation.
    angles=None
    # Binary changes affect exactly the selected signs.
    if representation=='binary':
        # The working signs are already owned independently of the frozen archive.
        signs[nodes]*=-1
        # Nonselected states must be identical, not merely equivalent in cut quality.
        if set(np.flatnonzero(signs!=before))!=set(nodes):
            # Preserve the graph/state invariant as an actual failed trial.
            raise ValueError('binary perturbation scope violation')
    # BM initialization takes angles around the actual frozen signs.
    elif representation=='angles':
        # The original angular mapping uses 0/pi for plus/minus labels.
        angles=angles_from_signs(before)
        # Each selected angle receives one seeded uniform displacement in radians.
        angles[nodes]+=rng.uniform(-strength,strength,size=len(nodes))
        # Unselected angles are bitwise unchanged; positions/momenta do not enter this representation.
        if np.any(angles[np.setdiff1d(np.arange(graph.node_count),nodes)]!=angles_from_signs(before)[np.setdiff1d(np.arange(graph.node_count),nodes)]):
            # A scope error cannot be hidden by subsequent rounding.
            raise ValueError('angular perturbation scope violation')
        # Full state is retained for replay without bloating the small summary.
        np.save(work/'pre_angles.npy',angles)
    # The graph hash must survive even a numerical selector hook.
    if identity([graph.node_count,graph.edges,graph.neighbors])!=graph_hash:
        # Research code cannot evolve fixed graph weights/order.
        raise ValueError('research selector mutated graph')
    # Publish the actual state that enters refinement, including temporarily worse binary cuts.
    write_assignment(work/'pre_assignment.txt',signs,graph)
    # Selection/strength/seed ownership are explicit and independent of the resulting best cut.
    return signs,angles,{'representation':representation,'selected_nodes':nodes,'count':len(nodes),'strength':strength,
                         'units':'radians' if representation=='angles' else 'flipped nodes','frozen_cut':cut_value(graph,before),
                         'pre_cut':cut_value(graph,signs),'pre_assignment_sha256':file_sha256(work/'pre_assignment.txt'),
                         'copied_arrays':True,'caller_mutated':False}

# The same staged candidate strategy serves real trials and tiny correctness validation.
def execute(graph,record,request,work,checks=False):
    """Return actual candidate result with stage/prestate evidence; no global writes.

    request supplies frozen labels, effective seed, end-to-end seconds, work caps,
    stagnation and campaign path. Up to two stages split one total deadline.
    Example a B-selection child followed by one tabu move escapes the toy trap.
    """
    # Total numerical allowance includes module import and perturbation, not a fresh allowance per stage.
    started=time.monotonic()
    # A hard outer process timeout additionally covers setup/serialization.
    deadline=started+request['seconds']
    # Original immutable labels seed only supported warm paths.
    frozen=validate_signs(request['initial_assignment'],graph.node_count)
    # Each run owns its local RNG stream.
    rng=np.random.default_rng(request['seed'])
    # Record exact immutable prerequisites before invoking a research hook.
    original_hash=identity([graph.node_count,graph.edges,graph.neighbors])
    # Candidate module resides in an immutable candidate-specific file.
    module=module_for(Path(request['campaign']),record)
    # All perturbation state is copied and independently inspectable.
    current,angles,pre=prepare(graph,frozen,record['content']['policy'],rng,module,request.get('stagnation',0),work)
    # Keep the actual perturbed start separate from the unperturbed campaign archive.
    best=current.copy()
    # Only searched/returned witnesses count as candidate comparisons.
    searched=False
    # Stage details preserve raw backend/fallback/proof distinctions.
    history=[]
    # A plain candidate is one stage with all its declared allocation.
    stages=record['content']['stages'] or [{'backend':record['content']['backend'],'config':record['content']['config'],'fraction':1.0}]
    # Aggregate calls never receive a new full trial budget at a stage boundary.
    for index,stage in enumerate(stages):
        # Every stage belongs to one original end-to-end deadline.
        remaining=deadline-time.monotonic()
        # Reserve a small amount for independent worker output/return before the hard outer kill.
        seconds=min(request['seconds']*stage['fraction'],max(0,remaining-.05))
        # An exhausted allocation is unlaunched/censored work, not a new failed native run.
        if seconds<=0:
            # The outer result retains honest work/fallback metadata.
            break
        # Every stage gets a unique native/output tree.
        directory=work/f'stage-{index}'
        # Existing output cannot be reused as fresh evidence.
        directory.mkdir(exist_ok=False)
        # Backend identity and warm-start behavior are explicit per stage.
        backend=stage['backend']
        if checks and backend in ('mixing','pt_icm','toroidal_window','toroidal_search','toroidal_bound'):
            request={**request,'work_caps':{**request['work_caps'],backend:min(2,request['work_caps'].get(backend,10000))}}
        # Fixed native seeds cannot become fictitious independent repeats.
        seed=2020 if backend in ('biqbin','madam') else request['seed']%65536 if backend=='mqlib' else request['seed']
        # Unsupported native starts are genuinely fresh competitors.
        supports=FEATURES[backend]['warm_start']!='unsupported'
        # Every numerical input is a copied full vector in original order.
        initial=best.copy() if supports else None
        # A custom search hook replaces only the numerical strategy, never verification/proof logic.
        if module is not None and hasattr(module,'search'):
            # Research code receives a copy and cannot change the controller's budget.
            hook_input=None if initial is None else initial.copy()
            # Full research-call input ownership remains testable after return.
            proposed=module.search(graph,dict(stage['config']),seed,{'seconds':seconds,'max_work':request['work_caps'].get(backend,10000)},hook_input)
            # A search may own its internal arrays but must not mutate its caller's incumbent.
            if hook_input is not None and not np.array_equal(hook_input,initial):
                # Wrong ownership cannot be selected or published.
                raise ValueError('custom search mutated caller initial_assignment')
            # A raw sign vector is sufficient; an optional claimed cut must agree independently.
            proposed=proposed if isinstance(proposed,dict) else {'assignment':proposed}
            # Validate length, order and membership before original-objective scoring.
            signs=validate_signs(proposed['assignment'],graph.node_count)
            # A false backend cut is an admission/evaluation failure, not a corrected quality number.
            if 'cut' in proposed and proposed['cut']!=cut_value(graph,signs):
                # Never publish a model-provided fake objective.
                raise ValueError('custom claimed cut disagrees with original objective')
            # Research hooks cannot manufacture global bounds or proof classifications.
            if set(proposed)-{'assignment','cut','work_counters'}:
                # Exact/native evidence must continue to come from protected adapters.
                raise ValueError('custom research result contains protected proof/status fields')
            # Trusted metadata marks a real local hook execution, with no upgraded certificate.
            result={'assignment':signs.tolist(),'cut':cut_value(graph,signs),'execution_status':'completed','solution_valid':True,
                    'optimality_status':'unproven','upper_bound':None,'work_counters':proposed.get('work_counters',{}),'termination_reason':'research_search_hook'}
            # Custom hooks are actual numerical executions subject to separate correctness checks.
            stage_searched=True
        # Selected-angle BM refinement uses the preserved real angular API.
        elif angles is not None and index==0:
            # This thin angular wrapper currently represents exactly one preserved BM refinement pass.
            if stage['config'].get('restarts',1)!=1 or stage['config'].get('perturb_rounds',0)!=0:
                # No ignored outer restarts are allowed under this wrapper.
                raise ValueError('angular policy currently requires one BM pass')
            # Pass only the settled core's documented numerical options.
            core={key:value for key,value in stage['config'].items() if key not in ('restarts','perturb_rounds','perturb_scale')}
            # Original solver returns all three values, keeping relaxed history separate from direct F.
            signs,value,details=solve_from_angles(graph,angles,rng,seed=seed,**core)
            # No BM relaxed value is classified as a global bound.
            result={'assignment':signs.tolist(),'cut':value,'execution_status':'completed','solution_valid':True,'optimality_status':'unproven','upper_bound':None,'work_counters':{'passes':1},'bm_history':details}
            # A full real angular refinement constitutes numerical search.
            stage_searched=True
        # Tiny regression calls use the same immutable API rather than 8 nested CLI startups.
        elif checks:
            # Work caps are deliberately small for correctness fixtures, with actual fixed native seeds.
            budget={'seconds':seconds}
            # Runtime-only native interfaces reject rather than ignore a work counter.
            if FEATURES[backend]['work_unit'] is not None:
                # The work ceiling is still in that backend's actual units.
                budget['max_work']=request['work_caps'].get(backend,10000)
            # Native APIs need a fresh recorded artifact tree inside the writable check directory.
            config={**stage['config'],**({'work_dir':str(directory/'native')} if backend in ('mqlib','scientific','biqbin','madam','biqcrunch') else {})}
            # Direct shared dispatch preserves distinct numerical implementations.
            result=solve(graph,config,seed,budget,initial,solver=backend)
            # Correctness admission is separate from comparative search credit.
            stage_searched=result['assignment'] is not None and result['execution_status'] not in ('failed','unavailable')
        # Ordinary built-in trials invoke the unchanged run_solver.py CLI from frozen source bytes.
        else:
            # This stage's explicit config belongs to its isolated numerical output.
            atomic_json(directory/'config.json',stage['config'])
            # All warm paths receive the actual perturbed/stage incumbent, not a silently ignored flag.
            if supports:
                # This original-format vector is independently reloaded by the preserved runner.
                write_assignment(directory/'initial.txt',initial,graph)
            # argv preserves parameter boundaries and actual solver name.
            command=[sys.executable,str(Path(__file__).parent/'run_solver.py'),'--solver',backend,'--instance',request['instance'],
                     '--config',str(directory/'config.json'),'--seed',str(seed),'--time-limit',str(max(0,seconds-.03)),'--output',str(directory/'runner')]
            # Unsupported work counters are never supplied.
            if FEATURES[backend]['work_unit'] is not None:
                # BM pass caps and integration/branch/proposal caps retain their distinct units.
                command+=['--max-work',str(request['work_caps'].get(backend,10000))]
            # Only actual supported warm-start paths receive the input.
            if supports:
                # Native exact adapters can now verify real incumbent injection.
                command+=['--initial-assignment',str(directory/'initial.txt')]
            # The trusted outer worker/session owns this serial child and any native descendants.
            with (directory/'runner_console.log').open('wb') as stream:
                # No separate full budget is added; the enclosing worker has the aggregate hard deadline.
                subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=False)
            # Actual structured outcome, never stdout prose, is the numerical evidence.
            result=json.loads((directory/'runner/result.json').read_text())
            # Native fallback is explicitly distinguished from a recovered backend witness.
            native=(result.get('optimality_evidence') or {}).get('recovered_native_assignment')
            # Hard fallback and unavailable/failed paths cannot win selection by borrowing an incumbent.
            stage_searched=result['assignment'] is not None and result['execution_status'] not in ('failed','unavailable') and not result.get('runner_time_limit_enforced',False) and native is not False
            # A deliberately zero-work local run is operational retention, not search evidence.
            if FEATURES[backend]['work_unit'] is not None and request['work_caps'].get(backend,10000)==0:
                # An initial state alone is not a newly searched witness.
                stage_searched=False
        # Original labels and graph must be unchanged by every numerical implementation/hook.
        if identity([graph.node_count,graph.edges,graph.neighbors])!=original_hash or not np.array_equal(frozen,request['initial_assignment']):
            # No candidate may edit the mathematical problem or common frozen archive.
            raise ValueError('candidate mutated graph or frozen incumbent')
        # A failed stage may legitimately lack any assignment.
        if result.get('assignment') is None:
            # Preserve raw failure and do not invent a replacement native witness.
            history.append({'backend':backend,'effective_seed':seed,'result':result,'searched':False})
            # Later dependent stages have no new valid state to refine.
            continue
        # Validate every returned witness in the original graph order.
        signs=validate_signs(result['assignment'],graph.node_count)
        # Strict original evaluator comparison rejects false reported cuts.
        if result['cut']!=cut_value(graph,signs):
            # A native/model narrative never substitutes for actual edge evaluation.
            raise ValueError('backend cut disagrees with returned original signs')
        # Do not let unsolved time-limit fallback be the best-ranked candidate witness.
        searched=searched or stage_searched
        # Across actual stages retain the strongest resulting candidate witness, separate from campaign best.
        if index==0 or cut_value(graph,signs)>cut_value(graph,best):
            # A temporarily worse initial state can be superseded only by this candidate's own stages.
            best=signs.copy()
        # Each stage records whether its result equals its supplied state.
        history.append({'backend':backend,'effective_seed':seed,'allocated_seconds':seconds,'result':result,'searched':stage_searched,
                        'returned_initial_unchanged':initial is not None and np.array_equal(signs,initial)})
    # A valid prestate can still be a useful operational fallback but cannot claim backend-search credit.
    return {'assignment':best.tolist(),'cut':cut_value(graph,best),'search_witness':searched,'preparation':pre,'stages':history,
            'frozen_assignment_sha256':request['frozen_assignment_sha256'],'artifact_id':record['id'],
            'graph_sha256':request['graph_sha256'],'runtime_seconds':time.monotonic()-started,'retains_original_archive_wrapper':False}

# Worker mode is intentionally not an evolutionary controller and cannot invoke Codex.
def main():
    """Read one numerical request path from argv, write result.json, return 0/1.

    Trial or admission-check mode; all writable files stay in request work.
    Example python evolution_worker.py request.json. Exceptions preserve raw
    tracebacks and explicit failure, never a forged feasible/proven result.
    """
    # Controller-provided request paths never contain shell substitutions.
    request=json.loads(Path(sys.argv[1]).read_text())
    # Writable directory is the only filesystem scope granted to this worker.
    work=Path(request['work'])
    # Candidate module identity is checked before any dynamic import.
    record=load_artifact(Path(request['campaign']),request['artifact_id'])
    # Actual failures must leave a structured diagnostic in addition to raw stderr.
    try:
        # Correctness fixtures use the unchanged Graph rather than editable instance data.
        if request.get('check'):
            # Import the existing graph type only for these tiny bounded checks.
            from bm_solver import Graph
            # Retain each actual direct-objective/ownership outcome.
            outcomes=[]
            # All required fixtures run within one enclosing hard process deadline.
            fixtures=admission_cases(record)
            for index,(fixture_name,n,edges) in enumerate(fixtures):
                # Separate check work trees prevent stale native/CLI output reuse.
                directory=work/f'check-{index}'
                # Every invocation owns a fresh directory.
                directory.mkdir()
                # Fixed inputs never depend on a model's claimed graph semantics.
                graph=Graph(n,edges)
                # Use valid original-order initial signs for every fixture size.
                initial=[1 if node<n//2 else -1 for node in range(n)]
                # Budget is divided across checks, not multiplied by eight.
                sub={**request,'initial_assignment':initial,'seconds':request['seconds']/len(fixtures)}
                # Fixed-node policies larger than a fixture must fail rather than corrupt memory.
                outcome=execute(graph,record,sub,directory,checks=True)
                # Independent original F and sign membership are the acceptance criteria, not heuristic optimality.
                outcomes.append({'case':index,'fixture':fixture_name,'nodes':n,'cut':outcome['cut'],'valid':cut_value(graph,validate_signs(outcome['assignment'],n))==outcome['cut']})
            # Actual subresults and bounded checks are persisted for admission review.
            result={'checks':outcomes,'passed':all(item['valid'] for item in outcomes)}
        # Ordinary candidate trials have exactly one fixed original graph.
        else:
            # Raw graph bytes must match the request before any numerical work.
            if file_sha256(request['instance'])!=request['graph_sha256']:
                # A changed input is not a new solver discovery.
                raise ValueError('trial graph raw hash mismatch')
            # The preserved loader fixes node order/edge representation.
            graph=load_graph(request['instance'])
            # The actual selected candidate executes under the one aggregate deadline.
            result=execute(graph,record,request,work)
        # Finite JSON rejects hidden NaN/Infinity in sampled states as well as objectives.
        atomic_json(work/'result.json',result)
        # Failures in correctness checks must not admit an artifact.
        return 0 if not request.get('check') or result['passed'] else 1
    # Candidate/backend errors remain diagnostic failures with original raw traceback.
    except Exception as error:
        # Raw stderr is captured unchanged by the controller.
        traceback.print_exc()
        # No fallback is silently invented after an invalid code artifact.
        atomic_json(work/'result.json',{'failed':True,'reason':f'{type(error).__name__}: {error}'})
        # Nonzero status prevents selection/publication.
        return 1

# Importing the worker has no process, Codex, numerical or filesystem side effects.
if __name__=='__main__':
    # Only an explicit controller-issued request executes one bounded numerical task.
    raise SystemExit(main())
