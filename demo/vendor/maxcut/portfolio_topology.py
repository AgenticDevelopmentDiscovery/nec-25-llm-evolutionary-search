"""Planar exact signed dual matching and sparse upstream toroidal matching/bounds."""

# Optional import discovery keeps basic solvers usable without matching dependencies.
import importlib.util
# Hashes identify the exact upstream primitives used by the topology adapter.
import hashlib
# The separate source manifest preserves the reviewed upstream commit.
import json
# Geometry checks infer and validate the supplied row-major square torus embedding.
import math
# Path locates the separately pinned upstream code without copying its source.
from pathlib import Path
# Native matching routines are bounded by the runner's process deadline between cooperative checks.
from time import perf_counter
# NumPy stores edge lists, face lists and vectors, not dense graph matrices.
import numpy as np
# Original cut evaluation and binary validation determine every returned assignment's actual value.
from bm_solver import cut_value
# Contracts and exact weight scaling distinguish bounds from feasible answers.
from portfolio_common import deadline_from, integer_weights, result_record, settings, starting_signs


# Explicit row-major embedding prevents guessing topology from a torus-looking filename.
def torus_faces(graph):
    """Validate n=L*L, L>=3, four grid neighbors including BOTH wraps; return L,faces.

    graph uses original IDs node=r*L+c. Each unordered right/down periodic edge
    must occur exactly once; arbitrary finite signed weights are allowed.
    faces is n length-four cycles in original IDs. Example L=3 has nine faces
    and eighteen edges. L=2 aliases parallel wrap edges and is explicitly
    unsupported by this simple-graph representation. No mutation, O(n+m).
    """
    # Integer square root avoids inferring an approximate floating side length.
    side = math.isqrt(graph.node_count)
    # A cellular square torus requires distinct left/right and up/down neighbors.
    if side < 3 or side*side != graph.node_count:
        # Reject a planar grid or arbitrary same-sized graph rather than inventing an embedding.
        raise ValueError("toroidal backend requires row-major L*L grid with L>=3")
    # Store all expected fixed topology edges independently of their signs/weights.
    expected = set()
    # Each face explicitly retains both periodic boundary directions.
    faces = []
    # Original input indices are preserved in every coordinate conversion.
    for row in range(side):
        # Each column contributes one right edge, one down edge and one elementary face.
        for column in range(side):
            # Row-major original node ID.
            node = row*side + column
            # Horizontal wrap uses modulo side without removing a seam edge.
            right = row*side + (column + 1) % side
            # Vertical wrap keeps the last/first rows adjacent.
            down = ((row + 1) % side)*side + column
            # The opposite face corner wraps independently in both directions.
            diagonal = ((row + 1) % side)*side + (column + 1) % side
            # Sort endpoints only for undirected membership, not for reordering output nodes.
            expected.add(tuple(sorted((node, right))))
            # Every node contributes a unique down edge for L>=3.
            expected.add(tuple(sorted((node, down))))
            # Counterclockwise/cyclic face ordering is explicit for the matching construction.
            faces.append([node, right, diagonal, down])
    # Compare complete graph topology, including zero-weight edges if represented.
    actual = {tuple(sorted((i, j))) for i, j, weight in graph.edges}
    # Both missing wrap edges and extra diagonals invalidate the assumed embedding.
    if actual != expected:
        # Never silently remove wraparounds or solve a different planar optimization problem.
        raise ValueError("graph edges do not match the required periodic square-grid embedding")
    # Return a small scalar plus sparse O(n) face storage.
    return side, faces


# Upstream loading calls only its sparse LP primitives, avoiding its dense H front-end.
def upstream_matching_module():
    """Load pinned MaxCutPlanarAndToroidal/toroid_lp_lib.py and return module.

    No args; the file imports NumPy/NetworkX/stdlib and has no solver launch
    on import. Example module.build_expanded_dual(edges,faces) exposes the
    authors' original implementation. No source edits or sys.path mutation.
    O(source bytes); raises FileNotFoundError if the optional checkout is absent.
    """
    # Resolve the original upstream file separately from project-owned adapters.
    path = Path(__file__).parent / "external/MaxCutPlanarAndToroidal/toroid_lp_lib.py"
    # A missing checkout is an availability issue, not a reason to relabel local code.
    if not path.is_file():
        # The portfolio discovery reports the reproducible pinned retrieval instructions.
        raise FileNotFoundError("MaxCutPlanarAndToroidal checkout is missing")
    # Import by explicit path without polluting global module-search order.
    spec = importlib.util.spec_from_file_location("maxcut_upstream_lp", path)
    # Create a fresh module namespace for this unmodified upstream file.
    module = importlib.util.module_from_spec(spec)
    # Execute the reviewed definitions; no main comparison or campaign is launched.
    spec.loader.exec_module(module)
    # Returning the actual upstream module preserves implementation identity.
    return module


# This adapter distinguishes the unconstrained face bound from toroidal feasible search.
def solve_toroidal(graph, config, seed, budget, initial_assignment=None, method="toroidal_bound"):
    """Call sparse upstream matching primitives on a verified torus embedding.

    config max_expanded_nodes=4096, max_stall=10; seed controls moved generator
    cycles; budget max_work counts cycle-repair iterations (bound always one
    initial matching), seconds is cooperative between matching calls. Caller
    warm signs seed retained best AND search cycle repairs. Return bound and
    feasible original-order assignment separately. Equality is solver-reported
    optimal under exact integer matching and the validated embedding, not a
    standalone rational dual certificate. O(n+m) graph storage; matching cost
    may be high, protected by size guard/process timeout. No source mutation.
    Example odd L=3 and even L=4 are tested against exhaustive search.
    """
    # Include topology validation and conversion in measured runtime.
    started = perf_counter()
    # Keep native-size and stagnation controls explicit; no hidden torus cut truncation.
    cfg = settings(config, {"max_expanded_nodes": 4096, "max_stall": 10})
    # Validate actual algorithm identity rather than mapping every topology method to the same call.
    if method not in {"toroidal_bound", "toroidal_search"}:
        # Planar optimization has a separate solver and different exactness assumptions.
        raise ValueError("unknown toroidal method")
    # Expanded quadrilateral dual uses four nodes per elementary face.
    if type(cfg["max_expanded_nodes"]) is not int or cfg["max_expanded_nodes"] < 1 or type(cfg["max_stall"]) is not int or cfg["max_stall"] < 1:
        # Resource guards cannot be silently disabled by invalid values.
        raise ValueError("invalid toroidal resource/stall controls")
    # Time/work validation precedes optional matching invocation.
    deadline = deadline_from(budget)
    # Check the actual original topology before asserting any torus-based bound.
    side, faces = torus_faces(graph)
    # A hard expanded-size guard prevents an unexpected huge NetworkX matching allocation.
    if 4*graph.node_count > cfg["max_expanded_nodes"]:
        # This is an explicit supported-size limit, not an assumed dense representation of large instances.
        return result_record(method, graph, cfg, seed, budget, started, status="unavailable", reason="expanded dual exceeds configured max_expanded_nodes")
    # NetworkX is optional and must not break import of BM or exhaustive search.
    if importlib.util.find_spec("networkx") is None:
        # Do not report a placeholder bound when matching is unavailable.
        return result_record(method, graph, cfg, seed, budget, started, status="unavailable", reason="install optional matching extra")
    # Local randomness controls the generator-cycle root policy.
    rng = np.random.default_rng(seed)
    # A valid supplied incumbent remains independently retained throughout bound/search work.
    best = starting_signs(graph, rng, initial_assignment)
    # A time limit before the first matching supplies only a feasible witness, no guessed bound.
    if perf_counter() >= deadline:
        # The bound is unavailable until matching genuinely completes.
        return result_record(method, graph, cfg, seed, budget, started, best, status="time_limit", reason="before_matching")
    # Lossless finite-decimal scaling is required by the upstream integer matching implementation.
    weights, scale = integer_weights(graph)
    # Sort edges into the exact endpoint ordering expected by upstream's face dictionary.
    ordered = sorted((min(i,j), max(i,j), weight) for (i,j,original),weight in zip(graph.edges,weights))
    # Endpoints and weights are sparse edge-sized arrays, not n*n matrices.
    edges = np.array([(i,j) for i,j,weight in ordered], dtype=int)
    # Original signed weights are retained after integer scaling, without negation or clipping.
    w = np.array([weight for i,j,weight in ordered], dtype=np.int64)
    # Load the actual reviewed upstream sparse primitives only on this requested path.
    module = upstream_matching_module()
    # The authors' expanded-dual construction captures every local face parity constraint.
    n_exp, zero_edges, corners, edge_faces = module.build_expanded_dual(edges, faces)
    # This unconstrained matching relaxes the two global torus cycle conditions and therefore yields an upper bound.
    mask = module.match_expanded_dual(n_exp, zero_edges, corners, w)
    # Exact integer summation gives the raw face-relaxation upper bound in scaled cut units.
    upper_integer = sum(int(weight) for weight,cut in zip(w,mask) if cut)
    # Build sparse original-node adjacency with edge IDs for parity reconstruction.
    adjacency = [[] for node in range(graph.node_count)]
    # Every original edge supplies both undirected adjacency directions.
    for edge, (i,j) in enumerate(edges):
        # Store ordinary integer IDs expected by upstream BFS/cycle helpers.
        adjacency[int(i)].append((int(j),edge))
        # The reverse adjacency is required to test all closed-cycle consistency.
        adjacency[int(j)].append((int(i),edge))
    # BFS reconstructs feasible labels and separately flags whether the matched mask was globally consistent.
    groups, consistent = module.paint_nodes_bfs(adjacency, mask)
    # Zero/one group labels map to original +/-1 output convention.
    candidate = (1 - 2*groups).astype(np.int8)
    # Even an inconsistent mask yields a feasible BFS labeling, which must be scored on the ORIGINAL full graph.
    if cut_value(graph,candidate) > cut_value(graph,best):
        # Retain only the independently recomputed strict cut improvement.
        best = candidate.copy()
    # Search begins from the actual strongest feasible incumbent, including supplied warm labels.
    current = best.copy()
    # Record the raw mask's consistency separately from the returned feasible assignment.
    history = [{"phase":"face_matching", "upper_bound":upper_integer/scale, "mask_is_global_cut":bool(consistent), "feasible_cut":cut_value(graph,best)}]
    # Counts distinguish the initial upper-bound solve from conditional repairs.
    matches, iterations, stall = 1, 0, 0
    # Toroidal search keeps global cycle conditions instead of treating the torus as planar.
    while method == "toroidal_search" and iterations < budget.get("max_work",10000) and stall < cfg["max_stall"] and perf_counter() < deadline and cut_value(graph,best) < upper_integer/scale:
        # Move the two generator-cycle locations through a seed-controlled original-node root.
        root = int(rng.integers(graph.node_count))
        # The unmodified upstream tree/cotree routine identifies the generator-cycle edge union.
        fixed_edges = module.find_generator_cycles(adjacency, edges, edge_faces, len(faces), root)
        # The current feasible cut defines the fixed cycle states exactly.
        current_mask = current[edges[:,0]] != current[edges[:,1]]
        # With generator-cycle edges fixed, upstream solves the remaining matching subproblem.
        repaired = module.match_expanded_dual(n_exp, zero_edges, corners, w, fixed_edges, current_mask[fixed_edges])
        # Check global feasibility independently of local face parity.
        groups, valid_mask = module.paint_nodes_bfs(adjacency,repaired)
        # A failed reconstruction invalidates the search result rather than being called an exact torus solve.
        if not valid_mask:
            # This protects against missing noncontractible constraints or an unsupported embedding.
            raise ValueError("upstream toroidal cycle repair returned an inconsistent cut mask")
        # Recover original node signs without renumbering or discarding seam edges.
        current = (1 - 2*groups).astype(np.int8)
        # Recompute the actual signed cut on the original graph.
        value = cut_value(graph,current)
        # Exact conditional repair cannot reduce its feasible cycle-fixed incumbent.
        if value + 1e-9 < cut_value(graph,best):
            # A regression would expose a conversion/constraint error rather than an accepted heuristic loss.
            raise ValueError("toroidal conditional repair decreased incumbent")
        # Stagnation counts actual non-improving conditional repairs.
        stall = 0 if value > cut_value(graph,best) else stall+1
        # The strongest feasible answer is copied; equal moves can still change current search state.
        if value > cut_value(graph,best):
            # Preserve a strict feasible gain independently of the working reconstruction.
            best = current.copy()
        # Count real matching calls and repair iterations.
        matches += 1
        # The work budget counts only additional conditional repairs.
        iterations += 1
        # Scalar history identifies actual cycle conditioning, cut and valid upper bound.
        if len(history)<200:
            # No fabricated optimality is inferred merely from local repair completion.
            history.append({"phase":"cycle_repair","root":root,"fixed_edges":len(fixed_edges),"feasible_cut":value,"upper_bound":upper_integer/scale})
    # Equality of a validated feasible cut and valid face-relaxation upper bound supports a conditional optimality conclusion.
    reaches_bound = sum(weight for (i,j,original),weight in zip(graph.edges,weights) if best[i]!=best[j]) == upper_integer
    # Keep feasibility, execution and proof evidence separate in the standard interface.
    result = result_record(method,graph,cfg,seed,budget,started,best,
                         status="time_limit" if perf_counter()>=deadline else "completed",
                         reason="bound_attained" if reaches_bound else "matching_bound" if method=="toroidal_bound" else "repair_limit",
                         upper_bound=upper_integer/scale,optimality="solver_reported_optimal" if reaches_bound else "unproven",
                         evidence={"bound":"integer face-parity matching relaxation","scale":scale,"side":side,
                                   "embedding":"verified original row-major two-direction periodic square grid",
                                   "bound_attained":reaches_bound,"assumptions":"exact integer maximum-weight matching; global consistency checked"},
                         counters={"matching_calls":matches,"repair_iterations":iterations,"expanded_nodes":n_exp},history=history,
                         implementation="upstream-MaxCutPlanarAndToroidal/sparse-LP-primitives")
    # Record the actual unmodified primitive source independently of the project wrapper's code hash.
    source=Path(__file__).parent/"external/MaxCutPlanarAndToroidal/toroid_lp_lib.py"
    # Exact file bytes and the pinned revision make this integration reproducible after checkout changes.
    result["upstream"]={**next(record for record in json.loads((Path(__file__).parent/"external/sources.json").read_text()) if record["name"]=="MaxCutPlanarAndToroidal"),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest()}
    # Return separately checked feasible labels and a computed face-relaxation bound.
    return result


# Exact planar signed matching has no noncontractible cycles; bridges and isolates need explicit handling.
def solve_planar(graph, config, seed, budget, initial_assignment=None):
    """Solve planar signed Max-Cut by dual minimum T-join matching.

    config max_defects=256 bounds the metric matching graph, max_nodes=100000.
    Graph must be planar; disconnected components and bridges are supported.
    Preferred cut states are w>0. Odd preferred face parities form T; shortest
    paths in the |w| dual and minimum perfect matching give minimum violations.
    F=sum(w_positive)-violation_cost. Warm labels are retention-only, not used
    to alter matching. budget seconds is cooperative between matching calls;
    max_work bounds components. Return validated original-order labels/bound
    when all components finish, otherwise only a feasible unproven result.
    No mutation/files; graph storage O(n+m), metric storage O(|T|**2), explicitly
    capped rather than allocating n*n. References: Pardella-Liers 2008 and
    Glass-Feder 2026 signed planar matching treatment. Example +1 triangle F=2.
    """
    # Start timing before validation/conversion so setup cost is not hidden.
    started=perf_counter()
    # Matching size limits concern defects and total graph size separately.
    cfg=settings(config,{"max_defects":256,"max_nodes":100000})
    # Explicit positive integer guards prevent unintended huge matching instances.
    if any(type(value) is not int or value<1 for value in cfg.values()) or graph.node_count>cfg["max_nodes"]:
        # Graph/backend size support remains an availability limit, not a guessed exact result.
        raise ValueError("invalid or exceeded planar size guard")
    # Validate ordinary time and component-work budgets.
    deadline=deadline_from(budget)
    # NetworkX is optional for basic solvers.
    if importlib.util.find_spec("networkx") is None:
        # Missing matching support does not produce a fabricated bound.
        return result_record("planar_matching",graph,cfg,seed,budget,started,status="unavailable",reason="install optional matching extra")
    # Use the actual general matching/embedding library only on this path.
    import networkx as nx
    # Lossless integer weights make dual shortest-path and matching costs exact.
    weights,scale=integer_weights(graph)
    # Build a sparse original-node graph, explicitly including isolated nodes.
    primal=nx.Graph()
    # Original node IDs remain unchanged through embedding and reconstruction.
    primal.add_nodes_from(range(graph.node_count))
    # Annotate each undirected edge with its fixed original integer weight.
    for edge,((i,j,original),weight) in enumerate(zip(graph.edges,weights)):
        # Edge IDs identify which primal indicator toggles along a dual correction path.
        primal.add_edge(i,j,weight=weight,edge=edge)
    # Own the supplied warm answer for retention even when topology/limits prevent solving.
    best=starting_signs(graph,np.random.default_rng(seed),initial_assignment)
    # Working output starts as a copy so completed components can be assigned independently.
    candidate=best.copy()
    # Every component must finish before a global planar optimum can be reported.
    completed=0
    # Add independently computed exact component matching bounds only after each component completes.
    total_upper_integer=0
    # Scalar component evidence exposes signed violation costs and embedding sizes.
    history=[]
    # Components do not share edges, so their exact objective contributions add independently.
    components=list(nx.connected_components(primal))
    # Actual connected components, rather than arbitrary chunks, define separable exact subproblems.
    for nodes in components:
        # A component-work or time interruption prevents a global exactness claim.
        if completed>=budget.get("max_work",10000) or perf_counter()>=deadline:
            # The current candidate remains feasible on all original graph edges.
            break
        # Take a sparse component view without changing its original node IDs.
        component=primal.subgraph(nodes)
        # An isolated vertex has no cut contribution or dual faces to optimize.
        if component.number_of_edges()==0:
            # Count this trivial exact component without allocating a matching graph.
            completed+=1
            # Its existing label is already an optimal feasible choice.
            continue
        # Planarity must be proven by an actual embedding algorithm, not inferred from a file name.
        planar,embedding=nx.check_planarity(component)
        # Nonplanar inputs must use another backend instead of having edges silently removed.
        if not planar:
            # Report the unsupported input explicitly, preserving the supplied feasible incumbent.
            return result_record("planar_matching",graph,cfg,seed,budget,started,best,status="unavailable",reason="input is nonplanar")
        # Map each directed half-edge to its incident face in this verified embedding.
        face_of={}
        # Traversed half-edges avoid counting an embedding face more than once.
        visited=set()
        # Face count includes the outer face, necessary for odd-parity matching.
        faces=0
        # Every original undirected edge has two directed sides, possibly in the same face for bridges.
        for i,j in embedding.edges():
            # Only an unvisited side starts a new face walk.
            if (i,j) not in visited:
                # NetworkX returns the cyclic face boundary while marking its directed sides.
                walk=embedding.traverse_face(i,j,visited)
                # Each consecutive directed edge belongs to this face, including a bridge's return direction.
                for k,node in enumerate(walk):
                    # Record oriented incidence; bridges naturally map both sides to one face.
                    face_of[(node,walk[(k+1)%len(walk)])]=faces
                # Increment only after storing every side of this genuine face.
                faces+=1
        # Dual edges carry absolute weights, which are nonnegative violation penalties.
        dual=nx.Graph()
        # Keep every face even when all its incident costs are zero.
        dual.add_nodes_from(range(faces))
        # Face parity records the preferred cut mask before correcting unsatisfied edges.
        parity=[0]*faces
        # Start with every signed edge's independently preferred state.
        cut_mask={data["edge"]:data["weight"]>0 for i,j,data in component.edges(data=True)}
        # Construct dual adjacency and the odd-face terminal set.
        for i,j,data in component.edges(data=True):
            # Each side's incident face comes from the verified embedding.
            left,right=face_of[(i,j)],face_of[(j,i)]
            # Preferred positive separation toggles parity on each incident face.
            if data["weight"]>0:
                # A bridge toggles the same face twice and thus contributes no parity defect.
                parity[left]^=1
                # Distinct faces receive one toggle each.
                parity[right]^=1
            # Bridges require no dual correction and keep their individually optimal preferred state.
            if left==right:
                # Omitting a dual self-loop does not remove the primal bridge from reconstruction or objective.
                continue
            # Parallel dual alternatives need only the cheapest primal violation edge.
            cost=abs(data["weight"])
            # Preserve its original edge ID for XOR correction along shortest paths.
            if not dual.has_edge(left,right) or cost<dual[left][right]["weight"]:
                # This is an exact shortest-path reduction over nonnegative integer costs.
                dual.add_edge(left,right,weight=cost,edge=data["edge"])
        # Only odd preferred face parities need correction.
        terminals=[face for face,value in enumerate(parity) if value]
        # The complete metric graph can be quadratic in defects, so guard before constructing it.
        if len(terminals)>cfg["max_defects"]:
            # Return explicit limited availability, not an approximated result labeled exact.
            return result_record("planar_matching",graph,cfg,seed,budget,started,best,status="unavailable",reason="dual defects exceed max_defects")
        # Pairwise terminal distances define the standard minimum T-join matching problem.
        metric=nx.Graph()
        # A no-defect graph needs no correction and still has a valid empty matching.
        metric.add_nodes_from(terminals)
        # Dijkstra distance-only evaluation avoids storing a path from every face to every terminal.
        for index,source in enumerate(terminals):
            # Keep only one O(faces) distance vector at a time, plus the capped terminal metric.
            distances=nx.single_source_dijkstra_path_length(dual,source,weight="weight")
            # Every pair appears once in the undirected metric graph.
            for target in terminals[index+1:]:
                # A connected planar component has a connected dual after bridge self-loops are removed.
                metric.add_edge(source,target,weight=distances[target])
        # Exact minimum-weight maximum-cardinality matching pairs all odd terminals.
        matching=nx.min_weight_matching(metric,weight="weight") if terminals else set()
        # An odd or incomplete terminal pairing would invalidate the T-join proof.
        if 2*len(matching)!=len(terminals):
            # Do not publish a bound from a defective matching conversion.
            raise ValueError("planar dual terminals were not perfectly matched")
        # Correct the preferred mask by XORing matched shortest paths.
        for source,target in matching:
            # Reconstruct only matched-pair routes, avoiding quadratic collections of full graph paths.
            path=nx.shortest_path(dual,source,target,weight="weight")
            # Shared path edges cancel modulo two, as required by a T-join.
            for left,right in zip(path,path[1:]):
                # Retrieve the original edge to mark this violation correction.
                edge=dual[left][right]["edge"]
                # XOR, rather than assignment, preserves cancellations of overlapping matched paths.
                cut_mask[edge]=not cut_mask[edge]
        # Reconstruct actual primal node labels with an explicit feasibility check on every cycle.
        root=min(nodes)
        # A component's complementary symmetry lets its BFS root be +1.
        assigned={root:1}
        # Use a simple list queue with one visit per original node.
        queue=[root]
        # BFS propagates the corrected cut indicators to actual signs.
        for node in queue:
            # All neighbors retain their original edge IDs.
            for neighbor,data in primal[node].items():
                # A cut indicator means opposite signs; an uncut edge means equal signs.
                sign=-assigned[node] if cut_mask[data["edge"]] else assigned[node]
                # Revisited coordinates must agree, proving global consistency in the planar component.
                if neighbor in assigned and assigned[neighbor]!=sign:
                    # Such a conflict exposes a conversion/parity error and invalidates exactness.
                    raise ValueError("planar matching mask failed global reconstruction")
                # Newly reached vertices extend the same verified labeling.
                if neighbor not in assigned:
                    # Store the determined sign before another BFS path reaches it.
                    assigned[neighbor]=sign
                    # Each node is queued exactly once.
                    queue.append(neighbor)
        # Publish only this exact component's reconstructed labels into working output.
        for node,sign in assigned.items():
            # No output-node reordering occurs during matching or BFS.
            candidate[node]=sign
        # Matching cost is the minimum possible signed-preference violation cost in this planar component.
        component_upper=sum(max(0,data["weight"]) for i,j,data in component.edges(data=True))-sum(metric[a][b]["weight"] for a,b in matching)
        # Recompute the reconstructed cut's scaled objective independently of matching-path bookkeeping.
        component_cut=sum(data["weight"] for i,j,data in component.edges(data=True) if candidate[i]!=candidate[j])
        # A feasible witness must attain the derived matching optimum before this component is credited exact.
        if component_cut!=component_upper:
            # A mismatch exposes an invalid embedding, path cancellation or objective conversion.
            raise ValueError("planar reconstructed cut does not attain matching-derived bound")
        # Add the independently computed component upper bound, including bridge contributions.
        total_upper_integer+=component_upper
        # Independently score a complete original-graph witness after this component update.
        if cut_value(graph,candidate)>cut_value(graph,best):
            # Preserve every usable partial gain if later work times out.
            best=candidate.copy()
        # Count only fully reconstructed, feasible exact components.
        completed+=1
        # Small scalar history distinguishes graph topology from an empirical heuristic claim.
        history.append({"component_nodes":len(nodes),"faces":faces,"odd_faces":len(terminals),"matching_pairs":len(matching)})
    # All connected components must finish before additive exactness is justified.
    complete=completed==len(components)
    # A full planar optimum may tie the supplied incumbent, which wins ties by retention policy.
    if complete and cut_value(graph,candidate)>cut_value(graph,best):
        # Keep independent original-order labels for the exact complete solve.
        best=candidate.copy()
    # Complete exact matching supplies an optimal value; interrupted matching supplies no guessed global bound.
    return result_record("planar_matching",graph,cfg,seed,budget,started,best,
                         status="time_limit" if not complete and perf_counter()>=deadline else "completed",
                         reason="complete_planar_matching" if complete else "component_limit",
                         upper_bound=total_upper_integer/scale if complete else None,
                         optimality="solver_reported_optimal" if complete else "unproven",
                         evidence={"complete_components":complete,"scale":scale,"method":"signed dual minimum T-join","matching":"integer NetworkX minimum perfect matching"},
                         counters={"completed_components":completed,"components":len(components)},history=history)
