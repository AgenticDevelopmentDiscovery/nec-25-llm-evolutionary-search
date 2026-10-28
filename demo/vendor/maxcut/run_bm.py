"""Single-instance BM CLI: settled defaults plus explicit refinement and safe retention."""

# argparse keeps old option names/defaults and explains new total/additional counts.
import argparse
# SHA-256 ties an incumbent's optional metadata to actual input and assignment bytes.
import hashlib
# JSON records finite histories and optional identity sidecars; it is not a source of trusted cuts.
import json
# math checks finite measurements and scale-aware agreement between independent summations.
import math
# Path distinguishes selected writes from protected graph/reference/source locations.
from pathlib import Path
# subprocess reads Git identity without mutating history or requiring a network connection.
import subprocess
# tempfile creates same-directory temporary files for atomic assignment and metadata replacement.
import tempfile
# perf_counter measures solver and stated end-to-end scopes independently.
from time import perf_counter

# Core mathematical routines retain their established meanings and original one-start API.
from bm_solver import cut_value, load_graph, solve_bm, solve_bm_extended, validate_signs, write_assignment
# The unchanged official loader and cut function independently corroborate saved labels.
import evaluate as official

# Resolve the implementation's location even when a test or user changes the current directory.
PROJECT_ROOT = Path(__file__).resolve().parent


# Stream hashing avoids building another full copy of a large input in memory.
def file_sha256(path):
    """Steps 11–12: return SHA-256 hex of Path/str path's actual bytes.

    Example file_sha256(Path('graph.txt')) identifies its exact text, not merely
    its name. No mutation. read(65536) returns at most 64 KiB until empty bytes;
    update consumes each chunk. O(file size) time and O(1) buffered storage.
    """
    # A fresh SHA state owns this file's byte identity independently of previous calls.
    digest = hashlib.sha256()
    # Binary mode preserves newlines/encoding exactly; with closes the descriptor on every exit.
    with Path(path).open("rb") as stream:
        # Keep reading until the actual end of file rather than trusting a size header.
        while True:
            # This fixed chunk size bounds temporary byte storage.
            chunk = stream.read(65536)
            # Empty bytes mean EOF, not an extra record in the hashed problem.
            if not chunk:
                # Finish without adding fabricated bytes.
                break
            # Incremental update hashes the same concatenation as reading the complete file at once.
            digest.update(chunk)
    # The stable 64-character hex form is JSON-compatible.
    return digest.hexdigest()


# The selected output may not replace fixed problem files or the current input/history dependencies.
def protect_destination(path, instance=None, additional_readonly=()):
    """Step 12: reject protected writes; return None without touching files.

    path is Path or str; instance is an optional read-only input Path (None
    for in-memory save helpers); additional_readonly is a sequence of paths,
    e.g. [initial_assignment]. Check resolved identities and official directory
    descendants. This permits ordinary /tmp fixture outputs. O(number of guards).
    """
    # Resolve aliases before comparing identities, including existing symbolic links.
    destination = Path(path).resolve()
    # These repository directories contain fixed inputs/references or agent/Git metadata.
    for directory in ("instances", "references", ".git", ".agents", ".codex"):
        # is_relative_to detects a descendant without relying on a string-prefix coincidence.
        if destination.is_relative_to(PROJECT_ROOT / directory):
            # Fail before making directories or opening any selected file.
            raise ValueError(f"refusing write into protected directory: {path}")
    # Guard fixed top-level instructions and dependency files as well as executable sources.
    protected = [PROJECT_ROOT / name for name in ("README.md", "problem.md", "pyproject.toml", "uv.lock")]
    # Any existing project Python script is implementation, not a history/output destination.
    protected.extend(PROJECT_ROOT.glob("*.py"))
    # The specific input is protected even when it lives outside the supplied instance directory.
    if instance is not None:
        # An in-memory graph has no claimed input filename to protect here.
        protected.append(Path(instance))
    # A caller can additionally protect an initial assignment, metadata, or assignment output.
    protected.extend(additional_readonly)
    # Compare complete resolved paths, never just basenames shared by different directories.
    for source in protected:
        # A selected write cannot destroy a required read-only source.
        if destination == Path(source).resolve():
            # Include the selected path in the CLI error for correction.
            raise ValueError(f"input/output/history collision or protected file: {path}")


# Sidecars are deliberately separate from the n binary lines accepted by the scorer.
def metadata_path(path):
    """Step 12: return Path(str(path)+'.metadata.json'), without I/O or mutation.

    path='out.txt' gives 'out.txt.metadata.json'. O(path length). The sidecar
    identifies graph/order metadata; it never changes the official assignment.
    """
    # Keep the original suffix so files such as graph.a.txt do not collide with graph.a metadata.
    return Path(str(path) + ".metadata.json")


# Old scores are ignored; labels are always validated and scored against the graph being solved.
def load_assignment(path, graph, input_digest):
    """Step 12: validate saved labels and available SHA metadata; return signs,F,info.

    path is an existing Path, graph is current Graph, input_digest is its raw
    SHA-256 str. Official load_solution checks n ordered +/-1 labels; the core
    recomputes F. Recognized metadata must match graph and assignment hashes.
    Without a sidecar, shape/labels are checkable but graph provenance is unknown.
    Return owned signs, finite direct cut, small dict; no mutation. O(n+m+bytes).
    """
    # Reuse the provided reader instead of trusting a stored score or inventing an input format.
    signs, status = official.load_solution(str(path), graph.node_count)
    # Missing, nonbinary, or wrong-length files are explicit failures, never overwritten silently.
    if status != "ok":
        # Preserve the official validation reason in the error.
        raise ValueError(f"invalid incumbent {path}: {status}")
    # Membership validation owns a fresh array in the original node order.
    signs = validate_signs(signs, graph.node_count)
    # A sidecar is optional for pre-extension files, but any available one must be valid.
    sidecar = metadata_path(path)
    # No unseen provenance is inferred from a matching basename or node count.
    provenance = "not_available"
    # A recognized sidecar supplies evidence of the exact graph and assignment bytes.
    if sidecar.exists():
        # loads decodes JSON data, not executable code or trusted objective values.
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        # Reject unrecognized or stale metadata rather than silently ignoring a graph mismatch.
        if not isinstance(metadata, dict) or metadata.get("instance_sha256") != input_digest:
            # Identical node counts cannot establish identical edge weights or node order.
            raise ValueError(f"incumbent graph digest mismatch: {sidecar}")
        # An old sidecar must not certify an assignment file edited after it was written.
        if metadata.get("assignment_sha256") != file_sha256(path):
            # F is still recomputed, but stale identity data must be corrected explicitly.
            raise ValueError(f"incumbent assignment digest mismatch: {sidecar}")
        # This status states exactly which available provenance was checked.
        provenance = "graph_and_assignment_sha256_verified"
    # Evaluate the current fixed graph rather than accepting any old reported objective.
    value = cut_value(graph, signs)
    # Return copied labels, actual F, and the metadata limitation/status.
    return signs.copy(), value, {"path": str(path), "cut": value, "metadata_status": provenance}


# JSON sidecars/history writes use a same-directory temporary file and finite standard JSON.
def atomic_json(path, report):
    """Step 12: atomically write finite JSON report to explicit Path path; return None.

    report is a dictionary, e.g. {'cut':4.0}; inputs unchanged. Serialization
    rejects NaN before touching files. NamedTemporaryFile(delete=False) reserves
    a unique sibling; replace atomically changes the directory entry; finally
    unlinks an unused temporary on failure. O(serialized size) time/storage.
    """
    # allow_nan=False rejects nonstandard NaN/Infinity JSON before creating a temporary.
    content = json.dumps(report, indent=2, allow_nan=False) + "\n"
    # Create only the selected parent directory and missing ancestors.
    path.parent.mkdir(parents=True, exist_ok=True)
    # None explicitly marks that no temporary file has been reserved yet.
    temporary = None
    # Every unsuccessful path must clean up its own temporary without deleting the selected output.
    try:
        # Same directory means replace does not cross filesystems; delete=False keeps it after close.
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".bm-json-", suffix=".tmp", delete=False) as stream:
            # name identifies this uniquely reserved sibling after the descriptor closes.
            temporary = Path(stream.name)
        # Write complete UTF-8 text, then atomically replace only the selected JSON destination.
        temporary.write_text(content, encoding="utf-8")
        # Path.replace replaces the directory entry atomically on the same filesystem.
        temporary.replace(path)
    # Cleanup also runs if writing or replacement raises an exception.
    finally:
        # A successful replace moved the temporary, so only failed leftovers still exist.
        if temporary is not None and temporary.exists():
            # Remove only the temporary created by this call, never a pre-existing assignment.
            temporary.unlink()


# Assignment persistence is monotone even when the caller supplies an older incumbent separately.
def save_verified_assignment(path, signs, graph, input_digest):
    """Step 12: retain a valid existing output on ties/losses; atomically save improvements.

    path is explicitly selected, signs shape-(n,) +/-1, graph current Graph,
    input_digest raw SHA str. Return saved owned signs, direct cut, status str
    ('created','improved','no_improvement'). No input-array mutation. An invalid
    existing output fails before writing. Same-directory temporary is written,
    reloaded/scored, then replaced; cleanup is unconditional. O(n+m+file bytes).
    """
    # Pure API saves also honor fixed repository directory/source protections.
    protect_destination(path)
    # The corresponding metadata path cannot overwrite a fixed file either.
    protect_destination(metadata_path(path))
    # An orphan sidecar may be unrelated evidence; a new assignment must not silently replace it.
    if not path.exists() and metadata_path(path).exists():
        # Ask for a separate output rather than destroying an unpaired old metadata file.
        raise ValueError("output metadata already exists without assignment; select a fresh output")
    # Verify the actual candidate before creating any file or changing an existing output.
    checked = validate_signs(signs, graph.node_count)
    # Selection uses direct F, never R, an incremental total, or an old history's claim.
    value = cut_value(graph, checked)
    # New files and improvements have distinct, honest output statuses.
    status = "created"
    # A valid output is another incumbent even if the user supplied a different initial file.
    if path.exists():
        # Validate provenance when available and recompute the existing file's actual cut.
        previous, previous_cut, info = load_assignment(path, graph, input_digest)
        # Preserve assignment bytes, inode and timestamps on every exact tie or loss.
        if value <= previous_cut:
            # No assignment or metadata write is needed when the existing file wins.
            return previous.copy(), previous_cut, "no_improvement"
        # Only a strict direct improvement may replace an existing output.
        status = "improved"
    # Parent creation happens after candidate and previous-file validation.
    path.parent.mkdir(parents=True, exist_ok=True)
    # Track this call's temporary so failures leave no unrelated cleanup targets.
    temporary = None
    # Cleanup must run if validation, writing, or replacement fails.
    try:
        # Reserve a unique sibling on the same filesystem for atomic replacement.
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".bm-assignment-", suffix=".tmp", delete=False) as stream:
            # Capture the reserved path after its descriptor closes.
            temporary = Path(stream.name)
        # Reuse the settled signed-line writer and its pre-write direct validation on this temporary only.
        write_assignment(temporary, checked, graph)
        # Re-read actual bytes rather than checking only the in-memory candidate.
        reloaded, reloaded_cut, info = load_assignment(temporary, graph, input_digest)
        # The sign vector and F must agree before replacing the selected output.
        if reloaded_cut != value or reloaded.tolist() != checked.tolist():
            # Leave the existing output untouched if a write/reload discrepancy is detected.
            raise FloatingPointError("temporary assignment failed direct round-trip validation")
        # A same-directory replace publishes the verified complete assignment atomically.
        temporary.replace(path)
    # An exception may leave a reserved temporary; a successful replace leaves none.
    finally:
        # Do not unlink the final assignment after a successful move.
        if temporary is not None and temporary.exists():
            # Delete only this failed call's temporary file.
            temporary.unlink()
    # Newly written files gain graph/order provenance without adding lines to the assignment format.
    atomic_json(metadata_path(path), {"instance_sha256": input_digest,
                "assignment_sha256": file_sha256(path), "node_count": graph.node_count,
                "edge_count": len(graph.edges), "node_order": "original input node order"})
    # A final reload also validates the just-written provenance metadata.
    saved, saved_cut, info = load_assignment(path, graph, input_digest)
    # Return the actually saved result, not an unverified candidate claim.
    return saved.copy(), saved_cut, status


# Git identity records uncommitted status explicitly instead of assigning changes a fictional revision.
def code_identity():
    """Steps 11–13: return revision, dirty status, source hashes; no mutation.

    No arguments. git -C uses PROJECT_ROOT even if a fixture changes cwd.
    Return dict with null revision/dirty when Git is unavailable; source SHA
    still identifies the implementation. O(source size + Git status work).
    """
    # Null means unavailable, not a clean working tree or invented commit identifier.
    identity = {"revision": None, "dirty_tree": None, "status": None, "source_sha256": {}}
    # Hash the actual implementation, which may differ from the reported committed revision.
    for name in ("bm_solver.py", "run_bm.py", "compare_bm.py"):
        # A comparison wrapper may not yet exist during incremental implementation.
        if (PROJECT_ROOT / name).exists():
            # Each actual code file receives a raw-byte SHA identifier.
            identity["source_sha256"][name] = file_sha256(PROJECT_ROOT / name)
    # Git information is additional provenance, not required for the mathematical solver to run.
    try:
        # check=True surfaces unavailable repository metadata instead of pretending success.
        revision = subprocess.run(["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
        # Porcelain output is stable machine-readable status, with untracked directories summarized.
        status = subprocess.run(["git", "-C", str(PROJECT_ROOT), "status", "--porcelain"], check=True, capture_output=True, text=True)
        # strip removes the subprocess's trailing newline from the hexadecimal revision.
        identity["revision"] = revision.stdout.strip()
        # Nonempty status means the recorded revision alone does not identify this working code.
        identity["dirty_tree"] = bool(status.stdout.strip())
        # splitlines retains the actual modified/untracked entries without parsing filename spaces.
        identity["status"] = status.stdout.splitlines()
    # File-not-found or a nonrepository environment leaves explicit unavailable metadata.
    except (OSError, subprocess.CalledProcessError):
        # The null fields distinguish this case from a false clean-tree claim.
        identity["status"] = "git_metadata_not_available"
    # A plain dictionary serializes with finite JSON and no source-code side effects.
    return identity


# Saving is corroborated against the unchanged official representation and summation procedure.
def official_check(instance, output, expected_cut):
    """Step 12: return independent saved cut and optional official reference score.

    instance/output are Paths, expected_cut finite core F. Read actual files
    with unchanged official functions; allow 64*eps*sum|w| summation roundoff.
    Official score is available only for the real supplied instance path and
    present reference. Missing references produce null/'not_available'; zero
    denominator raises scoring-data error. No mutation; O(n+m) I/O/work.
    """
    # Load each fixed edge once using the instructor's parser.
    n, i, j, weights = official.load_instance(str(instance))
    # Check exact binary membership/length through the independent official reader.
    signs, status = official.load_solution(str(output), n)
    # Do not attach a success claim to invalid or missing saved labels.
    if status != "ok":
        # Include the official loader's actual status in the error.
        raise ValueError(f"official saved assignment check failed: {status}")
    # The instructor's sum may differ from math.fsum only by floating reduction order.
    value = official.cut_value(i, j, weights, signs)
    # This scale accounts for signed cancellation without changing the scoring rule.
    allowance = 64.0 * math.ulp(1.0) * math.fsum(abs(float(w)) for w in weights)
    # Compare direct evaluations of the same labels with no relative loophole.
    if not math.isclose(value, expected_cut, rel_tol=0.0, abs_tol=allowance):
        # Any discrepancy beyond summation roundoff prevents a successful CLI report.
        raise FloatingPointError("core and official saved cuts disagree")
    # A custom toy graph is not silently assigned a public reference merely by sharing a basename.
    result = {"cut": value, "status": "ok", "score": None, "reference_status": "not_available"}
    # Only actual public paths may use the supplied public reference table here.
    if instance.resolve().is_relative_to(PROJECT_ROOT / "instances/public"):
        # Reference absence is explicit rather than an invented zero or optimum.
        reference_path = PROJECT_ROOT / "references/public.json"
        # A missing table does not prevent honest cut verification.
        if reference_path.exists():
            # JSON data contains fixed instructor reference values, not solver estimates.
            references = json.loads(reference_path.read_text(encoding="utf-8"))
            # Some custom public-directory inputs may have no corresponding reference.
            if instance.name in references:
                # Preserve the official summation for W/2 when computing its normalized score.
                half = float(weights.sum()) / 2.0
                # Convert the fixed reference into a finite scalar before normalization.
                reference = float(references[instance.name]["ref"])
                # A zero/nonfinite denominator is a scoring-data error, never a guessed score.
                if not math.isfinite(reference - half) or reference == half:
                    # Fail clearly instead of emitting infinity/NaN JSON.
                    raise ValueError("scoring-data error: invalid reference denominator")
                # This is the unchanged official normalization, not cut/reference.
                result["score"] = (value - half) / (reference - half)
                # An overflowed normalized value must not become nonstandard Infinity JSON.
                if not math.isfinite(result["score"]):
                    # Report unusable scoring data explicitly rather than fabricating a finite score.
                    raise ValueError("scoring-data error: normalized score is not finite")
                # State that a fixed reference is present without claiming it is an exact optimum.
                result["reference_status"] = "available"
    # Return small independently measured evidence for the history report.
    return result


# One graph CLI preserves old defaults while exposing every added search budget explicitly.
def main(argv=None):
    """Steps 1–12: validate, solve, retain output, recheck files, record provenance.

    argv is list[str] or None for shell options; returns None. Old default
    seed=42, sweeps=200, K=32 and M=1,P=0 use the settled solve_bm path when
    no incumbent exists. --initial-assignment adds saved signs, not RNG state.
    Explicit existing outputs are validated and never degraded. Timing starts
    after parsing and ends after saved-output official checks, excluding JSON
    history serialization and final console output. Costs the selected passes
    plus linear file validation and metadata work; writes only chosen outputs.
    """
    # Keep the established argument names, types and defaults.
    parser = argparse.ArgumentParser(description=__doc__)
    # The caller must select a real graph rather than a placeholder name.
    parser.add_argument("--instance", required=True, type=Path, help="Fixed n m / i j w graph; original node IDs start at 1.")
    # An omitted path keeps the settled, guarded default smoke directory.
    parser.add_argument("--output", type=Path, help="Selected assignment; existing valid output is retained unless strictly improved.")
    # Original seeds control restart-zero's coupled initialization/sweep stream unchanged.
    parser.add_argument("--seed", type=int, default=42, help="Nonnegative base seed (default: 42).")
    # These counts and tolerances retain all old meanings/units.
    parser.add_argument("--max-sweeps", type=int, default=200, help="Nonnegative sweep limit PER pass (default: 200).")
    # Count midpoint normal directions, not independent starts.
    parser.add_argument("--roundings", type=int, default=32, help="Positive normal count PER pass (default: 32).")
    # Field tolerance is relative to incident absolute weight.
    parser.add_argument("--field-rtol", type=float, default=1e-12, help="Relative negligible-field fraction of incident |weights| (default: 1e-12).")
    # Absolute sweep tolerance has weighted-objective units.
    parser.add_argument("--sweep-atol", type=float, default=1e-12, help="Absolute sweep-improvement threshold in weight units (default: 1e-12).")
    # Relative sweep tolerance is dimensionless.
    parser.add_argument("--sweep-rtol", type=float, default=1e-9, help="Relative sweep-improvement threshold (default: 1e-9).")
    # Binary gain tolerance has weight units and never authorizes worsening flips.
    parser.add_argument("--gain-tolerance", type=float, default=1e-10, help="Absolute accepted binary flip threshold in weight units (default: 1e-10).")
    # Projection tolerance is dimensionless with the old +1 near-boundary tie policy.
    parser.add_argument("--projection-tolerance", type=float, default=1e-12, help="Dimensionless +1 boundary-tie tolerance in [0,1) (default: 1e-12).")
    # Total initializations include the original one; this default adds none.
    parser.add_argument("--restarts", type=int, default=1, help="TOTAL independent starts M>=1, including the original (default: 1).")
    # Perturbations are additional passes after EACH independent initialization.
    parser.add_argument("--perturb-rounds", type=int, default=0, help="Additional refinement rounds P>=0 PER restart (default: 0).")
    # Scale is a uniform half-width in radians, never a flip fraction or Gaussian deviation.
    parser.add_argument("--perturb-scale", type=float, default=0.35, help="Uniform angular half-width sigma in RADIANS, 0<=sigma<=pi (default: .35).")
    # A binary incumbent can be continued without claiming exact angle/RNG checkpoint resumption.
    parser.add_argument("--initial-assignment", type=Path, help="Valid labels for THIS graph; include their recomputed cut and refine in restart zero.")
    # History remains optional, scalar and separate from the assignment's binary lines.
    parser.add_argument("--history", type=Path, help="Selected JSON history path, distinct from inputs/output/metadata.")
    # parse_args(None) reads shell arguments; explicit lists support bounded tests.
    args = parser.parse_args(argv)
    # Measure the stated end-to-end scope, starting before graph and incumbent I/O.
    end_started = perf_counter()
    # An omitted output cannot silently authorize replacing an existing smoke assignment.
    output = args.output
    # Derive the same default basename as the original CLI.
    if output is None:
        # Keep old smoke outputs separate from authoritative solution sets.
        output = Path("solutions_bm_smoke") / args.instance.name
        # Preserve the existing bounded test and deliberate default-path protection.
        if output.exists():
            # Require explicit selection of a path before considering an existing assignment.
            parser.error("default smoke output already exists; select --output explicitly to retain/refine it")
    # Validation and expected numerical/file errors become clear unsuccessful CLI exits.
    try:
        # Reject unsupported outer-loop settings even if the compatibility path would not use sigma.
        if args.restarts < 1 or args.perturb_rounds < 0 or not math.isfinite(args.perturb_scale) or not 0 <= args.perturb_scale <= math.pi:
            # Preserve clear total/additional count and radian-range semantics.
            raise ValueError("require restarts>=1, perturb-rounds>=0, and finite 0<=perturb-scale<=pi radians")
        # Output may equal an explicit initial assignment but may never equal the graph or protected files.
        protect_destination(output, args.instance)
        # Sidecar writes must obey the same directory/source protections.
        protect_destination(metadata_path(output), args.instance)
        # A different supplied initial file and its metadata remain read-only sources.
        if args.initial_assignment is not None and output.resolve() != args.initial_assignment.resolve():
            # A selected output cannot be disguised as the other initial file's metadata.
            protect_destination(output, args.instance, [metadata_path(args.initial_assignment)])
            # The output sidecar must not overwrite separately supplied binary labels or metadata.
            protect_destination(metadata_path(output), args.instance, [args.initial_assignment, metadata_path(args.initial_assignment)])
        # A history may not overwrite either labels, identity metadata, or a supplied incumbent.
        prior_history = None
        # Validate optional existing history metadata before any solver work.
        if args.history is not None:
            # Protect the selected assignment and its sidecar before any solver work.
            readonly = [output, metadata_path(output)]
            # Initial labels/metadata remain read-only unless the output path explicitly selects those labels.
            if args.initial_assignment is not None:
                # The history cannot disguise a destructive initial-file overwrite.
                readonly.extend([args.initial_assignment, metadata_path(args.initial_assignment)])
            # Check every guarded identity before loading and optimizing.
            protect_destination(args.history, args.instance, readonly)
            # Existing histories can be replaced only when they actually describe these selected files.
            if args.history.exists():
                # Invalid/non-JSON history paths fail instead of destroying unrelated user files.
                prior = json.loads(args.history.read_text(encoding="utf-8"))
                # Require matching current input and selected output identities, not just a .json suffix.
                if not isinstance(prior, dict) or Path(prior.get("instance", "")).resolve() != args.instance.resolve() or Path(prior.get("output", "")).resolve() != output.resolve():
                    # Ask for a fresh explicit history path when this file is unrelated.
                    raise ValueError("existing history belongs to different input/output; select a fresh history path")
                # Retain this available graph identity for checking after current input hashing.
                prior_history = prior
        # The settled loader validates fixed edges and original node order without changing official files.
        graph = load_graph(args.instance)
        # Raw-byte identity is independent of path aliases and shared filenames.
        input_digest = file_sha256(args.instance)
        # A matching history filename/path cannot override a conflicting available raw graph digest.
        if prior_history is not None and prior_history.get("instance_sha256", input_digest) != input_digest:
            # Preserve old histories from changed graph bytes rather than silently relabeling them.
            raise ValueError("existing history graph digest mismatch; select a fresh history path")
        # Record real revision, actual source hashes, and any dirty working tree before output writes.
        identity = code_identity()
        # Track every supplied valid incumbent with its directly recomputed cut/provenance.
        incumbents = []
        # No-incumbent defaults must preserve the original RNG path exactly.
        initial_signs = None
        # None records absence rather than inventing a previous saved cut.
        previous_saved_cut = None
        # Explicit valid existing output is an additional incumbent with tie precedence.
        if output.exists():
            # Malformed output or mismatched available metadata fails before any save.
            initial_signs, previous_saved_cut, info = load_assignment(output, graph, input_digest)
            # Record its role separately from a different user-supplied warm start.
            info["role"] = "existing_output"
            # Keep the actual old cut even if the user supplies a better starting assignment.
            incumbents.append(info)
        # A separate old solution may supply a stronger restart-zero refinement center.
        if args.initial_assignment is not None:
            # Check labels and available metadata against the current graph, not old reported scores.
            supplied, supplied_cut, info = load_assignment(args.initial_assignment, graph, input_digest)
            # Do not lose evidence of either supplied incumbent when both files exist.
            info["role"] = "initial_assignment"
            # Store both actual cuts/provenance values in the report.
            incumbents.append(info)
            # Only a strictly better supplied solution replaces the earlier saved incumbent on a tie.
            if initial_signs is None or supplied_cut > cut_value(graph, initial_signs):
                # Independent owned storage prevents caller/saved labels from becoming workspace.
                initial_signs = supplied.copy()
        # Time just the solver separately from end-to-end CLI operations.
        started = perf_counter()
        # Preserve the original mathematical history/stream when there is no incumbent or enabled extra work.
        if args.restarts == 1 and args.perturb_rounds == 0 and initial_signs is None:
            # Original argument order, values and core entry point remain available to old scripts.
            signs, value, history = solve_bm(graph, args.seed, args.max_sweeps, args.roundings,
                args.field_rtol, args.sweep_atol, args.sweep_rtol, args.gain_tolerance, args.projection_tolerance)
        # Explicit extended search also handles the intentional additional retention behavior.
        else:
            # Use stable basename and raw digest, M TOTAL starts, and P ADDITIONAL rounds per start.
            signs, value, history = solve_bm_extended(graph, args.seed, args.max_sweeps, args.roundings,
                args.field_rtol, args.sweep_atol, args.sweep_rtol, args.gain_tolerance, args.projection_tolerance,
                args.restarts, args.perturb_rounds, args.perturb_scale, initial_signs, args.instance.name, input_digest)
        # This is measured wall time for the solver call, not a stopping budget or guaranteed runtime.
        runtime = perf_counter() - started
        # Preserve solver return quality independently from any later save/verification status.
        returned_cut = cut_value(graph, signs)
        # The solver's scalar result must agree with its actual binary output.
        if returned_cut != value:
            # Surface a correctness failure rather than saving mismatched labels and scores.
            raise FloatingPointError("solver returned cut differs from directly recomputed signs")
        # Only strict improvements replace a selected existing assignment, using a verified sibling temporary.
        saved, saved_cut, output_status = save_verified_assignment(output, signs, graph, input_digest)
        # Re-read the published assignment and optional new metadata one more time.
        loaded, reloaded_cut, info = load_assignment(output, graph, input_digest)
        # The final public file must match the actual saved labels and value.
        if reloaded_cut != saved_cut or loaded.tolist() != saved.tolist():
            # Never report an improvement based solely on an in-memory candidate.
            raise FloatingPointError("saved assignment failed final reload check")
        # Independently corroborate F using the unchanged official loader and evaluator.
        corroboration = official_check(args.instance, output, reloaded_cut)
        # Stop the stated end-to-end scope immediately after saved-label official verification.
        end_elapsed = perf_counter() - end_started
        # Expose scalar attempt summaries even on the legacy one-pass path without changing its core history.
        attempts = []
        # Extended histories already distinguish restart-local/global incumbents and seed roles.
        if "attempts" in history:
            # Copy only small summaries here; the full per-pass scalar traces stay inside solver history once.
            for attempt in history["attempts"]:
                # Excluding core avoids duplicating all sweep/rounding arrays in the JSON report.
                summary = {}
                # Preserve each defined scalar or small seed dictionary, including optional tiny sign examples.
                for key, item in attempt.items():
                    # The complete nested mathematical trace remains available under solver.attempts.
                    if key != "core":
                        # Summaries are serialized immediately and never become optimization state.
                        summary[key] = item
                # Keep the chronological attempt identities, including losses and ties.
                attempts.append(summary)
        # The original path still represents one complete initial pass with the coupled seed stream.
        else:
            # Count the settled baseline and rounding local-search effort without changing any math.
            flips = history["baseline"]["accepted_flips"]
            # Every direction contributes its measured accepted-flip count.
            for rounding in history["roundings"]:
                # Adding counts is bookkeeping, not an extra optimization call.
                flips += rounding["accepted_flips"]
            # Legacy no-incumbent results have candidate/local/global cuts equal at their sole attempt.
            attempts.append({"restart_index": 0, "round_index": 0, "kind": "initial",
                             "seeds": {"initialization": args.seed, "sweep_order": args.seed,
                                       "noise": None, "legacy_coupled": True},
                             "candidate_cut": returned_cut, "restart_best_cut": returned_cut,
                             "global_best_cut": returned_cut, "elapsed_seconds": runtime,
                             "sweeps_used": len(history["continuous"]["sweeps"]),
                             "accepted_flips": flips, "stop_reason": history["continuous"]["stop_reason"]})
        # Report a previous-best difference only when an actual incumbent was available.
        previous_best = None if initial_signs is None else cut_value(graph, initial_signs)
        # The legacy report keys remain present for the existing ladder/refinement scripts.
        report = {"instance": str(args.instance), "instance_key": args.instance.name,
                  "instance_sha256": input_digest, "output": str(output),
                  "node_count": graph.node_count, "edge_count": len(graph.edges),
                  "runtime_seconds": runtime, "reloaded_cut": reloaded_cut, "solver": history,
                  "code_identity": identity, "incumbents": incumbents,
                  "previous_saved_cut": previous_saved_cut, "previous_best_cut": previous_best,
                  "best_returned_cut": returned_cut, "saved_cut": saved_cut,
                  "difference": None if previous_best is None else saved_cut - previous_best,
                  "difference_from_previous_saved": None if previous_saved_cut is None else saved_cut - previous_saved_cut,
                  "output_status": output_status, "official_verification": corroboration,
                  "extension": {"restarts": args.restarts, "perturb_rounds": args.perturb_rounds,
                                "perturb_scale_radians": args.perturb_scale}, "attempts": attempts,
                  "total_passes": args.restarts * (1 + args.perturb_rounds),
                  "end_to_end_seconds": end_elapsed,
                  "end_to_end_scope": "After parsing through graph/metadata reads, solver, atomic save and official reload; excludes JSON history write and console output."}
        # Optional history is a selected JSON artifact, not extra assignment lines.
        if args.history is not None:
            # Finite atomic JSON keeps a partial write from replacing a complete earlier report.
            atomic_json(args.history, report)
        # Print actual saved F and status so a retained incumbent is not presented as a fresh improvement.
        print(f"cut={saved_cut:.17g}; reloaded_cut={reloaded_cut:.17g}; runtime_seconds={runtime:.9f}; output={output}; status={output_status}; passes={report['total_passes']}")
    # Expected malformed inputs, invalid metadata and numerical errors fail visibly without silent repairs.
    except (OSError, ValueError, FloatingPointError, OverflowError, TypeError) as error:
        # argparse prints a concise message and exits unsuccessfully rather than claiming a completed solve.
        parser.error(str(error))


# Importing the CLI defines helpers without running optimization or creating files.
if __name__ == "__main__":
    # None argv means use the actual shell arguments.
    main()
