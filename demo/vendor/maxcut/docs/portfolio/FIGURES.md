# Figures and how to inspect them

Open these SVG files in VS Code's image preview or a browser. They are static mathematical teaching figures. The professor's interactive graph explorer remains the unchanged `viz.py`; launch it with `uv run --extra viz viz.py both --instance ... --assignment ...`. These two kinds of visualization serve different purposes.

The three earlier BM figures are preserved unchanged: [signs/vectors](../figures/bm_arrows.svg), [coordinate update](../figures/bm_coordinate.svg), [rounding normal and perpendicular line](../figures/bm_rounding.svg).

| New figure | Kind and source |
|---|---|
| [Worsening escape](figures/escape.svg) | Measured seed-7 tabu trajectory from cut-eight local trap; current and retained best are separate. |
| [Tabu memory](figures/tabu_memory.svg) | Conceptual tenure-two timeline; default solver tenure is 20. |
| [Adaptive strength](figures/adaptive.svg) | Conceptual deterministic controller inputs: threshold 3, multiplier 2, cap .8, improvement at observation 9. |
| [Ballistic trajectory](figures/bsb_trajectory.svg) | Actual first two node coordinates of replica zero, seed 4, 100 integration steps. |
| [GSB trajectory](figures/gsb_trajectory.svg) | Same measured setup, with its distinct nonlinear pump. |
| [Replica interactions](figures/replicas.svg) | Conceptual independent columns versus a periodic SBQA ring; no invented performance data. |
| [Branch and bound](figures/branch_bound.svg) | Conceptual four-node trap, conditional optima 8 for A=B and 10 for A≠B, global positive-edge bound 14. |
| [Bounds closing](figures/bounds.svg) | Actual BiqCrunch trap root bound and completed primal/dual; two observations, not an invented time trace. |
| [Torus wraps](figures/torus.svg) | Conceptual 3×3 original row-major topology; representative horizontal/vertical wraps highlighted, all rows/columns wrap. |
| [Boundary repair](figures/neighborhood.svg) | Hand-computable released node with +2 boundary and +3 fixed outside constant. |

Regenerate the ten new figures and bounded learning traces with:

```bash
uv run python scripts/make_portfolio_figures.py
```

The script runs only the four-node learning fixture, at most 100 work units per method. It rewrites its own generated portfolio SVG/learning-trace files, preserving prior BM figures, old experiments and official files. Numerical evidence is [`learning_traces.json`](../../evidence/portfolio/learning_traces.json), and the bound endpoints come from the preserved raw `shared_validation/biqcrunch_trap/native/backend.log` and its result JSON. Geometry and labels are standard-library SVG, not raster image generation.

Visual QA rendered the new SVGs and inspected a contact sheet plus the escape, replica and torus panels at full size. Equation pages from the primary GSB and SBQA PDFs were also rendered to check update order, axes and factors against the source. The verification script separately checks SVG XML, links, graph optima, equations and numerical evidence; visual inspection alone cannot establish solver correctness.
