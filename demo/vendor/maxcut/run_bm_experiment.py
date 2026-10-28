"""Step 13: preview or execute paired BM comparisons on pilot or unmatched graphs."""

# argparse makes execution an explicit flag; ordinary invocation only previews.
import argparse
# JSON preserves the predeclared plan separately from later measured results.
import json
# Path resolves this repository and selected fresh output locations.
from pathlib import Path
# sys.executable runs the comparison in the already selected Python environment.
import sys
# subprocess captures actual comparison output, including failures.
import subprocess
# perf_counter measures the complete execution stage in seconds.
from time import perf_counter

# Reuse graph validation instead of implementing another Max-Cut reader.
from bm_solver import load_graph
# Use the existing four-profile harness and official normalization unchanged.
from compare_bm import PROFILES, normalized_score
# The professor's evaluator remains the authority for retained full-ladder scores.
import evaluate as official
# Existing validated atomic writers also supply input and code provenance.
from run_bm import PROJECT_ROOT, atomic_json, code_identity, file_sha256, load_assignment, protect_destination, save_verified_assignment

# The legacy pilot selection remains available with its original default behavior.
SELECTED = ("torus_pm_32_s21.txt", "rand_pm_1000_s23.txt", "rand_pos_1000_s22.txt")
# Legacy pilot seeds remain unchanged for reproducibility of earlier commands.
SEEDS = (1, 2)
# The broader comparison uses fresh paired seeds rather than repeating the pilot's random streams.
ALL_UNMATCHED_SEEDS = (3, 4)
# Fixed official data paths keep this a small project-specific launcher, not a grid framework.
INSTANCES = PROJECT_ROOT / "instances/public"
# Never edit the fixed scoring references to match a candidate.
REFERENCES = PROJECT_ROOT / "references/public.json"


# Validate every incumbent before starting work and record the strict best source per graph.
def prepare_plan(baseline_dir, additional_dir, run_dir, scope="pilot", seeds=None):
    """Step 13: return a read-only comparison plan with recomputed common cuts.

    baseline_dir is a Path containing ALL public assignments; additional_dir
    is a Path containing optional sparse candidates, or None. run_dir is a
    fresh Path. scope is 'pilot' (default, three named cases) or 'all-unmatched'
    (every public case below its reference). seeds is a nonempty sequence of
    distinct nonnegative ints, or None for scope defaults: (1,2) or (3,4).
    Example: prepare_plan(Path('experiments/bm_real_pilot_s1_s2/solutions'),
    None, Path('experiments/bm_all_unmatched_s3_s4'), 'all-unmatched').
    No directories are created and no solver is called. Every source is
    validated against its graph and any available SHA sidecar. Return a JSON
    dict with owned scalar records, hashes, budgets and code identity; no
    arrays or caller objects are mutated. O(all input/assignment bytes+n+m),
    with one graph in memory at a time. Scores use official signed weights.
    """
    # Scope is explicit and never inferred from how long an experiment might take.
    if scope not in ("pilot", "all-unmatched"):
        # Unknown scope must not quietly fall back to a cheaper subset.
        raise ValueError("scope must be pilot or all-unmatched")
    # Scope-specific defaults preserve old commands while broad comparisons use fresh seeds.
    selected_seeds = tuple(SEEDS if scope == "pilot" else ALL_UNMATCHED_SEEDS) if seeds is None else tuple(seeds)
    # Duplicate or invalid seeds cannot count as independent repeated evidence.
    if not selected_seeds or any(type(seed) is not int or seed < 0 for seed in selected_seeds) or len(set(selected_seeds)) != len(selected_seeds):
        # Fail before reading large inputs or creating an output directory.
        raise ValueError("seeds must be distinct nonnegative integers and nonempty")
    # A preview must reject stale output just as execution will.
    if run_dir.exists():
        # A failed/finished comparison remains evidence and requires a new run identifier.
        raise ValueError("run-dir already exists; choose a fresh identifier")
    # Apply the established guards to a representative output inside this directory.
    protect_destination(run_dir / "plan.json")
    # Prevent new results from being nested within either immutable source folder.
    for folder in (baseline_dir, additional_dir):
        # None denotes no additional pool; an explicit folder must actually exist.
        if folder is not None:
            # A typo must not silently omit the user's most recent improvement.
            if not folder.is_dir() or run_dir.resolve().is_relative_to(folder.resolve()):
                # Fail before any snapshot or solver call can modify the output tree.
                raise ValueError(f"missing source folder or run-dir inside source folder: {folder}")
    # Read only fixed reference data; available denominators are validated below.
    references = json.loads(REFERENCES.read_text(encoding="utf-8"))
    # Discover the full retained ladder; all-unmatched scope tests every below-reference case.
    paths = sorted(INSTANCES.glob("*.txt"))
    # Only pilot scope requires the three legacy names; neither scope permits an empty ladder.
    if not paths or (scope == "pilot" and not set(SELECTED).issubset({path.name for path in paths})):
        # Do not substitute other graphs silently.
        raise ValueError("selected public graphs are missing")
    # Each row records only paths, identities and independently recomputed scalar values.
    rows = []
    # Include unselected graphs so the eventual result can be scored as a complete ladder.
    for path in paths:
        # The core validates edge indices/weights, with official arrays used for scoring.
        graph = load_graph(path)
        # Exact raw input identity prevents a same-name graph from substituting for this case.
        digest = file_sha256(path)
        # Independent official summation supplies signed W/2 and candidate cuts.
        n, i, j, weights = official.load_instance(str(path))
        # Every public comparison input requires an actual professor-supplied reference entry.
        reference = float(references[path.name]["ref"])
        # A complete base assignment is required, including the already matched graphs.
        sources = [baseline_dir / path.name]
        # A sparse additional pool is permitted, without treating missing files as zero cuts.
        if additional_dir is not None and (additional_dir / path.name).exists():
            # Include the latest separately saved candidate without overwriting its source.
            sources.append(additional_dir / path.name)
        # Keep all input records so even a rejected source's bytes remain auditable.
        checked = []
        # Validate every available source and recompute F instead of trusting a history's score.
        for source in sources:
            # Existing SHA sidecars are checked; old files honestly have unavailable provenance.
            signs, direct_cut, info = load_assignment(source, graph, digest)
            # Grading uses this official sum over cut edges in the saved node order.
            value = official.cut_value(i, j, weights, signs)
            # Record assignment bytes and any metadata identity as immutable dependencies.
            hashes = {str(source.resolve()): file_sha256(source)}
            # Metadata was validated above and must also remain unchanged during execution.
            sidecar = Path(str(source) + ".metadata.json")
            # Pre-extension assignments legitimately have no sidecar.
            if sidecar.exists():
                # Track the actual sidecar bytes rather than inventing old provenance.
                hashes[str(sidecar.resolve())] = file_sha256(sidecar)
            # Retain scalar evidence without holding every graph's signs in memory.
            checked.append({"source": str(source.resolve()), "cut": value,
                            "metadata_status": info["metadata_status"], "hashes": hashes})
        # Start with the settled baseline; exact ties retain its assignment.
        best = checked[0]
        # Sparse user candidates participate only through strictly higher actual F.
        for candidate in checked[1:]:
            # A larger cut, rather than a newer file or more passes, determines retention.
            if candidate["cut"] > best["cut"]:
                # This selects a source record without mutating its labels or prior output.
                best = candidate
        # Use the exact professor normalization and reject invalid denominators before execution.
        score = normalized_score(best["cut"], float(weights.sum()) / 2.0, reference)
        # Matches within floating summation tolerance need no new work; keep their files in the ladder.
        matched = score >= 1.0 - 1e-12
        # All-unmatched scope includes dense and large graphs whenever they are below reference.
        active = (scope == "all-unmatched" or path.name in SELECTED) and not matched
        # The source record preserves full provenance for both chosen and rejected incumbents.
        rows.append({"instance": str(path.resolve()), "name": path.name, "input_sha256": digest,
                     "n": n, "rung": official.rung_of(n), "cut": best["cut"], "score": score,
                     "source": best["source"], "sources": checked, "active": active,
                     "reason": scope.replace("-", "_") if active else ("reference_matched" if matched else "outside_selected_pilot")})
    # Compute actual work after the skip rule, not from an assumed three active graphs.
    active_count = sum(row["active"] for row in rows)
    # The budget identity is M*(1+P) for every profile and every paired seed.
    passes = active_count * len(selected_seeds) * sum(m * (1 + p) for m, p in PROFILES.values())
    # Code identity includes this new launcher separately from the existing solver identity helper.
    identity = code_identity()
    # A dirty checkout still has exact source hashes; never invent a new commit identity.
    identity["source_sha256"][Path(__file__).name] = file_sha256(Path(__file__))
    # The preview is explicitly planned, not a record of a future measured run.
    return {"status": "planned", "scope": scope, "run_dir": str(run_dir.resolve()), "seeds": list(selected_seeds),
            "max_sweeps": 200, "roundings": 32, "perturb_scale_radians": 0.35,
            "profiles": PROFILES, "active_graphs": active_count, "solver_calls": active_count * len(selected_seeds) * len(PROFILES),
            "total_passes": passes, "maximum_coordinate_sweeps": passes * 200,
            "budget_scope": "fixed passes, not matched time; runtime is measured during execution",
            "code_identity": identity, "references_sha256": file_sha256(REFERENCES), "instances": rows}


# Source immutability matters both before copying and after all comparisons finish.
def verify_sources(plan):
    """Step 13: check actual graph/reference/assignment/sidecar hashes; return None.

    plan is prepare_plan's JSON dict. Example verify_sources(plan) raises
    ValueError on any changed dependency. No mutations. O(source bytes),
    bounded memory. A changed source invalidates this run rather than resuming
    from a different incumbent under the same experimental identity.
    """
    # The normalization table is as immutable as the graph and assignment bytes.
    if file_sha256(REFERENCES) != plan["references_sha256"]:
        # A changed reference cannot redefine success during a pilot.
        raise ValueError("references changed after planning")
    # Check every retained graph, including those skipped by the solver.
    for row in plan["instances"]:
        # Actual input bytes establish which optimization problem was solved.
        if file_sha256(row["instance"]) != row["input_sha256"]:
            # No new solver output is promoted after a graph identity change.
            raise ValueError(f"graph changed after planning: {row['name']}")
        # Both chosen and rejected sources must remain available as original evidence.
        for source in row["sources"]:
            # Hash assignments and any original SHA sidecars independently.
            for path, digest in source["hashes"].items():
                # A concurrent edit is an explicit failure rather than a silent new common baseline.
                if file_sha256(path) != digest:
                    # Preserve the partial run folder for inspection.
                    raise ValueError(f"source changed after planning: {path}")


# Execute the existing comparison, then retain its best verified answers in a new complete set.
def execute_plan(plan):
    """Step 13: execute this prevalidated fixed comparison and return official full scores.

    plan is prepare_plan's dict (not mutated). Example execute_plan(plan)
    creates fresh plan.run_dir/common_baseline, comparison, solutions, figures,
    scores_before/after.json and selection.json. Prior solution folders remain
    immutable. Calls compare_bm.py serially; total work is the declared passes
    plus O(ladder bytes) validation/copy/scoring. Status is running/failed/
    complete in run.json; partial outputs are retained on failure. No checkpoint
    resume or automatic next experiment. Returned dict is official score_folder.
    """
    # Validate the immutable sources again before exclusive output creation.
    verify_sources(plan)
    # A fresh directory prevents results from inheriting previous profile outputs.
    root = Path(plan["run_dir"])
    # exist_ok=False rejects stale or concurrently created output locations.
    root.mkdir(parents=True, exist_ok=False)
    # Preserve the exact preview settings and source choices as the pre-run plan.
    atomic_json(root / "plan.json", plan)
    # This measured stage includes snapshots, subprocesses, scoring and figures.
    started = perf_counter()
    # The initial record must not claim successful results before any solver runs.
    state = {"status": "running"}
    # Publish an explicit lifecycle record separately from the immutable plan.
    atomic_json(root / "run.json", state)
    # Preserve actual partial evidence and failure status if any child or validation fails.
    try:
        # One immutable complete baseline is shared by all profile/seed comparisons.
        common = root / "common_baseline"
        # Create validated graph-bound snapshots using the established atomic assignment writer.
        for row in plan["instances"]:
            # Load one graph at a time instead of storing the whole ladder in memory.
            graph = load_graph(row["instance"])
            # Recheck selected source provenance against the exact graph digest.
            signs, cut, info = load_assignment(Path(row["source"]), graph, row["input_sha256"])
            # The destination is fresh, with independent labels and fresh metadata.
            save_verified_assignment(common / row["name"], signs, graph, row["input_sha256"])
        # Whole-ladder scoring includes all unchanged high-scoring graphs as well as selected cases.
        before = official.score_folder(str(common), str(INSTANCES), str(REFERENCES))
        # Store the real pre-run score, including the previously found torus improvement.
        atomic_json(root / "scores_before.json", before)
        # Only these predeclared below-reference instances enter solver subprocesses.
        active = [row["instance"] for row in plan["instances"] if row["active"]]
        # An all-matched selection legitimately costs zero solver passes.
        records = []
        # Do not call the comparison CLI with an empty required instance list.
        if active:
            # Every seed/profile receives the same immutable snapshots and inner settings.
            command = [sys.executable, str(PROJECT_ROOT / "compare_bm.py"), "--instances", *active,
                       "--seeds", *map(str, plan["seeds"]), "--baseline-dir", str(common),
                       "--refs", str(REFERENCES), "--run-dir", str(root / "comparison"),
                       "--max-sweeps", str(plan["max_sweeps"]), "--roundings", str(plan["roundings"]),
                       "--perturb-scale", str(plan["perturb_scale_radians"])]
            # Stream actual progress to the terminal and a raw run-local text log.
            with (root / "comparison.stdout.txt").open("w", encoding="utf-8") as log:
                # stderr joins stdout so child failures are preserved in the actual stream.
                with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as child:
                    # Each line is real child output, not a fabricated transcript.
                    for line in child.stdout:
                        # Retain progress evidence even if a later graph fails.
                        log.write(line)
                        # Flush before awaiting further solver work.
                        log.flush()
                        # Keep the user informed throughout the serial comparison.
                        print(line, end="", flush=True)
                    # Wait for actual process completion before declaring comparison success.
                    returncode = child.wait()
                # A failed comparison never produces a complete promoted ladder.
                if returncode:
                    # The child log and partial comparison histories remain in this fresh run folder.
                    raise RuntimeError(f"comparison failed with exit code {returncode}; see comparison.stdout.txt")
            # Read completed measurements only after the child successfully exits.
            records = json.loads((root / "comparison/comparison.json").read_text())["results"]
            # Completion requires every declared profile/seed call and exactly the planned passes.
            if len(records) != plan["solver_calls"] or sum(row["total_passes"] for row in records) != plan["total_passes"]:
                # Partial or mislabeled comparisons cannot be promoted as completed experiments.
                raise ValueError("completed comparison does not match the declared budget")
        # Do not promote results if any original dependency changed during comparison.
        verify_sources(plan)
        # Keep graph-by-graph output provenance without modifying the profile-selection policy.
        selections = []
        # A separate complete folder retains the common assignment or a strictly higher verified cut.
        for row in plan["instances"]:
            # Load one graph and its official arrays for independent output cut checks.
            graph = load_graph(row["instance"])
            # Scoring candidates from saved labels avoids trusting a report's cut field.
            n, i, j, weights = official.load_instance(row["instance"])
            # Begin with the run-local incumbent; common wins all ties.
            best_path = common / row["name"]
            # Load fresh owned signs for the eventual retained assignment.
            best_signs, cut, info = load_assignment(best_path, graph, row["input_sha256"])
            # Use official summation for selection, just as in the controlled comparison.
            best_cut = official.cut_value(i, j, weights, best_signs)
            # Every measured output is eligible as an answer; configuration selection remains separate.
            for trial in records:
                # Another graph's raw cut has no relevance to this assignment.
                if trial["instance"] == row["name"]:
                    # Reopen actual saved output and validate available graph/assignment metadata.
                    signs, cut, info = load_assignment(Path(trial["output"]), graph, row["input_sha256"])
                    # Never use continuous R or a stale stored score to promote an answer.
                    value = official.cut_value(i, j, weights, signs)
                    # Reject report/file disagreement rather than silently relabeling evidence.
                    if value != trial["cut"]:
                        # The fresh run remains incomplete and old solutions remain intact.
                        raise ValueError("comparison report and saved assignment disagree")
                    # Preserve the previous assignment on every exact tie or loss.
                    if value > best_cut:
                        # The loaded signs own their memory independently of other candidate states.
                        best_signs = signs.copy()
                        # Record the actual strict gain and its source.
                        best_cut = value
                        # Source path identifies the winning graph/profile/seed output.
                        best_path = Path(trial["output"])
            # Publish only into this new experiment's complete retained solution set.
            save_verified_assignment(root / "solutions" / row["name"], best_signs, graph, row["input_sha256"])
            # Keep an auditable strict-retention record for every graph, including skipped cases.
            selections.append({"instance": row["name"], "before": row["cut"], "after": best_cut,
                               "difference": best_cut - row["cut"], "source": str(best_path)})
        # Check all original graph and incumbent hashes again before publishing success.
        verify_sources(plan)
        # This is the full official ladder result, never an average of the three selected cases.
        after = official.score_folder(str(root / "solutions"), str(INSTANCES), str(REFERENCES))
        # Validate every retained answer, including untouched graphs outside the pilot.
        if set(after["instances"]) != {row["name"] for row in plan["instances"]} or any(row["status"] != "ok" for row in after["instances"].values()):
            # Missing references or labels cannot masquerade as a complete successful ladder.
            raise ValueError("incomplete or invalid full-ladder result")
        # The complete set cannot lose quality under strict per-graph retention.
        if any(after["instances"][row["name"]]["cut"] < row["cut"] for row in plan["instances"]):
            # A retention regression is a correctness failure, not a bad optimization result.
            raise ValueError("retained cut decreased")
        # Preserve raw official score fields and the full source-selection table.
        atomic_json(root / "scores_after.json", after)
        # Assignment retention and future profile recommendations are deliberately separate evidence.
        atomic_json(root / "selection.json", {"instances": selections, "overall_difference": after["overall"] - before["overall"]})
        # Completed selected-case measurements support real figures; no future values are invented.
        if records:
            # Import the existing dependency-free SVG generator only when evidence is available.
            from make_bm_figures import make_extension_figures
            # Any completed enhanced history supplies actual per-attempt retention states.
            history = next(row["history"] for row in records if row["profile"] == "combined")
            # The generator's function API expects its caller to create the selected output folder.
            (root / "figures").mkdir()
            # Reuse the existing five measured/teaching figures in this run's own output folder.
            make_extension_figures(root / "figures", json.loads(Path(history).read_text()),
                                   json.loads((root / "comparison/comparison.json").read_text()))
        # Only fully checked results and figures earn a completed lifecycle status.
        state = {"status": "complete", "wall_seconds": perf_counter() - started,
                 "solver_calls": len(records), "total_passes": sum(row["total_passes"] for row in records),
                 "overall_before": before["overall"], "overall_after": after["overall"]}
        # Publish completion after all verification; plan.json remains the original declaration.
        atomic_json(root / "run.json", state)
        # Expose the actual official result for the CLI and bounded tests.
        return after
    # Interruptions and ordinary exceptions leave explicit partial-run status, never fictitious completion.
    except BaseException as error:
        # Preserve the failure reason without deleting any source or partial evidence.
        atomic_json(root / "run.json", {"status": "failed", "wall_seconds": perf_counter() - started,
                                       "error": f"{type(error).__name__}: {error}"})
        # Keep the real error visible to callers and the terminal.
        raise


# A small interface selects scope and paired seeds without exposing an automatic search grid.
def main(argv=None):
    """Step 13 CLI: preview by default; --execute runs the declared comparison.

    argv is list[str] or None (shell arguments). Require fresh --run-dir;
    --scope is pilot (default) or all-unmatched. --baseline-dir defaults to
    the settled seed-0 set for pilot, or the completed pilot's retained set
    for all-unmatched. Optional --additional-incumbents is a sparse folder.
    --seeds accepts distinct nonnegative ints (scope defaults: 1/2 or 3/4).
    Example: --scope all-unmatched --run-dir experiments/bm_all_unmatched_s3_s4.
    Preview prints finite JSON and writes nothing; --execute creates only the
    new experiment tree and prints the full official score table. No argument
    mutation. Preview O(input bytes); execution cost is the declared pass count.
    """
    # Standard argparse keeps help available without loading graphs or starting a run.
    parser = argparse.ArgumentParser(description=__doc__)
    # The caller must name a fresh experiment, making evidence provenance visible.
    parser.add_argument("--run-dir", type=Path, required=True)
    # Explicit all-unmatched scope includes every remaining gap, including dense and large cases.
    parser.add_argument("--scope", choices=("pilot", "all-unmatched"), default="pilot")
    # Scope-specific baseline defaults are selected after parsing and never fall back if missing.
    parser.add_argument("--baseline-dir", type=Path)
    # Optional explicit seeds permit reproducible fresh-seed confirmations without editing source.
    parser.add_argument("--seeds", type=int, nargs="+")
    # New isolated outputs can improve the common incumbent without changing existing folders.
    parser.add_argument("--additional-incumbents", type=Path)
    # Preview is the default; execution is explicit in the user's command.
    parser.add_argument("--execute", action="store_true")
    # Tests can supply a list; ordinary invocation uses the actual shell arguments.
    args = parser.parse_args(argv)
    # Surface actionable input errors through the standard CLI error mechanism.
    try:
        # All-unmatched runs continue the newest complete retained set rather than losing pilot gains.
        default_baseline = "experiments/bm_seed0_s200_k32/solutions" if args.scope == "pilot" else "experiments/bm_real_pilot_s1_s2/solutions"
        # An explicit baseline overrides only this input folder, not graph selection or budgets.
        baseline_dir = args.baseline_dir if args.baseline_dir is not None else PROJECT_ROOT / default_baseline
        # Validation completes before any output directory or solver process is created.
        plan = prepare_plan(baseline_dir, args.additional_incumbents, args.run_dir, args.scope, args.seeds)
        # A preview is machine-readable and honest about planned rather than measured work.
        print(json.dumps(plan, indent=2, allow_nan=False), flush=True)
        # Only explicit execution launches the fixed profile comparison and promotion.
        if args.execute:
            # Print the unchanged official full-ladder table after successful verification.
            print(official.format_table(execute_plan(plan)))
    # Invalid paths, malformed saved labels, scoring-data errors and failed children stop clearly.
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        # Prior folders remain untouched and partial runs retain their failure records.
        parser.error(str(error))


# Importing this module never starts a solver or creates experiment directories.
if __name__ == "__main__":
    # Direct CLI execution selects preview or the explicit bounded pilot.
    main()
