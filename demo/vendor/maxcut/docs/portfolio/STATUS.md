# Component status — October 20, 2026

Current extension: [suite v3](SUITE_V3.md) adds `mixing`, `pt_icm`, and
`toroidal_window`, all with bounded work, retained incumbents and unproven global
optimality. The matrix below records the original portfolio phase; current test
counts and source-upgrade evidence are in [the v3 record](../../evidence/suite_v3/README.md).

All implemented entries progressed through source review, implementation, local checks and the actual one-shot shared interface. This table records the final state; raw stages/results are in [component_status.json](../../evidence/portfolio/component_status.json). Availability means installed here, not suitability for every input size.

| Method | Final stage | Actual warm-start use | Work unit | Upper bound |
|---|---|---|---|---|
| [exhaustive](exhaustive.md) | validated through shared interface | retained_incumbent | assignments | when computed |
| [bm](bm.md) | validated through shared interface | initial_refinement_center | configured complete passes | none |
| [tabu](tabu.md) | validated through shared interface | initial_state | iterations | none |
| [bls](bls.md) | validated through shared interface | initial_state | individual flips | none |
| [annealing](annealing.md) | validated through shared interface | initial_state | proposals; bounded polish separate | none |
| [lns](lns.md) | validated through shared interface | initial_state_and_fixed_boundary | neighborhoods | none |
| [milp](milp.md) | validated through shared interface | native_complete_incumbent | branch_nodes | when computed |
| [bsb](bsb.md) | validated through shared interface | replica_zero_initialization_and_retention | integration_steps | none |
| [dsb](dsb.md) | validated through shared interface | replica_zero_initialization_and_retention | integration_steps | none |
| [gsb](gsb.md) | validated through shared interface | replica_zero_initialization_and_retention | integration_steps | none |
| [sbqa](sbqa.md) | validated through shared interface | replica_zero_initialization_and_retention | integration_steps | none |
| [tesb](tesb.md) | validated through shared interface | warm_replica_zero_and_retention | total warm+checking integration_steps | none |
| [mqlib](mqlib.md) | validated through shared interface | unsupported | None | none |
| [scientific](scientific.md) | validated through shared interface | native_partition_incumbent | branch_nodes | when computed |
| [biqbin](biqbin.md) | validated through shared interface | unsupported | None | when computed |
| [madam](madam.md) | validated through shared interface | unsupported | None | when computed |
| [biqcrunch](biqcrunch.md) | validated through shared interface | unsupported | None | when computed |
| [planar_matching](planar_matching.md) | validated through shared interface | retention_only | connected_components | when computed |
| [toroidal_bound](toroidal_bound.md) | validated through shared interface | retention_only | one initial matching; no extra iterations | when computed |
| [toroidal_search](toroidal_search.md) | validated through shared interface | initial_cycle_repair_state | additional cycle_repairs | when computed |
| [qubowl](qubowl.md) | blocked — no obtainable official source | unavailable | None | when computed |

## External programs

MQLib, ScientificMaxcutSolver, BiqBin, MADAM and BiqCrunch are built and tested on signed/decimal fixtures. TESB and toroidal methods call their own pinned authors’ Python primitives. Generic MILP uses optional PySCIPOpt; local bSB/dSB/GSB/SBQA are sparse CPU implementations. [Pins/build logs](EXTERNAL_BUILDS.md) record exact identities and successful commands.

BiqBin and MADAM require seed **2020**, two MPI ranks, integer-compatible finite-decimal scaling and <=1024 nodes by default. BiqCrunch is guarded at 5000. Toroidal matching defaults to 4096 expanded vertices and a verified L×L periodic embedding, L>=3. Planar solving rejects nonplanar inputs. A toroidal bound must actually be attained before that method reports optimality.

## Blocked or limited sources

QuBowl: no official downloadable source/executable/API obtained; it is **not implemented**. Its expected unavailable smoke is not solver validation. The SMS SIAM paper, attempted author thesis, BiqCrunch 2017 TOMS paper and 2021 SB PDF were not obtained. SMS integrates actual C++ source/CLI; BiqCrunch has its official manual and earlier bounding manuscript; SB has full primary HTML reviewed. The [paper manifest](../../papers/manifest.json) records precise access failures.

## Practical limits

The original BM behavior is preserved. CPU dynamics and local BLS/tabu/SA variants have explicitly documented deviations from production paper settings. Only bounded tiny integration checks were run, with 61 regression tests and 21 explicit config smokes. No public algorithm campaign or evolutionary orchestration was started. No independently checked serialized certificate implementation is claimed. [Full verification and corrected failures](VERIFICATION.md).
