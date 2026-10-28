"""Shared sparse graph, honest solver results, budgets and exact decimal conversions."""

# Fractions make the small oracle's finite-decimal arithmetic exact.
from fractions import Fraction
# GCD/LCM and finite checks validate integer scaling and numerical limits.
import math
# perf_counter measures monotone elapsed seconds independent of wall-clock adjustments.
from time import perf_counter
# NumPy owns binary vectors; no dense graph matrix is required.
import numpy as np
# Reuse the settled graph and mathematical validation without changing their implementation.
from bm_solver import cut_value, graph_digest, validate_signs


# Budget checking is shared, while each method keeps explicit work counters.
def deadline_from(budget):
    """Return monotone deadline from budget dict seconds, default 60; no mutation.

    Example {'seconds':0} permits no work. Seconds must be finite and >=0.
    Other supported field is max_work (nonnegative integer, default 10000).
    Unknown budget keys fail. Return float seconds on perf_counter's scale.
    O(1); no solver work, random draws or file writes.
    """
    # Unknown limits must never be silently accepted and ignored.
    if set(budget) - {"seconds", "max_work"}:
        # Users need to know the actual implemented computational limits.
        raise ValueError("budget accepts seconds and max_work only")
    # A time limit is measured in seconds, not sweeps or iterations.
    seconds = float(budget.get("seconds", 60.0))
    # NaN/negative limits would invalidate stopping decisions.
    if not math.isfinite(seconds) or seconds < 0:
        # Reject before any optimization modifies working state.
        raise ValueError("seconds must be finite and nonnegative")
    # Optional work bounds have backend-specific documented counters.
    work = budget.get("max_work", 10000)
    # Boolean and fractional counts must not become accidental iteration budgets.
    if type(work) is not int or work < 0:
        # Distinguish a bad budget from a legitimate zero-work solve.
        raise ValueError("max_work must be a nonnegative integer")
    # Each solver establishes its deadline on entry; the CLI additionally enforces a child-process limit.
    return perf_counter() + seconds


# Explicit keys make a configuration reproducible rather than a bag of silently ignored flags.
def settings(config, defaults):
    """Copy defaults then apply known config keys; reject unknown names, O(keys).

    config/defaults are dicts, e.g. {'tenure':5} and {'tenure':20}. Return a new
    dict; neither input is mutated. Value ranges are checked by each method.
    This is ordinary dictionary validation, not an automatic configuration grid.

    Example: settings({'tenure':5},{'tenure':20}) returns {'tenure':5}.
    Reference: the shared explicit-configuration contract; no optimization equation.
    """
    # Misspellings must not produce experiments under unintended default settings.
    if set(config) - set(defaults):
        # Report actual unknown names so the caller can correct the input.
        raise ValueError(f"unknown configuration keys: {sorted(set(config) - set(defaults))}")
    # Defaults belong to the caller; independent results own a fresh dictionary.
    result = defaults.copy()
    # Apply only explicitly validated key names.
    result.update(config)
    # Return resolved parameters to be stored in every result.
    return result


# Every method starts with owned valid signs; supplied incumbents are never ignored.
def starting_signs(graph, rng, initial_assignment):
    """Return owned shape-(n,) int8 signs, using initial if supplied else random.

    graph is settled sparse Graph; rng is a local np.random.Generator, e.g.
    default_rng(1); initial_assignment is +/-1 length n or None. Validate before
    copying; no input mutation. O(n). A warm start may seed current state, and
    the controller must also preserve it in best-so-far state.

    Example: on a two-node graph, initial_assignment=[1,-1] returns a copy.
    Reference: s_i in {-1,+1}; only the supplied Generator consumes RNG draws.
    """
    # Supplied labels represent an explicit warm start, never merely an output-path hint.
    if initial_assignment is not None:
        # validate_signs copies and checks membership/node order length.
        return validate_signs(initial_assignment, graph.node_count)
    # Each independent node draw uses this solve's local seed stream.
    return rng.choice(np.array([-1, 1], dtype=np.int8), size=graph.node_count)


# Oracle arithmetic and integer-only backends share one documented lossless conversion.
def integer_weights(graph, max_scale=10**9, max_integer=2**50):
    """Return (integer edge weights,scale) with w=k/scale from decimal repr.

    graph contains finite Python float weights, one edge once. Decimal repr
    is Fraction(str(w)), e.g. [0.1,-0.25] -> ([2,-5],20). Defaults guard scale
    <=1e9 and sum(abs(k))<=2**50 for exact double representation downstream.
    No arbitrary rounding. Raises on unsupported precision/range. O(m), sparse
    memory. For supplied project decimal text, repr preserves its values.

    Example: weights .1 and -.25 return ([2,-5],20).
    No graph mutation or files; the identity is w=k/scale, not rounded approximation.
    """
    # Each Fraction recovers the explicitly documented finite-decimal representation.
    fractions = [Fraction(str(weight)) for i, j, weight in graph.edges]
    # Scale starts at one for empty or integer-weight graphs.
    scale = 1
    # A common denominator preserves every edge exactly rather than rounding individually.
    for weight in fractions:
        # LCM handles mixed decimal precision without factors of two or sign changes.
        scale = math.lcm(scale, weight.denominator)
        # Refuse dangerous scaling instead of silently approximating an exact problem.
        if scale > max_scale:
            # The caller can select a floating backend when exact integer scaling is unsuitable.
            raise ValueError("decimal scaling exceeds supported max_scale")
    # Multiplication by the LCM produces exact Python integers for every edge.
    weights = [int(weight * scale) for weight in fractions]
    # Some upstream C/Fortran routines use double precision even for integer objectives.
    if sum(abs(weight) for weight in weights) > max_integer:
        # A range guard is preferable to an unreported objective conversion error.
        raise ValueError("scaled objective exceeds supported exact integer range")
    # Record scale alongside weights so assignments and bounds can be translated back.
    return weights, scale


# Result creation separates execution, feasibility and optimality instead of conflating them.
def result_record(name, graph, config, seed, budget, started, assignment=None,
                  status="completed", reason="work_limit", upper_bound=None,
                  optimality="unproven", evidence=None, counters=None, history=None,
                  implementation="project-owned-v1", logs=None):
    """Return independently rescored JSON-compatible shared result, no file writes.

    name/config/seed/budget identify the solve; started is perf_counter seconds.
    assignment is +/-1 shape n or None, copied to a list. status is completed,
    time_limit, unavailable or failed; reason is specific termination text.
    upper_bound is finite weight units or None, never an invented relaxation
    value. optimality is unproven, solver_reported_optimal, or
    checked_certificate; evidence explains assumptions. counters/history/logs
    are optional method-owned JSON data. implementation identifies source.
    Example name='exhaustive', assignment=[1,-1] returns cut 2 on a +2 edge.
    O(n+m), no caller array mutation; validity is checked independently of status.
    """
    # Only explicit execution statuses belong in this field.
    if status not in {"completed", "time_limit", "unavailable", "failed"}:
        # Prevent an undocumented status from masquerading as an optimality conclusion.
        raise ValueError("invalid execution status")
    # Optimality is a separate small vocabulary, never an arbitrary execution-status string.
    if optimality not in {"unproven", "solver_reported_optimal", "checked_certificate"}:
        # Unsupported proof wording cannot silently become authoritative result metadata.
        raise ValueError("invalid optimality status")
    # Validate labels before claiming feasibility or recomputing the objective.
    signs = None if assignment is None else validate_signs(assignment, graph.node_count)
    # Independently score the original graph rather than an incremental or transformed total.
    value = None if signs is None else cut_value(graph, signs)
    # Finite edge inputs can still overflow their total; nonfinite cuts are not portable valid numerical results.
    if value is not None and not math.isfinite(value):
        # Preserve the actual numerical failure instead of emitting Infinity as a successful JSON cut.
        raise FloatingPointError("original cut is not finite")
    # A proof label requires a validated witness and explicit evidence, independently of execution status.
    if optimality != "unproven" and (signs is None or not evidence):
        # No successful exit or reference score alone can establish optimality.
        raise ValueError("optimality claim requires a valid assignment and evidence")
    # Bounds must be actual finite numbers in original objective units.
    if upper_bound is not None and (not math.isfinite(upper_bound) or (value is not None and upper_bound + 1e-8 * max(1, abs(value)) < value)):
        # An inconsistent claimed bound invalidates the result rather than becoming a certificate.
        raise ValueError("nonfinite or infeasible upper bound")
    # Separate validity and evidence explicitly, including on a time-limited solve.
    return {"solver": name, "implementation": implementation, "configuration": config.copy(),
            "seed": seed, "budget": budget.copy(), "input_sha256": graph_digest(graph),
            "input_hash_kind": "semantic_graph", "assignment": None if signs is None else signs.tolist(),
            "cut": value, "upper_bound": upper_bound, "execution_status": status,
            "solution_valid": signs is not None, "optimality_status": optimality,
            "optimality_evidence": evidence, "termination_reason": reason,
            "runtime_seconds": perf_counter() - started, "work_counters": counters or {},
            "history": history or [], "raw_backend_logs": logs or []}
