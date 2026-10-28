"""Step 13: explicit selected-graph BM profiles with immutable common baselines."""

# argparse requires actual instance and seed lists instead of launching an automatic grid.
import argparse
# JSON reads fixed references and records every profile's actual measured result.
import json
# math validates the fixed reference denominator rather than inventing missing scores.
import math
# Path names fresh per-profile directories and common baseline snapshots.
from pathlib import Path
# subprocess invokes the actual CLI, capturing each profile's stdout/stderr as evidence.
import subprocess
# sys.executable keeps each child in the same installed Python/NumPy environment.
import sys
# Wall-clock timing includes child startup and output verification, not just the inner solver.
from time import perf_counter

# The settled graph/assignment routines keep the original mathematics and data order.
from bm_solver import load_graph, write_assignment
# Official input and cut routines supply the same signed-weight normalization used at grading.
import evaluate as official
# Reuse file validation, identity, safe persistence, and finite JSON helpers rather than duplicating them.
from run_bm import atomic_json, code_identity, file_sha256, load_assignment, protect_destination

# Each pair is (TOTAL starts M, ADDITIONAL rounds P per start); three enhanced settings cost four passes.
PROFILES = {"baseline": (1, 0), "perturb_only": (1, 3), "restart_only": (4, 0), "combined": (2, 1)}


# Missing references are honest absences, while invalid available scoring data is an explicit failure.
def normalized_score(cut, half_weight, reference):
    """Step 13: return (cut-W/2)/(ref-W/2), or None when ref is unavailable.

    cut and half_weight are finite floats in weight units, reference is finite
    float or None. Example (8,4.5,8) gives 1.0. A zero/nonfinite denominator
    raises ValueError. No mutation, O(1). None is reported as not_available.
    """
    # Absence is distinct from a zero reference or a failed candidate.
    if reference is None:
        # Never invent a reference value from the best result in this comparison.
        return None
    # Validate the actual fixed normalization scale before division.
    denominator = reference - half_weight
    # Infinite, NaN or zero denominators cannot define the instructor's score.
    if not math.isfinite(denominator) or denominator == 0:
        # This describes a scoring-data error rather than optimization failure or score zero.
        raise ValueError("scoring-data error: invalid reference denominator")
    # Preserve signed weights and the exact specified normalization.
    result = (cut - half_weight) / denominator
    # Finite JSON must not conceal an overflowed normalized score.
    if not math.isfinite(result):
        # A nonrepresentable score is a scoring-data failure, not a guessed replacement value.
        raise ValueError("scoring-data error: normalized score is not finite")
    # Return the actual specified normalization once its finite representation is established.
    return result


# Selection happens after all profiles and never changes the common baseline during their runs.
def choose_setting(records, baseline_cut):
    """Step 13: choose quality first, measured runtime on ties, avoiding useless escalation.

    records is this graph's list[dict(profile,seed,cut,wall_seconds,...)];
    baseline_cut is the immutable common assignment's official cut. Return a
    copied winning dict or None if no result strictly improves that assignment.
    If no enhanced profile beats the best one-pass baseline, select a baseline
    result rather than escalating work. Among eligible equal cuts, use the
    smallest observed wall time. No file writes/mutation; O(number of trials).
    This observational tie rule is not a statistical runtime-superiority claim.
    """
    # Read the one-pass baseline's best observed cut across the explicit pilot seeds.
    baseline_best = max(row["cut"] for row in records if row["profile"] == "baseline")
    # Identify the best observed enhanced cut without averaging different graph scales.
    enhanced_best = max(row["cut"] for row in records if row["profile"] != "baseline")
    # Only a measured strict quality advantage justifies selecting extra passes here.
    allow_enhanced = enhanced_best > baseline_best
    # Keep eligible candidate records separate from the caller's immutable measurement list.
    eligible = []
    # Review all seeds independently, rather than silently carrying their improvements forward.
    for row in records:
        # Baseline-only selection avoids expensive settings when the enhanced calls offered no quality gain.
        if row["profile"] == "baseline" or allow_enhanced:
            # A common incumbent wins ties because it was already available before this experiment.
            if row["cut"] > baseline_cut:
                # Append the measurement record without changing its values.
                eligible.append(row)
    # No improvement means preserve previous settings and solution, without automatic escalation.
    if not eligible:
        # The common baseline is selected conceptually, not overwritten by a tied profile file.
        return None
    # Start with one measured eligible result, without changing the caller's list order.
    selected = eligible[0]
    # A simple comparison makes the quality-first/runtime-tiebreak policy explicit.
    for row in eligible[1:]:
        # Prefer a higher cut, or a shorter observed full-call runtime at exactly equal quality.
        if row["cut"] > selected["cut"] or (row["cut"] == selected["cut"] and row["wall_seconds"] < selected["wall_seconds"]):
            # Keep a reference only until returning an independent small dictionary copy.
            selected = row
    # Copy the winning dictionary so later metadata additions cannot mutate source measurements.
    return selected.copy()


# This fixed comparison harness is separate from any future agentic evolutionary framework.
def main(argv=None):
    """Step 13: compare four named profiles on explicit instances/seeds only.

    argv is list[str] or None. Return None; create a fresh --run-dir with
    common snapshots, per-profile/seed assignments, CLI histories/stdout, a
    comparison.json table, and selected_settings.json. --baseline-dir optionally
    supplies the same immutable assignment to EVERY profile; otherwise all run
    from scratch consistently, with all-plus cut zero as the displayed common
    raw-difference origin. Example: --instances toy.txt --seeds 0 42.
    Work is 13 complete passes per graph/seed (1+4+4+4), with different runtime
    per pass. No full-ladder aggregate, automatic graph discovery, or promotion
    into prior solution folders is performed. File work is linear in inputs.
    """
    # Keep the interface small and require the caller's selected-graph intent explicitly.
    parser = argparse.ArgumentParser(description=__doc__)
    # nargs='+' requires at least one actual path instead of silently traversing the ladder.
    parser.add_argument("--instances", nargs="+", required=True, type=Path)
    # A small explicit seed list is a pilot policy, not an automatic configuration grid.
    parser.add_argument("--seeds", nargs="+", required=True, type=int)
    # Refuse directory reuse so later profiles cannot inherit stale outputs.
    parser.add_argument("--run-dir", required=True, type=Path)
    # Every selected graph must have a matching valid common file when this option is supplied.
    parser.add_argument("--baseline-dir", type=Path)
    # Missing references are allowed and recorded explicitly; available values remain fixed.
    parser.add_argument("--refs", type=Path, default=Path("references/public.json"))
    # The core defaults are unchanged; bounded pilots can explicitly lower these budgets.
    parser.add_argument("--max-sweeps", type=int, default=200)
    # All profiles use the same normal count so their outer-loop differences remain visible.
    parser.add_argument("--roundings", type=int, default=32)
    # Every perturbation profile shares one fixed uniform half-width in radians.
    parser.add_argument("--perturb-scale", type=float, default=0.35)
    # Parse shell arguments or a test's explicit list through the same real interface.
    args = parser.parse_args(argv)
    # Expected input errors leave old files untouched and do not claim completed experiments.
    try:
        # A fresh run identifier is required even if earlier profile outputs would happen to match.
        if args.run_dir.exists():
            # Do not delete, resume, or quietly reuse an old comparison directory.
            raise ValueError("run-dir already exists; choose a fresh comparison identifier")
        # All explicit seeds must be nonnegative and unique; repeated measurements require a new run ID.
        if min(args.seeds) < 0 or len(set(args.seeds)) != len(args.seeds):
            # Avoid silently treating duplicate seeds as independent pilot evidence.
            raise ValueError("seeds must be distinct nonnegative integers")
        # Counts and scale retain the same units/ranges as the single-instance CLI.
        if args.max_sweeps < 0 or args.roundings < 1 or not math.isfinite(args.perturb_scale) or not 0 <= args.perturb_scale <= math.pi:
            # Fail before creating directories or running a child.
            raise ValueError("invalid sweeps, roundings, or radian perturb-scale")
        # Separate profile filenames are keyed by persistent basenames, so collisions must be explicit errors.
        if len({path.name for path in args.instances}) != len(args.instances):
            # Do not merge two different graphs that happen to share a filename.
            raise ValueError("selected instance basenames must be unique")
        # A missing reference table is data absence rather than a guessed score.
        references = {}
        # Read the selected fixed reference file only when it is actually available.
        if args.refs.exists():
            # The caller may pass a separate tiny-reference fixture without changing official references.
            references = json.loads(args.refs.read_text(encoding="utf-8"))
        # Store small immutable per-graph facts; avoid holding every large graph's adjacency at once.
        cases = []
        # Validate every selected graph/baseline/scoring datum before starting any comparison.
        for path in args.instances:
            # Protect fixed repository sources even if a run-dir was accidentally selected within them.
            protect_destination(args.run_dir / "comparison.json", path)
            # A valid fixed graph is required; missing inputs fail with their actual filename.
            graph = load_graph(path)
            # Hash raw input bytes to identify all attempts unambiguously.
            digest = file_sha256(path)
            # Official arrays supply W/2 under the same floating summation used by evaluate.py.
            n, i, j, weights = official.load_instance(str(path))
            # Preserve the sum of SIGNED weights, not absolute weights.
            half = float(weights.sum()) / 2.0
            # Missing keys remain unavailable, not an estimated optimum.
            reference = None if path.name not in references else float(references[path.name]["ref"])
            # Check normalization now, before spending optimization work or writing output directories.
            normalized_score(0.0, half, reference)
            # From-scratch comparisons consistently have no supplied incumbent.
            common_path = None
            # Raw all-plus cut zero is an explicit origin for displayed differences in from-scratch mode.
            common_cut = 0.0
            # A user baseline is validated identically before ALL profiles use an immutable snapshot.
            if args.baseline_dir is not None:
                # Preserve the selected graph's original expected filename.
                common_path = args.baseline_dir / path.name
                # Recompute its current graph cut and validate any available matching metadata.
                signs, direct_cut, info = load_assignment(common_path, graph, digest)
                # Use official summation for both the common difference origin and profile output reporting.
                common_cut = official.cut_value(i, j, weights, signs)
            # Record only scalar metadata/path identities until this graph's serial profile runs begin.
            cases.append({"instance": str(path), "instance_key": path.name, "input_sha256": digest,
                          "half_weight": half, "reference": reference, "common_cut": common_cut,
                          "common_source": None if common_path is None else str(common_path),
                          "common_source_sha256": None if common_path is None else file_sha256(common_path)})
        # Creation is exclusive; old work remains untouched if this identifier is already in use.
        args.run_dir.mkdir(parents=True, exist_ok=False)
        # No selected-subset average is mislabeled as a whole-ladder fitness.
        report = {"scope": "selected instances only; no full-ladder aggregate", "budget": "fixed pass counts, NOT matched time",
                  "baseline_mode": "from_scratch" if args.baseline_dir is None else "common_immutable_assignment",
                  "seeds": args.seeds, "max_sweeps": args.max_sweeps, "roundings": args.roundings,
                  "perturb_scale_radians": args.perturb_scale, "profiles": PROFILES,
                  "code_identity": code_identity(), "cases": cases, "results": []}
        # Configuration recommendations describe measured selections, not an automatic future search policy.
        choices = {"policy": "quality first; observed runtime tiebreak; do not escalate if no enhanced cut beats baseline",
                   "unselected_graphs": "retain prior settings and files unchanged", "instances": {}}
        # Process graphs serially so no parallel execution or hardware scheduling is hidden.
        for case in cases:
            # The selected filename remains stable across every profile and explicit seed.
            path = Path(case["instance"])
            # A snapshot prevents a later profile from inheriting a previous profile's improved output.
            snapshot = None
            # Every profile either receives this same snapshot or consistently starts from scratch.
            if case["common_source"] is not None:
                # Load only this graph's structure at this point, keeping memory bounded by one case.
                graph = load_graph(path)
                # Check that the common source has not changed since prevalidation.
                if file_sha256(case["common_source"]) != case["common_source_sha256"]:
                    # A changing baseline would invalidate the controlled comparison.
                    raise ValueError("common baseline changed during comparison")
                # Re-validate labels for the current graph before making a run-local snapshot.
                signs, value, info = load_assignment(Path(case["common_source"]), graph, case["input_sha256"])
                # Snapshot files are selected new outputs, never the user's original solution.
                snapshot = args.run_dir / "common_baseline" / path.name
                # Reuse the exact signed-line format; no profile writes to this path afterward.
                write_assignment(snapshot, signs, graph)
                # Save a snapshot hash to check immutability after all child runs.
                case["snapshot_sha256"] = file_sha256(snapshot)
            # Every named profile uses every explicit pilot seed independently.
            for profile, counts in PROFILES.items():
                # Unpack TOTAL starts and additional rounds per start.
                restarts, rounds = counts
                # A new child is started for each explicit seed, never initialized from earlier profile output.
                for seed in args.seeds:
                    # Separate directories expose profile identity and prevent accidental stale reuse.
                    profile_dir = args.run_dir / profile / f"seed_{seed}"
                    # Each generated assignment keeps the selected instance's basename.
                    output = profile_dir / "solutions" / path.name
                    # Full CLI histories preserve per-attempt seeds, timings, gains, and retention outcomes.
                    history = profile_dir / "histories" / (path.stem + ".json")
                    # The same core settings and perturbation scale are explicit in every profile call.
                    command = [sys.executable, str(Path(__file__).with_name("run_bm.py")),
                               "--instance", str(path), "--output", str(output), "--history", str(history),
                               "--seed", str(seed), "--max-sweeps", str(args.max_sweeps),
                               "--roundings", str(args.roundings), "--restarts", str(restarts),
                               "--perturb-rounds", str(rounds), "--perturb-scale", str(args.perturb_scale)]
                    # Warm comparisons use exactly the same copied labels for every profile/seed.
                    if snapshot is not None:
                        # No profile output is ever passed as another profile's input.
                        command.extend(["--initial-assignment", str(snapshot)])
                    # The wall measurement includes subprocess startup, solve, verification, history write, and console output.
                    started = perf_counter()
                    # Capture real child text rather than manufacturing an experiment transcript.
                    completed = subprocess.run(command, check=True, capture_output=True, text=True)
                    # Different convergence/local-search work makes equal pass counts unequal elapsed times.
                    wall_seconds = perf_counter() - started
                    # Child history is actual measured evidence, not a substitute for checking the saved file.
                    child = json.loads(history.read_text(encoding="utf-8"))
                    # Corroborated output cut comes from the unchanged official saved-label evaluator.
                    value = child["official_verification"]["cut"]
                    # Count actual completed passes and reject a mislabeled/incomplete profile.
                    if child["total_passes"] != restarts * (1 + rounds):
                        # A failed budget identity cannot enter a controlled profile comparison.
                        raise ValueError("profile pass-count mismatch")
                    # Score only where a fixed corresponding reference was actually supplied.
                    score = normalized_score(value, case["half_weight"], case["reference"])
                    # Preserve actual subprocess output alongside its history and assignment.
                    stdout_path = history.with_suffix(".stdout.txt")
                    # Both stdout and stderr are text returned by the actual completed child.
                    stdout_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
                    # Raw improvement and runtime have separate units and are never merged into one score.
                    row = {"instance": path.name, "seed": seed, "profile": profile,
                           "restarts": restarts, "perturb_rounds": rounds, "total_passes": child["total_passes"],
                           "cut": value, "common_baseline_cut": case["common_cut"],
                           "difference": value - case["common_cut"], "score": score,
                           "score_status": "not_available" if score is None else "available",
                           "wall_seconds": wall_seconds, "solver_seconds": child["runtime_seconds"],
                           "output": str(output), "history": str(history), "stdout": str(stdout_path)}
                    # Include every completed outcome, even when it ties or loses against another setting.
                    report["results"].append(row)
                    # Partial progress remains honest evidence if a later child fails or is interrupted.
                    atomic_json(args.run_dir / "comparison.json", report)
                    # Compact console output exposes the actual graph/seed/profile budget and measured result.
                    print(f"{path.name} seed={seed} {profile}: F={value:.12g}; passes={row['total_passes']}; wall={wall_seconds:.6f}s", flush=True)
            # Source and run-local baseline must remain immutable throughout all profile calls.
            if snapshot is not None:
                # Verify both the user file and shared snapshot after the independent runs complete.
                if file_sha256(snapshot) != case["snapshot_sha256"] or file_sha256(case["common_source"]) != case["common_source_sha256"]:
                    # Do not report a controlled result after any silent baseline change.
                    raise ValueError("common baseline mutated during profile runs")
            # Configuration selection uses only records for this graph, never another graph's raw scale.
            graph_rows = [row for row in report["results"] if row["instance"] == path.name]
            # Apply the declared quality/runtime policy after collecting every profile, not during search.
            selected = choose_setting(graph_rows, case["common_cut"])
            # A null selection means retain the prior common assignment and settings.
            choices["instances"][path.name] = {"common_baseline_cut": case["common_cut"], "selected": selected,
                                               "evidence": graph_rows, "selection_is_observational": True}
            # Write a small explicit mapping; unselected graph settings/outputs are never modified.
            atomic_json(args.run_dir / "selected_settings.json", choices)
        # Final report includes snapshot verification and all cases without inventing a full-ladder aggregate.
        atomic_json(args.run_dir / "comparison.json", report)
    # Missing inputs, malformed incumbents, scoring errors, or failed child calls stop honestly.
    except (OSError, ValueError, TypeError, subprocess.CalledProcessError) as error:
        # Existing comparison folders and prior solution sets remain untouched on these failures.
        parser.error(str(error))


# Imports expose the comparison helpers without running expensive profiles implicitly.
if __name__ == "__main__":
    # Only direct execution reads shell arguments and launches the explicit selected pilot.
    main()
