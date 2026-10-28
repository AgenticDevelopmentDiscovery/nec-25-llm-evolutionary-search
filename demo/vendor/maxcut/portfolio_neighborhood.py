"""Conditional exact repair includes internal, boundary and fixed outside contributions."""

# Monotone deadlines bound both neighborhood selection and restricted exact optimization.
from time import perf_counter
# NumPy stores copied full assignments and independently selected node IDs.
import numpy as np
# Reuse original sparse objective and binary membership validation.
from bm_solver import cut_value, validate_signs
# Exact decimal scaling provides a discriminating conditional oracle.
from portfolio_common import deadline_from, integer_weights, result_record, settings, starting_signs
# Shared release rules are explicit project perturbation variants.
from portfolio_perturbations import select_subset


# Exact restricted enumeration cannot remove complement symmetry when outside signs are fixed.
def repair_exact(graph, initial_assignment, nodes, deadline, max_states=1048576):
    """Optimize selected B by exhaustive enumeration with fixed outside labels.

    graph sparse Graph; initial_assignment +/-1 length n; nodes unique original
    indices, at most 20; deadline perf_counter seconds; max_states positive
    int, default 2**20. Decompose F into outside constant, internal edges and
    boundary terms w*(1-s_i*s_out)/2. Enumerate 2**len(B), WITHOUT fixing a B
    spin: boundary terms break local complement symmetry. Return dict signs,
    complete, evaluated, exact_fraction and decomposition. No input mutation
    or files. Example one released endpoint of a +2 edge optimizes to opposite
    its fixed neighbor. O(m+2**|B|*(internal+boundary)), sparse memory.
    """
    # The retained answer owns full valid labels even on immediate timeout.
    initial = validate_signs(initial_assignment, graph.node_count)
    # Normalize index storage while rejecting duplicate and invalid caller coordinates.
    selected = list(nodes)
    # A hard subset-size guard prevents accidental exponential work.
    if len(selected) > 20 or len(set(selected)) != len(selected) or any(type(node) is not int or not 0 <= node < graph.node_count for node in selected):
        # Larger neighborhoods must use an explicitly selected exact backend.
        raise ValueError("enumerated neighborhood requires <=20 unique original node IDs")
    # Work counters must distinguish partial from complete enumeration.
    if type(max_states) is not int or max_states < 0:
        # Zero states is a legitimate interrupted subproblem, not an exact optimum.
        raise ValueError("max_states must be a nonnegative integer")
    # Integer scaling preserves every signed finite-decimal contribution.
    weights, scale = integer_weights(graph)
    # A set provides constant-time inside/outside membership checks.
    inside = set(selected)
    # Internal edge records retain the original endpoint IDs.
    internal = []
    # Boundary records name the free endpoint, fixed sign and original scaled weight.
    boundary = []
    # Constant outside–outside cut contribution remains part of the reported full objective.
    constant = 0
    # Every original edge enters exactly one decomposition category.
    for (i, j, original), weight in zip(graph.edges, weights):
        # Both released endpoints are optimized together.
        if i in inside and j in inside:
            # Internal edge indicators retain the usual XOR form.
            internal.append((i, j, weight))
        # One released endpoint creates a linear term dependent on a fixed outside sign.
        elif (i in inside) != (j in inside):
            # Orient this record toward its free endpoint without reordering output labels.
            free, fixed = (i, j) if i in inside else (j, i)
            # Store boundary data explicitly instead of discarding it with outside variables.
            boundary.append((free, int(initial[fixed]), weight))
        # Fixed endpoints still contribute to the full cut and its comparison with the incumbent.
        elif initial[i] != initial[j]:
            # This is an exact integer constant in scaled original objective units.
            constant += weight
    # Start from the supplied feasible state rather than an arbitrary released assignment.
    best = initial.copy()
    # Its full integer objective includes every internal, boundary and outside edge once.
    best_value = sum(weight for (i, j, original), weight in zip(graph.edges, weights) if best[i] != best[j])
    # Candidate changes affect only the selected coordinates.
    candidate = initial.copy()
    # Fixed outside labels remove the global symmetry reduction on a proper subset.
    required = 1 << len(selected)
    # Count genuinely evaluated restricted assignments.
    evaluated = 0
    # A work/time-interrupted repair still returns its strongest valid witness.
    for mask in range(min(required, max_states)):
        # Stop before consuming another restricted evaluation beyond the deadline.
        if perf_counter() >= deadline:
            # Incomplete enumeration remains explicitly unproven for this neighborhood.
            break
        # Each mask encodes every free sign while all other coordinates stay fixed.
        for bit, node in enumerate(selected):
            # No arbitrary fixed free spin is introduced; even a singleton may need either sign.
            candidate[node] = -1 if mask & (1 << bit) else 1
        # Begin with the fixed outside contribution.
        value = constant
        # Internal objective terms depend only on released labels.
        for i, j, weight in internal:
            # Each internal cut edge contributes its signed scaled weight.
            value += weight if candidate[i] != candidate[j] else 0
        # Boundary terms are w/2 - (w*s_out/2)*s_free, evaluated exactly as cut indicators.
        for node, fixed_sign, weight in boundary:
            # A negative edge is allowed to penalize a separated boundary pair.
            value += weight if candidate[node] != fixed_sign else 0
        # Keep the existing incumbent on ties, even if another restricted optimum is equivalent.
        if value > best_value:
            # Copy full original-order labels before the next mask changes the candidate.
            best = candidate.copy()
            # Retain the exact scaled objective with that witness.
            best_value = value
        # Increment only after all internal/boundary terms were evaluated.
        evaluated += 1
    # A restricted optimality claim requires visiting the full conditional search space.
    return {"assignment": best, "complete": evaluated == required, "evaluated": evaluated,
            "required": required, "exact_fraction": f"{best_value}/{scale}",
            "decomposition": {"internal_edges": len(internal), "boundary_edges": len(boundary),
                              "outside_constant": constant / scale}}


# LNS is a local controller; an exact neighborhood never implies a globally exact graph solve.
def solve_lns(graph, config, seed, budget, initial_assignment=None):
    """Release subsets and retain strictly better conditional repairs.

    config: subset_size=12, selection='mixed', repair='auto', repair_work=2**20.
    auto enumerates up to 20 released nodes and uses optional SCIP above that.
    budget max_work counts neighborhoods, seconds bounds all work. Supplied
    labels seed both current and retained best; releases use original IDs.
    Return shared result with conditional-complete flags per neighborhood,
    never a global upper bound/certificate. Example cut-eight four-node trap
    can improve when releasing enough nodes together. No mutation/files;
    memory sparse O(n+m), runtime exponential in enumerated release size.
    """
    # Measure selection and exact repairs within one overall wall budget.
    started = perf_counter()
    # Ordinary explicit parameters avoid a hidden automatic tuning policy.
    cfg = settings(config, {"subset_size": 12, "selection": "mixed", "repair": "auto", "repair_work": 1048576})
    # Requested size is clipped to graph size explicitly, while invalid cardinalities fail.
    if type(cfg["subset_size"]) is not int or cfg["subset_size"] < 1 or type(cfg["repair_work"]) is not int or cfg["repair_work"] < 0:
        # No accidental enormous/negative work counter is silently accepted.
        raise ValueError("invalid LNS subset_size/repair_work")
    # Only implemented repair backends belong in a reproducible configuration.
    if cfg["repair"] not in {"auto", "enumeration", "milp"}:
        # An absent named solver is not replaced silently by a heuristic.
        raise ValueError("repair must be auto, enumeration or milp")
    # The absolute deadline is passed into restricted enumeration without restarting its clock.
    deadline = deadline_from(budget)
    # Local randomness governs subset selection, not exact repair optimality.
    rng = np.random.default_rng(seed)
    # A supplied incumbent is validated and copied before selecting a release set.
    best = starting_signs(graph, rng, initial_assignment)
    # Original direct F is the monotone global-incumbent comparison value.
    best_value = cut_value(graph, best)
    # Keep bounded per-neighborhood conditional evidence.
    history = []
    # Real work counts distinguish exact repairs from interrupted feasible subproblem results.
    counts = {"neighborhoods": 0, "complete_repairs": 0, "partial_repairs": 0, "improvements": 0, "enumerated_states": 0}
    # The explicit work limit counts attempted neighborhoods, not a mislabeled global search tree.
    for iteration in range(budget.get("max_work", 10000)):
        # Check time before selecting or releasing more coordinates.
        if perf_counter() >= deadline:
            # The best full assignment remains valid if no neighborhood can be started.
            break
        # The requested subset may cover every node on a tiny correctness graph.
        count = min(cfg["subset_size"], graph.node_count)
        # Selection includes uniform, connected, weighted-violation and mixture rules.
        nodes = [int(node) for node in select_subset(graph, best, count, rng, cfg["selection"])]
        # Auto switches only on supported exact subset size, not on measured candidate quality.
        method = ("enumeration" if count <= 20 else "milp") if cfg["repair"] == "auto" else cfg["repair"]
        # The readable oracle explicitly preserves boundary and outside terms.
        if method == "enumeration":
            # Each restricted solve shares the remaining deadline and declared state-work cap.
            repaired = repair_exact(graph, best, nodes, deadline, cfg["repair_work"])
            # Returned labels are a valid feasible conditional witness even if enumeration stopped early.
            candidate = repaired["assignment"]
            # Completeness concerns this restricted neighborhood only.
            complete = repaired["complete"]
            # Count actual assignment evaluations, including incomplete searches.
            counts["enumerated_states"] += repaired["evaluated"]
            # Small decomposition fields make omitted-boundary errors visible in evidence.
            detail = {"decomposition": repaired["decomposition"], "evaluated": repaired["evaluated"]}
        # Larger releases use the separately identified optional generic SCIP model.
        else:
            # Import only on this path so enumeration-only LNS requires no optional MILP installation.
            from portfolio_milp import solve_milp
            # Outside labels stay fixed in the original full graph model, including every boundary edge.
            repaired = solve_milp(graph, {"max_nodes": max(5000, graph.node_count)}, seed,
                                  {"seconds": max(0.0, deadline - perf_counter()), "max_work": cfg["repair_work"]},
                                  initial_assignment=best, free_nodes=nodes)
            # Missing SCIP is explicit unavailability rather than a fabricated exact repair.
            if repaired["execution_status"] == "unavailable":
                # Retain the valid old full assignment while reporting that this controller could not execute the requested repair.
                return result_record("lns", graph, cfg, seed, budget, started, best, status="unavailable",
                                     reason="requested MILP repair backend unavailable", counters=counts, history=history)
            # The shared MILP result has already independently validated its saved-order labels.
            candidate = np.asarray(repaired["assignment"], dtype=np.int8)
            # Native solver-reported optimality remains conditional and tolerance-qualified.
            complete = bool((repaired["optimality_evidence"] or {}).get("conditional_optimal", False))
            # Bound scope is explicitly local, never promoted into the global result.
            detail = {"conditional_upper_bound": repaired["upper_bound"], "termination": repaired["termination_reason"]}
        # Rescore every repair using original graph weights, independently of its subproblem arithmetic.
        value = cut_value(graph, candidate)
        # A complete or partial repair can contribute a feasible strict gain.
        improved = value > best_value
        # Retained global labels remain monotone, unlike exploratory proposals inside subproblem solvers.
        if improved:
            # Own the chosen full assignment after the repair's work arrays are discarded.
            best = candidate.copy()
            # Record direct original F, not only the subproblem's internal-edge objective.
            best_value = value
            # Count genuine accepted full-graph gains.
            counts["improvements"] += 1
        # Each executed restricted solve consumes one neighborhood budget unit.
        counts["neighborhoods"] += 1
        # Exactness counters must not treat a time/work-limited repair as complete.
        counts["complete_repairs"] += int(complete)
        # Partial feasible searches are useful, but have a different optimality interpretation.
        counts["partial_repairs"] += int(not complete)
        # Keep actual per-neighborhood evidence bounded on long runs.
        if len(history) < 200:
            # The released IDs and conditional completion status identify the exact local problem solved.
            history.append({"iteration": iteration, "released": nodes, "method": method, "conditional_complete": complete,
                            "candidate_cut": value, "best_cut": best_value, "improved": improved, **detail})
    # A sequence of exact local repairs still supplies no global upper bound or proof.
    return result_record("lns", graph, cfg, seed, budget, started, best,
                         status="time_limit" if perf_counter() >= deadline else "completed",
                         reason="time_limit" if perf_counter() >= deadline else "neighborhood_limit", counters=counts, history=history)
