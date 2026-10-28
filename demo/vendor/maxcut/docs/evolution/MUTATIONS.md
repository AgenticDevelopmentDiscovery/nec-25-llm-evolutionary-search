# What actually evolves

Numerical state perturbation changes a partition or angles. Algorithm mutation changes the recipe that performs search. Both can be useful; only changing the seed of unchanged code is not evidence that an agent designed a variant.

A child records its actual current parent IDs, hypothesis, category, changed configuration keys, complete optional source, policy, stages, expected effect, required checks and resource estimate. The controller checks these against the parent bytes and real interfaces. The full strict response schema is in `evolution_codex.py`; it is copied into each raw call record.

| Category | Example | Required distinction |
|---|---|---|
| `parameter` | tabu tenure 0 → 2 | Config only; code/policy inheritance is preserved |
| `state_policy` | binary count 1 → 2 | A real initialization-policy change, without pretending code changed |
| `algorithm_policy` | choose boundary nodes instead of uniform nodes | Complete isolated numerical hook/policy; code and hypothesis are reviewable |
| `backend_switch` | tabu → existing annealing | Existing method switch, not an invented new optimizer |
| `recombination` | two actual parents, at most two stages | Actual lineage and one split aggregate allowance |

The fixture's parent uses the validated tabu backend with tenure 0 and no state perturbation. The first inherited child adds `{"representation":"binary","count":1}` and this numerical selector (complete saved code in the fixture artifact):

```python
# Keep this deterministic one-node choice explicit in the tiny trap example.
def choose_nodes(graph, signs, rng, policy):
    """Return one original node ID for a fixture perturbation; no mutation or I/O.

    Inputs graph/signs/RNG/policy; returns [0]. Intended for four-node trap
    and signed-example regression checks. The controller validates scope.
    """
    # Flipping A leaves the cut-eight local optimum through a cut-seven prestate.
    return [0]
```

This code illustrates the actual hook contract; the raw saved fixture source remains the authoritative bytes. Its hypothesis is that a controlled worse prestate permits the one-step local refinement to reach a different basin. The saved observation confirms cut 7 before refinement and cut 10 afterward. The second fixture round changes tenure to 2 while inheriting that selector and policy. A deliberately higher target of 1.1 permits testing two inherited rounds without pretending the toy can exceed its exact optimum.

Custom `search(graph, config, seed, budget, initial)` hooks may replace numerical local-heuristic strategy. The returned assignment/cut/work counters are independently checked; they cannot emit proof/status/bound fields. Graph and input arrays must remain unchanged. Use `budget['seconds']` and `budget['max_work']`; the external process deadline enforces time even if research code fails to cooperate. Arbitrary custom counters are reported values, not independent proof of work units.

Research edits are restricted to complete `variant.py` source and validated config/policy data. Imports are numerical and narrowly checked. Objective/scorer, original graph, archive, selection, promotion, proof classification, cleanup and Git/logging are protected. Exact/native algorithms cannot be relabeled custom heuristic hooks; unsupported native starts cannot silently receive ignored perturbations. Comment/docstring-only changes produce the same semantic identity and are rejected as duplicate novelty. Module bytes must match both their source hash and reconstructed semantic identity before execution.

Each new child passes actual bounded tests on +2/-2 edges, triangle, cycle, weighted/mixed-signed triples and the four-node trap, including ownership/scope checks. Passing tiny tests establishes the contract, not public-graph performance or convergence.

The current validator accepts real preceding or inline explanatory comments,
including closing-line comments on multiline statements. Every statement and
compound header still needs its own explanation. The model receives the complete
known-candidate catalogue. Valid novel children survive a mixed batch containing
duplicates; duplicate handles are recorded and skipped without numerical work.
An entirely duplicate continuation still needs correction or an honest stop.
See the [failure analysis, regression evidence and saved-campaign compatibility
notes](ADMISSION_FIXES.md) before applying this version to an existing campaign.
