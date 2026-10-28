"""Run one fixed BM setting on below-reference instances; retain better saved cuts."""

# argparse exposes the complete experimental setting instead of hiding repeated starts.
import argparse
# json preserves the official before/after profiles and every selection decision.
import json
# Path identifies separate input, candidate, history, and retained-output locations.
from pathlib import Path
# shutil copies saved assignments without changing the original solution folders.
import shutil
# subprocess runs the already tested single-instance CLI with explicit settings.
import subprocess
# sys.executable keeps child calls in the same synchronized Python environment.
import sys

# The unchanged official functions validate and score both incumbents and candidates.
from evaluate import cut_value, load_instance, load_solution, score_folder


# A named predicate makes the numerical skip rule visible and independently checkable.
def matches_reference(score):
    """Accept a normalized score >= 1-1e-12 as reference-matching for this pass.

    score is a float, e.g. 0.9999999999999998; return bool without mutation.
    The dimensionless allowance handles summation roundoff, not printed rounding.
    This O(1) allocation rule does not certify a global optimum.
    """
    # Scores above one already exceed the supplied reference and can also be kept.
    return score >= 1.0 - 1e-12


# Each call describes one fixed-setting pass, not an evolutionary framework.
def main(argv=None):
    """Plan or execute one refinement pass, preserving all input assignments.

    argv is list[str] or None for shell arguments. Return None; --dry-run only
    prints the plan. An actual run creates a new --run-dir containing all retained
    solutions, below-reference trials, scalar histories, and before/after JSON.
    For example, --seed 0 --max-sweeps 200 --roundings 32 changes the original
    initialization while holding its budgets fixed. Each trial costs one existing
    solver call; validation/copying is linear in the input and assignment sizes.
    """
    # Keep the original single-instance solver and the Week 1 batch command unchanged.
    parser = argparse.ArgumentParser(description=__doc__)
    # The separate probe folder already contains the five earlier verified improvements.
    parser.add_argument("--incumbents", type=Path, default=Path("solutions_bm_probe"))
    # A new run folder makes trial outputs explicit and prevents silent evidence replacement.
    parser.add_argument("--run-dir", type=Path, required=True)
    # These overrides also permit bounded verification fixtures without editing official inputs.
    parser.add_argument("--instances", type=Path, default=Path("instances/public"))
    # The official reference file remains read only.
    parser.add_argument("--refs", type=Path, default=Path("references/public.json"))
    # Seed zero is supported by the earlier small/medium comparisons, not a universal optimum.
    parser.add_argument("--seed", type=int, default=0)
    # Preserve the original budget while isolating the seed change in this next experiment.
    parser.add_argument("--max-sweeps", type=int, default=200)
    # Preserve 32 sampled normals because the tested 128-normal calls did not improve cuts.
    parser.add_argument("--roundings", type=int, default=32)
    # Inspect fresh official scores and all skip decisions without starting optimization.
    parser.add_argument("--dry-run", action="store_true")
    # None reads shell arguments; a list allows bounded checks to invoke the same entry point.
    args = parser.parse_args(argv)
    # Reject invalid settings before creating outputs or running any solver call.
    if args.seed < 0 or args.max_sweeps < 0 or args.roundings < 1:
        # Reuse argparse's concise error and unsuccessful exit status.
        parser.error("require seed >= 0, max-sweeps >= 0, and roundings >= 1")
    # Existing outputs may be valuable even if a previous pass was interrupted.
    if args.run_dir.exists():
        # A fresh selected directory is required rather than overwriting prior histories.
        parser.error("run-dir already exists; select a new directory to preserve earlier evidence")
    # Resolve directory overlap before creating anything inside protected input locations.
    for input_dir in (args.incumbents, args.instances, args.refs.parent):
        # Check both nesting directions so output creation cannot contain or enter an input tree.
        if (args.run_dir.resolve().is_relative_to(input_dir.resolve())
                or input_dir.resolve().is_relative_to(args.run_dir.resolve())):
            # Ordinary sibling folders such as experiments/ and solutions_bm_probe/ are allowed.
            parser.error("run-dir must be separate from incumbent, instance, and reference directories")
    # Re-score saved files now; a stale JSON report must not determine whether to skip a graph.
    before = score_folder(str(args.incumbents), str(args.instances), str(args.refs))
    # Count the actual input files so missing references cannot silently shrink the workload.
    expected = len(list(args.instances.glob("*.txt")))
    # Require a complete, valid incumbent set before copying or optimizing anything.
    if not expected or len(before["instances"]) != expected:
        # A full retained folder needs a scored row for every actual input.
        parser.error("incumbent report must cover every instance and contain at least one graph")
    # Preserve the official status text if any incumbent is malformed or missing.
    for name, row in before["instances"].items():
        # Invalid assignments must be addressed explicitly rather than accidentally skipped.
        if row["status"] != "ok":
            # Include only the relevant filename/status, not the whole assignment.
            parser.error(f"invalid incumbent {name}: {row['status']}")
    # Show all decisions before running, using more precision than the scorer's printed table.
    for name, row in before["instances"].items():
        # A printed 1.0000 may still be below one; apply the full-precision rule.
        action = "SKIP reference matched" if matches_reference(row["score"]) else "TRY new setting"
        # The name and actual score explain why this graph receives or avoids more work.
        print(f"{action}: {name}; score={row['score']:.12g}", flush=True)
    # A dry run performs only input validation/scoring and prints no invented result.
    if args.dry_run:
        # Exit before making the run directory or invoking the solver.
        return
    # Reserve a new directory; exist_ok=False also prevents accidental concurrent reuse.
    args.run_dir.mkdir(parents=True, exist_ok=False)
    # A complete retained folder lets the official scorer include skipped graphs in every rung.
    retained = args.run_dir / "solutions"
    # Create the separate assignment folder inside the selected fresh run directory.
    retained.mkdir()
    # Initialize a complete valid set so an interrupted pass still preserves unprocessed incumbents.
    for name in before["instances"]:
        # Copy labels without modifying either source folder or the per-run history files.
        shutil.copyfile(args.incumbents / name, retained / name)
    # Preserve the measured starting score independently of the original report files.
    (args.run_dir / "scores_before.json").write_text(json.dumps(before, indent=2) + "\n")
    # Store each actual selection, including skips and rejected trials, in one manifest.
    report = {"incumbents": str(args.incumbents), "seed": args.seed,
              "max_sweeps": args.max_sweeps, "roundings": args.roundings,
              "reference_score_tolerance": 1e-12, "decisions": []}
    # Process each official input once with no hidden seed loop or parameter mutation.
    for name, row in before["instances"].items():
        # Start each decision with the actually measured saved cut.
        decision = {"instance": name, "previous_cut": row["cut"], "retained_cut": row["cut"]}
        # Matching graphs stay in the retained folder but consume no optimization call.
        if matches_reference(row["score"]):
            # Distinguish a reference-based skip from a trial that tied or lost.
            decision["action"] = "skipped_reference_matched"
        # Only below-reference graphs receive the one requested candidate call.
        else:
            # Preserve the trial even if it is worse than the retained assignment.
            trial = args.run_dir / "trials" / name
            # Keep scalar history separate from submitted labels, following run_bm.py's interface.
            history_path = args.run_dir / "histories" / (Path(name).stem + ".json")
            # Print the active graph before the child starts so long calls remain identifiable.
            print(f"Running {name}", flush=True)
            # check=True aborts on solver errors rather than presenting a partial pass as complete.
            subprocess.run([sys.executable, str(Path(__file__).with_name("run_bm.py")),
                            "--instance", str(args.instances / name), "--output", str(trial),
                            "--history", str(history_path), "--seed", str(args.seed),
                            "--max-sweeps", str(args.max_sweeps), "--roundings", str(args.roundings)],
                           check=True)
            # Re-read the fixed graph using the unchanged official loader.
            n, i, j, w = load_instance(args.instances / name)
            # Check the actual candidate file before using a history's claimed cut.
            signs, status = load_solution(trial, n)
            # A failed candidate never replaces an incumbent assignment.
            if status != "ok":
                # Stop with the official validation explanation rather than assuming success.
                raise ValueError(f"invalid trial {name}: {status}")
            # Compare cuts from the same official summation procedure used for the incumbent.
            trial_cut = cut_value(i, j, w, signs)
            # Record the attempted cut whether it improves, ties, or loses.
            decision["trial_cut"] = trial_cut
            # Read the CLI's actual solver-call time instead of inventing a full-pass estimate.
            decision["runtime_seconds"] = json.loads(history_path.read_text())["runtime_seconds"]
            # Keep the earlier assignment on ties and losses to preserve the best known cut.
            decision["action"] = "kept_incumbent"
            # Direct discrete improvement is the only reason to replace a retained file.
            if trial_cut > row["cut"]:
                # Copy into this run's output only; the input solution folders remain unchanged.
                shutil.copyfile(trial, retained / name)
                # Save the official cut of the selected candidate for later auditing.
                decision["retained_cut"] = trial_cut
                # Make acceptance explicit alongside each rejected candidate's record.
                decision["action"] = "accepted_improvement"
        # Keep a completed decision even when a subsequent long graph call is interrupted.
        report["decisions"].append(decision)
        # Rewriting only this fresh run's manifest preserves completed work after each graph.
        (args.run_dir / "selection.json").write_text(json.dumps(report, indent=2) + "\n")
    # Re-evaluate the complete retained folder, including every reference-matching graph.
    after = score_folder(str(retained), str(args.instances), str(args.refs))
    # A coverage mismatch or invalid output is a failure, not an improved score claim.
    if len(after["instances"]) != expected or any(row["status"] != "ok" for row in after["instances"].values()):
        # Preserve the existing input folders while identifying the failed new output set.
        raise ValueError("retained output failed final official validation")
    # Enforce the retention promise across every graph, not merely the overall average.
    for name, row in after["instances"].items():
        # Using the same unchanged scorer makes this a direct comparison of saved labels.
        if row["cut"] < before["instances"][name]["cut"]:
            # This should be unreachable unless selection/output behavior is broken.
            raise ValueError(f"retained cut regressed for {name}")
    # Save the full official rung profile rather than just a rounded console summary.
    (args.run_dir / "scores_after.json").write_text(json.dumps(after, indent=2) + "\n")
    # The final path is the folder to pass to evaluate.py and viz.py for this new run.
    print(f"overall: {before['overall']:.9f} -> {after['overall']:.9f}; solutions={retained}")


# Importing this helper must neither start optimization nor create output folders.
if __name__ == "__main__":
    # Shell execution runs the same public entry point used by the bounded checks.
    main()
