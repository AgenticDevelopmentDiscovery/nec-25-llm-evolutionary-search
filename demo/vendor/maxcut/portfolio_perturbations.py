"""Explicit project perturbations and subset choices; no hidden solver policy changes."""

# Finite angular/strength checks use mathematical units rather than flip percentages.
import math
# NumPy owns sampled node indices and copied sign/angle state.
import numpy as np
# Reuse the settled validation and canonical angle wraparound behavior.
from bm_solver import perturb_angles, validate_signs


# A subset selection is meaningful for binary repair and selected-angle perturbation alike.
def select_subset(graph, signs, count, rng, rule="uniform"):
    """Return unique node indices for uniform/connected/violated/mixed selection.

    graph is sparse Graph; signs shape n +/-1; count integer 0..n; rng local
    Generator. rule defaults uniform; mixed randomly chooses one of the other
    three rules. Connected grows BFS from a random root, filling other components
    if necessary (documented disconnected fallback). Violated uses incident
    abs(weight) on unsatisfied preferences; all-zero scores fall back to uniform.
    Example a +2 edge with equal signs weights both endpoints. No mutation;
    O(n+m) work/storage, no dense matrix or optimization is performed.
    """
    # Validate owned labels before using graph endpoints as vector indices.
    checked = validate_signs(signs, graph.node_count)
    # Enforce integer cardinality rather than silently clipping a user's neighborhood size.
    if type(count) is not int or not 0 <= count <= graph.node_count:
        # The controller can explicitly choose min(requested,n) when that is its documented policy.
        raise ValueError("subset count must be integer in [0,n]")
    # Selection rules are explicit method choices, not arbitrary callback implementations.
    if rule not in {"uniform", "connected", "violated", "mixed"}:
        # Unknown rules must not be replaced by an unintended random selection.
        raise ValueError("unknown subset selection rule")
    # Empty subsets are useful for exact boundary-case validation.
    if count == 0:
        # Return owned integer indices with no random draw.
        return np.array([], dtype=np.int64)
    # A mixed policy selects a rule once per neighborhood, not a changing rule per node.
    if rule == "mixed":
        # The explicit three-way mixture has equal probabilities.
        rule = str(rng.choice(["uniform", "connected", "violated"]))
    # Independent uniformly sampled nodes need no adjacency traversal.
    if rule == "uniform":
        # Sampling without replacement enforces the requested unique release set.
        return rng.choice(graph.node_count, size=count, replace=False)
    # Region selection follows actual graph edges and preserves original node IDs.
    if rule == "connected":
        # Begin a reproducible random component exploration.
        selected = [int(rng.integers(graph.node_count))]
        # Membership memory avoids repeated nodes on cyclic graphs.
        seen = set(selected)
        # An integer queue cursor makes BFS linear without O(n) front deletions.
        cursor = 0
        # Grow until the requested cardinality, or fill another component if the first is exhausted.
        while len(selected) < count:
            # Exhaustion on a disconnected graph needs a documented new-component seed.
            if cursor == len(selected):
                # A single uniform fill keeps even an all-isolated graph linear in n.
                remaining = [i for i in range(graph.node_count) if i not in seen]
                # Disconnected fallback is a union of the explored component and uniformly selected remaining nodes.
                selected.extend(rng.choice(remaining, size=count - len(selected), replace=False).tolist())
                # No further BFS is needed once the requested cardinality is reached.
                break
            # The next queued node supplies a genuine adjacent frontier.
            node = selected[cursor]
            # Advance ownership of this queue entry exactly once.
            cursor += 1
            # Random frontier ordering avoids a fixed graph-file-order directional bias.
            neighbors = rng.permutation([j for j, weight in graph.neighbors[node]])
            # Stop growing as soon as the requested number of released coordinates is reached.
            for neighbor in neighbors:
                # Unseen coordinates can be appended while room remains.
                if int(neighbor) not in seen and len(selected) < count:
                    # Store ordinary original node IDs for later serialization.
                    selected.append(int(neighbor))
                    # Prevent a cycle from adding this vertex again.
                    seen.add(int(neighbor))
        # Return a new array rather than exposing a controller-owned list.
        return np.asarray(selected, dtype=np.int64)
    # Violation scores measure weighted unsatisfied preferences, not just uncut positive edges.
    scores = np.zeros(graph.node_count, dtype=float)
    # Each violated signed edge contributes its magnitude to both incident nodes.
    for i, j, weight in graph.edges:
        # Positive weights prefer opposite signs; negative weights prefer equal signs.
        violated = (weight > 0 and checked[i] == checked[j]) or (weight < 0 and checked[i] != checked[j])
        # Zero edges create neither a preference nor a spurious selection weight.
        if violated:
            # Each endpoint is a meaningful possible release or perturbation target.
            scores[i] += abs(weight)
            # Symmetric incidence preserves the graph's undirected interpretation.
            scores[j] += abs(weight)
    # Weighted choice without replacement requires enough strictly positive probabilities.
    positive = np.flatnonzero(scores > 0)
    # Select all possible violation-guided coordinates before any documented uniform fill.
    guided_count = min(count, len(positive))
    # An entirely satisfied graph has no guided nodes, so start with an empty subset.
    selected = [] if not guided_count else rng.choice(positive, size=guided_count, replace=False, p=scores[positive] / scores[positive].sum()).tolist()
    # If few nodes touch violations, fill the rest without duplicates rather than inventing violation weights.
    if len(selected) < count:
        # Build a single membership set rather than reconstructing it for every remaining node.
        chosen = set(selected)
        # Build the remaining original indices explicitly in one scan.
        remaining = [node for node in range(graph.node_count) if node not in chosen]
        # Uniform completion also handles the all-satisfied fallback.
        selected.extend(rng.choice(remaining, size=count - len(selected), replace=False).tolist())
    # Return an owned release set, leaving signs and graph unchanged.
    return np.asarray(selected, dtype=np.int64)


# Binary perturbations change labels, whereas BM perturbations change angles without forcing label changes.
def perturb_binary(graph, signs, count, rng, rule="uniform"):
    """Copy signs and flip selected unique nodes; return (owned signs,indices).

    Arguments follow select_subset; count is nodes, not radians. Example
    signs=[1,1], count=2 produces [-1,-1], possibly an equal complementary cut.
    No input mutation; O(n+m) selection worst case, O(count) actual flips.
    This is a project perturbation for future experiments, not a claimed BLS
    operator unless the calling controller actually uses the paper's rules.
    """
    # Owned validation prevents an in-place update from modifying the caller's incumbent.
    candidate = validate_signs(signs, graph.node_count)
    # The same explicit rule vocabulary supports random nodes, regions or weighted violations.
    nodes = select_subset(graph, candidate, count, rng, rule)
    # Each selected node flips once because the release list has no duplicates.
    candidate[nodes] *= -1
    # Return actual affected IDs so experiment evidence can identify the applied perturbation.
    return candidate, nodes


# Selected angular noise reuses the settled all-angle helper's correct modulo policy.
def perturb_selected_angles(graph, angles, signs, count, rng, scale=0.35, rule="uniform"):
    """Copy angles, add uniform [-scale,scale] only on selected nodes, return angles,IDs.

    angles is shape n finite radians; signs are current +/-1 labels for weighted
    selection; count nodes; rng local Generator; scale radians in [0,pi].
    rule='connected' gives region angular perturbation. Example count=0 leaves
    all angles unchanged; count=n matches independent all-angle noise in law.
    The settled helper wraps into [0,2*pi). No graph/sign/angle mutation;
    O(n+m) selection memory, no allocation of n*n graph matrices.
    """
    # Own numerical angular storage before selecting or changing coordinates.
    checked = np.array(angles, dtype=float, copy=True)
    # Shape and finiteness follow the settled BM vector-validation requirements.
    if checked.shape != (graph.node_count,) or not np.all(np.isfinite(checked)):
        # Invalid coordinates cannot be repaired by randomly changing a subset of them.
        raise ValueError("angles must be a finite length-n vector")
    # A selected perturbation must use the same supported angular range as full BM noise.
    if not math.isfinite(scale) or not 0 <= scale <= math.pi:
        # Reject invalid radians instead of guessing a percentage or degree conversion.
        raise ValueError("angular scale must be finite in [0,pi]")
    # The rule determines affected coordinates, without changing their existing angles yet.
    nodes = select_subset(graph, signs, count, rng, rule)
    # Empty subsets preserve every stored coordinate and consume no angular-noise draws.
    if len(nodes):
        # The settled helper draws one Uniform(-scale,scale) radian offset per selected coordinate and wraps it.
        checked[nodes] = perturb_angles(checked[nodes], rng, scale=scale)
    # Unselected coordinates remain byte-for-byte unchanged in the independently owned array.
    return checked, nodes


# An explicit adaptive-strength function is available without altering any settled BM defaults.
def adaptive_strength(strength, stagnation, improved, minimum=0.05, maximum=1.0, multiplier=1.5, threshold=5):
    """Return (next strength,next stagnation) under the documented project rule.

    strength/minimum/maximum share caller units (e.g. radians); stagnation is
    nonnegative integer; improved bool; multiplier>=1; threshold positive int.
    Improvement resets to minimum and zero. Otherwise increment counter; at
    threshold multiply strength capped at maximum and reset the counter.
    Example (.2,4,False,.05,1,1.5,5)->(.3,0). No mutation/files; O(1).
    This is a project-specific extension, not attributed to a published method.
    """
    # Numerical bounds define what an increased/reset strength actually means.
    if not all(math.isfinite(v) for v in (strength, minimum, maximum, multiplier)) or not 0 <= minimum <= strength <= maximum or multiplier < 1:
        # Undefined or decreasing multiplicative schedules are rejected explicitly.
        raise ValueError("invalid adaptive strength range/multiplier")
    # Counters and reset flags must have their documented discrete types.
    if type(stagnation) is not int or stagnation < 0 or type(threshold) is not int or threshold < 1 or type(improved) is not bool:
        # Reject an ambiguous state transition before returning a new schedule state.
        raise ValueError("invalid stagnation, threshold or improvement flag")
    # A real retained improvement resets strength rather than accumulating stale stagnation.
    if improved:
        # The returned pair owns no mutable state and can be recorded directly.
        return minimum, 0
    # A failed attempt consumes one stagnation event.
    count = stagnation + 1
    # Increase only at the declared threshold, retaining explicit maximum protection.
    return (min(multiplier * strength, maximum), 0) if count >= threshold else (strength, count)
