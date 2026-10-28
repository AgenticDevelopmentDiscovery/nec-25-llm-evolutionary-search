"""Faithful CPU adapter to the authors' pinned TESB class, kept distinct from local SB."""

# Import discovery/path loading keeps optional upstream dependencies isolated.
import importlib.util
# Exact upstream source bytes and pinned revision supplement the native method identity.
import hashlib
# The source manifest records the revision used by the separate authors' checkout.
import json
# Finite scale checks prevent the upstream signed-row-sum normalization from dividing by zero.
import math
# Preserve import-time thread environment changes made by the original authors' module.
import os
# Resolve the separate source checkout without copying or reformatting its code.
from pathlib import Path
# Measure native phase times and check the shared cooperative budget between phases.
from time import perf_counter
# The authors' class uses NumPy's legacy global RNG, which the adapter saves/restores.
import numpy as np
# Original graph objective is independent of upstream Ising-energy calculations.
from bm_solver import cut_value, validate_signs
# Common helpers provide validated metadata and limits without requiring pandas/SciPy globally.
from portfolio_common import deadline_from, result_record, settings


# This adapter invokes the actual source implementation rather than giving a generic tabu solver its name.
def solve_tesb(graph,config,seed,budget,initial_assignment=None):
    """Run authors' tSB.py SB.update_b in warm-up then tabu checking phases.

    config: warm_fraction=.2,warm_samples=16,check_samples=8,tabu_sample=2,
    dt=1,warm_xi=None(author signed-row auto normalization),check_xi=.05.
    budget max_work is TOTAL integration steps split between two phases;
    seconds is checked between upstream phase calls, with a hard process limit
    supplied by run_solver.py. Optional warm signs initialize warm replica zero
    and remain a retained incumbent. Returns independently scored raw final
    checking labels/phase history/source identity; no polish or global optimum.
    Sparse SciPy CSR A=-W; x,y shape (n,samples). Preserves caller RNG/env;
    this legacy-global-RNG adapter is serial, not thread-safe. CPU O(steps*m*R)
    and O(n*R+m) storage. Requires optional tesb extra and pinned source.

    Example: solve_tesb(g,{},1,{'seconds':2,'max_work':20}) on a tiny graph.
    Reference: authors' tSB.py update_b and DOI 10.1038/s42005-026-02538-2.
    """
    # Runtime includes imports, CSR conversion and both genuine upstream phases.
    started=perf_counter()
    # These explicit defaults scale down the authors' demonstration sample counts for local use.
    cfg=settings(config,{"warm_fraction":0.2,"warm_samples":16,"check_samples":8,"tabu_sample":2,
                         "dt":1.0,"warm_xi":None,"check_xi":0.05})
    # The warm-up phase must leave some scheduled work for checking.
    if not math.isfinite(cfg["warm_fraction"]) or not 0<cfg["warm_fraction"]<1 or not math.isfinite(cfg["dt"]) or cfg["dt"]<=0:
        # Invalid numerical/phase controls are not passed into native arrays silently.
        raise ValueError("invalid TESB warm_fraction/dt")
    # Positive bounded sample counts prevent accidental large n*replica allocations.
    if any(type(cfg[k]) is not int or not 1<=cfg[k]<=64 for k in ("warm_samples","check_samples","tabu_sample")):
        # All sample controls count actual trajectories/history entries.
        raise ValueError("TESB sample counts must be integers in 1..64")
    # Validate shared work/time limits before doing backend-specific work.
    deadline=deadline_from(budget)
    # The raw source path is separately pinned in external/sources.json.
    source=Path(__file__).parent/"external/TESB/tSB.py"
    # Missing source or optional imports produce availability evidence, never an unrelated substitute.
    if not source.is_file() or any(importlib.util.find_spec(name) is None for name in ("scipy","pandas")):
        # Pure project-owned methods remain usable without these optional packages.
        return result_record("tesb",graph,cfg,seed,budget,started,status="unavailable",reason="obtain TESB source and install optional tesb extra")
    # Validate and preserve a caller incumbent before temporary upstream RNG changes.
    incumbent=np.ones(graph.node_count,dtype=np.int8) if initial_assignment is None else validate_signs(initial_assignment,graph.node_count)
    # A time limit before initialization must return the valid incumbent without a claimed native trajectory.
    if perf_counter()>=deadline:
        # No upper bound or optimality is fabricated from an unexecuted phase.
        return result_record("tesb",graph,cfg,seed,budget,started,incumbent,status="time_limit",reason="before_initialization")
    # Import sparse matrix storage only on the requested TESB path.
    from scipy.sparse import coo_matrix
    # Explicit arrays store each symmetric Ising coefficient twice, without any n*n dense allocation.
    rows,columns,weights=[],[],[]
    # The authors' auto scale uses signed row sums, which may cancel even on a nonempty signed graph.
    row_sums=np.zeros(graph.node_count)
    # Each graph edge maps J_ij=-w_ij for energy minimization.
    for i,j,weight in graph.edges:
        # Preserve symmetric node interactions and original node IDs.
        rows.extend([i,j])
        # These are sparse column indices, not a permutation of output labels.
        columns.extend([j,i])
        # Both directed matrix entries have the same negated graph weight.
        weights.extend([-weight,-weight])
        # Retain exact author normalization behavior where its denominator is nonzero.
        row_sums[i]-=weight
        # The reverse endpoint supplies its own signed row sum.
        row_sums[j]-=weight
    # Convert COO edge lists into efficient CSR multiplication for the unmodified CPU class.
    coupling=coo_matrix((weights,(rows,columns)),shape=(graph.node_count,graph.node_count)).tocsr()
    # The zero-row-sum case has an explicit finite scale override instead of division by zero.
    auto_scale=0.0 if np.max(np.abs(row_sums))==0 else 1.0/float(np.max(np.abs(row_sums)))
    # Actual warm scale is persisted in the resolved configuration.
    cfg["warm_xi"]=auto_scale if cfg["warm_xi"] is None else cfg["warm_xi"]
    # Both stage scales must be finite/nonnegative; zero is a valid no-interaction ablation.
    if any(not math.isfinite(cfg[k]) or cfg[k]<0 for k in ("warm_xi","check_xi")):
        # Reject numerical instability before calling native methods.
        raise ValueError("TESB xi scales must be finite and nonnegative")
    # Save external legacy RNG state before import resets it to the authors' fixed seed.
    previous_rng=np.random.get_state()
    # The upstream module writes three thread-related environment variables during import.
    previous_env={k:os.environ.get(k) for k in ("MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","OMP_NUM_THREADS")}
    # Always restore caller globals, including on native numerical or import failures.
    try:
        # Import by source path leaves repository code and sys.path untouched.
        spec=importlib.util.spec_from_file_location("authors_tesb",source)
        # A fresh namespace avoids inheriting another invocation's native class state.
        module=importlib.util.module_from_spec(spec)
        # Execute the actual reviewed authors' definitions; its demonstration main block does not run.
        spec.loader.exec_module(module)
        # Reseed AFTER import so the caller's requested seed actually governs both phases.
        np.random.seed(seed % 2**32)
        # A single total work budget is split, not independently applied twice.
        warm_steps=int(budget.get("max_work",10000)*cfg["warm_fraction"])
        # Every remaining scheduled step belongs to checking.
        check_steps=budget.get("max_work",10000)-warm_steps
        # Use the authors' actual ballistic class and explicit finite scale.
        warm=module.SB(coupling,n_iter=warm_steps,xi=cfg["warm_xi"],dt=cfg["dt"],batch_size=cfg["warm_samples"],device="cpu")
        # Optional supplied labels affect actual continuous state, not only output retention.
        if initial_assignment is not None:
            # The original initialize() amplitude is +/-0.005; warm replica zero uses that signed magnitude.
            warm.x[:,0]=0.005*incumbent
        # Execute native bSB warm-up, without adding local binary polishing.
        warm.update_b()
        # Preserve zero-boundary extraction as explicit +1 rather than returning invalid zero signs.
        tabu=np.where(warm.x>=0,1,-1)
        # Every warm sample becomes part of the original authors' tabu-history matrix.
        warm_cuts=[cut_value(graph,tabu[:,k]) for k in range(cfg["warm_samples"])]
        # The strongest warm witness remains useful if checking times out before it starts.
        raw=tabu[:,int(np.argmax(warm_cuts))].copy()
        # Counter reflects only actually executed native integration steps.
        executed=warm_steps
        # Record genuine phase evidence, not claimed speed/quality from the publication.
        history=[{"phase":"warm","steps":warm_steps,"raw_best_cut":max(warm_cuts),"tabu_entries":cfg["warm_samples"]}]
        # Respect the original overall deadline between native phase calls.
        if perf_counter()<deadline:
            # Native checking samples a minibatch of warm history at each integration step.
            checking=module.SB(coupling,tabu=tabu,xi=cfg["check_xi"],n_iter=check_steps,dt=cfg["dt"],
                               batch_size=cfg["check_samples"],num_tabu=cfg["tabu_sample"],device="cpu")
            # This is the authors' actual tabued ballistic update, not local discrete tabu search.
            checking.update_b()
            # Extract valid original-order binary candidates from actual checking positions.
            samples=np.where(checking.x>=0,1,-1)
            # Independent scoring ignores the upstream demonstration's transformed-energy statistics.
            values=[cut_value(graph,samples[:,k]) for k in range(cfg["check_samples"])]
            # Record raw checking output separately from stronger warm/incumbent retention.
            raw=samples[:,int(np.argmax(values))].copy()
            # This completes the declared remaining native steps.
            executed+=check_steps
            # Save actual phase outcome and minibatch policy for source-to-code explanation.
            history.append({"phase":"checking","steps":check_steps,"raw_best_cut":max(values),"sampled_tabu_entries":cfg["tabu_sample"]})
        # Retain the best warm/checking/supplied feasible answer explicitly.
        candidates=[incumbent,tabu[:,int(np.argmax(warm_cuts))],raw]
        # Selection uses original F, with independent copies for ownership.
        best=max(candidates,key=lambda signs:cut_value(graph,signs)).copy()
    # Restore the user's globals even when a solver or timeout exception interrupts execution.
    finally:
        # Caller code sees exactly its previous random stream state after this serial adapter returns.
        np.random.set_state(previous_rng)
        # Import-time environment writes do not persist into unrelated local solver behavior.
        for key,value in previous_env.items():
            # Variables originally absent remain absent.
            if value is None:
                # Remove only the exact import-time variable owned by this temporary scope.
                os.environ.pop(key,None)
            # Existing user settings are restored exactly.
            else:
                # This is environment restoration, not a hidden permanent thread policy.
                os.environ[key]=value
    # Shared result checks original signs/cut independently of raw native phase metadata.
    result=result_record("tesb",graph,cfg,seed,budget,started,best,
                         status="time_limit" if perf_counter()>=deadline else "completed",
                         reason="phase_time_limit" if perf_counter()>=deadline else "two_native_phases",
                         counters={"integration_steps":executed,"warm_steps":warm_steps},history=history,
                         implementation="authors-TESB/tSB.py/SB.update_b")
    # Preserve the actual raw final phase result and explicitly report that no polish was added.
    result.update({"raw_assignment":raw.tolist(),"raw_cut":cut_value(graph,raw),"hybrid":False,
                   "source_file":str(source),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
                   "upstream":next(record for record in json.loads((Path(__file__).parent/"external/sources.json").read_text()) if record["name"]=="TESB"),
                   "backend_seed":seed % (2**32),"seed_protocol":"upstream legacy RNG reseeded modulo 2**32 after import; caller state restored"})
    # Returned best may come from a stronger warm state, which remains distinguishable from raw checking output.
    return result
