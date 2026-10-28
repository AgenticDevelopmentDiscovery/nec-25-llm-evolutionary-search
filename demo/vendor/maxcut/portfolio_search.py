"""Readable exhaustive, tabu, BLS and annealing searches on the settled sparse Graph."""

# Exponential probabilities implement BLS mode selection and maximization Metropolis acceptance.
import math
# Monotone timing permits cooperative stopping between ordinary search operations.
from time import perf_counter
# Local RNGs and one-dimensional state arrays keep graph storage sparse.
import numpy as np
# Reuse the previously verified objective and old-sign incremental flip kernel.
from bm_solver import compute_flip_gains, cut_value, flip_node
# Shared metadata, finite-decimal arithmetic and validation are method-independent.
from portfolio_common import deadline_from, integer_weights, result_record, settings, starting_signs


# Small exact enumeration is the correctness oracle; it never runs on a ladder-sized graph by accident.
def solve_exhaustive(graph, config, seed, budget, initial_assignment=None):
    """Enumerate 2**(n-1) assignments with s[0]=+1 using exact scaled integers.

    graph is sparse Graph; config accepts max_nodes (default 24, hard cap 26).
    seed is recorded but enumeration is deterministic. budget seconds/max_work
    limits elapsed time/assignments; initial_assignment is validated and copied.
    Return shared result with exact fraction evidence and a computed edgewise
    bound when incomplete. Example a +2 edge completes at F=U=2. No input
    mutation or files; O(2**(n-1)*m) time, O(n+m) memory. Complement invariance
    follows because (-s_i)*(-s_j)=s_i*s_j. No Gray-code optimization is hidden.
    """
    # Count elapsed time across validation, conversion and enumeration.
    started = perf_counter()
    # Reject unknown configuration fields rather than accepting an unused solver option.
    cfg = settings(config, {"max_nodes": 24})
    # This explicit hard guard is independent of a mistaken large work budget.
    if type(cfg["max_nodes"]) is not int or not 1 <= cfg["max_nodes"] <= 26 or graph.node_count > cfg["max_nodes"]:
        # No exponential allocation or enumeration occurs for a large graph.
        raise ValueError("exhaustive requires n <= max_nodes <= 26")
    # The budget checks finite time and integer work limits before starting a search.
    deadline = deadline_from(budget)
    # Decimal integer scaling makes comparisons exact for the supported written weights.
    weights, scale = integer_weights(graph)
    # A valid supplied incumbent is a candidate even if the enumeration is interrupted immediately.
    best = starting_signs(graph, np.random.default_rng(seed), initial_assignment)
    # Canonicalize complementary signs without changing their objective.
    best = best * int(best[0])
    # Each edge is counted once and evaluated in exact Python integer arithmetic.
    best_value = sum(weight for (i, j, original), weight in zip(graph.edges, weights) if best[i] != best[j])
    # Fixing node zero removes exactly the complementary duplicate half of the search space.
    required = 1 << (graph.node_count - 1)
    # Count genuinely evaluated assignments, not the size of a prospective search space.
    evaluated = 0
    # Working labels are distinct from the retained best vector.
    signs = np.ones(graph.node_count, dtype=np.int8)
    # Never enumerate more than the declared work budget.
    for mask in range(min(required, budget.get("max_work", 10000))):
        # A zero time limit can still return the independently validated incumbent.
        if perf_counter() >= deadline:
            # Incomplete enumeration must not receive an optimality label.
            break
        # Node zero stays +1; mask bits specify nodes one through n-1.
        for node in range(1, graph.node_count):
            # Every remaining assignment appears exactly once in binary enumeration.
            signs[node] = -1 if mask & (1 << (node - 1)) else 1
        # Integer edge contributions preserve signed weights and avoid floating comparison ambiguity.
        value = sum(weight for (i, j, original), weight in zip(graph.edges, weights) if signs[i] != signs[j])
        # Retain the earlier assignment on an exact objective tie.
        if value > best_value:
            # Copy before the next mask modifies working labels.
            best = signs.copy()
            # The independently representable scaled objective accompanies the retained witness.
            best_value = value
        # Record only completed assignment evaluations.
        evaluated += 1
    # A work/time interruption is not exhaustive completion.
    complete = evaluated == required
    # The sum of positive weights is a valid independently computed bound for incomplete searches.
    upper = best_value if complete else sum(max(0, weight) for weight in weights)
    # Report exact arithmetic assumptions, search completeness and the original-unit objective.
    return result_record("exhaustive", graph, cfg, seed, budget, started, best,
                         status="time_limit" if not complete and perf_counter() >= deadline else "completed",
                         reason="complete_enumeration" if complete else "time_limit" if perf_counter() >= deadline else "work_limit",
                         upper_bound=upper / scale, optimality="solver_reported_optimal" if complete else "unproven",
                         evidence={"complete_enumeration": complete, "scale": scale, "exact_cut_fraction": f"{best_value}/{scale}",
                                   "fixed_node": 0, "required_assignments": required, "arithmetic": "exact finite-decimal integer scaling"},
                         counters={"assignments_evaluated": evaluated})


# Seeded random tie-breaking is shared without changing the set of eligible moves.
def best_node(gains, eligible, rng):
    """Return highest-gain eligible node, uniform tie choice, or None if empty.

    gains is shape-(n,) float; eligible shape-(n,) bool; rng local Generator.
    Example gains=[-1,2,2], eligible=[True,True,True] chooses 1 or 2. No
    mutation, O(n) scan/storage. Eligibility must be supplied by the method;
    this helper does not silently relax tabu restrictions.
    """
    # Candidate indices preserve the original node-order convention.
    nodes = np.flatnonzero(eligible)
    # A fully prohibited move set means wait or stop, not ignore tenure.
    if not len(nodes):
        # The controller explicitly handles a no-admissible-move state.
        return None
    # The exact maximum of maintained gains defines steepest ascent or least degradation.
    maximum = gains[nodes].max()
    # Uniform selection among exact ties uses the solve's reproducible local stream.
    return int(rng.choice(nodes[gains[nodes] == maximum]))


# This is a documented one-flip tabu variant, distinct from BLS's alternating trajectory.
def solve_tabu(graph, config, seed, budget, initial_assignment=None):
    """One-flip tabu search with aspiration, worsening moves and optional restarts.

    config: tenure=20 accepted-move iterations, restart_after=0 (disabled).
    The one-flip/aspiration principles follow Palubeckis & Krivickiene 2004;
    fixed-budget best-admissible scans, no transformed-QUBO aspirational
    descent and optional fixed stagnation restart are documented project
    variations, not their full MST/RRT algorithm. budget max_work counts
    iterations including tabu waits; seconds is cooperative. initial signs
    seed current AND best states. Return shared result; no caller mutation or
    files. Example cut-eight trap may accept -1 to escape toward ten.
    O(n+degree(i)) per move, sparse O(n+m) memory, history capped at 200 events.
    """
    # Establish measurement before method-specific validation.
    started = perf_counter()
    # Visible rules avoid attributing an unspecified generic search to a named published implementation.
    cfg = settings(config, {"tenure": 20, "restart_after": 0})
    # Both controls count iterations, not seconds or nodes.
    if any(type(cfg[key]) is not int or cfg[key] < 0 for key in cfg):
        # Zero tenure is a deliberate ablation; negative/fractional counts are errors.
        raise ValueError("tenure and restart_after must be nonnegative integers")
    # The shared budget validates and supplies an absolute stop time.
    deadline = deadline_from(budget)
    # Randomness belongs to this solve, independent of other solver invocation order.
    rng = np.random.default_rng(seed)
    # Explicit warm-start labels are validated and copied before any move.
    current = starting_signs(graph, rng, initial_assignment)
    # Best and exploratory arrays must never alias.
    best = current.copy()
    # A direct initial cut starts the incremental total.
    current_value = cut_value(graph, current)
    # Incumbent quality never decreases even when exploratory states worsen.
    best_value = current_value
    # Cached gains use the previously verified single-flip identity.
    gains = compute_flip_gains(graph, current)
    # expiry[i] is the first permitted iteration; initial zero permits all moves.
    expiry = np.zeros(graph.node_count, dtype=np.int64)
    # Bounded scalar history illustrates actual accepted worsening and aspiration decisions.
    history = []
    # Counters separate iterations, actual flips, waits, restarts and tabu aspiration.
    counts = {"iterations": 0, "flips": 0, "waits": 0, "restarts": 0, "aspiration_moves": 0}
    # Track the last strict global improvement for the optional diversification rule.
    last_improvement = 0
    # The work limit remains explicit and independent of the clock.
    for iteration in range(budget.get("max_work", 10000)):
        # Check time before scanning or applying another move.
        if perf_counter() >= deadline:
            # A valid best witness survives a time-limited trajectory.
            break
        # A tabu move is admissible only if it strictly beats the global incumbent.
        aspiration = current_value + gains > best_value + 1e-10
        # Expired moves or aspirational moves form the actual eligible neighborhood.
        eligible = (iteration >= expiry) | aspiration
        # Random ties do not introduce any hidden gain-based acceptance rule.
        node = best_node(gains, eligible, rng)
        # Count an elapsed iteration even when all nodes remain tabu.
        counts["iterations"] += 1
        # Waiting respects tenure instead of forcing a prohibited immediate reversal.
        if node is None:
            # A wait consumes work while the logical iteration clock advances.
            counts["waits"] += 1
            # No working signs or cached gains changed.
            continue
        # Store the gain before the old-sign flip kernel negates its entry.
        gain = float(gains[node])
        # Aspiration is evidence only when a move was actually still tabu.
        aspirational = bool(iteration < expiry[node])
        # This applies worsening, neutral or improving admissible moves intentionally.
        flip_node(graph, current, gains, node)
        # Maintain the original cut units; final results are independently rescored.
        current_value += gain
        # Forbid reversal for exactly tenure subsequent iterations.
        expiry[node] = iteration + cfg["tenure"] + 1
        # Record real accepted flips rather than nominal work iterations.
        counts["flips"] += 1
        # Counts expose whether the aspiration exception affected the actual trajectory.
        counts["aspiration_moves"] += int(aspirational)
        # A prospective retained gain is verified on the original graph before copying.
        if current_value > best_value + 1e-10:
            # Direct scoring prevents drift in the running total from creating a false improvement.
            current_value = cut_value(graph, current)
            # Only a directly confirmed strict improvement can update global best.
            if current_value > best_value:
                # Independent storage prevents later worsening moves from damaging the incumbent.
                best = current.copy()
                # Retain the exact directly recomputed floating cut with its witness.
                best_value = current_value
                # Stagnation is measured since a strict verified improvement.
                last_improvement = iteration
        # Scalar event capture is bounded on large instances and long work budgets.
        if len(history) < 200:
            # These values describe the actual move, not a conceptual trajectory.
            history.append({"iteration": iteration, "node": node, "gain": gain, "current_cut": current_value,
                            "best_cut": best_value, "aspiration": aspirational})
        # Optional diversification is explicit, disabled by default, and leaves best untouched.
        if cfg["restart_after"] and iteration - last_improvement >= cfg["restart_after"]:
            # A fresh random assignment changes only exploratory state.
            current = starting_signs(graph, rng, None)
            # Recompute fields because every node may have changed.
            gains = compute_flip_gains(graph, current)
            # Reset the incremental total to the direct original objective.
            current_value = cut_value(graph, current)
            # A restart may itself be a better feasible assignment.
            if current_value > best_value:
                # Preserve such a strict gain even if time expires before another move.
                best = current.copy()
                # Record its independently computed objective.
                best_value = current_value
            # New exploratory states inherit no move prohibitions from the old trajectory.
            expiry.fill(0)
            # Restart spacing is measured from this fresh exploration point.
            last_improvement = iteration
            # Expose the actual number of random restarts.
            counts["restarts"] += 1
    # Termination is separate from feasibility and never implies global optimality.
    return result_record("tabu", graph, cfg, seed, budget, started, best,
                         status="time_limit" if perf_counter() >= deadline else "completed",
                         reason="time_limit" if perf_counter() >= deadline else "work_limit", counters=counts, history=history)


# Metropolis annealing is a project comparison baseline, not Myklebust's optimized implementation.
def solve_annealing(graph, config, seed, budget, initial_assignment=None):
    """Single-flip SA with geometric proposal cooling and optional bounded polish.

    config defaults: initial_temperature=2 weight units, final_temperature=.01,
    polish=True. budget max_work counts proposals, seconds limits all work;
    one n-proposal block is one sweep. Every proposal picks a uniform node;
    accept min(1,exp(gain/T)), with log(U)<gain/T for numerical stability.
    Warm signs seed both current/best. Return shared result, raw and polished
    cuts separately; no mutation/files. Example +2 edge improves by flipping
    either endpoint. Sparse O(n+m) memory; per proposal O(degree) when accepted.
    References: Myklebust 2015 for context; schedule here is project-specific.
    """
    # Timing includes initial validation and any final polishing.
    started = perf_counter()
    # The numerical temperature scale is explicit, never silently auto-tuned to a graph family.
    cfg = settings(config, {"initial_temperature": 2.0, "final_temperature": 0.01, "polish": True})
    # Both temperatures must be positive finite objective units.
    if any(not math.isfinite(cfg[key]) or cfg[key] <= 0 for key in ("initial_temperature", "final_temperature")) or type(cfg["polish"]) is not bool:
        # Reject invalid probability scales or an ambiguous polishing flag.
        raise ValueError("temperatures must be positive finite numbers; polish must be bool")
    # All proposals and polishing obey this cooperative deadline.
    deadline = deadline_from(budget)
    # Random proposal/acceptance streams are local to this solver invocation.
    rng = np.random.default_rng(seed)
    # Own the initial vector while preserving a caller-supplied incumbent separately.
    current = starting_signs(graph, rng, initial_assignment)
    # Later accepted worsening proposals must not mutate best-so-far.
    best = current.copy()
    # Direct F is the initial quality reference for both states.
    current_value = cut_value(graph, current)
    # The scalar best accompanies the independent retained vector.
    best_value = current_value
    # Incremental fields avoid recomputing every graph edge for each proposal.
    gains = compute_flip_gains(graph, current)
    # These counters reveal actual work, including accepted downhill proposals.
    counts = {"proposals": 0, "accepted": 0, "accepted_worsening": 0, "polish_flips": 0}
    # A small actual trajectory supports temperature/acceptance illustrations.
    history = []
    # max_work bounds random proposals; polish is separately bounded below by n flips.
    proposals = budget.get("max_work", 10000)
    # Each iteration is a single uniformly chosen-node proposal, not a full sweep.
    for proposal in range(proposals):
        # Stop before sampling another move after time is exhausted.
        if perf_counter() >= deadline:
            # The current best remains a valid feasible result.
            break
        # Geometric interpolation reaches both configured endpoint temperatures when work >1.
        fraction = proposal / max(1, proposals - 1)
        # Interpolating logarithms avoids exponentiating an unnecessary huge temperature ratio.
        temperature = math.exp((1 - fraction) * math.log(cfg["initial_temperature"]) + fraction * math.log(cfg["final_temperature"]))
        # Random node proposals are independent of current gain, unlike greedy local search.
        node = int(rng.integers(graph.node_count))
        # This is the change in MAXIMIZED F, so negative gains have acceptance below one.
        gain = float(gains[node])
        # Clamp U away from zero so log is defined without altering ordinary acceptance draws.
        accepted = gain >= 0 or math.log(max(float(rng.random()), np.finfo(float).tiny)) < gain / temperature
        # Count proposals even when rejected.
        counts["proposals"] += 1
        # A rejection leaves current labels and all gains untouched.
        if accepted:
            # Apply the established old-sign incremental update only for accepted flips.
            flip_node(graph, current, gains, node)
            # Update the exploratory objective, which is allowed to decrease.
            current_value += gain
            # Expose the distinction between proposals and actual state changes.
            counts["accepted"] += 1
            # Downhill moves are an intentional annealing mechanism, not retained-answer regressions.
            counts["accepted_worsening"] += int(gain < 0)
            # Confirm a prospective retained improvement directly on the original graph.
            if current_value > best_value + 1e-10:
                # Recompute before crediting a higher quality assignment.
                current_value = cut_value(graph, current)
                # Strict direct comparison prevents replacing the incumbent on a tie.
                if current_value > best_value:
                    # Retain independent labels before further proposals alter them.
                    best = current.copy()
                    # Store directly recomputed F, never an Ising energy without conversion.
                    best_value = current_value
        # Sparse sampling keeps histories bounded while preserving actual numerical evidence.
        if len(history) < 200 and proposal % max(1, proposals // 200) == 0:
            # Temperature and actual current/best cuts have separate units in later figures.
            history.append({"proposal": proposal, "temperature": temperature, "current_cut": current_value, "best_cut": best_value})
    # Record the raw SA output before adding an explicitly identified local-search hybrid.
    raw_cut = cut_value(graph, best)
    # Optional greedy polishing works on the retained raw best, never discards it.
    if cfg["polish"]:
        # Polishing owns labels and gains independently of raw-result storage.
        polished = best.copy()
        # Recompute fresh fields to remove any trajectory accumulation error.
        polish_gains = compute_flip_gains(graph, polished)
        # A separate finite work cap avoids an unlimited tail after proposal exhaustion.
        for step in range(min(graph.node_count, proposals)):
            # The original deadline also limits hybrid work.
            if perf_counter() >= deadline or polish_gains.max() <= 1e-10:
                # Either time or local stationarity terminates the bounded polish.
                break
            # Greedy deterministic tie-breaking is documented separately from random SA proposals.
            node = int(np.argmax(polish_gains))
            # Each accepted polish move has a strictly positive direct gain within tolerance.
            flip_node(graph, polished, polish_gains, node)
            # This work is not hidden in the SA proposal count.
            counts["polish_flips"] += 1
        # Independent scoring decides whether a polished candidate may replace the raw result.
        if cut_value(graph, polished) > raw_cut:
            # Keep the validated strict gain with independent storage.
            best = polished.copy()
    # State clearly that polishing produces a hybrid when requested.
    result = result_record("annealing", graph, cfg, seed, budget, started, best,
                           status="time_limit" if perf_counter() >= deadline else "completed",
                           reason="time_limit" if perf_counter() >= deadline else "work_limit", counters=counts, history=history)
    # Raw and final cuts prevent crediting local polish as intrinsic SA output quality.
    result.update({"raw_cut": raw_cut, "polished_cut": result["cut"], "hybrid": cfg["polish"]})
    # Return the ordinary shared contract plus explicit hybrid evidence.
    return result


# BLS follows the paper's alternating descent/current-attractor trajectory and adaptive perturbation.
def solve_bls(graph, config, seed, budget, initial_assignment=None):
    """Reproduce Benlic-Hao 2013 Algorithms 1–3 with documented readable scans.

    config: jump=max(1,ceil(.01*n)), stagnation=1000 attractors, p_min=.8,
    q=.5, tenure_min=3, tenure_max=max(3,n//10). Scan gains instead of integer
    buckets; finite-decimal weights and tiny-graph tenure floors are explicit
    extensions. M1 is a single best-gain move; M2 chooses one eligible highest
    gain node per side and evaluates the true pair gain; M3 is uniform random.
    Descent ignores tabu. Perturbations may worsen; next descent starts from
    that current state, not global best. budget max_work counts flips (M2=2),
    seconds is cooperative. Return shared record with mode/jump history, no
    caller mutation/files. Sparse O(n+m), O(n) selection per flip; this omits
    the paper's performance-oriented bucket structure, not its diversification.

    Example: solve_bls(g,{},7,{'seconds':2,'max_work':20},[1,1,-1,-1])
    on the four-node cut-eight trap preserves that incumbent while diversifying.
    """
    # Full timing includes descent and perturbation, not only retained improvements.
    started = perf_counter()
    # Table 1's nominal jump/tenure receive documented integer floors for small instances.
    cfg = settings(config, {"jump": max(1, math.ceil(0.01 * graph.node_count)), "stagnation": 1000,
                            "p_min": 0.8, "q": 0.5, "tenure_min": 3, "tenure_max": max(3, graph.node_count // 10)})
    # The first four controls are meaningful integer search counts.
    if any(type(cfg[key]) is not int or cfg[key] < 1 for key in ("jump", "stagnation", "tenure_min", "tenure_max")) or cfg["tenure_max"] < cfg["tenure_min"]:
        # Invalid tenure ranges cannot be sampled reproducibly.
        raise ValueError("BLS counts must be positive integers with tenure_max >= tenure_min")
    # Mode probabilities must be finite dimensionless values within the unit interval.
    if any(not math.isfinite(cfg[key]) or not 0 <= cfg[key] <= 1 for key in ("p_min", "q")):
        # Reject an undefined diversification policy before modifying state.
        raise ValueError("BLS probabilities must lie in [0,1]")
    # The same clock bounds every descent and perturbation phase.
    deadline = deadline_from(budget)
    # One solve-local generator controls tied moves, modes and random tenures.
    rng = np.random.default_rng(seed)
    # Copy optional warm labels into the actual starting trajectory.
    current = starting_signs(graph, rng, initial_assignment)
    # Best-so-far storage never aliases the trajectory that may accept worse attractors.
    best = current.copy()
    # Direct initial F seeds the incumbent, including a supplied high-quality assignment.
    best_value = cut_value(graph, best)
    # Fresh incremental gains support both descending and intentionally worsening moves.
    gains = compute_flip_gains(graph, current)
    # Expiry stores one last-move-plus-tenure value, not tenure added twice.
    expiry = np.zeros(graph.node_count, dtype=np.int64)
    # Previous attractor begins at the paper's initial C_p state.
    previous = current.copy()
    # Adaptive jump magnitude evolves with repeated attractors, not automatic global-best resets.
    jump = cfg["jump"]
    # Non-improving-attractor count controls directed probability and strong random diversification.
    stagnation = 0
    # Attractor progress is measured separately from transient improvements retained during perturbation.
    last_attractor_best = best_value
    # All counters expose actual accepted state transitions.
    counts = {"flips": 0, "attractors": 0, "directed_single": 0, "directed_pair": 0, "random": 0, "strong_random": 0}
    # Bound scalar evidence while retaining every actual event on tiny examples.
    history = []
    # All phases consume one shared maximum flip budget.
    limit = budget.get("max_work", 10000)
    # Alternate local improvement and perturbation exactly as the paper's controller requires.
    while counts["flips"] < limit and perf_counter() < deadline:
        # Descent intentionally does not use the tabu list (paper Section 2.4).
        while gains.max() > 1e-10 and counts["flips"] < limit and perf_counter() < deadline:
            # Steepest improving M1 uses uniform random ties among all nodes.
            node = best_node(gains, np.ones(graph.node_count, dtype=bool), rng)
            # The settled incremental kernel updates only affected fields.
            flip_node(graph, current, gains, node)
            # Descent flips also contribute to the history/tenure iteration clock.
            counts["flips"] += 1
            # Uniform inclusive tenure follows the paper's random-memory mechanism.
            expiry[node] = counts["flips"] + int(rng.integers(cfg["tenure_min"], cfg["tenure_max"] + 1))
        # Direct scoring at each reached state protects retained answers from field drift.
        value = cut_value(graph, current)
        # Remember any valid strict gain even if the budget ends during descent.
        if value > best_value:
            # Store an independent best witness before another perturbation may worsen current.
            best = current.copy()
            # Reset stagnation after an actual retained quality improvement.
            best_value = value
        # A transient new best also resets stagnation at the next completed descent endpoint.
        if best_value > last_attractor_best:
            # Remember all discoveries since the previous attractor, including perturbation intermediates.
            last_attractor_best = best_value
            # This keeps the extension's incumbent retention from falsely increasing stagnation.
            stagnation = 0
        # Unimproved attractors increase the pressure toward random diversification.
        else:
            # This counts attractors, not individual failed flip proposals.
            stagnation += 1
        # If descent was interrupted, no fictitious attractor/perturbation is claimed.
        if counts["flips"] >= limit or perf_counter() >= deadline:
            # Return the best verified feasible labels found within the consumed work.
            break
        # A reached descent endpoint is a genuine single-flip local optimum at the configured tolerance.
        counts["attractors"] += 1
        # Compare actual previous labels as in Algorithm 1, not just equal cut values.
        jump = jump + 1 if np.array_equal(current, previous) else cfg["jump"]
        # Store THIS attractor before perturbing its owned current vector.
        previous = current.copy()
        # Strong perturbation is forced when the non-improvement threshold is exceeded.
        strong = stagnation > cfg["stagnation"]
        # The paper resets omega to zero to signal strong random perturbation.
        if strong:
            # This reset affects future mode probabilities but never changes the saved best.
            stagnation = 0
        # Equation (2) sets directed probability with the minimum floor P0.
        directed_probability = max(math.exp(-stagnation / cfg["stagnation"]), cfg["p_min"])
        # Select one perturbation type for all L moves in this phase.
        mode = "random" if strong or rng.random() >= directed_probability else "directed_single" if rng.random() < cfg["q"] else "directed_pair"
        # Record a bounded actual attractor and its chosen diversification strength.
        if len(history) < 200:
            # Numeric values come from the just-completed real descent.
            history.append({"attractor": counts["attractors"], "current_cut": value, "best_cut": best_value,
                            "jump": jump, "stagnation": stagnation, "mode": mode, "strong": strong})
        # Every mode perturbs the current attractor, accepting its resulting trajectory regardless of quality.
        for perturbation in range(jump):
            # No phase can escape the declared global work/time limit.
            if counts["flips"] >= limit or perf_counter() >= deadline:
                # Partial perturbation is still a valid exploratory state, not a completed new descent.
                break
            # Fresh direct F makes aspiration refer to the actual current cut.
            value = cut_value(graph, current)
            # Directed eligibility combines expiry and strict aspiration against global best.
            eligible = (counts["flips"] >= expiry) | (value + gains > best_value + 1e-10)
            # Random perturbation ignores tabu by definition; directed M1 respects it.
            nodes = [int(rng.integers(graph.node_count))] if mode == "random" else [best_node(gains, eligible, rng)]
            # A one-flip remainder cannot truthfully be called a two-node perturbation.
            actual_mode = "directed_single" if mode == "directed_pair" and limit - counts["flips"] < 2 else mode
            # M2 exchanges one currently positive and one currently negative label.
            if mode == "directed_pair" and limit - counts["flips"] >= 2:
                # Highest eligible individual gain on each side follows the stated M2 rule.
                first = best_node(gains, eligible & (current == 1), rng)
                # The second candidate is selected BEFORE flipping first, as a joint move.
                second = best_node(gains, eligible & (current == -1), rng)
                # An empty side cannot support a two-node exchange.
                nodes = [first, second] if first is not None and second is not None else []
                # Pair aspiration must use the joint gain, including its internal edge correction.
                if nodes and (counts["flips"] < expiry[first] or counts["flips"] < expiry[second]):
                    # The once-counted internal edge contributes to both individual gains but is unchanged by exchanging both signs.
                    internal_weight = sum(weight for neighbor, weight in graph.neighbors[first] if neighbor == second)
                    # This correction is valid for any two signs, including the opposite-side exchange used here.
                    joint_gain = gains[first] + gains[second] - 2 * internal_weight * current[first] * current[second]
                    # A tabu exchange is admissible only if its completed pair beats the retained incumbent.
                    if value + joint_gain <= best_value + 1e-10:
                        # Without joint aspiration, choose the highest non-tabu vertex on each side instead.
                        first = best_node(gains, (counts["flips"] >= expiry) & (current == 1), rng)
                        # Both vertices are selected from the pre-move state.
                        second = best_node(gains, (counts["flips"] >= expiry) & (current == -1), rng)
                        # An unavailable side triggers the explicit random fallback below.
                        nodes = [first, second] if first is not None and second is not None else []
            # A prohibited or undefined directed move falls back to the paper's random operator explicitly.
            if not nodes or nodes[0] is None:
                # This small-graph fallback is recorded as random, never as a successful directed move.
                nodes = [int(rng.integers(graph.node_count))]
                # The actual applied operator is what contributes to the mode counter.
                applied_mode = "random"
            # Ordinary eligible choices keep their intended method identity.
            else:
                # M2's two sequential gain updates implement its joint change exactly, including the internal edge correction.
                applied_mode = actual_mode
            # Count perturbation OPERATORS separately from the number of individual flips they contain.
            counts[applied_mode] += 1
            # Forced random mode exposes stagnation handling separately from ordinary random choices.
            counts["strong_random"] += int(strong)
            # Apply each selected coordinate using updated gains and the old sign at that step.
            for node in nodes:
                # Signs and field updates remain synchronized even inside a two-node exchange.
                flip_node(graph, current, gains, node)
                # Individual flips define the exact computational work counter.
                counts["flips"] += 1
                # Every perturbation move updates the same search-history memory as descent.
                expiry[node] = counts["flips"] + int(rng.integers(cfg["tenure_min"], cfg["tenure_max"] + 1))
            # Retain a transient strict gain as well as improvements at descent endpoints.
            value = cut_value(graph, current)
            # Global best never follows a worsened perturbation simply because it is more recent.
            if value > best_value:
                # Copy now so a subsequent perturbation cannot erase a discovered useful answer.
                best = current.copy()
                # Record the independent direct value for this witness.
                best_value = value
    # The result names its readable reproduction and lists performance/tiny-input deviations in its guide.
    return result_record("bls", graph, cfg, seed, budget, started, best,
                         status="time_limit" if perf_counter() >= deadline else "completed",
                         reason="time_limit" if perf_counter() >= deadline else "work_limit",
                         counters=counts, history=history, implementation="project-BenlicHao2013-readable-v1")
