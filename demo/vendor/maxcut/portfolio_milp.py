"""Transparent optional SCIP edge-XOR MILP, separate from ScientificMaxcutSolver."""

# Import discovery keeps SCIP optional for every other solver.
import importlib.util
# Finite checks prevent invalid tolerance/bound fields from entering results.
import math
# Cooperative solver time includes model construction as well as optimize().
from time import perf_counter
# NumPy owns warm-start labels and extracted original-order signs.
import numpy as np
# The shared sparse graph and independent original objective remain authoritative.
from bm_solver import cut_value
# Contract helpers validate explicit config, budget and returned witnesses.
from portfolio_common import deadline_from, result_record, settings, starting_signs


# Extra fixed/free parameters are only for conditional neighborhood subproblems.
def solve_milp(graph, config, seed, budget, initial_assignment=None, free_nodes=None):
    """SCIP MILP maximize sum(w*y) with four exact binary-XOR inequalities.

    graph is sparse Graph; config accepts feasibility_tolerance=1e-9,
    relative_gap=0, max_nodes=5000 (model-size guard). seed integer seeds SCIP;
    budget seconds/max_work limits time/branch nodes. initial_assignment is a
    real warm start. Optional free_nodes is a unique subset of original node
    IDs; outside nodes are fixed to initial_assignment for LNS. None means
    global solve with x[0]=0 symmetry fixing. x=(1-s)/2, y in [0,1] continuous.
    Warm complementary labels are canonicalized only for global symmetry.
    Return assignment, primal/dual/gap/tolerances in the shared result; no caller
    mutation/files. Example a -2 edge forces equal x at optimum F=0, unlike an
    incomplete XOR formulation. O(n+m) model storage, exponential worst case.
    Optimal labels are solver reports within tolerances, not checked certificates.
    """
    # Include model construction and incumbent injection in runtime measurements.
    started = perf_counter()
    # Keep all numerical and size controls visible in the resolved configuration.
    cfg = settings(config, {"feasibility_tolerance": 1e-9, "relative_gap": 0.0, "max_nodes": 5000})
    # Numerical solver tolerances are explicit positive/nonnegative finite quantities.
    if not math.isfinite(cfg["feasibility_tolerance"]) or not 1e-10 <= cfg["feasibility_tolerance"] <= 1e-3 or not math.isfinite(cfg["relative_gap"]) or cfg["relative_gap"] < 0:
        # Avoid unsupported SCIP tolerances or a misleading claim of exact arithmetic.
        raise ValueError("invalid MILP tolerance/gap")
    # The model guard prevents accidental huge MILPs during a small one-shot test.
    if type(cfg["max_nodes"]) is not int or cfg["max_nodes"] < 1 or graph.node_count > cfg["max_nodes"]:
        # A caller can explicitly increase this guard, acknowledging a larger sparse model.
        raise ValueError("MILP graph exceeds configured max_nodes")
    # Validate the shared limits before even checking an optional dependency.
    deadline = deadline_from(budget)
    # Initial labels have their documented original order and owned storage.
    initial = starting_signs(graph, np.random.default_rng(seed), initial_assignment)
    # Conditional subproblems need explicit fixed outside labels, not an ignored warm-start suggestion.
    if free_nodes is not None and initial_assignment is None:
        # Without outside labels the claimed conditional problem would be undefined.
        raise ValueError("conditional MILP requires initial_assignment")
    # Missing optional SCIP remains a structured unavailability result, not a heuristic fallback.
    if importlib.util.find_spec("pyscipopt") is None:
        # Never relabel exhaustive search or another backend as SCIP.
        return result_record("milp", graph, cfg, seed, budget, started, status="unavailable", reason="install optional milp extra (PySCIPOpt)")
    # Import only within the requested backend so basic solver installation remains minimal.
    from pyscipopt import Model, quicksum
    # Global complement symmetry allows fixing x0=0 without losing any cut.
    if free_nodes is None:
        # Multiplying all signs preserves every s_i*s_j product and thus the complete objective.
        initial *= int(initial[0])
    # A declared zero-time budget should return the warm witness without constructing a large model.
    if perf_counter() >= deadline:
        # No bound or optimality is fabricated before SCIP actually solves anything.
        return result_record("milp", graph, cfg, seed, budget, started, initial, status="time_limit", reason="time_limit_before_model")
    # Create a distinct generic model; this is not the ScientificMaxcutSolver formulation.
    model = Model("project_maxcut_xor")
    # Numerical tolerances define the meaning of a solver-reported optimum and gap.
    model.setRealParam("numerics/feastol", cfg["feasibility_tolerance"])
    # A requested nonzero relative gap is visible as an approximation tolerance.
    model.setRealParam("limits/gap", cfg["relative_gap"])
    # SCIP's seedshift range is a signed 32-bit nonnegative integer.
    model.setIntParam("randomization/randomseedshift", seed % (2**31 - 1))
    # Branch-node work limits are distinct from proposal/iteration counts of heuristics.
    model.setLongintParam("limits/nodes", budget.get("max_work", 10000))
    # Binary node variables preserve the original zero-based graph order.
    x = [model.addVar(vtype="B", name=f"x_{node}") for node in range(graph.node_count)]
    # One continuous edge variable is sufficient because binary endpoints force its exact XOR value.
    y = [model.addVar(lb=0, ub=1, vtype="C", name=f"y_{edge}") for edge in range(len(graph.edges))]
    # Add every required inequality, including the upper inequalities needed for negative weights.
    for edge, (i, j, weight) in enumerate(graph.edges):
        # A 1/0 endpoint pair requires y>=1.
        model.addCons(y[edge] >= x[i] - x[j])
        # The opposite 0/1 pair must impose the same lower bound.
        model.addCons(y[edge] >= x[j] - x[i])
        # Two zero endpoints require y<=0.
        model.addCons(y[edge] <= x[i] + x[j])
        # Two one endpoints also require y<=0.
        model.addCons(y[edge] <= 2 - x[i] - x[j])
    # No offset or factor-of-two change occurs: y is exactly an edge's cut indicator.
    model.setObjective(quicksum(weight * y[edge] for edge, (i, j, weight) in enumerate(graph.edges)), "maximize")
    # Symmetry removal is valid only when no external fixed boundary breaks complement invariance.
    if free_nodes is None:
        # x0=0 corresponds to s0=+1 after the canonicalized warm start.
        model.addCons(x[0] == 0)
    # Conditional repair keeps every original outside node fixed, including its boundary edges.
    else:
        # A release set must contain distinct valid original IDs.
        free = set(free_nodes)
        # Reject ambiguous duplicate/out-of-range coordinates before optimization.
        if len(free) != len(free_nodes) or any(type(node) is not int or not 0 <= node < graph.node_count for node in free):
            # No node permutation or extra symmetry constraint is silently introduced.
            raise ValueError("invalid conditional MILP free_nodes")
        # Outside variables stay at their supplied binary values.
        for node in range(graph.node_count):
            # Edges remain in the full model, so boundary terms cannot disappear.
            if node not in free:
                # Conversion s=+1 -> x=0, s=-1 -> x=1 is exact.
                model.addCons(x[node] == int((1 - int(initial[node])) // 2))
    # Supply a complete feasible solution, including continuous XOR values.
    warm = model.createSol()
    # Every original node receives its corresponding binary warm label.
    for node in range(graph.node_count):
        # addSol can use this incumbent immediately even if the node budget is tiny.
        model.setSolVal(warm, x[node], int((1 - int(initial[node])) // 2))
    # Edge values must agree with the node labels for all signed weights.
    for edge, (i, j, weight) in enumerate(graph.edges):
        # A warm solution never uses relaxed fractional cut indicators.
        model.setSolVal(warm, y[edge], int(initial[i] != initial[j]))
    # Native SCIP validation determines whether the supplied complete incumbent is accepted.
    warm_accepted = bool(model.addSol(warm))
    # Check the deadline again after model construction, before starting branch-and-bound.
    remaining = deadline - perf_counter()
    # A construction-time timeout retains the validated supplied assignment without a guessed bound.
    if remaining <= 0:
        # The model exists but has not computed a usable global dual bound.
        return result_record("milp", graph, cfg, seed, budget, started, initial, status="time_limit", reason="time_limit_during_model")
    # SCIP's time limit receives the remaining solve allowance, not a fresh full budget.
    model.setRealParam("limits/time", remaining)
    # Native stdout is preserved by the one-shot runner as the real backend log.
    model.optimize()
    # A validated initial incumbent remains an answer if no better native solution is returned.
    best = initial.copy()
    # Extract actual SCIP labels only if a primal solution exists.
    if model.getNSols() > 0:
        # Query the native best solution, keeping the original variable order.
        solution = model.getBestSol()
        # Threshold binary variables within documented solver tolerances, then independently score labels.
        candidate = np.array([1 if model.getSolVal(solution, variable) < 0.5 else -1 for variable in x], dtype=np.int8)
        # Best-so-far retention protects a stronger caller incumbent on ties or numerical disagreement.
        if cut_value(graph, candidate) > cut_value(graph, best):
            # Copy rather than keeping views into native solver storage.
            best = candidate.copy()
    # Native status describes search termination independently of assignment feasibility.
    native_status = str(model.getStatus())
    # SCIP may use a large sentinel for an uncomputed/infinite upper bound.
    dual = float(model.getDualbound())
    # Unknown native bounds remain null, never replaced by a relaxed BM objective.
    upper = dual if math.isfinite(dual) and abs(dual) < 1e19 else None
    # Gap is recorded only when finite, under SCIP's documented definition.
    gap = float(model.getGap())
    # A positive requested gap can terminate without an exact proof; status and tolerances stay visible.
    optimal = native_status == "optimal"
    # The shared result independently recomputes F on the original graph.
    result = result_record("milp", graph, cfg, seed, budget, started, best,
                           status="time_limit" if native_status == "timelimit" else "completed",
                           reason=native_status, upper_bound=upper,
                           optimality="solver_reported_optimal" if optimal and free_nodes is None else "unproven",
                           evidence={"backend": "SCIP", "version": str(model.getMajorVersion()) + "." + str(model.getMinorVersion()),
                                     "feasibility_tolerance": cfg["feasibility_tolerance"], "relative_gap_limit": cfg["relative_gap"],
                                     "warm_start_accepted": warm_accepted, "conditional_optimal": optimal and free_nodes is not None},
                           counters={"branch_nodes": int(model.getNNodes())}, implementation="project-XOR-MILP/PySCIPOpt")
    # Native bounds/gaps are additional evidence, never substitutes for independently validated labels.
    result.update({"primal_bound": float(model.getPrimalbound()) if model.getNSols() else None,
                   "dual_bound": upper, "relative_gap": gap if math.isfinite(gap) else None,
                   "bound_scope": "conditional_neighborhood" if free_nodes is not None else "global"})
    # Return the distinct generic MILP identity, with solver tolerances visible.
    return result
