# Calibrated simulated-annealing experiment

**Result update:** the user completed all 24 public comparisons. No schedules
were censored and no incumbent improved. See [actual results](../../experiments/sa_calibrated_01/RESULTS.md).
The following sections retain the design and preparation-time account.

The user requested a better annealing experiment after reviewing the exact runs
and discovering that previous suite-v3 annealing stages all stopped at 10000
proposals. This experiment is prepared, not run on public graphs. It preserves
the existing annealing kernel and every campaign/source contract. The new driver
is `scripts/run_sa_experiment.py`; it calls the existing `run_solver.py`.

## Diagnosis and hypothesis

Actual stage results show 97 signed-random1000 and 91 Torus100 annealing
executions, each with exactly 10000 proposals. A sweep here means n uniformly
random single-node proposals; vertices can repeat. The old cap therefore meant
10 sweeps on signed random1000 and one sweep on Torus100. Temperature cooling
was defined over those proposals, so the schedules completed very quickly.
The 97 signed-random stages totalled 10.8828 backend seconds; the 91 torus stages
totalled 41.3930 backend seconds, including their initialization/polishing.
These totals exclude process startup, admission, scoring and other backends.
They cannot be described as 97/91 sustained 30-second independent restarts.

More search per cooling schedule and several independent seeds may help escape
the current plateau. Fresh starts test different basins; warmer incumbent
refinement tests stronger diversification. These are hypotheses, not promised
improvements. [Myklebust's primary paper](https://arxiv.org/abs/1505.03068)
provides context for the importance of iteration throughput in Max-Cut SA. This
experiment uses the project's existing Python baseline, not that paper's fast
implementation or the instructor's undocumented annealing implementation.

## Declared design

Graphs are `rand_pm_1000_s23.txt` and `torus_pm_100_s31.txt`. Their frozen public
incumbents have cuts 1097 and 6878; scoring targets are 1098 and 6922. All 18
public labels and references are frozen for subsequent full-ladder evaluation.

| Condition | Start | Initial temperature | Final temperature | Seeds |
| --- | --- | ---: | ---: | --- |
| `fresh_t2` | Kernel's seeded random assignment | 2 | 0.01 | 101, 102, 103, 104 |
| `warm_t2` | Same frozen incumbent for every seed | 2 | 0.01 | 101, 102, 103, 104 |
| `warm_t6` | Same frozen incumbent for every seed | 6 | 0.01 | 101, 102, 103, 104 |

There are **12 comparisons per graph, 24 total**, plus one throughput calibration
per graph. Seeds and conditions are fixed before any comparison results. The
runner interleaves the three conditions within each seed to reduce time-order
load bias. Fresh initialization consumes random draws, so a shared seed does
not mean identical subsequent proposal streams across fresh/warm conditions.
No condition inherits another condition's improved assignment; this keeps the
comparison fixed. A separate retained-best folder harvests all valid improvements.

### Work and cooling

1. Run a 100000-proposal throughput calibration at constant temperature 6, seed
   zero, using the frozen incumbent and no greedy polish. Its worker limit is
   30s. Require all calibration proposals; incomplete/failing calibration aborts
   instead of inferring throughput from a timeout fallback.
2. Let r be completed proposals divided by measured backend seconds. With n
   vertices, choose:

   ```text
   sweeps = floor(r * 30 seconds * 0.8 / n)
   proposals = n * sweeps
   ```

   Require at least 100 sweeps. If the calibrated machine cannot support that
   budget, stop for review rather than running another tiny schedule. All
   conditions/seeds for that graph receive this same declared proposal count.
3. The existing geometric schedule cools from its configured initial temperature
   to 0.01 over exactly that many proposals. The hotter calibration and 20%
   margin reduce the risk of missing the endpoint. The comparison worker has a
   60s hard limit, providing extra room for load variation, setup and bounded
   polish. The outer driver has another 30s for CLI verification/cleanup.
4. Record actual proposals/n, accepted/worsening moves, raw and polished cuts,
   backend time, total runner time, and whether the schedule completed. A run
   completing fewer proposals is marked **censored**; it cannot enter the
   completed-schedule comparison statistics. Its independently validated witness
   can still improve the separately retained best.

Temperature and proposal endpoints are explicit. Merely setting an enormous cap
with a 30s cutoff would risk terminating while still hot because the old kernel
uses proposal-based cooling. The calibrated cap addresses that failure mode.
The 30s value is a sizing target, not a promise of actual runtime. The formula
predicts about 24s at the measured hot throughput; cooled trajectories can run
faster. Machine-load changes can still cause censoring, which must be reported.

Greedy polish remains enabled in all comparison conditions, as a separately
recorded hybrid step. `raw_cut` and `polished_cut` distinguish its contribution.
Calibration discoveries are retained but excluded from the three-condition
statistics. Neither reference attainment nor a completed cooling schedule is a
global optimality proof.

## Run locally

The default two-graph plan is already prepared at `experiments/sa_calibrated_01`.
Its baseline public score is 0.9814511551814886. Source and input hashes are
checked before execution. No numerical calibration or public comparison has
been launched by preparation.

The plan fixes the public starting cuts at preparation time. The ongoing exact
Torus100 run subsequently logged a native cut6888, but had not yet written a
verifiable final assignment at this handback. That log does not replace the
frozen cut6878 seed. If a stronger exact witness is later validated and published,
prepare a fresh experiment directory to compare from that newer baseline; do not
edit the frozen labels or their hashes inside this plan.

After the current exact attempt finishes, launch sequential execution:

```bash
uv run python scripts/run_sa_experiment.py \
  --run-dir experiments/sa_calibrated_01 --execute
```

Omit `--execute` to inspect the prepared plan without solving. To prepare a
separate signed-random-only plan, use a fresh directory:

```bash
uv run python scripts/run_sa_experiment.py \
  --run-dir experiments/sa_signed_only_01 --graphs rand_pm_1000_s23.txt
```

Add `--execute` to that command when deliberately launching it. Do not launch
both alternatives accidentally. The comparison worker ceilings total 24 minutes
for both graphs, plus calibration/parent/summary work; expected core time from
the formula is about 9.6 minutes, with actual runtime dependent on throughput.
The outer guards permit additional cleanup/validation time. This is neither an
unbounded campaign nor a model-driven search; it makes zero model calls.

### Progress and results

The console prints calibration counts and each completed attempt. From another
terminal:

```bash
watch -n 3 cat experiments/sa_calibrated_01/progress.json
```

`progress.json` identifies the active graph, condition, seed and planned work.
`summary.json` is updated after every completed attempt. It contains per-seed
results and each condition's best/median cut and reference matches. It separates
complete and censored schedules and distinguishes calibration and main timings.
`scores.json` evaluates the retained best against the **entire frozen ladder**,
not the one-file attempt folder. `best/solutions/` always retains at least the
frozen baseline. Current public labels remain unchanged.

Each `attempts/<graph>_<condition>_s<seed>/` retains the real request, runner
result, worker logs and validated assignment. Outer commands, exit codes and
result hashes are under `logs/`. Completed attempts are reused on same-plan
resume without extra numerical calls. Failed, partial or altered attempts are
refused for review, not silently rerun; preserve their evidence before choosing
another explicitly named experiment. Ctrl+C requests owned-child cleanup and
leaves partial evidence. Do not run the same experiment directory concurrently.

On class001, perform preparation/execution within a submitted allocation and
prepare a fresh cluster-specific directory after deployment reconciliation.
This local plan pins laptop source bytes and is not a portable active checkpoint.
No sudo, login-node optimization or automatic job submission is involved here.

## Verification and limits

[Evidence](../../evidence/sa_calibrated_design_01/README.md) records five focused
tests, including real generated-graph execution, endpoint completion, public
preservation, cached resume without new calls and actual hard-timeout censoring.
The generated fixture uses shortened budgets; it is not a benchmark on public
graphs. No new public SA result is claimed before the user runs this experiment.
The old kernel/config files, exact-run evidence and campaign archives are intact.
No commit, push or automatic publication occurs.
