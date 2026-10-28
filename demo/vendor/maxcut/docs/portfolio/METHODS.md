# Illustrated method guides

New methods: [conditional torus windows](SUITE_V3.md#toroidal_window),
[parallel tempering and cluster moves](SUITE_V3.md#pt_icm), and
[higher-rank Mixing](SUITE_V3.md#mixing). Earlier methods remain available.

Each guide covers inputs, intuition, equations, steps, a worked example, figures, controls, cost, proof limits, source mapping, a run command and deviations.

| CLI name | Method |
|---|---|
| [exhaustive](exhaustive.md) | Exhaustive search |
| [bm](bm.md) | Preserved rank-two Burer–Monteiro solver |
| [tabu](tabu.md) | Discrete one-flip tabu search |
| [bls](bls.md) | Breakout Local Search |
| [annealing](annealing.md) | Simulated annealing comparison baseline |
| [lns](lns.md) | Large-neighborhood search with exact conditional repair |
| [milp](milp.md) | Generic exact XOR MILP using SCIP |
| [bsb](bsb.md) | Ballistic simulated bifurcation |
| [dsb](dsb.md) | Discrete simulated bifurcation |
| [gsb](gsb.md) | Generalized ballistic simulated bifurcation |
| [tesb](tesb.md) | Authors’ Tabu-Enhanced Simulated Bifurcation |
| [sbqa](sbqa.md) | Simulated Bifurcation Quantum Annealing |
| [mqlib](mqlib.md) | MQLib independent heuristic portfolio |
| [scientific](scientific.md) | ScientificMaxcutSolver exact integration |
| [biqbin](biqbin.md) | BiqBin semidefinite branch-and-bound |
| [madam](madam.md) | MADAM semidefinite exact integration |
| [biqcrunch](biqcrunch.md) | BiqCrunch semidefinite branch-and-bound |
| [planar_matching](planar_matching.md) | Exact signed planar matching reduction |
| [toroidal_bound](toroidal_bound.md) | Toroidal face-parity upper bound |
| [toroidal_search](toroidal_search.md) | Toroidal cycle-repair search |
| [qubowl](qubowl.md) | QuBowl availability investigation — blocked |

[Contract and commands](ARCHITECTURE.md) · [Shared mathematics](MATHEMATICS.md) · [Validation](VERIFICATION.md) · [Current status](STATUS.md)
