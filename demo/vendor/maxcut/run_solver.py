"""One solver, one graph, fresh artifacts and independently verified labels."""

# argparse supplies a small one-shot CLI and a private worker mode for hard deadlines.
import argparse
# JSON records exact configuration, request, result and raw process registrations.
import json
# Finite limits are checked before reserving an experiment directory.
import math
# Process identifiers and signals are used only for owned timeout cleanup.
import os
# Path resolves original inputs and a fresh user-selected output tree.
from pathlib import Path
# Native/worker subprocesses use explicit argv arrays without shell evaluation.
import subprocess
# The current isolated Python interpreter is reused by the solver worker.
import sys
# Tracebacks are retained in real worker logs on implementation/backend failure.
import traceback
# Monotone elapsed time records complete runner execution independently of solver time.
from time import perf_counter
# A no-work timeout fallback owns a valid original-order +/-1 vector.
import numpy as np
# The original graph and direct evaluator remain authoritative for returned labels.
from bm_solver import cut_value,load_graph,validate_signs
# Shared result validation keeps execution, feasibility and optimality distinct.
from portfolio_common import result_record
# Owned process cleanup handles both a worker and its separately registered native sessions.
from portfolio_external import process_tick,stop_process_group
# Ordinary explicit dispatch avoids an evolutionary or automatic portfolio policy.
from solver_portfolio import FEATURES,list_solvers,solve
# Reuse graph metadata checks, safe persistence and the unchanged official-file corroboration.
from run_bm import atomic_json,code_identity,file_sha256,load_assignment,official_check,protect_destination,save_verified_assignment


# Race-safe cleanup is shared by timeout and interruption paths.
def cleanup_native(directory, owner_pid):
    """Stop registered native groups belonging to owner_pid in fresh directory.

    Arguments Path directory and int worker PID identify only this run. Return
    None; signal owned groups, tolerate registrations removed during reads.
    Example cleanup_native(Path('runs/example'), worker.pid). Start ticks
    prevent PID reuse; work is O(active records), with no graph operations.
    """
    # Native registrations are atomically written and may disappear after successful completion.
    for registration in directory.rglob("process.json"):
        # A disappearing registration means its adapter has already finished cleanup.
        try:
            # Atomic publication prevents a partially written JSON document being read here.
            active=json.loads(registration.read_text())
        # Missing files are an expected adapter/parent completion race.
        except FileNotFoundError:
            # Continue checking any other active own-run sessions.
            continue
        # Restrict cleanup to the exact worker launched for this request.
        if active.get("owner_pid")==owner_pid:
            # This targets the registered incarnation and its MPI descendants only.
            stop_process_group(active["pid"],active["tick"])


# A child process permits strict time limits without changing the settled BM kernels or upstream code.
def worker(request_path):
    """Read one request JSON, run one solver and write actual worker_result.json.

    request_path Path contains instance, solver, config, seed, budget, optional
    initial labels and output directory. Returns exit code 0 success, 2
    unavailable, 1 failure. Only the fresh selected run tree is written.
    Errors preserve tracebacks in the parent's captured raw log. No automatic
    retries, alternate solvers or campaign loop. Cost is exactly one requested
    solve plus serialization and independent validation.

    Example: worker(Path('runs/example/request.json')) runs that declared request.
    Reference: the shared solver contract and original F; worker never chooses a different method.
    """
    # Read the explicit parent request rather than inheriting unstated mutable settings.
    request=json.loads(request_path.read_text())
    # This fresh tree belongs to one invocation only.
    directory=Path(request["directory"])
    # Reload fixed graph data in the isolated worker without changing original files.
    graph=load_graph(request["instance"])
    # Worker failures also need their own honest elapsed measurement.
    started=perf_counter()
    # Native methods receive a run-local artifact subtree controlled by the parent runner.
    config=request["config"].copy()
    # No caller-specified work path can escape the timeout-cleanup/artifact tree.
    if request["solver"] in {"mqlib","scientific","biqbin","madam","biqcrunch"}:
        # Each actual native execution uses a separately reserved new directory.
        config["work_dir"]=str(directory/"native")
    # Exceptions become explicit failed records and raw tracebacks, not fake zero-score successes.
    try:
        # Equivalent graph, method config, seed, time/work budget and real incumbent enter the shared API.
        result=solve(graph,config,request["seed"],request["budget"],request["initial_assignment"],solver=request["solver"])
        # This native result is separate from final parent reload/official validation.
        atomic_json(directory/"worker_result.json",result)
        # Missing optional backends have a distinct exit status and a structured unavailable record.
        return 2 if result["execution_status"]=="unavailable" else 1 if result["execution_status"]=="failed" else 0
    # Implementation/backend errors must remain visible and reproducible.
    except Exception as error:
        # The raw traceback identifies the actual failing source line and operation.
        traceback.print_exc()
        # No assignment or bound is invented after an exception.
        result=result_record(request["solver"],graph,config,request["seed"],request["budget"],started,
                             status="failed",reason=f"{type(error).__name__}: {error}")
        # Preserve failure evidence in the same unique run tree as raw stdout/stderr.
        atomic_json(directory/"worker_result.json",result)
        # The CLI must not return success for an unvalidated backend execution.
        return 1


# The public entry point owns one fresh run and never replaces an existing solution set.
def main(argv=None):
    """List capabilities or run one selected solver on one original graph.

    argv list[str] or None. --list prints JSON availability/features, --features
    with --solver prints one entry. Solve requires --solver,--instance,--output;
    config JSON defaults {}, seed=1, time-limit=60 seconds; optional max-work
    maps to the selected method's explicit counter. --initial-assignment is
    validated with graph metadata and rejected if unsupported. Example:
    --solver bm --instance instances/public/rand_pos_20_s2.txt --output runs/bm.
    Returns exit code 0 completed/time_limit,2 unavailable,1 failed. Writes
    request/result JSON, actual worker/native logs, and validated labels under
    output/solutions/<instance>. The worker hard deadline includes its setup;
    parent validation/output work is separately measured and may extend total
    wall time. No input mutation, stale resume, campaigns or evolution.
    """
    # Keep a small conventional CLI whose help/list paths start no solver.
    parser=argparse.ArgumentParser(description=__doc__)
    # Capability discovery does not require an instance or output folder.
    parser.add_argument("--list",action="store_true")
    # One named method's capabilities are useful before choosing a warm start or work budget.
    parser.add_argument("--features",action="store_true")
    # Choices prevent silently treating a misspelled published method as another solver.
    parser.add_argument("--solver",choices=list(FEATURES))
    # Inputs remain the existing one-based edge-list files, interpreted in original node order.
    parser.add_argument("--instance",type=Path)
    # Explicit method configuration is preserved verbatim alongside resolved result parameters.
    parser.add_argument("--config",type=Path)
    # The seed is recorded and supported native ranges are validated by their adapters.
    parser.add_argument("--seed",type=int,default=1)
    # A hard subprocess deadline complements method-specific cooperative checks.
    parser.add_argument("--time-limit",type=float,default=60.0)
    # Unsupported native work limits are explicitly rejected instead of ignored.
    parser.add_argument("--max-work",type=int)
    # The existing assignment reader validates shape, signs and available graph/assignment metadata.
    parser.add_argument("--initial-assignment",type=Path)
    # Every public solve requires a deliberately selected fresh output directory.
    parser.add_argument("--output",type=Path)
    # Private worker mode is an implementation detail, not another user workflow.
    parser.add_argument("--worker",type=Path,help=argparse.SUPPRESS)
    # Tests can call the same actual parser with a supplied argument list.
    args=parser.parse_args(argv)
    # Worker mode executes exactly one previously declared parent request.
    if args.worker is not None:
        # The parent performs final input/assignment/official validation after this returns.
        return worker(args.worker)
    # Basic capability listing must remain available even when optional backends are missing.
    if args.list:
        # Plain JSON exposes actual available paths and supported features without installing packages.
        print(json.dumps(list_solvers(),indent=2))
        # No input/output tree or solver child is created.
        return 0
    # Per-solver features are a read-only alternative to printing the full list.
    if args.features:
        # A method must be explicitly selected for a per-solver capability query.
        if args.solver is None:
            # Explain the missing CLI relationship before doing any solver work.
            parser.error("--features requires --solver")
        # Return only that method's actual capabilities/availability.
        print(json.dumps(list_solvers()[args.solver],indent=2))
        # Feature inspection creates no result artifacts.
        return 0
    # A one-shot run needs all three explicit identifying paths/names.
    if args.solver is None or args.instance is None or args.output is None:
        # Do not launch a default public graph or choose an output folder on the user's behalf.
        parser.error("run requires --solver, --instance and --output")
    # Limits are validated before any result directory is reserved.
    if args.seed<0 or not math.isfinite(args.time_limit) or args.time_limit<0 or (args.max_work is not None and args.max_work<0):
        # User typos are input errors, not timed-out solver performance.
        parser.error("seed/time/work limits must be finite and nonnegative")
    # Retain a complete end-to-end measurement including parent validation and output.
    started=perf_counter()
    # Input errors preserve all prior source/result directories.
    try:
        # Existing outputs are evidence and cannot be silently reused for a new request.
        if args.output.exists():
            # Resumption requires a distinct explicit design, not stale file discovery.
            raise ValueError("output directory exists; choose a fresh run path")
        # Original graph metadata and numerical indexing are validated by the settled loader.
        graph=load_graph(args.instance)
        # Raw bytes identify the actual input, separately from the semantic graph hash in API results.
        digest=file_sha256(args.instance)
        # Configuration files must contain a JSON dictionary of method parameters.
        config={} if args.config is None else json.loads(args.config.read_text())
        # Reject malformed or escapable native-artifact configuration at the public runner boundary.
        if not isinstance(config,dict) or config.get("work_dir") is not None:
            # The runner owns its fresh native directory so hard-timeout cleanup can find every backend process.
            raise ValueError("config must be an object; omit work_dir in one-shot runner configs")
        # Time is universal; work limits retain actual method-specific units only when supplied.
        budget={"seconds":args.time_limit}
        # A caller can explicitly impose supported work limits in addition to time.
        if args.max_work is not None:
            # The selected adapter validates whether it supports this work control.
            budget["max_work"]=args.max_work
        # No explicit incumbent means the normal solver initialization path remains unchanged.
        initial=None
        # Record actual warm provenance separately from the algorithm's resolved settings.
        initial_info=None
        # Supplying an incumbent must be meaningful for the selected method.
        if args.initial_assignment is not None:
            # The capability declaration prevents silently ignored warm input.
            if FEATURES[args.solver]["warm_start"] in {"unsupported","unavailable"}:
                # The user can run from scratch or choose a genuinely supported warm-start backend.
                raise ValueError("selected backend does not support initial_assignment")
            # Verify signs, n and any graph/assignment SHA sidecar before launching the worker.
            initial,value,initial_info=load_assignment(args.initial_assignment,graph,digest)
        # Protect official files and every explicitly supplied read-only dependency.
        readonly=[path for path in (args.instance,args.config,args.initial_assignment) if path is not None]
        # Representative output guards resolve symlinks and protected directory descendants.
        protect_destination(args.output/"result.json",args.instance,readonly)
        # A directory containing a read-only input must not be used as the output ancestor.
        if any(Path(path).resolve().is_relative_to(args.output.resolve()) for path in readonly):
            # Reserve an independent run tree instead of mixing inputs with fresh evidence.
            raise ValueError("output must not contain input/config/incumbent paths")
        # Exclusive reservation makes concurrent or stale identifier collisions explicit.
        args.output.mkdir(parents=True,exist_ok=False)
        # Use absolute paths so worker cwd and backend cwd never change the input identity.
        directory=args.output.resolve()
        # Record the exact declared request before running one solver.
        request={"solver":args.solver,"instance":str(args.instance.resolve()),"input_sha256":digest,
                 "config":config,"seed":args.seed,"budget":budget,"initial_assignment":None if initial is None else initial.tolist(),
                 "initial_assignment_info":initial_info,"directory":str(directory)}
        # Preserve the pre-run command inputs and warm labels as independent JSON evidence.
        atomic_json(directory/"request.json",request)
        # Only a valid already-known assignment can be returned when the worker is forcibly stopped.
        fallback=np.ones(graph.node_count,dtype=np.int8) if initial is None else initial.copy()
        # Real worker stdout/stderr is retained even on backend import/setup/process failure.
        raw_log=directory/"worker.log"
        # A timeout record is distinct from a native solver that completed within its own limits.
        timed_out=False
        # The parent captures worker output without giving a backend direct access to an existing solution file.
        with raw_log.open("w",encoding="utf-8") as stream:
            # A fresh process session permits safe termination of the one requested worker.
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),"--worker",str(directory/"request.json")],
                                   stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
            # Preserve the exact worker incarnation for safe cleanup on a deadline.
            tick=process_tick(child.pid)
            # Always stop/reap children if the parent is interrupted as well as on time expiration.
            try:
                # The hard limit includes worker graph loading, optional imports and method setup.
                child.wait(timeout=args.time_limit)
            # A stalled matching/native/BM call cannot bypass the user's explicit one-shot deadline.
            except subprocess.TimeoutExpired:
                # The deadline was actually enforced rather than only printed in result metadata.
                timed_out=True
                # Native executables may own separate sessions registered inside this unique run tree.
                cleanup_native(directory,child.pid)
                # Terminate the worker's own session after any separate native sessions.
                stop_process_group(child.pid,tick)
                # Reap the stopped process before reading partial/final evidence.
                child.wait()
            # Terminal interruption must not leave a long native solver running behind the user's back.
            except BaseException:
                # Clean up every active native session declared by this exact worker.
                cleanup_native(directory,child.pid)
                # The worker session is also owned by this one-shot invocation.
                stop_process_group(child.pid,tick)
                # Reap before propagating the real interruption.
                child.wait()
                # No fabricated completed result is created after a user interruption.
                raise
        # A completed atomic worker record can survive a race between result write and process timeout.
        if (directory/"worker_result.json").exists():
            # Parent validates this result again; presence alone is not a success claim.
            result=json.loads((directory/"worker_result.json").read_text())
        # A hard timeout without a completed native record only permits the known initial/all-plus witness.
        else:
            # Report no invented counters, bound or unobserved intermediate assignment.
            result=result_record(args.solver,graph,config,args.seed,budget,started,
                                 fallback if timed_out else None,status="time_limit" if timed_out else "failed",
                                 reason="hard_worker_time_limit_known_incumbent_only" if timed_out else "worker_exited_without_result",
                                 evidence={"fallback":"supplied incumbent" if initial is not None else "all-plus cut zero"})
        # A hard timeout remains explicit even if a complete result was written just before termination.
        if timed_out:
            # Assignment validity/proof evidence is separately assessed from process completion.
            result["execution_status"]="time_limit"
            # Preserve that the runner, rather than a guessed native stop reason, ended this invocation.
            result["runner_time_limit_enforced"]=True
        # Input identity must remain fixed across the entire execution before any authoritative labels are published.
        if file_sha256(args.instance)!=digest:
            # A graph edited mid-run invalidates the request/results association.
            raise ValueError("input graph changed during solver run")
        # Independently revalidate actual labels instead of trusting a claimed cut or feasible flag.
        if result["assignment"] is not None:
            # This copies and checks original node order, length and exact +/-1 membership.
            signs=validate_signs(result["assignment"],graph.node_count)
            # Recompute the original fixed-graph objective independently of every solver's maintained total.
            value=cut_value(graph,signs)
            # A report/witness mismatch is a correctness failure, not a tolerated quality regression.
            if value!=result["cut"]:
                # No invalid authoritative assignment file is published.
                raise ValueError("worker cut disagrees with original-graph assignment")
            # Preserve the input basename for compatibility with the unchanged official scorer.
            assignment_path=directory/"solutions"/args.instance.name
            # Atomic original-format publication includes checked graph/assignment metadata.
            saved,saved_cut,save_status=save_verified_assignment(assignment_path,signs,graph,digest)
            # The actual saved labels receive independent official-loader/cut corroboration.
            result["official_verification"]=official_check(args.instance,assignment_path,value)
            # The structured result points to the authoritative original-format file.
            result["assignment_path"]=str(assignment_path)
        # Preserve semantic/API identity separately from this actual raw-input-file identity.
        result["semantic_input_sha256"]=result["input_sha256"]
        # Public file runs identify the exact raw instance bytes rather than just graph semantics.
        result["input_sha256"]=digest
        # Avoid confusing a file hash with a floating-semantic canonicalization hash.
        result["input_hash_kind"]="raw_instance_file"
        # Raw worker output remains evidence even when a native solver also has its own log.
        result["raw_backend_logs"].append(str(raw_log))
        # Git identity never claims uncommitted code has a new committed revision.
        identity=code_identity()
        # Portfolio source hashes supplement the existing BM-oriented identity helper.
        for path in [Path(__file__).resolve(),Path(__file__).with_name("solver_portfolio.py"),*Path(__file__).parent.glob("portfolio_*.py")]:
            # Hash actual implementations used by this checkout, including adapters and converters.
            identity["source_sha256"][path.name]=file_sha256(path)
        # This identity captures the actual runner version, not an imagined future commit.
        result["code_identity"]=identity
        # Parent setup/output work is separate from the backend-reported/worker execution interval.
        result["runner_wall_seconds"]=perf_counter()-started
        # Explain the exact timing boundary so a 60-second worker limit is not confused with total shell time.
        result["runner_timing_scope"]="parent entry through independent save/official verification; excludes final JSON write/console"
        # Publish only the complete checked structured record for this unique invocation.
        atomic_json(directory/"result.json",result)
        # A concise terminal report points to detailed evidence without printing every trajectory frame.
        print(f"solver={args.solver}; status={result['execution_status']}; valid={result['solution_valid']}; cut={result['cut']}; optimality={result['optimality_status']}; result={directory/'result.json'}")
        # Time limits can return useful valid answers; unavailable and failed runs remain nonzero exits.
        return 2 if result["execution_status"]=="unavailable" else 1 if result["execution_status"]=="failed" else 0
    # Routine user input/path errors preserve prior work and expose the concrete cause.
    except (OSError,ValueError,TypeError) as error:
        # Do not present an invalid run as successful or silently choose another backend.
        parser.error(str(error))


# Importing the runner has no side effects or background processes.
if __name__=="__main__":
    # Shell exit status agrees with the structured execution outcome.
    raise SystemExit(main())
