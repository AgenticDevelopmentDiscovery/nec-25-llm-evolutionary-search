# Validated Max-Cut solver portfolio

Current [suite v3](SUITE_V3.md) adds topology-aware admission, equal 120s screening,
four MQLib initial configurations and three sparse search backends. It has 23
runnable entries plus the explicitly unavailable QuBowl entry. Earlier counts
and scores below describe the original portfolio validation phase.

The portfolio adds **20 runnable solver entries** with one shared contract while preserving the existing BM pipeline and solutions. **QuBowl is explicitly blocked** because no official source was obtained. Optional methods retain their actual topology, size, native-seed and warm-start restrictions.

Start with [the basic architecture and data flow](ARCHITECTURE.md), then [the illustrated method index](METHODS.md). The [status matrix](STATUS.md) distinguishes implementations, tests, paper access and blocked work. [Verification](VERIFICATION.md) records actual results and corrected failures; [build instructions](EXTERNAL_BUILDS.md) reproduce the separate native environment.

```bash
uv run python run_solver.py --list
uv run python run_solver.py --solver tabu --features
uv run python run_solver.py --solver tabu \
  --instance instances/public/rand_pm_1000_s23.txt \
  --config configs/portfolio/tabu.json --seed 1 \
  --time-limit 60 --max-work 10000 --output runs/tabu_example_01
```

Every run needs a new output path. Inspect `result.json`, `worker.log`, any native logs and its independently checked original-format assignment. A valid time-limited answer is useful; it is distinct from an optimality proof. The professor's unchanged interactive visualizer can open that assignment:

```bash
uv run --extra viz viz.py both \
  --instance instances/public/rand_pm_1000_s23.txt \
  --assignment runs/tabu_example_01/solutions/rand_pm_1000_s23.txt
```

The [math guide](MATHEMATICS.md) derives signs, gains, XOR MILP, integer scaling and bounds. [Perturbation functions](PERTURBATIONS.md) are prepared explicit variants for future experiments. [Figures](FIGURES.md) separate conceptual diagrams from actual numerical traces. The [paper collection](../../papers/README.md) has 17 verified full PDFs, with inaccessible sources and alternate primary HTML clearly recorded. [Source reading notes](SOURCE_REVIEW.md) disclose implementation deviations rather than treating an algorithm's name as proof of fidelity.

Only bounded validation was run in this phase. The full retained public-set fitness remains **0.9713800081806563**, independently rechecked over all 18 instances; these new test fixtures do not replace any earlier solution.
