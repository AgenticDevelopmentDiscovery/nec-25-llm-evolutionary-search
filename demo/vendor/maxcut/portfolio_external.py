"""Thin pinned-source adapters with lossless conversions, raw logs and process cleanup."""

# JSON reads actual upstream results and the pinned source manifest.
import json
# Finite checks and conservative rounding translate textual native bounds.
import math
# Environment handling preserves caller settings while locating project-local native libraries.
import os
# Path resolves source, binary and run-local artifacts explicitly.
from pathlib import Path
# Regex parses the documented native text interfaces, never a guessed heuristic identifier.
import re
# Signals terminate only the process group launched by this adapter.
import signal
# Native executables run with argument arrays, without a shell.
import subprocess
# Unique directories retain backend logs instead of reusing stale outputs.
import tempfile
# Runtime includes native startup, conversion, solve and result parsing.
from time import perf_counter, sleep
# NumPy owns the recovered original-order binary assignment.
import numpy as np
# Reuse original-graph validation and independent cut scoring.
from bm_solver import cut_value, validate_signs
# Shared contracts and exact decimal-to-integer scaling remain backend-independent.
from portfolio_common import deadline_from, integer_weights, result_record, settings
# SHA identities and protected-path checks are already established in the project.
from run_bm import atomic_json, file_sha256, protect_destination

# Upstream code remains separate from every project-owned adapter.
ROOT=Path(__file__).resolve().parent
# Actual executable paths correspond to the reviewed build outputs.
BINARIES={"mqlib":"external/MQLib/bin/MQLib", "biqbin":"external/BiqBin/biqbin",
          "madam":"external/MADAM/admm", "biqcrunch":"external/BiqCrunch/BiqCrunch_second_release/BiqCrunch/problems/max-cut/biqcrunch",
          "scientific":"external/ScientificMaxcutSolver/build-compat/sms"}
# Source-repository names preserve independent implementation identities.
SOURCES={"mqlib":"MQLib","biqbin":"BiqBin","madam":"MADAM","scientific":"ScientificMaxcutSolver","biqcrunch":"BiqCrunch"}


# A start tick prevents a stale PID record from referring to an unrelated reused process ID.
def process_tick(pid):
    """Return Linux /proc start tick string for int pid, or None if gone.

    Example process_tick(os.getpid()) identifies this process incarnation.
    No mutation; O(proc record bytes). Used only for owned subprocess cleanup,
    not as a wall-clock runtime or a solver work counter.
    """
    # Proc files disappear when processes exit, which is an ordinary cleanup race.
    try:
        # Split after the executable-name parentheses so spaces inside comm do not shift fields.
        text=Path(f"/proc/{pid}/stat").read_text().rsplit(")",1)[1].split()
        # Field 22 is offset 19 after the pid/comm prefix (fields 1 and 2).
        return text[19]
    # A finished process requires no signal or error report.
    except (OSError,IndexError):
        # None means no verified matching process incarnation is available.
        return None


# SIGKILL delivery is asynchronous; cleanup must wait for an owned child to cease running.
def process_live(pid,tick):
    """Return whether this exact owned PID incarnation is alive and not a zombie.

    pid int and tick recorded /proc start tick; no mutation or signals. Example
    process_live(child.pid,tick) distinguishes a reaped/killed rank from a
    pending live process. O(one proc read); vanished or reused PIDs are false.
    """
    # Process state and start tick must come from the same kernel snapshot.
    try:
        # comm can contain spaces, so split only after the final parenthesis.
        fields=Path(f"/proc/{pid}/stat").read_text().rsplit(")",1)[1].split()
        # Zombies and dead states consume no executing solver work.
        return fields[19]==tick and fields[0] not in {"Z","X"}
    # Process exit during observation is a successful stopped-state result.
    except (OSError,IndexError):
        # A reused numeric PID cannot match the exact old start tick.
        return False


# MPI ranks may own separate process groups, so ownership must follow the actual descendant tree.
def owned_descendants(pid,tick):
    """Return [(pid,start_tick),...] descendants of a verified owned root.

    Arguments int root PID and its recorded Linux start tick; no mutation.
    Example owned_descendants(launcher.pid, process_tick(launcher.pid)). Reads
    /proc children/stat only, checks parent links and incarnations before
    recording ownership. O(number of owned descendants), never name matching.
    """
    # PID reuse invalidates an old ownership record before traversal starts.
    if tick is None or process_tick(pid)!=tick:
        # An unrelated or vanished root provides no safe descendant ownership evidence.
        return []
    # An explicit stack handles nested launchers without recursive Python depth limits.
    pending=[(pid,tick)]
    # Keep descendants separate from the root's independently owned process group.
    descendants=[]
    # Every recorded child must belong to a still-matching parent incarnation at observation.
    while pending:
        # Inspect the next verified parent and its direct kernel-reported children.
        parent,parent_tick=pending.pop()
        # Parent/children files can disappear when an owned process exits normally.
        try:
            # The kernel lists direct fork descendants, including ranks with distinct process groups.
            children=Path(f"/proc/{parent}/task/{parent}/children").read_text().split()
            # Capture each child's parent relationship and start tick from the same stat read.
            for child in children:
                # Parse after comm to preserve field positions for executable names with spaces.
                fields=Path(f"/proc/{child}/stat").read_text().rsplit(")",1)[1].split()
                # Check both the child's current parent PID and the parent's exact incarnation.
                if int(fields[1])==parent and process_tick(parent)==parent_tick:
                    # A later reused child PID will fail its own recorded start-tick check before signaling.
                    record=(int(child),fields[19])
                    # Keep an ownership witness for stopping this exact descendant.
                    descendants.append(record)
                    # Traverse grandchildren before terminating the launcher.
                    pending.append(record)
        # Exit races mean no further live children can be verified through that vanished record.
        except (OSError,IndexError):
            # Continue other verified branches rather than targeting processes by executable name.
            continue
    # The caller can signal only these observed owned process incarnations.
    return descendants


# The runner and adapter share one safe cleanup primitive for recorded native sessions.
class OwnedCleanupError(RuntimeError):
    """Cleanup is incomplete; retain exact owned PID/start ticks for safe recovery."""
    state = 'cleanup_failed'

    def __init__(self, survivors):
        self.survivors = survivors
        super().__init__('owned processes have not stopped after SIGKILL: ' + str(survivors))


def stop_process_group(pid,tick):
    """Stop owned group AND verified descendants, including separate MPI rank groups.

    pid int was launched with start_new_session=True; tick is process_tick(pid)
    recorded immediately after launch. Return None. No other process group is
    signaled. Example used on native timeout or parent worker cleanup. O(descendants)
    traversal/system calls plus at most 5.1 seconds for exit confirmation; vanished
    incarnations are no-ops. Descendant ownership uses /proc parent/start ticks.
    """
    # PID reuse must not let stale run evidence target another user's process.
    if tick is None or process_tick(pid)!=tick:
        # The adapter no longer has a verified owned running process to terminate.
        return
    # Capture owned ranks before signaling the launcher, while their ancestry can still be checked.
    descendants=owned_descendants(pid,tick)
    # Terminate ranks first so the launcher has an opportunity to reap its own children.
    for child,child_tick in reversed(descendants):
        # Never signal an unrelated process that reused a finished rank's numeric PID.
        if process_tick(child)==child_tick:
            # A rank can finish between identity verification and its signal.
            try:
                # Individual signaling reaches ranks that created separate process groups.
                os.kill(child,signal.SIGTERM)
            # Already-finished ranks require no additional cleanup.
            except ProcessLookupError:
                # Continue to other verified descendants.
                pass
    # A leader may exit after its ranks, so group termination has its own harmless exit race.
    try:
        # SIGTERM permits the owned launcher to complete native shutdown.
        os.killpg(pid,signal.SIGTERM)
    # The root group can vanish while separately grouped descendants remain.
    except ProcessLookupError:
        # Descendant cleanup below must still run even when the root already exited.
        pass
    # Allow the MPI launcher to reap terminated ranks before forcing surviving owned incarnations.
    sleep(0.1)
    # Captured descendant ownership remains valid even after reparenting to init.
    for child,child_tick in reversed(descendants):
        # Reused PIDs fail this exact incarnation check.
        if process_tick(child)==child_tick:
            # A rank may finish after this check but before delivery.
            try:
                # Force only this previously verified descendant, including separately grouped ranks.
                os.kill(child,signal.SIGKILL)
            # Already-reaped descendants require no signal.
            except ProcessLookupError:
                # Continue stopping remaining owned descendants.
                pass
    # Recheck the root incarnation before the final group signal to avoid numeric PID reuse.
    if process_tick(pid)==tick:
        # A final root-exit race does not change which group we own.
        try:
            # The adapter reaps its own launcher immediately after this cleanup returns.
            os.killpg(pid,signal.SIGKILL)
        # No active root group remains if native shutdown already completed.
        except ProcessLookupError:
            # Cleanup has already stopped any surviving verified descendants above.
            pass
    # A successful signal is not yet evidence that an asynchronously killed descendant has stopped.
    cleanup_deadline=perf_counter()+5.0
    # Give only these owned incarnations a bounded interval to transition to stopped/reaped state.
    while any(process_live(child,child_tick) for child,child_tick in descendants) and perf_counter()<cleanup_deadline:
        # Ten milliseconds is enough to yield scheduling without blocking ordinary progress updates.
        sleep(0.01)
    # An uninterruptible surviving child must remain a visible cleanup failure, never a false success.
    survivors=[(child,child_tick) for child,child_tick in descendants if process_live(child,child_tick)]
    if survivors:
        # Preserve the actual cause for the worker's raw error record.
        raise OwnedCleanupError(survivors)



# Full raw output stays on disk even if a backend fails or times out.
def native_call(command,directory,seconds):
    """Run explicit argv in fresh directory; return text,exit code,timed_out,log.

    command list[str], directory Path, seconds>=0 remaining budget. Captures
    stdout/stderr to backend.log. Records process.json while active for parent
    cleanup, uses a new session and reaps on timeout/exception. No shell or
    source edits. Runtime bounded by requested process timeout plus cleanup;
    output memory is O(log bytes). Example ['MQLib','-l'] lists actual codes.
    """
    # Copy environment instead of modifying the user's library/thread settings in place.
    environment=os.environ.copy()
    # A project-local native prefix supplies optional BLAS/SCIP/SuiteSparse libraries.
    environment["LD_LIBRARY_PATH"]=str(ROOT/"external/native/lib")+os.pathsep+environment.get("LD_LIBRARY_PATH","")
    # Small validation jobs should not silently occupy every BLAS/OpenMP thread.
    environment["OMP_NUM_THREADS"]="1"
    # Native BLAS libraries honor their separate worker-count setting.
    environment["OPENBLAS_NUM_THREADS"]="1"
    # The actual command is part of raw evidence, with each argument retained independently.
    (directory/"command.json").write_text(json.dumps(command,indent=2)+"\n")
    # A new run owns this log; no previous backend output is appended or treated as current.
    log=directory/"backend.log"
    # Default completion state is overwritten only after a real timeout occurs.
    timed_out=False
    # Open the selected log before launching the child so even startup errors remain locatable.
    with log.open("w",encoding="utf-8") as stream:
        # A separate process session lets cleanup kill MPI descendants as well as the launcher.
        child=subprocess.Popen(command,cwd=directory,stdout=stream,stderr=subprocess.STDOUT,env=environment,start_new_session=True)
        # Record the exact process incarnation for safe parent timeout cleanup.
        tick=process_tick(child.pid)
        # Parent runner only acts on this own-run registration file.
        atomic_json(directory/"process.json",{"pid":child.pid,"tick":tick,"owner_pid":os.getpid()})
        # Always reap and clear active registration, including on an outer worker interruption.
        try:
            # Native allowance uses remaining time rather than a new independent budget.
            child.wait(timeout=max(0.001,seconds))
        # A time-limited backend may still leave a useful feasible solution/checkpoint.
        except subprocess.TimeoutExpired:
            # Mark timeout before stopping the owned process group.
            timed_out=True
            # No subprocess survives this adapter's timeout path.
            stop_process_group(child.pid,tick)
            # Reap the owned launcher after killing its group.
            child.wait()
        # Exceptions must not leak native children beyond a failed worker.
        except BaseException:
            # Stop only the verified native session owned by this invocation.
            stop_process_group(child.pid,tick)
            # Reap the owned process before propagating the actual error.
            child.wait()
            # The outer runner records the real failure instead of fabricating completion.
            raise
        # Active PID records cannot remain after ordinary native completion.
        finally:
            # Remove only this invocation's own ephemeral registration file.
            (directory/"process.json").unlink(missing_ok=True)
    # Read raw output only after the writer descriptor is closed.
    return log.read_text(errors="replace"),child.returncode,timed_out,str(log)


# Upstream identities combine pinned revisions with actual executable hashes.
def upstream_identity(name,binary):
    """Return source metadata plus actual executable SHA for selected native name.

    name is mqlib/biqbin/madam/biqcrunch/scientific; binary is existing Path.
    Reads external/sources.json without mutation, O(manifest+binary bytes).
    Example mqlib retains its independent revision instead of being called
    the project BM implementation merely because BURER2002 is selected.
    """
    # Source manifest may be absent on a minimal basic-only installation.
    path=ROOT/"external/sources.json"
    # An empty list is honest missing provenance, not an invented revision.
    records=json.loads(path.read_text()) if path.exists() else []
    # Find the source identity corresponding to this independent backend.
    source=next((r.copy() for r in records if r["name"]==SOURCES[name]),{})
    # Hash the actual built executable; identical source can have different build flags.
    source["executable_sha256"]=file_sha256(binary)
    # Full native identity is preserved alongside the standard result fields.
    return source


# Native conversions are deliberately explicit and individually validated on signed/decimal fixtures.
def mqlib_codes(listing):
    """Read nonindented native identifiers; legitimate codes contain lowercase b."""
    return set(re.findall(r"^[A-Z][A-Za-z0-9_]+$",listing,re.M))


def partition_signs(zero, one, node_count):
    """Validate native partitions and map them once in O(n) time/storage."""
    if any(type(vertex) is not int or not 0 <= vertex < node_count for part in (zero, one) for vertex in part):
        raise ValueError("SMS partition contains invalid original vertex IDs")
    zero_set, one_set = set(zero), set(one)
    if len(zero) + len(one) != node_count or zero_set & one_set or zero_set | one_set != set(range(node_count)):
        raise ValueError("SMS partition mapping does not cover original nodes")
    signs = np.ones(node_count, dtype=np.int8)
    signs[list(one_set)] = -1
    return signs


def solve_native(graph,config,seed,budget,initial_assignment=None,method="mqlib"):
    """Run one actual external implementation with guarded conversion and parsing.

    config max_nodes defaults 1024 for BiqBin/MADAM, 5000 BiqCrunch,100000
    MQLib/SMS; work_dir optional fresh Path string; MQLib heuristic='BURER2002'.
    seed is 0..65535 for MQLib, nonnegative int32 for BiqCrunch/SMS; pinned
    BiqBin/MADAM hardcode srand(2020), so REQUIRE seed=2020 rather than ignoring
    it. budget seconds is native/process time; max_work maps SMS branch-node
    limit, otherwise must be omitted (native API has no work limit).
    Native warm input is currently supported by SMS only; all other adapters
    reject it explicitly. Integer-only SDP backends use exact decimal scaling.
    Return independently scored original-order labels, reported bounds/status,
    native identity and persistent raw artifacts. No prior solutions/source
    writes; only fresh run-local files. Dense native SDP allocation is guarded
    by supported sizes. Timeouts may retain all-plus if native output is absent.

    Example: solve_native(g,{},1,{'seconds':1},method='mqlib').
    Reference: native objective conventions are checked against F=sum_E w*(1-s_i*s_j)/2.
    """
    # Time includes configuration, conversion, native run and independent validation.
    started=perf_counter()
    # Use the actual supported sizes rather than allocating huge native SDP matrices.
    maximum=1024 if method in {"biqbin","madam"} else 5000 if method=="biqcrunch" else 100000
    # Config controls are explicit and method-specific.
    defaults={"max_nodes":maximum,"work_dir":None}
    # Heuristic selection uses the actual MQLib build's identifier listing.
    if method=="mqlib":
        # The requested reference comparison is independent upstream BURER2002.
        defaults["heuristic"]="BURER2002"
    # Unknown method settings must never silently change a different backend.
    cfg=settings(config,defaults)
    # Fixed-size upstream arrays cannot be enlarged by merely overriding an adapter's parameter.
    if type(cfg["max_nodes"]) is not int or cfg["max_nodes"]<1 or graph.node_count>cfg["max_nodes"] or (method in {"biqbin","madam"} and graph.node_count>1024):
        # Explicit unsupported size is distinguishable from a solver error or a bad cut.
        return result_record(method,graph,cfg,seed,budget,started,status="unavailable",reason="graph exceeds backend/adapter size limit")
    # Generic time budgets are accepted, but unsupported work-limit requests cannot be ignored.
    if "max_work" in budget and method!="scientific":
        # Native time-only backends expose exactly that capability in --list.
        raise ValueError(f"{method} supports seconds only, not max_work")
    # Validate finite nonnegative seconds using the common budget contract.
    deadline=deadline_from(budget)
    # Explicit warm-start rejection prevents an apparently accepted incumbent from having no effect.
    if initial_assignment is not None and method!="scientific":
        # The native CLI does not expose a vector warm-start interface for these pinned versions.
        raise ValueError(f"{method} adapter does not support initial_assignment")
    # The original BiqBin/MADAM C sources fix their seed internally.
    if method in {"biqbin","madam"} and seed!=2020:
        # Users must see that arbitrary requested seed changes would otherwise have no effect.
        raise ValueError(f"{method} upstream hardcodes seed=2020; request 2020 explicitly")
    # Respect actual native seed ranges rather than undocumented modular remapping.
    if seed<0 or seed>(65535 if method=="mqlib" else 2**31-1):
        # This error occurs before creating solver output directories.
        raise ValueError("seed exceeds native supported range")
    # Unknown names must not dispatch to a different executable.
    if method not in BINARIES:
        # A project baseline is not a substitute implementation for a missing published solver.
        raise ValueError("unknown native backend")
    # The binary path resolves only this reviewed project-local upstream build.
    binary=ROOT/BINARIES[method]
    # Absent optional builds do not prevent local methods from running.
    if not binary.is_file():
        # Return honest unavailability, with no false native solution or bound.
        return result_record(method,graph,cfg,seed,budget,started,status="unavailable",reason=f"native executable missing: {binary}")
    # Persistent run-local artifacts are required for scientific backend evidence.
    if cfg["work_dir"] is None:
        # Create only a project-owned optional run-artifact parent.
        parent=ROOT/"runs/native"
        # Independent native API calls receive unique directories rather than a shared stale log.
        parent.mkdir(parents=True,exist_ok=True)
        # mkdtemp atomically reserves a fresh owned artifact directory.
        directory=Path(tempfile.mkdtemp(prefix=method+"-",dir=parent))
    # The one-shot runner explicitly selects its unique output subtree.
    else:
        # Resolve the caller's selected location before writing any converted problem.
        directory=Path(cfg["work_dir"]).resolve()
        # Existing evidence is never reused for a supposedly fresh solve.
        if directory.exists():
            # Preserve the old run rather than deleting or appending to its native files.
            raise ValueError("native work_dir exists; choose a fresh path")
        # Guard official/source destinations even for a manually supplied work directory.
        protect_destination(directory/"backend.log")
        # Reserve only the explicitly selected fresh directory and missing parents.
        directory.mkdir(parents=True,exist_ok=False)
    # Default feasible fallback is all-plus cut zero, explicitly distinguished from native output.
    signs=np.ones(graph.node_count,dtype=np.int8) if initial_assignment is None else validate_signs(initial_assignment,graph.node_count)
    # The three SDP integer solvers require an exact finite-decimal scale.
    weights,scale=integer_weights(graph,max_integer=2**45) if method in {"biqbin","madam","biqcrunch"} else ([weight for i,j,weight in graph.edges],1)
    # Prevent overflow where upstream reads integer edges/graph-size-dependent dense operators.
    if method in {"biqbin","madam","biqcrunch"} and any(abs(weight)>2**30 for weight in weights):
        # No undocumented clipping or decimal rounding is performed.
        raise ValueError("scaled native edge exceeds conservative 32-bit range")
    # GSet-style conversion keeps every isolated vertex through the explicit n header.
    text=f"{graph.node_count} {len(graph.edges)}\n"+"".join(f"{i+1} {j+1} {weight}\n" for (i,j,original),weight in zip(graph.edges,weights))
    # SMS explicitly rejects zero-weight records, whose objective contribution is identically zero.
    if method=="scientific":
        # Keep the full original node count, including isolates, and remove only mathematically null edges.
        nonzero=[(i,j,weight) for i,j,weight in graph.edges if weight!=0]
        # Ascending compaction after removing native dummy node zero preserves original node order.
        text=f"{graph.node_count} {len(nonzero)}\n"+"".join(f"{i+1} {j+1} {weight}\n" for i,j,weight in nonzero)
    # Short relative filenames avoid the upstream fixed 200-byte output-path buffers.
    (directory/"graph.txt").write_text(text)
    # SDP backends use their actual documented native input format.
    if method=="biqcrunch":
        # The BC objective is the integer graph Laplacian, matching upstream mc2bc.py exactly.
        diagonal=[0]*graph.node_count
        # Each signed edge contributes w to both Laplacian diagonal entries.
        for (i,j,original),weight in zip(graph.edges,weights):
            # Row sums preserve negative weights as well as positive weights.
            diagonal[i]+=weight
            # Symmetric node j receives the same weighted degree contribution.
            diagonal[j]+=weight
        # The auxiliary homogenizing dimension is n+1, as in the original converter.
        records=["1 = max problem","0 = number of constraints","1 = number of blocks",str(graph.node_count+1)]
        # Store only nonzero diagonal entries; no dense Laplacian array is allocated.
        records.extend(f"0 1 {i+1} {i+1} {value}" for i,value in enumerate(diagonal) if value)
        # Symmetric BC upper-triangle storage supplies each off-diagonal Laplacian coefficient once.
        records.extend(f"0 1 {min(i,j)+1} {max(i,j)+1} {-weight}" for (i,j,original),weight in zip(graph.edges,weights) if weight)
        # The native BC file is an explicit independently inspectable conversion artifact.
        (directory/"graph.bc").write_text("\n".join(records)+"\n")
        # Native seed/time are actual parameter names from the reviewed release manual.
        (directory/"params").write_text(f"seed = {seed}\ntime_limit = {max(1,math.ceil(deadline-perf_counter()))}\n")
        # Use the Max-Cut-specific executable, independently identified from the generic MILP.
        command=[str(binary),"graph.bc","params"]
    # BiqBin/MADAM use a graph text input and their own default parameter files.
    elif method in {"biqbin","madam"}:
        # The pinned upstream defaults are copied, never modified in place.
        parameters=(ROOT/"external"/SOURCES[method]/"params").read_text()
        # Native parameter readers use the last actual time_limit assignment.
        parameters+=f"\ntime_limit = {max(1,math.ceil(deadline-perf_counter()))}\n"
        # Keep the exact native settings alongside the returned raw log.
        (directory/"params").write_text(parameters)
        # Two MPI ranks are required (coordinator + worker), with original backend execution preserved.
        command=["mpirun","-n","2",str(binary),"graph.txt","params"]
        # This pinned BiqBin CLI has exactly five user arguments; the README's older extra-bound argument is not used.
        if method=="biqbin":
            # ID/start/temp control only raw checkpoint naming and output intervals.
            command.extend(["run","1","2"])
    # MQLib's actual build discovers available heuristic identifiers before executing a selected one.
    elif method=="mqlib":
        # This read-only native listing is distinct from the timed heuristic solve.
        listing=subprocess.check_output([str(binary),"-l"],text=True)
        # Heuristic identifiers are the build's uppercase nonindented lines, not invented names.
        available=mqlib_codes(listing)
        # Preserve discovery output for review and future command reproduction.
        (directory/"heuristics.txt").write_text(listing)
        # Reject unavailable identifiers rather than silently running another heuristic.
        if cfg["heuristic"] not in available:
            # The result cannot claim BLS is part of MQLib when this actual build does not expose it.
            raise ValueError("heuristic is not in the actual MQLib -l listing")
        # -ps prints the native original-node +/-1 vector; no postprocessor guesses it from the cut value.
        cfg["native_runtime_seconds"]=max(0.001,0.8*(deadline-perf_counter()))
        # Reserve twenty percent for native final output, parsing and the enclosing worker's serialization.
        command=[str(binary),"-h",cfg["heuristic"],"-fM","graph.txt","-r",str(cfg["native_runtime_seconds"]),"-s",str(seed),"-ps"]
    # ScientificMaxcutSolver retains its own model, native JSON solution and warm-start interface.
    else:
        # An empty explicit SCIP settings file avoids a missing upstream default relative-path file.
        (directory/"params.set").write_text("# Native SCIP defaults for this source-pinned SMS run.\n")
        # Native flags come from the actual CLParser and preserve mc input node compacting in ascending original order.
        command=[str(binary),"graph.txt","mc","--seed",str(seed),"--timelimit",str(max(0.001,deadline-perf_counter())),
                 "--nodelimit",str(budget.get("max_work",10000)),"--paramfile","params.set","--solution","solution.json"]
        # SMS accepts a real complete zero-based partition warm start.
        if initial_assignment is not None:
            # Both sides include every original node exactly once.
            warm={"partition_0":np.flatnonzero(signs==1).tolist(),"partition_1":np.flatnonzero(signs==-1).tolist()}
            # Store actual original-order warm labels in the native documented format.
            (directory/"warm.json").write_text(json.dumps(warm))
            # Passing this flag invokes native addWarmStartSolution rather than merely preserving an output file.
            command.extend(["--warm-start-solution","warm.json"])
    # A deadline exhausted during conversion returns only the validated fallback witness.
    if perf_counter()>=deadline:
        # Do not claim the native solver ran or computed a bound.
        return result_record(method,graph,cfg,seed,budget,started,signs,status="time_limit",reason="conversion_time_limit")
    # Execute with an enforceable child-group timeout and persistent raw output.
    output,code,timed_out,log=native_call(command,directory,max(0.0,deadline-perf_counter()))
    # Native primal/dual values are parsed separately from the actual feasible vector.
    primal,upper,optimal=None,None,False
    # All returned labels are independently checked, even after native timeout/failure.
    recovered=False
    # MQLib prints an explicit +/-1 assignment after its Solution marker.
    if method=="mqlib" and "Solution:" in output:
        # Parse labels in original native order, not a sorted membership set.
        candidate=np.array([int(v) for v in output.rsplit("Solution:",1)[1].split()],dtype=np.int8)
        # Validate length/membership before publishing the recovered assignment.
        signs=validate_signs(candidate,graph.node_count)
        # The CSV objective field is a separate consistency check.
        primal=float(output.splitlines()[0].split(',')[3])
        # Native output, rather than fallback, supplied the actual witness.
        recovered=True
    # BiqBin final and periodic outputs use a real JSON object.
    elif method=="biqbin":
        # Prefer complete on-disk checkpoints if the native stdout stream ended mid-write.
        texts=[output]+[p.read_text(errors="replace") for p in sorted(directory.glob("*.output*"))]
        # Review every complete native payload; keep the last/best valid witness later.
        for text in texts:
            # MPI messages can precede the JSON object, so scan actual object starts.
            for match in re.finditer(r"\{",text):
                # A partial JSON write is not a completed result record.
                try:
                    # The native object may be followed by other text, which raw_decode handles explicitly.
                    data,end=json.JSONDecoder().raw_decode(text[match.start():])
                # Try another complete checkpoint instead of treating truncation as valid output.
                except ValueError:
                    # No native witness is credited from this incomplete object.
                    continue
                # Only the actual BiqBin metadata object carries a feasible assignment.
                if "ExecutionMD" in data:
                    # Native side lists are 1-based, and the last reference node is fixed outside the listed side.
                    payload=data["ExecutionMD"]
                    # Recover all original labels with a default opposite side.
                    candidate=-np.ones(graph.node_count,dtype=np.int8)
                    # Every reported membership ID must refer to an original vertex.
                    for vertex in payload["OneSideOfTheCut"]:
                        # Invalid native mapping is a conversion failure, not an omitted node.
                        if type(vertex) is not int or not 1<=vertex<=graph.node_count:
                            # Reject rather than wrapping an out-of-range index.
                            raise ValueError("invalid BiqBin vertex ID")
                        # Native side one maps to +1; complement equivalence leaves objective unchanged.
                        candidate[vertex-1]=1
                    # Independently evaluate each checkpoint so an older weaker checkpoint cannot replace a better witness.
                    if not recovered or cut_value(graph,candidate)>=cut_value(graph,signs):
                        # The native vector is now a validated feasible candidate in original order.
                        signs=candidate.copy()
                        # Convert native integer objective and conservatively rounded root bound back to original units.
                        primal=float(payload["Solution"])/scale
                        # A native optimal status is only credited after successful process completion below.
                        optimal=payload["SolutionType"]=="Optimal"
                        # Native root output has two decimal places; outward padding protects truncation/rounding.
                        upper=primal if optimal else math.floor(float(payload["RootBound"])+0.005+1e-7)/scale
                        # This actual checkpoint supplied the witness.
                        recovered=True
    # MADAM and BiqCrunch expose side membership and objective as documented text.
    elif method in {"madam","biqcrunch"}:
        # Native output files retain fuller state if the stdout log ended at a process timeout.
        text=output+"\n"+"\n".join(p.read_text(errors="replace") for p in sorted(directory.glob("*.output*")))
        # These solvers delimit side membership with parentheses or braces, respectively.
        matches=list(re.finditer(r"Solution\s*=\s*[({]([^)}]*)[)}]",text))
        # No membership output means the fallback remains explicit and unproven.
        if matches:
            # A final side-list is original one-based vertex membership; the auxiliary fixed node is excluded.
            vertices=[int(value) for value in matches[-1].group(1).split()]
            # Only an optional BiqCrunch homogenizing vertex n+1 can be beyond original n.
            if len(set(vertices))!=len(vertices) or any(not 1<=v<=graph.node_count+(method=="biqcrunch") for v in vertices):
                # Prevent silent node truncation or an invalid inverse permutation.
                raise ValueError("invalid native side-membership output")
            # Recover the complete original-node assignment, including isolates and unlisted nodes.
            signs=np.array([1 if node+1 in vertices else -1 for node in range(graph.node_count)],dtype=np.int8)
            # Best/Maximum output identifies the native primal value, not the root SDP value.
            values=re.findall(r"(?:Maximum|Best) value\s*=\s*([-+0-9.eE]+)",text)
            # A vector without its matching objective still cannot justify a native-result claim.
            if not values:
                # Record a parse failure rather than substituting the root bound as a cut.
                raise ValueError("native primal objective missing")
            # Exact integer scaling restores original decimal objective units.
            primal=float(values[-1])/scale
            # Native Maximum wording means completed branch-and-bound only if no native time-limit marker is present.
            optimal="Maximum value" in text and "TIME LIMIT" not in text
            # Printed root bounds differ in precision between the two native programs.
            roots=re.findall(r"Root node bound\s*=\s*([-+0-9.eE]+)",text)
            # An unknown bound stays null; an optimum's primal/dual equality is solver-reported evidence.
            upper=primal if optimal else (math.floor(float(roots[-1])+0.005+1e-7)/scale if roots else None)
            # A real original-order feasible vector was recovered from native output.
            recovered=True
    # SMS writes explicit JSON partitions rather than side text or signs.
    elif method=="scientific" and (directory/"solution.json").exists():
        # Read only this fresh native output, never a stale solution from another run.
        payload=json.loads((directory/"solution.json").read_text())
        # Validate partitions once and recover original-order labels in linear time.
        candidate=partition_signs(payload["partition_0"],payload["partition_1"],graph.node_count)
        # A stronger supplied warm assignment remains retained if native output is weaker.
        if cut_value(graph,candidate)>cut_value(graph,signs) or initial_assignment is None:
            # Copy validated labels rather than keeping references into parsed containers.
            signs=candidate.copy()
        # Extract full native SCIP primal and dual reports when present.
        primals=re.findall(r"Primal Bound\s*:\s*([-+0-9.eE]+)",output)
        # Dual is a reported bound under native SCIP tolerances, never a separately checked certificate.
        duals=re.findall(r"Dual Bound\s*:\s*([-+0-9.eE]+)",output)
        # Missing native bound text remains absent.
        primal=float(primals[-1]) if primals else None
        # Infinite sentinels are not valid finite Max-Cut bounds.
        upper=float(duals[-1]) if duals and abs(float(duals[-1]))<1e19 else None
        # Native solver status must explicitly say optimal; returning a vector alone proves only feasibility.
        optimal="optimal solution found" in output
        # The actual JSON file supplied a complete feasible assignment.
        recovered=True
    # Native reported objective must corroborate the independently evaluated output witness.
    if recovered and primal is not None and not math.isclose(cut_value(graph,signs),primal,rel_tol=1e-8,abs_tol=1e-7):
        # Conversion mistakes must never become published solver performance.
        raise ValueError(f"{method} native objective disagrees with recovered original cut")
    # A timeout, failed process or absent native witness cannot earn an optimal label.
    optimal=optimal and code==0 and not timed_out and recovered
    # Explicit execution status survives even when a useful witness can be returned.
    status="time_limit" if timed_out else "failed" if code or not recovered else "time_limit" if method=="mqlib" else "completed"
    # Independent result creation checks signs, direct F and bound consistency once more.
    result=result_record(method,graph,cfg,seed,budget,started,signs,status=status,
                         reason="process_time_limit" if timed_out else "native_exit_"+str(code),upper_bound=upper,
                         optimality="solver_reported_optimal" if optimal else "unproven",
                         evidence={"native_optimal":optimal,"scale":scale,"recovered_native_assignment":recovered,
                                   "fallback":"none" if recovered else "validated initial or all-plus", "tolerances":"upstream floating SDP/SCIP; no standalone checked certificate"},
                         implementation=SOURCES[method],logs=[log])
    # Preserve source pin and actual executable hash, as well as the exact conversion scale.
    result.update({"upstream":upstream_identity(method,binary),"integer_scale":scale,"native_primal_bound":primal,
                   "artifact_directory":str(directory)})
    # Every native method retains its own solver identity and raw evidence directory.
    return result
