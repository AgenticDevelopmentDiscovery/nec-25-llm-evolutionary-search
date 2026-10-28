"""Teaching rank-two Max-Cut: settled Steps 1–9 and explicit Steps 10–13 extensions."""

# SHA-256 supplies stable graph and attempt identities, independent of Python hash randomization.
import hashlib
# JSON serializes seed fields unambiguously, including instance keys containing punctuation.
import json
# perf_counter measures attempt durations without imposing a time-based stopping rule.
from time import perf_counter

# Scalar trigonometry uses radians and needs only the standard library.
import math
# Version information makes the recorded reproducibility scope explicit.
import platform
# Dataclasses provide a small graph record; field excludes derived neighbors from its constructor.
from dataclasses import dataclass, field
# Integral recognizes Python and NumPy integers without accepting fractional counts.
from numbers import Integral
# Path represents filenames, such as Path("instances/public/rand_pos_20_s2.txt").
from pathlib import Path

# NumPy supplies one-dimensional arrays and a local random generator; no other package is needed.
import numpy as np


# The decorator supplies Graph's constructor from its declared fields.
@dataclass
# One graph record owns copied edges and the derived symmetric neighbor lists.
class Graph:
    """Step 1: fixed undirected graph, stored in O(n+m) space.

    Args: node_count is a positive int (e.g. 3); edges is an iterable of
    (0-based int i, int j, finite float w), e.g. [(0,1,0.5)].
    neighbors is derived, not a constructor argument: neighbors[0]=[(1,0.5)].
    Construction copies edges and creates new neighbor lists in O(n+m).
    Treat all fields as read-only after construction. Weights never depend on signs.
    Graph(2, [(0,1,-4)]) describes one negative edge, counted once in F.
    """

    # The original node order fixes every vector's length and indexing.
    node_count: int
    # Each undirected edge occurs exactly once here, for objective evaluation.
    edges: list[tuple[int, int, float]]
    # field(init=False) builds this derived attribute later, rather than accepting inconsistent input.
    neighbors: list[list[tuple[int, float]]] = field(init=False)

    # The dataclass calls this validator immediately after assigning constructor arguments.
    def __post_init__(self):
        """Step 1: validate self (Graph) and replace its input edges with owned copies.

        No other arguments; returns None. Mutates only this newly constructed
        record, not the supplied edge list. Example: Graph(3, [(1,2,-0.25)])
        gets neighbors [[], [(2,-0.25)], [(1,-0.25)] in O(n+m).
        """
        # Reject booleans as counts even though Python considers bool an integer subtype.
        if isinstance(self.node_count, bool) or not isinstance(self.node_count, Integral) or self.node_count < 1:
            # ValueError identifies an invalid graph rather than guessing its intended size.
            raise ValueError("node_count must be a positive integer")
        # Convert a NumPy integer count, for example np.int64(3), into a plain Python int.
        self.node_count = int(self.node_count)
        # The empty list will own normalized copies of all accepted edges.
        owned_edges = []
        # The outer list preserves the original node order.
        self.neighbors = []
        # range(n) yields 0,...,n-1; each node gets a distinct empty neighbor list.
        for node in range(self.node_count):
            # append adds one new list, avoiding aliasing between isolated nodes.
            self.neighbors.append([])
        # set() stores unordered endpoint pairs so reversed duplicates are also rejected.
        seen = set()
        # enumerate starts edge numbering at 1 to make constructor errors readable.
        for edge_number, edge in enumerate(self.edges, start=1):
            # Each input record must have exactly two endpoints and one weight.
            if len(edge) != 3:
                # The edge number identifies the malformed record.
                raise ValueError(f"edge {edge_number}: expected (i, j, weight)")
            # Unpacking names the fixed endpoints and the supplied weight separately.
            node_i, node_j, weight = edge
            # Validate each endpoint before using it as a list index.
            for endpoint in (node_i, node_j):
                # bool and fractional endpoint values are not accepted as node indices.
                if isinstance(endpoint, bool) or not isinstance(endpoint, Integral) or not 0 <= endpoint < self.node_count:
                    # The message explicitly describes the internal, zero-based convention.
                    raise ValueError(f"edge {edge_number}: endpoints must be integers in [0, n-1]")
            # Self-loops have no supported interpretation in this first implementation.
            if node_i == node_j:
                # Reject rather than silently discarding an input edge.
                raise ValueError(f"edge {edge_number}: self-loop")
            # float preserves fractional weights, such as -0.25, instead of truncating them to integers.
            weight = float(weight)
            # isfinite rejects both NaNs and positive/negative infinity.
            if not math.isfinite(weight):
                # Invalid weights cannot enter either objective.
                raise ValueError(f"edge {edge_number}: weight must be finite")
            # min/max give (smaller, larger), so (0,1) and (1,0) have the same duplicate key.
            pair = (min(node_i, node_j), max(node_i, node_j))
            # Set membership detects an already supplied undirected edge.
            if pair in seen:
                # There is no implicit merging policy for duplicate weights.
                raise ValueError(f"edge {edge_number}: duplicate unordered edge {pair}")
            # add remembers this accepted pair for later records.
            seen.add(pair)
            # Keep the original endpoint ordering; the tuple itself is a new owned record.
            owned_edges.append((int(node_i), int(node_j), weight))
            # append supplies the neighbor of i with the same fixed real weight.
            self.neighbors[node_i].append((int(node_j), weight))
            # Undirected adjacency requires the reverse entry as well.
            self.neighbors[node_j].append((int(node_i), weight))
        # Replace the input edge container only after validation succeeds.
        self.edges = owned_edges


# This helper centralizes finite, nonnegative numerical-threshold validation.
def _nonnegative(value, name):
    """Steps 5–8: validate a scalar tolerance without mutation.

    value is a real scalar, e.g. 1e-12; name is an error-label str, e.g.
    'field_rtol'. Return its finite nonnegative float in O(1); otherwise raise
    ValueError. Example: _nonnegative(0, 'sweep_atol') returns 0.0.
    """
    # Conversion accepts ordinary Python/NumPy real scalars.
    result = float(value)
    # NaN comparisons are insufficient, so finiteness is checked explicitly.
    if not math.isfinite(result) or result < 0:
        # Include the caller's setting name in the error.
        raise ValueError(f"{name} must be finite and nonnegative")
    # Return the checked scalar for use in inequalities.
    return result


# Objectives and iterative routines use this helper to validate vector dimensions and ownership.
def _vector(values, count, name):
    """Steps 2–8: copy a finite real vector and validate its shape.

    values is a sequence/array, e.g. [0, math.pi]; count is its expected int
    length, e.g. 2; name is a str for errors. Return an owned float64 array
    of shape (count,), without mutating input, in O(count) time/space.
    Example: _vector([1,-1],2,'signs') returns array([1.,-1.]).
    """
    # array(..., dtype=float, copy=True) creates owned floating storage, not a view of caller memory.
    result = np.array(values, dtype=float, copy=True)
    # A column matrix (n,1) is deliberately different from the required flat vector (n,).
    if result.shape != (count,):
        # Report both expected and received shapes.
        raise ValueError(f"{name} must have shape ({count},), got {result.shape}")
    # isfinite acts elementwise; all reduces the boolean vector to one validation decision.
    if not np.all(np.isfinite(result)):
        # Nonfinite angles or signs cannot be interpreted geometrically.
        raise ValueError(f"{name} must contain only finite real values")
    # The new array can safely become working storage.
    return result


# Binary signs have a stronger public-interface contract than general real vectors.
def validate_signs(signs, node_count):
    """Steps 2/9: return an owned int8 vector of valid signs.

    signs is a flat sequence/array, e.g. [1,-1,1]; node_count is int n=3.
    Return shape-(n,) int8 values in {-1,+1}, without input mutation, in O(n).
    This validates membership, not integrality by rounding: [1,0.9] is invalid.
    Example: validate_signs([1,-1],2) returns independent binary storage.
    """
    # Validate shape/finiteness and copy the input before checking membership.
    result = _vector(signs, node_count, "signs")
    # Visit each entry explicitly so no integer conversion can hide invalid values.
    for value in result:
        # Only the two prescribed values are acceptable.
        if value != -1 and value != 1:
            # Zero and fractional labels are not valid assignments.
            raise ValueError("signs must contain only -1 or +1")
    # astype returns a new array; int8 is sufficient to store -1 and +1 exactly.
    return result.astype(np.int8)


# File loading is independent of optimization and does not change official files.
def load_graph(path):
    """Step 1: read exactly m weighted edges and convert 1-based IDs to 0-based.

    path is str/Path, e.g. 'instances/public/rand_pos_20_s2.txt'. Return Graph
    with copied edges/adjacency; no input mutation or writing. Header '2 1'
    followed by '1 2 -0.5' becomes Graph(2, [(0,1,-0.5)]). O(n+m) storage/time.
    Blank trailing lines are allowed; missing/extra nonblank records are errors.
    """
    # Path(path) normalizes a string or existing Path without reading anything yet.
    source = Path(path)
    # open in UTF-8 text-read mode closes the file automatically when the with block ends.
    with source.open("r", encoding="utf-8") as stream:
        # readline reads the header only; split removes whitespace around its two fields.
        header = stream.readline().split()
        # The exact header shape prevents ambiguous interpretation of extra fields.
        if len(header) != 2:
            # Include the path and line number in parsing errors.
            raise ValueError(f"{source}: line 1: expected n m")
        # Catch numeric conversion errors to provide useful file context.
        try:
            # int('3') returns 3 but int('3.5') fails instead of silently truncating.
            node_count = int(header[0])
            # The second integer is the exact number of edge records to read.
            edge_count = int(header[1])
        # Malformed counts are reported as a graph-file error.
        except ValueError as error:
            # Exception chaining retains the original conversion detail.
            raise ValueError(f"{source}: line 1: n and m must be integers") from error
        # Positive n supports isolated nodes; m=0 supports an empty edge set.
        if node_count < 1 or edge_count < 0:
            # Negative counts cannot describe a graph.
            raise ValueError(f"{source}: require n > 0 and m >= 0")
        # Collect input records before Graph validates endpoints and duplicates.
        edges = []
        # range(m) visits exactly the advertised number of edge lines.
        for edge_index in range(edge_count):
            # The header occupies line 1, so the first edge is line 2.
            line_number = edge_index + 2
            # An EOF or blank record has too few fields and is rejected below.
            fields = stream.readline().split()
            # Require two endpoint fields and one weight field, with no hidden extras.
            if len(fields) != 3:
                # The expected record format is included in the error.
                raise ValueError(f"{source}: line {line_number}: expected i j w")
            # Group conversion errors under the offending input line.
            try:
                # Subtract one once: external node 1 becomes internal index 0.
                node_i = int(fields[0]) - 1
                # Apply the same conversion to the other endpoint.
                node_j = int(fields[1]) - 1
                # float preserves real signed and fractional weights.
                weight = float(fields[2])
            # Both endpoints and weight must be parseable numbers.
            except ValueError as error:
                # The source record remains available by its path and line number.
                raise ValueError(f"{source}: line {line_number}: invalid endpoint or weight") from error
            # Graph will validate ranges, self-loops, duplicate pairs, and weight finiteness.
            edges.append((node_i, node_j, weight))
        # Any remaining nonblank line is an extra edge or unsupported extra data.
        for trailing_line in stream:
            # strip returns an empty string for whitespace-only trailing lines.
            if trailing_line.strip():
                # Reject a mismatch rather than ignoring part of the problem.
                raise ValueError(f"{source}: extra data after {edge_count} edges")
    # Contextualize constructor validation errors with the filename too.
    try:
        # Graph creates symmetric neighbor lists while keeping each edge once for F.
        return Graph(node_count, edges)
    # Re-raise semantic errors with their file source.
    except (ValueError, TypeError) as error:
        # This preserves the original self-loop/duplicate/range message.
        raise ValueError(f"{source}: {error}") from error


# The discrete evaluator is deliberately independent of the continuous objective.
def cut_value(graph, signs):
    """Step 2: compute F(s)=sum(w for crossing edges), counting edges once.

    graph is Graph, e.g. one +4 edge; signs is shape-(n,) ±1 data, e.g.
    [1,-1]. Return finite float 4.0 in that example. Inputs are not mutated.
    Validation costs O(n); the edge sum costs O(m), with O(n+m) temporary space.
    Fixed weights are retained; same-label edges contribute zero.
    """
    # Validate binary membership at this public evaluation boundary.
    checked = validate_signs(signs, graph.node_count)
    # Terms are stored for math.fsum, which reduces cancellation error in signed sums.
    terms = []
    # The edge list avoids double-counting symmetric neighbor entries.
    for node_i, node_j, weight in graph.edges:
        # Crossing is determined by labels, not by the sign of the fixed weight.
        if checked[node_i] != checked[node_j]:
            # A negative crossing edge contributes its negative weight unchanged.
            terms.append(weight)
    # fsum([5.,3.]) returns 8.0, summing real terms with improved accuracy.
    value = math.fsum(terms)
    # Overflow must not result in an invalid retained or written score.
    if not math.isfinite(value):
        # A failed numerical evaluation is not an optimization result.
        raise FloatingPointError("direct cut is not finite")
    # This recomputed value is the source of truth for candidate selection.
    return value


# The relaxed evaluator shares input weights but never calls the discrete evaluator.
def relaxed_value(graph, angles):
    """Step 3: R(theta)=0.5*sum(w*(1-cos(theta_i-theta_j))).

    graph is Graph; angles is shape-(n,) finite radians, e.g. [0,math.pi]
    on a +4 edge gives 4.0. Return finite float; copy validation does not
    mutate input. O(n+m) time/temporary space. General angles are not signs;
    theta=(0,2*pi/3,4*pi/3) on a unit triangle gives R=2.25, not cut 2.
    """
    # Copy and validate one radian-valued angle per node.
    checked = _vector(angles, graph.node_count, "angles")
    # Accurate summation also matters when relaxed terms have mixed signs.
    terms = []
    # Every undirected edge has exactly one continuous contribution.
    for node_i, node_j, weight in graph.edges:
        # cos of the radian difference is the dot product of the two unit arrows.
        dot_product = math.cos(float(checked[node_i] - checked[node_j]))
        # The factor one half recovers the binary indicator at differences 0 or pi.
        terms.append(0.5 * weight * (1.0 - dot_product))
    # Reduce edge terms to one relaxed objective value, not a submitted score.
    value = math.fsum(terms)
    # Fail explicitly if floating arithmetic cannot represent the objective.
    if not math.isfinite(value):
        # A nonfinite relaxed value invalidates numerical progress comparisons.
        raise FloatingPointError("relaxed objective is not finite")
    # Return the measured R without replacing decreases by a cumulative maximum.
    return value


# Coordinate ascent queries only the incident neighbor list.
def weighted_neighbor_vector(graph, node, cosines, sines):
    """Step 5: compute h_i=sum_j w_ij*(cos(theta_j),sin(theta_j)).

    graph is Graph; node is valid 0-based int, e.g. 0; cosines/sines are
    synchronized finite shape-(n,) real caches. Caller validates caches once
    per ascent call. Return (h_x,h_y), two floats, without mutation, in
    O(degree(node)) time/space. For weights AB=2, AC=1 and B=(1,0), C=(0,1),
    weighted_neighbor_vector(graph,0,[1,1,0],[0,0,1]) returns (2.,1.).
    """
    # Collect horizontal terms separately from vertical terms for accurate sums.
    x_terms = []
    # The second list has the same degree-sized shape.
    y_terms = []
    # Each neighbor contributes its fixed weight times its current cached unit arrow.
    for neighbor, weight in graph.neighbors[node]:
        # float removes NumPy scalar wrappers before standard-library summation.
        x_terms.append(weight * float(cosines[neighbor]))
        # The vertical coordinate uses sine of that same neighbor's angle.
        y_terms.append(weight * float(sines[neighbor]))
    # fsum returns zero on an empty list, handling isolated nodes naturally.
    return math.fsum(x_terms), math.fsum(y_terms)


# A named coordinate kernel makes the exact geometry inspectable and testable.
def update_coordinate(graph, node, angles, cosines, sines, field_rtol=1e-12):
    """Step 5: point one unit arrow opposite its weighted neighbor field.

    graph is Graph; node is valid int i; angles/cosines/sines are independent,
    writable shape-(n,) floating arrays with synchronized radian/cos/sin values.
    field_rtol is a validated nonnegative relative threshold (e.g. 1e-12).
    This low-level kernel MUTATES only entry i of all three arrays; it returns
    bool updated. Caller supplies validated caches to avoid O(n) work per node.
    theta_i <- atan2(-h_y,-h_x) mod 2*pi; (2,1) gives 206.565 degrees.
    If |h| <= field_rtol*sum_j|w_ij|, return False unchanged. O(degree(i)).
    """
    # Compute h from the latest cached neighbor values, including earlier updates in this sweep.
    field_x, field_y = weighted_neighbor_vector(graph, node, cosines, sines)
    # hypot(2,1) returns sqrt(5), using a stable scalar Euclidean norm.
    field_norm = math.hypot(field_x, field_y)
    # Incident magnitudes set a scale even when positive and negative fields cancel.
    magnitudes = []
    # Scan only this node's neighbor list to form its weight scale.
    for neighbor, weight in graph.neighbors[node]:
        # abs(-3.0) returns 3.0 without changing the graph's negative weight.
        magnitudes.append(abs(weight))
    # fsum of an empty list is zero, so isolated-node thresholds are defined.
    incident_scale = math.fsum(magnitudes)
    # Both a zero field and one negligible relative to incident weights lack a reliable direction.
    if field_norm <= field_rtol * incident_scale:
        # Keeping the old arrow also prevents atan2(0,0) from choosing an arbitrary rotation.
        return False
    # atan2 takes y FIRST and x SECOND; negating both points opposite h.
    # Modulo tau=2*pi expresses the direction in [0,2*pi) radians.
    angles[node] = math.atan2(-field_y, -field_x) % math.tau
    # cos returns the new horizontal component of this single unit arrow.
    cosines[node] = math.cos(float(angles[node]))
    # sin updates the vertical component immediately, before the next node uses it.
    sines[node] = math.sin(float(angles[node]))
    # Report that a non-negligible field supplied an exact coordinate maximizer.
    return True


# One independent continuous optimization starts from the caller's single initialization.
def coordinate_ascent(graph, initial_angles, rng, max_sweeps=200,
                      field_rtol=1e-12, sweep_atol=1e-12, sweep_rtol=1e-9):
    """Steps 5–6: sequential exact coordinate sweeps with measured stopping.

    graph is Graph; initial_angles is shape-(n,) radians, e.g. [0,1,2];
    rng is a local np.random.Generator, e.g. np.random.default_rng(42), whose
    state IS advanced. max_sweeps is nonnegative int (200); field_rtol is
    relative field tolerance (1e-12); sweep_atol has weight units (1e-12),
    sweep_rtol is dimensionless (1e-9). Input angles are copied, never mutated.
    Return (owned angles, dict(initial_value, sweeps, stop_reason)). Each sweep
    records before/after/improvement/threshold. Stop when dR <= atol +
    rtol*max(|before|,|after|), or at the budget. No optimality certificate.
    A sweep costs O(n+m); history uses O(number_of_sweeps) scalars.
    """
    # Counts must be integers; zero deliberately permits a rounding-only diagnostic run.
    if isinstance(max_sweeps, bool) or not isinstance(max_sweeps, Integral) or max_sweeps < 0:
        # Fractional or negative sweep budgets cannot define a visit schedule.
        raise ValueError("max_sweeps must be a nonnegative integer")
    # Validate dimensionless field tolerance before passing it to the low-level kernel.
    field_rtol = _nonnegative(field_rtol, "field_rtol")
    # Absolute sweep stopping is expressed in objective/weight units.
    sweep_atol = _nonnegative(sweep_atol, "sweep_atol")
    # Relative sweep stopping scales with the measured objective, not graph size alone.
    sweep_rtol = _nonnegative(sweep_rtol, "sweep_rtol")
    # Copy the requested initialization, so optimization cannot overwrite caller memory.
    angles = _vector(initial_angles, graph.node_count, "initial_angles")
    # np.cos acts elementwise on shape (n,), returning a new horizontal cache of that shape.
    cosines = np.cos(angles)
    # np.sin similarly builds the synchronized vertical cache.
    sines = np.sin(angles)
    # Record R before the first coordinate update.
    initial_value = relaxed_value(graph, angles)
    # Sum magnitudes to bound cancellation-related floating error even when R is near zero.
    magnitudes = []
    # Each fixed edge contributes once to this roundoff scale.
    for node_i, node_j, weight in graph.edges:
        # The absolute value is used only for numerical checking.
        magnitudes.append(abs(weight))
    # fsum returns a nonnegative overall weight magnitude.
    weight_scale = math.fsum(magnitudes)
    # Only scalar sweep records are retained, not full angle vectors per step.
    history = {"initial_value": initial_value, "sweeps": [], "stop_reason": "max_sweeps"}
    # range(max_sweeps) executes the fixed budget unless the tolerance test stops earlier.
    for sweep_index in range(max_sweeps):
        # Re-evaluate R directly before this sweep, rather than trusting an incremental total.
        before = relaxed_value(graph, angles)
        # permutation(n) returns a shuffled array containing each node 0,...,n-1 exactly once.
        order = rng.permutation(graph.node_count)
        # Later nodes must see the immediately updated cosine/sine caches.
        for node in order:
            # Convert the permutation's NumPy integer and update this coordinate in place.
            update_coordinate(graph, int(node), angles, cosines, sines, field_rtol)
        # Measure the actual post-sweep objective; do not mask decreases.
        after = relaxed_value(graph, angles)
        # Subtraction gives the signed improvement, which may have tiny floating error.
        improvement = after - before
        # max chooses the larger absolute measured objective for the specified stopping scale.
        threshold = sweep_atol + sweep_rtol * max(abs(before), abs(after))
        # finfo(float).eps is machine epsilon; 64 eps times total weight is a roundoff allowance.
        roundoff = 64.0 * np.finfo(float).eps * max(weight_scale, abs(before), abs(after))
        # A decrease beyond roundoff indicates inconsistent updates or unusable arithmetic.
        if improvement < -roundoff:
            # Fail visibly rather than replacing history with a nondecreasing envelope.
            raise FloatingPointError(f"coordinate sweep decreased R by {improvement}, allowance {roundoff}")
        # append records the exact measurements and both numerical thresholds.
        history["sweeps"].append({"sweep": sweep_index + 1, "before": before,
                                  "after": after, "improvement": improvement,
                                  "stopping_threshold": threshold, "roundoff_allowance": roundoff})
        # A small full-sweep improvement is the explicit teaching stopping rule.
        if improvement <= threshold:
            # Distinguish convergence by the configured tolerance from exhausting the budget.
            history["stop_reason"] = "sweep_tolerance"
            # Stop only this continuous loop; rounding still runs afterward.
            break
    # Returning a further copy makes the ownership boundary explicit.
    return angles.copy(), history


# Hyperplane rounding converts continuous arrows into an actual binary candidate.
def round_angles(angles, direction_angle, projection_tolerance=1e-12):
    """Step 7: signs from projections onto a unit NORMAL r=(cos(alpha),sin(alpha)).

    angles is a nonempty flat finite radian vector, e.g. [0,2*pi/3,4*pi/3];
    direction_angle is finite alpha in radians (e.g. 0); projection_tolerance
    is dimensionless in [0,1), default 1e-12. Return owned shape-(n,) int8
    signs without input mutation, in O(n). Assign +1 for projection >= -tol:
    negative values within tol are boundary ties, also +1. Example alpha=0
    gives [1,-1,-1]. The dividing line x dot r=0 is perpendicular to r.
    """
    # Determine n from a general sequence before enforcing a flat shape.
    count = len(angles)
    # A candidate must have at least one node.
    if count < 1:
        # Empty input cannot form this project's positive-node-count graph assignment.
        raise ValueError("angles must be nonempty")
    # Validate and own the input angles without changing them.
    checked = _vector(angles, count, "angles")
    # float turns an ordinary numeric alpha into a scalar radian angle.
    direction_angle = float(direction_angle)
    # Nonfinite normals have no valid geometric direction.
    if not math.isfinite(direction_angle):
        # Reject before evaluating any trigonometric function.
        raise ValueError("direction_angle must be finite")
    # The tie tolerance measures unit-vector dot products, not edge weights.
    projection_tolerance = _nonnegative(projection_tolerance, "projection_tolerance")
    # A tolerance reaching one could call every unit projection a boundary tie.
    if projection_tolerance >= 1:
        # Keep the boundary neighborhood strictly smaller than the unit projection scale.
        raise ValueError("projection_tolerance must be less than 1")
    # ones(count,dtype=int8) creates one +1 default per node, including boundary ties.
    signs = np.ones(count, dtype=np.int8)
    # Enumerate returns each original node index and its own angle.
    for node, angle in enumerate(checked):
        # cos(theta-alpha) is the projection onto the NORMAL, not onto the boundary line.
        projection = math.cos(float(angle) - direction_angle)
        # Only reliably negative projections become -1; zero and near-zero projections stay +1.
        if projection < -projection_tolerance:
            # This writes an integer label, never an angle or a zero sign.
            signs[node] = -1
    # All entries are exactly one of the required two labels.
    return signs


# A fresh gain computation is independent of the incremental neighbor-update formula.
def compute_flip_gains(graph, signs):
    """Step 8: gain_i=s_i*sum_j w_ij*s_j, the increase from flipping only i.

    graph is Graph; signs is shape-(n,) ±1, e.g. [-1,1,1] on weights 5,3,1.
    Return shape-(n,) float64 [-6,-2,2] for that example. No mutation;
    O(n+m) time and O(n+max_degree) temporary storage. This recomputation
    guards against accumulated drift in the incremental update path.
    """
    # Binary validation copies signs before accessing the graph's adjacency.
    checked = validate_signs(signs, graph.node_count)
    # zeros creates one scalar gain slot per original node.
    gains = np.zeros(graph.node_count, dtype=float)
    # Every node has its own weighted neighbor sum.
    for node in range(graph.node_count):
        # The temporary terms list is at most this node's degree.
        terms = []
        # Each undirected neighbor is represented in this node's adjacency once.
        for neighbor, weight in graph.neighbors[node]:
            # int converts the label without changing the real edge weight.
            terms.append(weight * int(checked[neighbor]))
        # Multiplying by the current node sign gives the exact single-flip difference in real arithmetic.
        gains[node] = int(checked[node]) * math.fsum(terms)
    # Check all entries before using them for an argmax selection.
    if not np.all(np.isfinite(gains)):
        # A nonfinite gain cannot justify a move.
        raise FloatingPointError("flip gains are not finite")
    # This is fresh data, not a view into the signs vector.
    return gains


# The incremental kernel exposes the old-sign rule directly for teaching and tests.
def flip_node(graph, signs, gains, node):
    """Step 8: update one binary sign and only its affected cached gains.

    graph is Graph; signs is writable shape-(n,) int8, gains is synchronized
    shape-(n,) float64, node is valid int (e.g. C=2). Caller validates these
    low-level inputs. MUTATES signs/gains, returns None. On weights 5,3,1,
    signs [-1,1,1], gains [-6,-2,2], flipping 2 gives [-1,1,-1], [-4,-8,-2].
    Use OLD s_i in g_j <- g_j-2*w_ij*old_s_i*s_j; g_i <- -old_g_i.
    Cost O(degree(i)); the separate best-gain scan costs O(n).
    """
    # Save the sign before changing it, since every neighbor correction needs this OLD value.
    old_sign = int(signs[node])
    # The flipped coordinate's gain must be the negative of its previous gain.
    old_gain = float(gains[node])
    # Change only this node's label, preserving all other endpoint signs.
    signs[node] = -old_sign
    # Reversing the same move would undo its original improvement.
    gains[node] = -old_gain
    # Only incident neighbors' fields contain the changed label.
    for neighbor, weight in graph.neighbors[node]:
        # The OLD sign is essential: using signs[node] here would reverse the correction.
        gains[neighbor] = gains[neighbor] - 2.0 * weight * old_sign * int(signs[neighbor])


# Best-improvement local search is intentionally simple rather than tuned for huge graphs.
def local_search(graph, initial_signs, gain_tolerance=1e-10, verify_moves=False):
    """Step 8: polish a copied assignment until no fresh gain exceeds tolerance.

    graph is Graph; initial_signs is shape-(n,) ±1 (e.g. [-1,1,1]);
    gain_tolerance is finite nonnegative weight units (1e-10); verify_moves
    is bool False, or True for tiny examples' direct per-flip diagnostics.
    Return (owned signs, direct float cut, dict(accepted_flips, refreshes,
    moves)). moves is empty normally; verification stores only scalar records,
    never n-vectors. No input mutation. Example weights 5,3,1 gives cut 8.
    np.argmax selects the largest gain with smallest-index ties. Each accepted
    iteration costs O(n+degree(i)); verification adds O(n+m). Final gain refresh
    costs O(n+m). A local optimum need not be global.
    """
    # Validate/copy so the caller can retain its raw rounded assignment unchanged.
    signs = validate_signs(initial_signs, graph.node_count)
    # This is an absolute numerical move threshold, not an exact stationarity certificate.
    gain_tolerance = _nonnegative(gain_tolerance, "gain_tolerance")
    # Initialize gains independently from the current signs and fixed graph.
    gains = compute_flip_gains(graph, signs)
    # The history stays compact unless the caller explicitly requests tiny-case diagnostics.
    history = {"accepted_flips": 0, "refreshes": 0, "moves": []}
    # Continue until a freshly recomputed set of gains confirms termination.
    while True:
        # argmax returns the first maximum index, implementing smallest-node-index tie breaking.
        node = int(np.argmax(gains))
        # Apparent termination requires a fresh full gain calculation to remove drift.
        if gains[node] <= gain_tolerance:
            # Refresh ALL gains from the current signs before declaring a local stop.
            gains = compute_flip_gains(graph, signs)
            # Count full refreshes without storing additional vectors.
            history["refreshes"] += 1
            # Re-select the actual best fresh gain using the same deterministic tie rule.
            node = int(np.argmax(gains))
            # Only this fresh condition permits stopping.
            if gains[node] <= gain_tolerance:
                # Exit with no single-node gain larger than the stated threshold.
                break
        # Check this prospective move against its fresh incident field too.
        terms = []
        # Rebuilding one field costs O(degree(node)), not O(m).
        for neighbor, weight in graph.neighbors[node]:
            # Current labels, not cached gains, determine the move's actual mathematical gain.
            terms.append(weight * int(signs[neighbor]))
        # The fresh local formula avoids accepting a move whose cached gain drifted above threshold.
        fresh_gain = int(signs[node]) * math.fsum(terms)
        # A stale optimistic gain must not force a worsening or non-improving move.
        if fresh_gain <= gain_tolerance:
            # A full refresh restores deterministic best-improvement selection.
            gains = compute_flip_gains(graph, signs)
            # Record this numerical refresh separately from accepted flips.
            history["refreshes"] += 1
            # Try again with the corrected gains; no sign has changed.
            continue
        # Tiny-case verification records direct objective values before and after the move.
        if verify_moves:
            # The direct edge-list evaluator is independent of gain maintenance.
            before = cut_value(graph, signs)
        # The kernel needs synchronized old g_i as well as the OLD sign.
        gains[node] = fresh_gain
        # Update only this label and its affected gain entries.
        flip_node(graph, signs, gains, node)
        # Increment the accepted count only after performing an improving move.
        history["accepted_flips"] += 1
        # Diagnostics are opt-in so production search does not evaluate all edges after each flip.
        if verify_moves:
            # Recompute F on the new signs, independently from old_gain or any running sum.
            after = cut_value(graph, signs)
            # Record actual measurements for mathematical tests and examples.
            history["moves"].append({"node": node, "gain": fresh_gain, "before": before, "after": after})
            # Tiny teaching graphs should show strict actual improvements for every accepted move.
            if after <= before:
                # Surface disagreement rather than hiding it in the trace.
                raise FloatingPointError("accepted local move did not increase the direct cut")
    # The final score is always directly recomputed; no running total controls retention.
    final_cut = cut_value(graph, signs)
    # Copy again so the returned vector cannot alias working storage.
    return signs.copy(), final_cut, history


# The orchestration function contains exactly the requested one-initialization pipeline.
def solve_bm(graph, seed=42, max_sweeps=200, rounding_count=32,
             field_rtol=1e-12, sweep_atol=1e-12, sweep_rtol=1e-9,
             gain_tolerance=1e-10, projection_tolerance=1e-12):
    """Steps 4–9: initialize once, ascend, round K times, polish, retain by F.

    graph is Graph. seed is nonnegative int (42); max_sweeps nonnegative int
    (200); rounding_count positive int K (32). field_rtol (1e-12) is relative
    to incident |weights|; sweep_atol (1e-12) and gain_tolerance (1e-10) have
    weight units; sweep_rtol (1e-9) and projection_tolerance (1e-12) are
    dimensionless. Return (owned shape-(n,) int8 signs, finite float cut,
    plain history dict). graph is not mutated. History contains settings,
    versions, continuous scalars, baseline, roundings and retained source;
    no full vectors. Example: solve_bm(Graph(2,[(0,1,4)]),seed=42) gives cut 4.
    Memory O(n+m+sweeps+K). Sequential full scans can dominate runtime.
    No timing is stored here, allowing same-environment histories to repeat.
    """
    # Reject invalid seeds before constructing NumPy's local generator.
    if isinstance(seed, bool) or not isinstance(seed, Integral) or seed < 0:
        # Global random state is never used as a fallback.
        raise ValueError("seed must be a nonnegative integer")
    # At least one explicit direction is necessary for sampled rounding.
    if isinstance(rounding_count, bool) or not isinstance(rounding_count, Integral) or rounding_count < 1:
        # A fractional K cannot define alpha_k=(k+1/2)*pi/K.
        raise ValueError("rounding_count must be a positive integer")
    # default_rng(42) creates a locally owned Generator; the seed fixes initialization and sweep order.
    rng = np.random.default_rng(seed)
    # uniform includes low=0, excludes high=2*pi, and size=n yields one radian angle per node.
    initial_angles = rng.uniform(low=0.0, high=math.tau, size=graph.node_count)
    # Reuse the same Steps 5–9 block without changing the RNG state after its original angle draw.
    return solve_from_angles(graph, initial_angles, rng, seed, max_sweeps, rounding_count,
                             field_rtol, sweep_atol, sweep_rtol, gain_tolerance, projection_tolerance)


# Both original starts and perturbed angles enter exactly the same mathematical core.
def solve_from_angles(graph, initial_angles, rng, seed=42, max_sweeps=200, rounding_count=32,
                      field_rtol=1e-12, sweep_atol=1e-12, sweep_rtol=1e-9,
                      gain_tolerance=1e-10, projection_tolerance=1e-12):
    """Steps 5–9: polish the zero baseline, ascend SUPPLIED angles, round and retain.

    graph is Graph; initial_angles is finite shape-(n,) radians, e.g. [0,1];
    rng is a Generator, advanced only by coordinate sweep permutations. seed
    is the recorded nonnegative integer stream label (42), not a reset of rng.
    max_sweeps=200 is a nonnegative integer; rounding_count=32 is positive.
    field_rtol=1e-12, sweep_rtol=1e-9 and projection_tolerance=1e-12 are
    dimensionless; sweep_atol=1e-12 and gain_tolerance=1e-10 have weight units.
    Return owned signs, direct float F, and the settled scalar history. Graph
    and supplied angles are unchanged. Passing a freshly drawn original angle
    vector with its already-advanced rng reproduces solve_bm exactly. Cost is
    the existing O(n+m) sweeps plus K full-scan local searches; no new starts.
    """
    # The stream label must be a valid seed identity even though this helper never resets its RNG.
    seed = _integer_count(seed, "seed")
    # Direct callers need the same valid rounding count as the one-start entry point.
    if isinstance(rounding_count, bool) or not isinstance(rounding_count, Integral) or rounding_count < 1:
        # Prevent an empty rounding loop or an accidental fractional count.
        raise ValueError("rounding_count must be a positive integer")
    # ones creates the valid all-+1 baseline, whose raw direct cut is zero.
    baseline = np.ones(graph.node_count, dtype=np.int8)
    # Apply exactly the same binary local search once to the zero baseline.
    best_signs, best_cut, baseline_history = local_search(graph, baseline, gain_tolerance)
    # Retention starts from a polished incumbent, not an unpolished emergency fallback.
    best_signs = best_signs.copy()
    # Optimize this ONE initialization; the local RNG also supplies seeded sweep permutations.
    angles, continuous_history = coordinate_ascent(
        graph, initial_angles, rng, max_sweeps, field_rtol, sweep_atol, sweep_rtol)
    # Record scalar settings explicitly so the exact run can be repeated.
    settings = {"max_sweeps": int(max_sweeps), "rounding_count": int(rounding_count),
                "field_rtol": float(field_rtol), "sweep_atol": float(sweep_atol),
                "sweep_rtol": float(sweep_rtol), "gain_tolerance": float(gain_tolerance),
                "projection_tolerance": float(projection_tolerance)}
    # platform.python_version returns a string such as '3.14.7'; NumPy's version scopes RNG reproducibility.
    history = {"seed": int(seed), "settings": settings,
               "versions": {"python": platform.python_version(), "numpy": np.__version__},
               "continuous": continuous_history,
               "baseline": {"raw_cut": 0.0, "polished_cut": best_cut,
                            "accepted_flips": baseline_history["accepted_flips"]},
               "roundings": [], "retained": "baseline"}
    # range(K) indexes the midpoint directions, not independent angular restarts.
    for direction_index in range(rounding_count):
        # These are evenly spaced NORMAL angles in [0,pi), not an exhaustive partition sweep.
        alpha = (direction_index + 0.5) * math.pi / rounding_count
        # Convert the final continuous arrows into signs using the documented boundary tie policy.
        raw_signs = round_angles(angles, alpha, projection_tolerance)
        # Evaluate raw candidate quality using F, never R.
        raw_cut = cut_value(graph, raw_signs)
        # Polish a COPY of this particular rounded candidate with best-improvement single-node flips.
        polished_signs, polished_cut, polish_history = local_search(graph, raw_signs, gain_tolerance)
        # Direct evaluation is required again at the retention boundary.
        polished_cut = cut_value(graph, polished_signs)
        # Save scalar measurements and flip counts for this explicit normal direction.
        history["roundings"].append({"index": direction_index, "alpha_radians": alpha,
                                    "raw_cut": raw_cut, "polished_cut": polished_cut,
                                    "accepted_flips": polish_history["accepted_flips"]})
        # Exact floating-value ties keep the earlier incumbent; no tolerance comparison is used here.
        if polished_cut > best_cut:
            # Own the signs independently so later candidates cannot change the saved incumbent.
            best_signs = polished_signs.copy()
            # The stored number is the directly recomputed F for those copied signs.
            best_cut = polished_cut
            # The zero-based index identifies the selected direction in history.
            history["retained"] = direction_index
    # Recompute once more on the actual return vector to enforce the final sign/score pairing.
    best_cut = cut_value(graph, best_signs)
    # The polished zero baseline guarantees a nonnegative final cut; surface any numerical violation.
    if best_cut < 0:
        # Do not replace this with a fabricated zero score or mismatched fallback vector.
        raise FloatingPointError("retained cut fell below the zero baseline")
    # Save the direct result as a scalar convenient for CLI and figure readers.
    history["best_cut"] = best_cut
    # The returned independent vector is the only object that may become an assignment file.
    return best_signs.copy(), best_cut, history


# Assignment writing validates binary entries but needs the graph for a finite-cut check.
def write_assignment(path, signs, graph):
    """Step 9: write one signed integer per original node, after direct validation.

    path is selected str/Path, e.g. 'solutions_bm_smoke/example.txt'; signs
    is shape-(graph.node_count,) ±1; graph is Graph. Return direct float cut.
    Does not mutate inputs; creates parent directories and overwrites ONLY
    this explicitly chosen path. Example [1,-1] writes '+1\\n-1\\n'. O(n+m).
    """
    # Shape and membership are checked BEFORE creating directories or opening the output file.
    checked = validate_signs(signs, graph.node_count)
    # A direct finite objective is required before any assignment is written.
    value = cut_value(graph, checked)
    # Path converts the explicitly selected output location into a filesystem object.
    destination = Path(path)
    # parents=True creates missing ancestors; exist_ok=True permits already existing directories.
    destination.parent.mkdir(parents=True, exist_ok=True)
    # 'w' overwrites this selected path; encoding/newline specify portable UTF-8 text with LF records.
    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        # Iteration follows the original node order, not the optimizer's sweep permutation.
        for sign in checked:
            # int produces an integer; +d writes '+1' or '-1', with one newline and no header.
            stream.write(f"{int(sign):+d}\n")
    # Return the already checked score so callers can compare their round-trip measurement.
    return value


# Count validation is shared by explicit starts, rounds, and stable seed identities.
def _integer_count(value, name, minimum=0):
    """Steps 11–13: return an integer >= minimum; reject bool/fractional counts.

    value is an Integral, name an error-label str, minimum an int (0 by default).
    Example _integer_count(2,'restarts',1) returns 2. No mutation; O(1).
    Counts express attempts, not weights, angles, or elapsed seconds.
    """
    # bool is deliberately excluded even though it subclasses int.
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        # Describe the actual invalid parameter at the public boundary.
        raise ValueError(f"{name} must be an integer >= {minimum}")
    # Convert NumPy integral scalars into JSON-compatible Python integers.
    return int(value)


# Binary signs embed exactly into the existing circle representation.
def angles_from_signs(signs):
    """Step 10: theta_i=0 for +1, pi for -1, so R(theta)=F(signs).

    signs is a nonempty flat +/-1 sequence, e.g. [1,1,-1,-1]. Return an
    owned shape-(n,) float64 radian vector [0,0,pi,pi]. Input is copied and
    never mutated. Validation and construction cost O(n) time/storage.
    Equal signs give cos difference 1; unequal signs give -1, yielding F.
    """
    # A positive node count is necessary for this solver's graph convention.
    if len(signs) < 1:
        # Empty arrays cannot identify a graph's assignment.
        raise ValueError("signs must be nonempty")
    # Validate membership before any conversion could round a fractional entry.
    checked = validate_signs(signs, len(signs))
    # np.where(condition,0,pi) returns one new floating angle per binary entry.
    return np.where(checked == 1, 0.0, math.pi)


# Uniform noise changes arrow directions without altering signs or graph weights in place.
def perturb_angles(base_angles, noise_rng, scale=0.35, offsets=None):
    """Step 10: return (base+xi) mod 2*pi, xi~Uniform(-scale,scale).

    base_angles is a finite nonempty shape-(n,) radian sequence; noise_rng is
    a NumPy Generator. scale is a finite half-width in RADIANS, 0<=scale<=pi,
    default .35. Optional offsets is explicit shape-(n,) radians in [-scale,
    scale], e.g. [-.35,.35,-.30,.30]; supplied offsets consume no RNG draws.
    Return an owned wrapped angle array; mutate no inputs except advancing
    noise_rng when drawing noise. scale=0 gives the wrapped base unchanged.
    Example [0,0,pi,pi] with those offsets gives [5.933185,.35,2.841593,
    3.441593]. O(n) time/storage; no guarantee of changing rounded labels.
    """
    # Scale has angular units and must remain within the prescribed half-turn range.
    scale = _nonnegative(scale, "perturb_scale")
    # Larger half-widths are outside this explicitly bounded experiment.
    if scale > math.pi:
        # Fail rather than silently clipping or adapting the noise schedule.
        raise ValueError("perturb_scale must be <= pi radians")
    # Reject an empty representation before copying and drawing offsets.
    if len(base_angles) < 1:
        # Every supported graph contains at least one node.
        raise ValueError("base_angles must be nonempty")
    # Copy the n finite angles to protect the caller's restart-local center.
    base = _vector(base_angles, len(base_angles), "base_angles")
    # Explicit offsets support a worked mathematical example without pretending it was a random draw.
    if offsets is not None:
        # Validate shape and own the caller's numerical example.
        noise = _vector(offsets, len(base), "offsets")
        # The explicit interval includes endpoints; random uniform excludes its upper endpoint.
        if np.any(np.abs(noise) > scale):
            # Reject a deterministic example inconsistent with the stated sigma.
            raise ValueError("offsets must lie in [-perturb_scale, perturb_scale]")
    # Normal solver calls get a separate independent angular offset for each node.
    else:
        # low/high give the angular interval, size=n gives one offset per node; sigma is not a standard deviation.
        noise = noise_rng.uniform(low=-scale, high=scale, size=len(base))
    # Addition and remainder create new arrays, mapping negative angles into one angular period.
    wrapped = (base + noise) % math.tau
    # A tiny negative value can round its remainder to exactly 2*pi in floating arithmetic.
    wrapped[wrapped >= math.tau] = 0.0
    # Zero is the equivalent periodic representative and enforces the promised strict upper bound.
    return wrapped


# In-memory graphs need a stable identity even when no input-file path exists.
def graph_digest(graph):
    """Step 11: SHA-256 of n and ordered fixed edge records; return hex str.

    graph is Graph, e.g. Graph(2,[(0,1,.5)]). float.hex preserves each input
    float exactly; update consumes UTF-8 bytes one record at a time. No mutation,
    O(n+m) existing graph storage and O(m) hashing time with O(1) extra storage.
    This semantic-record digest is distinct from a CLI's raw input-file SHA.
    """
    # sha256 creates deterministic incremental hashing state, not randomized Python hash().
    digest = hashlib.sha256()
    # encode turns the unambiguous count line into UTF-8 bytes for update.
    digest.update(f"{graph.node_count} {len(graph.edges)}\n".encode("utf-8"))
    # Keep each original ordered edge once, matching the stored graph identity.
    for node_i, node_j, weight in graph.edges:
        # float.hex avoids decimal formatting changes in the canonical edge record.
        digest.update(f"{node_i} {node_j} {weight.hex()}\n".encode("utf-8"))
    # hexdigest returns a portable 64-character identifier.
    return digest.hexdigest()


# Attempt seeds depend on explicit identities rather than earlier convergence or batch order.
def derive_seed(base_seed, instance_key, restart_index, round_index, role):
    """Step 11: derive a nonnegative 128-bit integer from five stable fields.

    base_seed=42, instance_key='graph.txt' (nonempty str), restart_index=1,
    round_index=0 are nonnegative integers; role='initialization' is nonempty
    str. JSON encodes boundaries; SHA-256 then int.from_bytes(...,'big') maps
    the first 16 bytes to a seed. No mutation/RNG consumption. O(key length).
    Increasing M/P or changing processing order leaves these identities fixed.
    """
    # Validate the original seed without accepting a negative or fractional identifier.
    base_seed = _integer_count(base_seed, "base_seed")
    # Restart zero is a valid index even though the total restart count must be at least one.
    restart_index = _integer_count(restart_index, "restart_index")
    # Round zero denotes the initial independent solve; positive rounds denote perturbations.
    round_index = _integer_count(round_index, "round_index")
    # Stable role/key strings must be explicit rather than depending on object repr addresses.
    if not isinstance(instance_key, str) or not instance_key or not isinstance(role, str) or not role:
        # Empty or non-string identities cannot support a documented persistent mapping.
        raise ValueError("instance_key and role must be nonempty strings")
    # Compact JSON unambiguously separates fields even if a key contains separators or quotes.
    payload = json.dumps([base_seed, instance_key, restart_index, round_index, role], separators=(",", ":"))
    # Encode text to bytes before applying stable standard-library hashing.
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    # Big-endian conversion fixes byte interpretation across systems; NumPy accepts large integer seeds.
    return int.from_bytes(digest[:16], "big")


# The extended solver owns independent candidate, restart-best, and global-best states.
def solve_bm_extended(graph, seed=42, max_sweeps=200, rounding_count=32,
                      field_rtol=1e-12, sweep_atol=1e-12, sweep_rtol=1e-9,
                      gain_tolerance=1e-10, projection_tolerance=1e-12,
                      restarts=1, perturb_rounds=0, perturb_scale=0.35,
                      initial_signs=None, instance_key=None, input_digest=None):
    """Steps 10–11: M independent starts, each followed by P local perturbations.

    graph and the core settings have solve_bm's meanings/units/defaults. seed=42
    is a nonnegative integer. restarts=M=1 is TOTAL starts; perturb_rounds=P=0
    is additional attempts PER start. perturb_scale=.35 is finite uniform
    half-width radians in [0,pi]. initial_signs=None or shape-(n,) valid signs
    supplies a copied incumbent (not a checkpoint). instance_key=None uses a
    canonical graph digest; otherwise give a nonempty stable str such as
    'local_trap.txt'. input_digest=None uses that semantic digest; the CLI passes
    its raw input SHA-256 string. Return owned global signs, direct float F,
    scalar per-attempt history including timings. Mutate only owned working
    arrays/local RNGs; no files. M=2,P=2 yields exactly six complete core passes.
    Restart zero uses solve_bm unchanged, preserving its original coupled RNG.
    Other initial/noise/sweep streams use stable identity seeds. Memory is the
    existing core workspace plus O(M*(1+P)*(sweeps+K)) scalar history; full
    per-attempt states are recorded only on tiny n<=8 teaching graphs.
    """
    # Measure all API work including identity generation, copies, and completed attempts.
    started = perf_counter()
    # Validate the total initialization count before starting any optimization.
    restarts = _integer_count(restarts, "restarts", 1)
    # A zero perturbation count deliberately selects the original behavior.
    perturb_rounds = _integer_count(perturb_rounds, "perturb_rounds")
    # The base seed keeps restart-zero's original stream exactly intact.
    seed = _integer_count(seed, "seed")
    # Even unused scale values are validated so a bad CLI setting cannot pass silently.
    perturb_scale = _nonnegative(perturb_scale, "perturb_scale")
    # A fixed bounded uniform interval is the only noise model in this extension.
    if perturb_scale > math.pi:
        # Do not infer a different unit, distribution, or adaptive schedule.
        raise ValueError("perturb_scale must be <= pi radians")
    # Compute an in-memory graph identity without using filenames or batch order implicitly.
    semantic_digest = graph_digest(graph)
    # Default API identities are stable for the same stored graph.
    if instance_key is None:
        # The prefix distinguishes a semantic graph record from a user-provided filename.
        instance_key = "graph:" + semantic_digest
    # Require meaningful caller identities even when only the compatibility attempt is requested.
    if not isinstance(instance_key, str) or not instance_key:
        # Empty keys could accidentally merge unrelated experimental identities.
        raise ValueError("instance_key must be a nonempty string")
    # Distinguish a semantic graph-record digest from a caller's raw-file digest explicitly.
    digest_kind = "canonical_graph_records" if input_digest is None else "supplied_raw_input_sha256"
    # Raw file bytes are unavailable to the pure in-memory API unless explicitly passed.
    if input_digest is None:
        # Record the digest's origin rather than claiming it hashes an unseen input file.
        input_digest = semantic_digest
    # A supplied digest must have a genuine SHA-256 hexadecimal representation.
    if not isinstance(input_digest, str) or len(input_digest) != 64 or any(c not in "0123456789abcdef" for c in input_digest):
        # Reject inconsistent metadata rather than attaching it to otherwise valid signs.
        raise ValueError("input_digest must be a lowercase SHA-256 hex string")
    # No artificial sign vector is invented before the settled first core pass.
    global_best_signs = None
    # Null is explicit when no saved incumbent exists yet.
    global_best_cut = None
    # A supplied binary assignment is copied and scored from the CURRENT fixed graph.
    if initial_signs is not None:
        # Preserve caller ownership and original node ordering.
        global_best_signs = validate_signs(initial_signs, graph.node_count)
        # Never trust the old solution's reported score or relaxed objective.
        global_best_cut = cut_value(graph, global_best_signs)
    # Copy the supplied center separately from the mutable global incumbent.
    supplied_signs = None if global_best_signs is None else global_best_signs.copy()
    # Keep its direct initial score for documenting warm continuation and tie precedence.
    supplied_cut = global_best_cut
    # Histories contain scalar progress, role seeds, and only tiny optional vector examples.
    history = {"seed": seed, "instance_key": instance_key, "input_sha256": input_digest,
               "input_digest_kind": digest_kind,
               "semantic_graph_sha256": semantic_digest, "restarts": restarts,
               "perturb_rounds": perturb_rounds, "perturb_scale_radians": perturb_scale,
               "initial_cut": supplied_cut, "attempts": [], "total_passes": 0,
               "versions": {"python": platform.python_version(), "numpy": np.__version__},
               "timing_scope": "API entry through all attempts and retention; excludes file I/O."}
    # Each restart gets a fresh initialization rather than copying another restart's global best.
    for restart_index in range(restarts):
        # Restart-local ownership is reset independently of previous restarts.
        restart_best_signs = None
        # Only restart zero may use the supplied incumbent as a refinement center.
        restart_best_cut = None
        # This earlier assignment keeps precedence over an exact tie from restart zero's first solve.
        if restart_index == 0 and supplied_signs is not None:
            # Own the local center independently from both supplied and global storage.
            restart_best_signs = supplied_signs.copy()
            # Its quality was directly recomputed before the outer loop.
            restart_best_cut = supplied_cut
        # Round zero initializes; rounds 1..P each add exactly one complete refinement pass.
        for round_index in range(perturb_rounds + 1):
            # Include seed derivation, embeddings/noise, and core work in this attempt's elapsed time.
            attempt_started = perf_counter()
            # A scalar center score is available only for the perturbation attempts.
            center_cut = None
            # Fresh random starts do not inherit angles from any prior retained solution.
            if round_index == 0:
                # Mark the difference between exploration and perturbation explicitly.
                kind = "initial"
                # Compatibility means restart INDEX zero, for any user base seed.
                if restart_index == 0:
                    # The old solver couples its angle draw and sweep permutations in one stream.
                    seeds = {"initialization": seed, "sweep_order": seed, "noise": None, "legacy_coupled": True}
                    # Preserve exactly the settled initial draw, baseline polish, update and rounding order.
                    candidate_signs, reported_cut, core = solve_bm(
                        graph, seed, max_sweeps, rounding_count, field_rtol, sweep_atol,
                        sweep_rtol, gain_tolerance, projection_tolerance)
                # Other initializations have their own separate stable initialization/order roles.
                else:
                    # These seeds depend only on explicit fields, never earlier convergence.
                    init_seed = derive_seed(seed, instance_key, restart_index, 0, "initialization")
                    # The order role is independent of the number of initialization draws.
                    order_seed = derive_seed(seed, instance_key, restart_index, 0, "sweep_order")
                    # A local generator cannot reset global NumPy random state.
                    init_rng = np.random.default_rng(init_seed)
                    # Uniform [0,2*pi) supplies one fresh random radian angle per node.
                    start_angles = init_rng.uniform(low=0.0, high=math.tau, size=graph.node_count)
                    # This generator is reserved for this attempt's sequential sweep permutations.
                    order_rng = np.random.default_rng(order_seed)
                    # Record both seed roles without implying they share a stream.
                    seeds = {"initialization": init_seed, "sweep_order": order_seed, "noise": None, "legacy_coupled": False}
                    # Consume the supplied fresh angles through the shared unchanged Steps 5–9 kernel.
                    candidate_signs, reported_cut, core = solve_from_angles(
                        graph, start_angles, order_rng, order_seed, max_sweeps, rounding_count,
                        field_rtol, sweep_atol, sweep_rtol, gain_tolerance, projection_tolerance)
            # Later rounds exploit only this restart's retained binary assignment.
            else:
                # This operation is a local refinement attempt rather than another independent start.
                kind = "perturbed"
                # Record the true local center quality even if another restart has a better global best.
                center_cut = restart_best_cut
                # The exact 0/pi embedding is a new array; restart signs are unchanged.
                base_angles = angles_from_signs(restart_best_signs)
                # Noise is reproducible independently of how many sweeps any earlier attempt used.
                noise_seed = derive_seed(seed, instance_key, restart_index, round_index, "perturb_noise")
                # Separate the perturbation offsets from subsequent visit-order randomness.
                order_seed = derive_seed(seed, instance_key, restart_index, round_index, "sweep_order")
                # This generator is used only for one uniform offset per node in this round.
                noise_rng = np.random.default_rng(noise_seed)
                # The uniform half-width is in radians; no sign/edge mutation happens here.
                start_angles = perturb_angles(base_angles, noise_rng, perturb_scale)
                # Sweep permutations use their own identity-derived generator.
                order_rng = np.random.default_rng(order_seed)
                # The initial random-angle role is absent in a 0/pi lift plus noise attempt.
                seeds = {"initialization": None, "sweep_order": order_seed, "noise": noise_seed, "legacy_coupled": False}
                # Actually optimize these perturbed angles; never resample or ignore them.
                candidate_signs, reported_cut, core = solve_from_angles(
                    graph, start_angles, order_rng, order_seed, max_sweeps, rounding_count,
                    field_rtol, sweep_atol, sweep_rtol, gain_tolerance, projection_tolerance)
            # Recompute the mathematical selection value from the actual candidate, not reported R or totals.
            candidate_cut = cut_value(graph, candidate_signs)
            # A restart's local best changes only on strict improvement; input ties remain earlier.
            local_improved = restart_best_cut is None or candidate_cut > restart_best_cut
            # Keep each restart-local state in its own storage.
            if local_improved:
                # Later calls may reuse candidate memory without corrupting this local center.
                restart_best_signs = candidate_signs.copy()
                # Store the directly recomputed F paired with those exact copied signs.
                restart_best_cut = candidate_cut
            # Global comparisons include the saved incumbent and every independent restart.
            global_improved = global_best_cut is None or candidate_cut > global_best_cut
            # A worsening candidate remains an honest measurement, never a retained regression.
            if global_improved:
                # Global storage never aliases candidate or restart-local arrays.
                global_best_signs = candidate_signs.copy()
                # The monotone retained quality is a discrete cut, not a relaxed value.
                global_best_cut = candidate_cut
            # Count the binary effort across the polished zero baseline and every normal direction.
            flip_count = core["baseline"]["accepted_flips"]
            # Every sampled rounding uses the same settled single-node local search.
            for rounding in core["roundings"]:
                # Add measured accepted flips without storing per-node moves on large graphs.
                flip_count += rounding["accepted_flips"]
            # Scalar records identify each attempt and both separate incumbent levels.
            record = {"restart_index": restart_index, "round_index": round_index, "kind": kind,
                      "seeds": seeds, "center_cut": center_cut, "candidate_cut": candidate_cut,
                      "restart_best_cut": restart_best_cut, "global_best_cut": global_best_cut,
                      "local_improved": local_improved, "global_improved": global_improved,
                      "elapsed_seconds": perf_counter() - attempt_started,
                      "sweeps_used": len(core["continuous"]["sweeps"]), "accepted_flips": flip_count,
                      "stop_reason": core["continuous"]["stop_reason"], "core": core}
            # Tiny teaching examples may record actual candidate assignments for figure verification.
            if graph.node_count <= 8:
                # tolist copies small JSON-compatible values, never a mutable NumPy view.
                record["tiny_candidate_signs"] = candidate_signs.tolist()
            # Completed attempts, including losses and ties, remain in chronological order.
            history["attempts"].append(record)
    # Every requested initial/refinement pass is counted once, including its all-plus baseline policy.
    history["total_passes"] = len(history["attempts"])
    # Directly re-evaluate the actual owned vector at the return boundary.
    global_best_cut = cut_value(graph, global_best_signs)
    # Keep explicit core settings accessible without guessing them from an attempt's elapsed time.
    history["settings"] = history["attempts"][0]["core"]["settings"].copy()
    # The stored final best always belongs to the returned signs.
    history["best_cut"] = global_best_cut
    # This measurement has the API timing scope stated above; it is not a stopping condition.
    history["runtime_seconds"] = perf_counter() - started
    # Caller mutation cannot alter any retained internal state or supplied incumbent.
    return global_best_signs.copy(), global_best_cut, history
