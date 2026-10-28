# Verification and honest limitations — October 20, 2026

The latest [concurrent execution report](CONCURRENT_CAMPAIGNS.md) documents the
user-requested no-commit/private-output mode and explicit public consolidation.
Initial implementation/live-check evidence below is historical and retains its
original commit and preservation claims for that phase.

This page records the original implementation/live-check evidence, before the
user's subsequent public campaign. Later admission maintenance passes **103
tests**, preserves that campaign and its cut-1097 archive, and does not launch
another public search. See the [admission follow-up](ADMISSION_FIXES.md) for
current tests, precise score-folder labels and pinned-version compatibility.

The framework, deterministic fixtures and **bounded real Codex integration are verified**. After the user upgraded to CLI 0.163.0, one real model call proposed inherited parameter/state-policy variants and the scratch campaign reached its verified target. The earlier 0.114.0 compatibility failure is preserved below as historical evidence. No public optimization campaign was started; the public ladder score is unchanged.

## Baseline and complete regressions

Starting HEAD was `a19c75865983911186e26af417519e8dfd5d6f84`, with ancestry confirmed and no reset. The supplied evolution brief was the only original untracked file. [Starting identities](../../evidence/evolution/baseline_identity.json), [61-test rerun](../../evidence/evolution/baseline_tests.txt) and [full retained-set scoring](../../evidence/evolution/baseline_scores.json) were captured before implementation.

The final command was:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

**91 tests pass**: the 61 original tests plus 30 focused framework tests, in 35.441 seconds in this recorded run. [Raw output](../../evidence/evolution/final_tests.txt) preserves actual counts and timings. Earlier failed verification runs are retained alongside fixes; they are not relabeled successes. The synced `.venv` interpreter was used because this outer sandbox cannot launch the host's Snap `uv`; normal user commands remain `uv run python …`.

| Requirement | Actual checks in `tests/test_evolution.py` |
|---|---|
| Already achieved target | Committed initialization, zero model/solver work |
| Two inherited ordinary rounds | Actual numerical workers, selection, inherited source, three local round commits |
| Worse prestate / monotone archive | Saved working cuts 8→7→10; retained archive 8→8→10 |
| Unselected useful witness | Independent official scoring and harvesting despite parent ineligibility |
| Dishonest/invalid result | False cut, bad signs, caller mutation, corrupted artifact, protected evaluator edit, unsafe source path |
| Codex failure cases | Missing executable, malformed schema/JSON, one correction, two rejections, call quota, real fake-CLI process timeout |
| Actual capabilities | Fixed seed 2020, unsupported native warm starts, torus topology and expanded-size guards |
| Comparable evaluation | Common frozen labels/budgets, changed archive triggers fresh state-sensitive work, exact-condition replay deduplicated |
| Early success | Remaining comparisons censored, target publication and local commit |
| Full official scoring | Fresh complete folders, missing other assignments remain failures, unequal-rung delta relation |
| Honest target/proof | No epsilon/rounding success, exact/float discrepancy review, unproven bound not a certificate |
| Interruption / Git recovery | Actual SIGINT and descendant timeout, fast launcher orphan, prepared reservation, partial promotion, before/after commit crashes, manifest corruption |
| No collateral user mutation | Global lock, unique paths, destination/metadata CAS, no degradation, symlink escape refusal, unrelated staged file preserved |
| Committed unedited logs | Both inherited rounds' actual Git trees contain artifacts/logs; gzip decompresses to exact original bytes |
| Aggregate stage limits | Reject excessive fractions and unequal clipped trials; actually execute two split-budget stages |
| Real CLI surface | Actual doctor/plan/status/stop/resume subprocesses on temporary repositories |

These tests establish mechanics and consistency, not that any public graph will reach target within a finite budget. The existing native portfolio's own tests still provide its method-specific coverage; new framework fixtures do not repeat a full public native campaign.

## Saved successful fixtures and actual commits

[Target fixture receipt](../../evidence/evolution/fixture_checked/verification.json) uses the explicitly named `fixture-test` provider. Its checked active runtime is 3.322 seconds. The checked run executes three candidate trials, eight admission examples, one fixture protocol turn, and zero real Codex calls. Actual checked commits are:

| Run | Round | Actual local commit |
|---|---:|---|
| Target fixture | 0 | `350c8a12f492d6cf4202822744cf224820b16c3a` |
| Target fixture | 1 | `502aee347ceae4dd5d1e19ee6f1bbd7b34e84dfd` |
| Two-round fixture | 0 | `c62a56d1b4b8819571c9b486af012b046b411a5e` |
| Two-round fixture | 1 | `20a4afaf4b38a83d2644d540a5ea1d52eb83702f` |
| Two-round fixture | 2 | `fed92beb56dc19caae4d33dc6bd85d950b4f37df` |

The [two-round receipt](../../evidence/evolution/inherited_checked/verification.json) deliberately requests score 1.1, stops `round_budget_exhausted`, and archives cut 10. Its checked active runtime is 9.259 seconds. It records nine candidate trials, sixteen admission example calls, two fixture turns and no real model call. This is actual inherited control-flow testing, not a claim the impossible toy target was attained. Sources and three raw streams per turn are in its exported archive and actual round Git history.

[Figure source data](../../evidence/evolution/figure_trace.json) comes from the checked target fixture. The selector flips original node 0 (A), symmetry-equivalent to flipping B in the brief. All three schematic figures are labeled conceptual; only the trap figure plots saved numerical observations. `scripts/build_evolution_guides.py` regenerates them from current discovery and original saved JSON, including exported-archive reading.

Scratch repositories are exported losslessly with [an archive index](../../evidence/evolution/scratch_exports.json), verified Git bundles and original worktree/Git metadata tarballs. This avoids accidentally adding nested `.git` repositories as gitlinks. To inspect the checked history without touching this root repository:

```bash
git clone evidence/evolution/inherited_checked/history.bundle /tmp/inherited-history-review
# To recover its exact final checkpoint too, unpack repository.tar.gz in a fresh directory.
```

Absolute paths inside original raw records describe their actual execution location and are not rewritten to appear portable. Native builds remain separately pinned prerequisites from this repository; restore paths deliberately before attempting to resume an exported fixture. These are completed scratch checks, not public campaign checkpoints.

## Actual Codex smoke: original failure and resolved follow-up

The original smoke used `/snap/bin/codex` **0.114.0**. Host read-only version/help/doctor probes passed; [host doctor](../../evidence/evolution/doctor_host.json) reports no live call, and actual [exec help](../../evidence/evolution/codex_exec_help.txt) confirms `--json`, `--output-schema`, `--output-last-message`, `--cd` and `--sandbox`. CLI construction follows the locally verified flags and [official noninteractive documentation](https://developers.openai.com/codex/noninteractive/) and [CLI reference](https://developers.openai.com/codex/cli/reference/). Existing model/profile/reasoning and authentication are inherited; no bypass or replacement account is introduced.

The bounded scratch smoke had two total launch attempts across distinct preserved scratch outputs. The first returned empty streams when Snap inherited regular files. A pipe-capture diagnostic established and corrected that launch/capture issue. The second reached the real service and emitted:

```text
failed to decode models response: unknown variant `max`, expected one of
`none`, `minimal`, `low`, `medium`, `high`, `xhigh`
```

The [original live receipt](../../evidence/evolution/live_smoke/verification.json) remains `awaiting_codex`, with one reserved real call attempt in that scratch campaign, one screening numerical trial, no admitted child and no final model response. Its actual screening and blocked-round commits are `dfe63d1e1a473bd97aeb0beecf0c268811db0419` and `63357160df5a91d18617b68789538cc69258a290`. The final JSON file is empty, not a model proposal. Model usage/cost cannot be inferred from failed catalog access. Raw stderr is large because the CLI dumped the model-catalog response; it is preserved unedited and gzip-verified.

That original failure was a client/catalog incompatibility. The user subsequently installed the official npm CLI and reported `codex-cli 0.163.0`; the active binary is `/home/mht/.local/bin/codex`. An authorized bounded follow-up now passes through the production bridge, admission checks, paired numerical evaluation, scoring, target publication in the scratch repository and actual local commits. The [follow-up report](../../evidence/evolution/cli_update_0163/README.md), [verification receipt](../../evidence/evolution/cli_update_0163/live_check/verification.json) and raw streams preserve this new result separately.

One actual CLI call took 27.057 seconds; total active scratch campaign time was 33.038 seconds. It proposed tenure 2; tenure 1 with restart interval 4; and a uniform two-node binary state policy. All three children passed eight signed/ownership examples each. Parent and both parameter children returned cut 8; the state-policy child selected nodes `[0, 2]`, reached pre-cut 10, and bounded tabu refinement retained cut 10. The remaining four scheduled repeats were censored after target success. This is configuration/policy mutation evidence; no new Python search kernel was proposed. The 8→7→10 figure still shows the earlier explicit fixture, not this live trace.

The run used one real call, zero fixture turns, five numerical trials and 29 reserved solver/check slots under the cap of 30. Actual scratch commits are screening `32599be966fd01dcf74002c788a321c127f0965e` and mutation `c7c521e1a5f93a300b69c3b2ab22b82b99f9ca04`. The full raw CLI stream and generated schema response are preserved under `logs/evolution/integration-cli0163/`, with the losslessly exported scratch repository and Git bundle under the follow-up evidence directory. A featured-plugin cache warning was nonfatal: CLI exit was zero and its structured response passed verification. No model/reasoning/profile override, permission bypass, public optimization, remote push or tag change was made.

## Preservation and limits

The retained complete 18-graph set still scores **0.9713800081806563**, with rungs `[1.0, 0.9999116211844504, 0.9745366308953478, 0.9422224369775468, 0.940229351845936]`. [Final audit](../../evidence/evolution/final_audit.json) checks all originally tracked bytes, except the explicitly updated process/log index whose original content is preserved. Official instances/references/scorer/visualizer/README/problem, portfolio code/configs, upstream tracked files and existing solution folders remain unchanged. Current score includes the retained improvements for all eighteen graphs.

[Actual capabilities](CAPABILITIES.md) and the [read-only one-graph plan](../../evidence/evolution/public_plan_only.json) show exclusions without running public optimization. Linux Bubblewrap, `/proc`, file locks and subreaper support are required; unavailable isolation blocks research-code execution. Candidate code scope is intentionally narrower than unrestricted Python. This is not a hostile-code security guarantee or a new independent certificate checker. Certification-after-target is explicitly rejected as unimplemented.

Budgets gate launches, share numerical/verification allocations, reserve finalization time, and record actual active elapsed costs. Cleanup and durable filesystem/Git work can exceed estimates; observed overrun cannot establish a completed fair comparison. No hard real-time deadline is promised for OS I/O. Missing other labels remain visible official failures. A target match stops promptly but does not imply proof, and any finite campaign may stop below its target.
