"""Sparse CPU bSB/dSB/GSB and replica-coupled SBQA from identified primary equations."""

# Mathematical scaling and regularization remain explicit scalar parameters.
import math
# Cooperative stopping is checked between actual integration steps.
from time import perf_counter
# Arrays have axes (original node, replica); no n*n coupling matrix is allocated.
import numpy as np
# Original cut and binary polishing kernels remain unchanged.
from bm_solver import compute_flip_gains, cut_value, flip_node
# Shared contracts validate settings and preserve actual source/method identities.
from portfolio_common import deadline_from, result_record, settings, starting_signs


# Sparse symmetric Ising multiplication preserves the graph's one-edge storage convention.
def ising_field(graph, states):
    """Return J@states for J_ij=-w_ij, h=0, without a dense coupling matrix.

    graph is settled Graph; states is finite shape (n,R) real array. Each edge
    contributes to BOTH endpoint fields, unlike the once-counted objective.
    Example one +2 edge and states=[[1],[-1]] gives [[2],[-2]]. No mutation;
    O((n+m)*R) work and O(n*R) output, suitable for large sparse inputs.
    """
    # Shape validation catches swapped node/replica axes before indexing.
    if states.ndim != 2 or states.shape[0] != graph.node_count or not np.all(np.isfinite(states)):
        # Nonfinite dynamics must fail honestly instead of being rounded to signs.
        raise ValueError("states must be finite shape (n,replicas)")
    # Only a state-sized field array is allocated, never a graph-sized square matrix.
    field = np.zeros_like(states, dtype=float)
    # Each stored undirected edge represents two symmetric entries of J.
    for i, j, weight in graph.edges:
        # The Ising convention E=-sum(J*s_i*s_j) requires J=-w when maximizing F.
        field[i] -= weight * states[j]
        # Symmetry supplies the other endpoint's weighted-neighbor field.
        field[j] -= weight * states[i]
    # Return independent numerical workspace for the next momentum update.
    return field


# The replica schedule is independently testable and distinct from an independent-restart loop.
def replica_coupling(fraction, replicas, beta=1.0, gamma_initial=1.0, alpha=1.0, regularization=1e-5):
    """SBQA Eq.(5): J_perp=-log(tanh(beta*Gamma/R))/(2*beta).

    fraction=t/T in [0,1], replicas integer>=2, beta>0 inverse temperature,
    gamma_initial>0, alpha>0, regularization>0. Gamma=Gamma0*(1-t/T)**alpha
    +regularization. Example fraction=1 stays finite because of 1e-5. Return
    finite float; no mutation/files; O(1). Reference: Pawlowski et al.,
    arXiv:2604.01050v1 Eq.(5), not a generic all-to-all replica attraction.
    """
    # Every schedule quantity has an explicit admissible numerical range.
    if type(replicas) is not int or replicas < 2 or not math.isfinite(fraction) or not 0 <= fraction <= 1:
        # A single replica cannot silently stand in for interacting-replica dynamics.
        raise ValueError("SBQA needs replicas>=2 and fraction in [0,1]")
    # Positive finite beta and field/regularization controls keep the logarithm defined.
    if any(not math.isfinite(value) or value <= 0 for value in (beta, gamma_initial, alpha, regularization)):
        # An undefined/singular schedule is not repaired by an undocumented numerical clip.
        raise ValueError("SBQA schedule parameters must be positive finite values")
    # This is the paper's decaying transverse-field schedule plus its stated additive epsilon.
    gamma = gamma_initial * (1 - fraction)**alpha + regularization
    # tanh is positive for the validated arguments; underflow is checked explicitly.
    argument = math.tanh(beta * gamma / replicas)
    # Extreme invalid numerical scales should not generate infinite forces unnoticed.
    if argument <= 0:
        # Users can choose a representable schedule rather than obtaining NaN trajectories.
        raise ValueError("SBQA coupling underflow; adjust beta/regularization")
    # The logarithmic coupling strengthens as the transverse field decreases.
    return -math.log(argument) / (2 * beta)


# One explicit step permits discriminating equation/order tests independently of heuristic success.
def dynamics_step(graph, positions, momenta, pumps, step, steps, config, method):
    """Return copied next x,y,p and coupling for one symplectic-Euler CPU step.

    x/y/p are shape (n,R) finite arrays; p is GSB's per-coordinate parameter
    initialized to one. step=0..steps-1, steps>=1. config resolves dt,a0,c0,
    nonlinear_strength,beta,gamma_initial,alpha,regularization,replica_coupling.
    method bsb/dsb/gsb/sbqa. b/d use Goto2021 Eqs.(15)-(18), GSB uses
    published arXiv:2508.17655v5 Eqs.(3)-(7), SBQA Eqs.(5)-(8), with momentum-first
    then position updates and inelastic |x|>1 walls. Example A=0 GSB follows
    the linearly decreasing-p bSB convention (different schedule sampling from
    the legacy bSB endpoint convention is recorded). No input mutation;
    O((n+m)*R), no dense graph array. Coupling off is an explicit SBQA ablation.
    """
    # Own every updated state because old coordinates are required simultaneously in the force.
    x = np.array(positions, dtype=float, copy=True)
    # Momentum updates must not change the caller's previous trajectory frame.
    y = np.array(momenta, dtype=float, copy=True)
    # GSB's nonlinear control has one evolving parameter per node and replica.
    p = np.array(pumps, dtype=float, copy=True)
    # Reject swapped axes, mismatched replicas or invalid time indices before numerical updates.
    if x.ndim != 2 or x.shape[0] != graph.node_count or y.shape != x.shape or p.shape != x.shape or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(p)) or not 0 <= step < steps:
        # Numerical instability remains visible, never converted into a binary success.
        raise ValueError("invalid bifurcation state/time index")
    # Read an explicit integration interval and natural-frequency scale.
    dt, a0 = config["dt"], config["a0"]
    # Conventional b/d use a ramp including endpoints when more than one step is requested.
    fraction = step / max(1, steps - 1)
    # Distinct replicas occupy columns, not separate independently invoked solvers in SBQA.
    replicas = x.shape[1]
    # Only SBQA computes a physical replica-ring interaction.
    coupling = 0.0
    # Generalized SB evolves its own nonlinear per-coordinate bifurcation parameters first.
    if method == "gsb":
        # Eq.(7) has denominator M-m, which is at least one for every executed step.
        p -= (1 - config["nonlinear_strength"] * x*x) * p / (steps - step)
        # Eq.(3) uses the NEW p value but OLD positions in the weighted-neighbor force.
        force = -p*x + config["c0"] * ising_field(graph, x)
    # SBQA has 1/R factors in BOTH Hamilton equations, distinct from ordinary b/d.
    elif method == "sbqa":
        # Eq.(8) suppresses weak coordinates with the increasing 0.7*t/T threshold.
        activated = np.where(np.abs(x) > 0.7 * fraction, np.sign(x), 0.0)
        # Node interactions are sparse and scaled by c0/R, with h=0 for Max-Cut.
        force = -(a0 - fraction)*x / replicas + config["c0"] * ising_field(graph, activated) / replicas
        # The enabled schedule couples adjacent replicas on a PERIODIC replica ring.
        if config["replica_coupling"]:
            # Use the paper's regularized log-tanh schedule, not a guessed constant attraction.
            coupling = replica_coupling(fraction, replicas, config["beta"], config["gamma_initial"], config["alpha"], config["regularization"])
            # Axis one is replica; rolling axis zero would incorrectly couple different graph nodes.
            force += coupling * (np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1))
    # Ballistic uses continuous neighbors; discrete uses only their signs in the Ising force.
    elif method in {"bsb", "dsb"}:
        # Zero has sign zero DURING dSB force evaluation, as in the mathematical sign function.
        activated = x if method == "bsb" else np.sign(x)
        # Goto2021 momentum update uses old positions and linearly scheduled a(t).
        force = -(a0 - fraction)*x + config["c0"] * ising_field(graph, activated)
    # An unknown method must not silently reuse bSB equations under another published name.
    else:
        # Keep algorithm identity tied to its actual implementation.
        raise ValueError("unknown bifurcation dynamics")
    # Inelastic walls constrain finite trajectories; they must not hide an overflowed force.
    if not np.all(np.isfinite(force)):
        # A numerical failure is not a legitimate wall collision or successful binary extraction.
        raise FloatingPointError("bifurcation force overflow")
    # Momentum changes first; positions then use the NEW momentum (symplectic Euler).
    y += dt * force
    # SBQA's q-dot also carries the required 1/R factor from its Hamiltonian.
    x += dt * a0 * y / (replicas if method == "sbqa" else 1)
    # Check BEFORE clipping, since sign(infinity) and zeroed momentum could conceal unstable integration.
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        # Users must choose a representable step/scale rather than receive a false stable-state result.
        raise FloatingPointError("bifurcation integration overflow before walls")
    # Perfectly inelastic walls act only when a position strictly exceeds unit magnitude.
    outside = np.abs(x) > 1
    # Clamp the positions to their signed wall locations.
    x[outside] = np.sign(x[outside])
    # Wall collisions dissipate momentum on exactly the same coordinates.
    y[outside] = 0.0
    # Extreme settings must fail before NaNs can be hidden by sign extraction.
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(p)):
        # Stability is empirical within documented stepsizes, not guaranteed for arbitrary inputs.
        raise FloatingPointError("bifurcation numerical instability")
    # Return all owned next-state arrays and the actual coupling used for trajectory evidence.
    return x, y, p, coupling


# The controller records raw dynamic results separately from optional binary-polished hybrid output.
def solve_bifurcation(graph, config, seed, budget, initial_assignment=None, method="bsb"):
    """Run a CPU dynamical method under the common one-shot solver contract.

    graph sparse Graph; config defaults replicas=8,dt=.25,a0=1,c0=None (paper
    RMS normalization), nonlinear_strength=1 (GSB only), beta=1,Gamma0=1,
    alpha=1,regularization=1e-5,coupling=True (SBQA),polish=False. Unknown or
    inapplicable algorithm-specific keys fail. seed local RNG; budget max_work
    is integration steps, seconds cooperative; initial signs initialize replica
    zero near +/-0.1 and remain an independently retained incumbent. Other
    replicas initialize independently near zero. Return shared result plus raw
    final-replica cut and optional polished cut; no caller mutation/files.
    O(n*R+m) memory; CPU O(steps*m*R). SBQA replicas interact, not independent
    restarts. GSB and SBQA auto-tuning/GPU benchmarks are not reproduced.

    Example: solve_bifurcation(g,{'replicas':3},4,{'seconds':2,'max_work':30},method='sbqa').
    References: published GSB Eqs.(3)-(7), SBQA Eqs.(5)-(8), b/d Goto2021 Methods.
    """
    # Measure actual initialization, integration and optional polishing work.
    started = perf_counter()
    # Common numerical controls apply to all four local CPU formulations.
    defaults = {"replicas": 8, "dt": 0.25, "a0": 1.0, "c0": None, "polish": False}
    # GSB has its own published nonlinear per-coordinate control parameter.
    if method == "gsb":
        # A=0 is a meaningful ablation against a matching linearly scheduled bSB step.
        defaults["nonlinear_strength"] = 1.0
    # Replica schedule parameters apply only to SBQA, never silently to another SB family member.
    if method == "sbqa":
        # The additive epsilon is exactly the regularization identified in the paper.
        defaults.update({"beta": 1.0, "gamma_initial": 1.0, "alpha": 1.0, "regularization": 1e-5, "replica_coupling": True})
    # Reject irrelevant settings rather than suggesting all SB variants are interchangeable.
    cfg = settings(config, defaults)
    # Replica count is explicitly limited to protect memory on large sparse graphs.
    if type(cfg["replicas"]) is not int or not 1 <= cfg["replicas"] <= 64 or (method == "sbqa" and cfg["replicas"] < 2):
        # SBQA needs at least two actual interacting trajectories.
        raise ValueError("replicas must be 1..64, or 2..64 for SBQA")
    # Explicit positive finite numerical scales define a meaningful integration step.
    if any(not math.isfinite(cfg[key]) or cfg[key] <= 0 for key in ("dt", "a0")) or type(cfg["polish"]) is not bool:
        # A negative time step or ambiguous hybrid flag is a configuration error.
        raise ValueError("invalid dt/a0/polish")
    # This simple control follows the paper's a0=1 normalization, not an undocumented generalized schedule.
    if cfg["a0"] != 1.0:
        # Other frequency/ramp conventions require a separate documented derivation.
        raise ValueError("this published normalization requires a0=1")
    # GSB's feedback strength may be zero but cannot be negative/nonfinite.
    if method == "gsb" and (not math.isfinite(cfg["nonlinear_strength"]) or cfg["nonlinear_strength"] < 0):
        # Expose the allowed physical-control convention explicitly.
        raise ValueError("nonlinear_strength must be finite and nonnegative")
    # Validate SBQA schedules even when a zero-work budget prevents executing a step.
    if method == "sbqa":
        # This independent schedule evaluation catches invalid beta/Gamma/alpha/epsilon.
        replica_coupling(0.0, cfg["replicas"], cfg["beta"], cfg["gamma_initial"], cfg["alpha"], cfg["regularization"])
        # An ablation must be an explicit Boolean rather than a truthy arbitrary object.
        if type(cfg["replica_coupling"]) is not bool:
            # Otherwise a user could believe coupling was off when it was accidentally enabled.
            raise ValueError("replica_coupling must be bool")
    # RMS scale counts each symmetric matrix entry twice while storing each edge only once.
    squared_sum = 2 * math.fsum(weight*weight for i, j, weight in graph.edges)
    # c0=.5/(Jrms*sqrt(n))=.5*sqrt(n-1)/sqrt(sum_ij J_ij**2).
    automatic_scale = 0.0 if squared_sum == 0 else 0.5 * math.sqrt(graph.node_count - 1) / math.sqrt(squared_sum)
    # Record the actual numerical scale, including the explicit zero-field policy for an empty graph.
    cfg["c0"] = automatic_scale if cfg["c0"] is None else cfg["c0"]
    # A supplied coupling scale must remain finite and nonnegative.
    if not math.isfinite(cfg["c0"]) or cfg["c0"] < 0:
        # Never turn an invalid scale into a graph sign reversal.
        raise ValueError("c0 must be finite and nonnegative")
    # All state initialization and integration use a solve-local reproducible stream.
    rng = np.random.default_rng(seed)
    # The deadline validates work/time limits before allocating numerical state.
    deadline = deadline_from(budget)
    # GSB uses published random +/-0.1 positions; b/d/SBQA use small independent uniform coordinates.
    x = rng.choice(np.array([-0.1,0.1]), size=(graph.node_count,cfg["replicas"])) if method=="gsb" else rng.uniform(-0.1, 0.1, size=(graph.node_count, cfg["replicas"]))
    # GSB's published initial momentum is zero; b/d/SBQA use small symmetric random momentum.
    y = np.zeros_like(x) if method == "gsb" else rng.uniform(-0.1, 0.1, size=x.shape)
    # Each GSB trajectory owns its own per-node parameter, initialized at one.
    pumps = np.ones_like(x)
    # Warm signs genuinely affect replica zero's continuous starting state.
    if initial_assignment is not None:
        # Validation supplies owned +/-1 signs before embedding at small signed amplitude.
        warm = starting_signs(graph, rng, initial_assignment)
        # Other replicas remain independent fresh initializations rather than copies of the incumbent.
        x[:, 0] = 0.1 * warm
    # No supplied incumbent means there is no claimed warm-start effect.
    else:
        # None is retained as an explicit absence until raw final states are extracted.
        warm = None
    # Work counts actual completed integration steps, not nominal scheduled frames.
    completed = 0
    # Only small trajectory slices are retained, even on n=100000.
    history = []
    # max_work defines the schedule length and its numerical integration work limit.
    steps = budget.get("max_work", 10000)
    # The explicit loop permits checking time between expensive sparse field multiplications.
    for step in range(steps):
        # An interrupted schedule is not silently continued with a reset clock.
        if perf_counter() >= deadline:
            # Final extraction uses the actual current state at interruption.
            break
        # Execute the selected method's verified equations with copied old/new state ownership.
        x, y, pumps, coupling = dynamics_step(graph, x, y, pumps, step, steps, cfg, method)
        # A finished step consumes one actual work unit.
        completed += 1
        # Sample at most one hundred small frames for precise observed trajectory figures.
        if step % max(1, steps // 100) == 0 or step == steps - 1:
            # These are actual node/replica coordinates, not synthetic performance trajectories.
            history.append({"step": step, "fraction": step / max(1, steps - 1), "coupling": coupling,
                            "positions_first_nodes_replicas": x[:min(4, graph.node_count), :min(2, cfg["replicas"])].tolist(),
                            "pumps_first_nodes_replicas": pumps[:min(4, graph.node_count), :min(2, cfg["replicas"])].tolist()})
    # Zero continuous coordinates are explicitly mapped to +1 at final binary extraction.
    samples = np.where(x >= 0, 1, -1).astype(np.int8)
    # Independently rescore all final replicas using the original graph, not Ising energy signs.
    raw_values = [cut_value(graph, samples[:, replica]) for replica in range(cfg["replicas"])]
    # Raw output is the strongest final replica; it is distinct from any supplied incumbent.
    raw_index = int(np.argmax(raw_values))
    # Own raw labels before optional polishing modifies a separate vector.
    raw = samples[:, raw_index].copy()
    # Retain a stronger supplied assignment rather than overwriting it with a worse dynamic result.
    best = warm.copy() if warm is not None and cut_value(graph, warm) >= raw_values[raw_index] else raw.copy()
    # Polishing is an explicit hybrid with its own separate work counter.
    polish_flips = 0
    # Disabled-by-default polishing leaves pure dynamical results identifiable.
    if cfg["polish"]:
        # Apply optional local search to the raw solver result, not a hidden unrelated incumbent.
        polished = raw.copy()
        # Fresh gain calculation protects against any continuous/discrete convention mismatch.
        gains = compute_flip_gains(graph, polished)
        # A finite extra cap and the same deadline bound the hybrid tail.
        for iteration in range(min(graph.node_count, steps)):
            # Do not spend unbounded work after integration or ignore time during postprocessing.
            if perf_counter() >= deadline or gains.max() <= 1e-10:
                # The raw and supplied assignments remain available if polish cannot proceed.
                break
            # This is the original strictly improving best-single-flip polishing rule.
            flip_node(graph, polished, gains, int(np.argmax(gains)))
            # Record actual extra hybrid work independently of integration steps.
            polish_flips += 1
        # Select only a directly recomputed strict improvement over the retained incumbent.
        if cut_value(graph, polished) > cut_value(graph, best):
            # Copy so no working buffer aliases the returned retained state.
            best = polished.copy()
    # Without polishing, a separate null field avoids suggesting that hybrid work occurred.
    else:
        # Keep raw labels for explicit raw/polished reporting without changing them.
        polished = raw.copy()
    # No dynamical method supplies a certified global upper bound.
    result = result_record(method, graph, cfg, seed, budget, started, best,
                           status="time_limit" if perf_counter() >= deadline else "completed",
                           reason="time_limit" if perf_counter() >= deadline else "integration_steps",
                           counters={"integration_steps": completed, "replicas": cfg["replicas"], "polish_flips": polish_flips},
                           history=history, implementation="project-sparse-CPU/" + method + "-primary-equations-v1")
    # Preserve the raw binary labels as well as their value so future hybrid comparisons can be independently rescored.
    result.update({"raw_assignment": raw.tolist(), "raw_cut": raw_values[raw_index],
                   "polished_cut": cut_value(graph, polished) if cfg["polish"] else None,
                   "hybrid": cfg["polish"], "final_replica_cuts": raw_values,
                   "replica_semantics": "interacting_periodic_ring" if method == "sbqa" and cfg["replica_coupling"] else "independent"})
    # The final retained cut may come from a stronger supplied incumbent, which is explicitly separate from raw output.
    return result
