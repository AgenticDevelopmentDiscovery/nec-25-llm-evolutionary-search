"""One small explicit dispatcher; no evolutionary orchestration or plugin framework."""

# Availability checks avoid importing optional heavyweight packages on ordinary --list.
import importlib.util
# Path resolves actual optional build outputs and source checkouts.
from pathlib import Path
# perf_counter records the adapted BM runtime without altering its random stream.
from time import perf_counter
# NumPy supports a valid no-work incumbent when a deadline has already expired.
import numpy as np
# Existing correct BM algorithms are reused without touching the settled kernels.
from bm_solver import solve_bm, solve_bm_extended
# Shared contracts keep validation, budgets and feasibility independent of backend identity.
from portfolio_common import deadline_from, result_record, settings, starting_signs

# Ordinary metadata describes the real methods without constructing solver classes or factories.
FEATURES={
    "mixing":{"warm_start":"noisy_vector_initialization_and_retention","bound":False,"work_unit":"coordinate_sweeps","input":"sparse signed Graph, rank 2..64"},
    "pt_icm":{"warm_start":"cold_replica_initialization_and_retention","bound":False,"work_unit":"tempering_cycles","input":"sparse zero-field signed Graph"},
    "toroidal_window":{"warm_start":"fixed_boundary_window_state","bound":False,"work_unit":"conditional_windows","input":"verified row-major square torus; bounded planar windows"},
    "exhaustive":{"warm_start":"retained_incumbent","bound":True,"work_unit":"assignments","input":"n<=26, finite-decimal scaling"},
    "bm":{"warm_start":"initial_refinement_center","bound":False,"work_unit":"configured complete passes","input":"sparse signed Graph"},
    "tabu":{"warm_start":"initial_state","bound":False,"work_unit":"iterations","input":"sparse signed Graph"},
    "bls":{"warm_start":"initial_state","bound":False,"work_unit":"individual flips","input":"sparse signed Graph"},
    "annealing":{"warm_start":"initial_state","bound":False,"work_unit":"proposals; bounded polish separate","input":"sparse signed Graph"},
    "lns":{"warm_start":"initial_state_and_fixed_boundary","bound":False,"work_unit":"neighborhoods","input":"sparse signed Graph; optional MILP above 20 released nodes"},
    "milp":{"warm_start":"native_complete_incumbent","bound":True,"work_unit":"branch_nodes","input":"signed edge-XOR MILP; optional PySCIPOpt"},
    "bsb":{"warm_start":"replica_zero_initialization_and_retention","bound":False,"work_unit":"integration_steps","input":"sparse signed Graph, independent replicas"},
    "dsb":{"warm_start":"replica_zero_initialization_and_retention","bound":False,"work_unit":"integration_steps","input":"sparse signed Graph, independent replicas"},
    "gsb":{"warm_start":"replica_zero_initialization_and_retention","bound":False,"work_unit":"integration_steps","input":"sparse signed Graph, per-node pump control"},
    "sbqa":{"warm_start":"replica_zero_initialization_and_retention","bound":False,"work_unit":"integration_steps","input":"sparse signed Graph, interacting replica ring"},
    "tesb":{"warm_start":"warm_replica_zero_and_retention","bound":False,"work_unit":"total warm+checking integration_steps","input":"authors CPU CSR implementation"},
    "mqlib":{"warm_start":"unsupported","bound":False,"work_unit":None,"input":"upstream GSet text; selected discovered heuristic"},
    "scientific":{"warm_start":"native_partition_incumbent","bound":True,"work_unit":"branch_nodes","input":"upstream SMS mc input and JSON partitions"},
    "biqbin":{"warm_start":"unsupported","bound":True,"work_unit":None,"input":"integer-scaled n<=1024; fixed native seed 2020; two MPI ranks"},
    "madam":{"warm_start":"unsupported","bound":True,"work_unit":None,"input":"integer-scaled n<=1024; fixed native seed 2020; two MPI ranks"},
    "biqcrunch":{"warm_start":"unsupported","bound":True,"work_unit":None,"input":"integer-scaled BC Laplacian, n<=5000 guard"},
    "planar_matching":{"warm_start":"retention_only","bound":True,"work_unit":"connected_components","input":"verified planar signed graph, <=256 parity defects default"},
    "toroidal_bound":{"warm_start":"retention_only","bound":True,"work_unit":"one initial matching; no extra iterations","input":"verified row-major L*L torus, L>=3, expanded-size guard"},
    "toroidal_search":{"warm_start":"initial_cycle_repair_state","bound":True,"work_unit":"additional cycle_repairs","input":"same verified torus embedding"},
    "qubowl":{"warm_start":"unavailable","bound":True,"work_unit":None,"input":"source not obtained from reviewed official sources"}}


# Capability discovery is read-only and does not build/download/run a solver implicitly.
def list_solvers():
    """Return name->availability/features dict for the current isolated installation.

    No arguments; no mutation/files or native execution. Optional imports are
    discovered with find_spec; compiled binary paths must exist. Availability
    is not proof of validation or suitability for every size. Every method is
    documented in docs/portfolio; raw validation is in evidence/portfolio.
    O(number of solver names). Example list_solvers()['bm']['available']=True.
    """
    # Native paths and source identity remain centralized in their thin adapter.
    from portfolio_external import BINARIES,ROOT
    # Fresh copied entries avoid modifying the shared static feature definitions.
    result={}
    # Keep discovery ordering explicit and stable for user-facing lists.
    for name,features in FEATURES.items():
        # Project-owned basic methods are usable with the existing required NumPy dependency.
        available=True
        # A missing optional dependency is reported with a concrete installation hint.
        reason="project implementation available"
        # Native backend availability is based on the actual build output, not a downloaded repository alone.
        if name in BINARIES:
            # A binary must have actually been produced in the documented build directory.
            available=(ROOT/BINARIES[name]).is_file()
            # Compilation logs retain failures even if a later build succeeds.
            reason="built native executable" if available else "native build missing; see external source/build records"
        # Generic SCIP MILP is independent of SMS, even if both use SCIP.
        elif name=="milp":
            # Do not import native solver code merely to list other methods.
            available=importlib.util.find_spec("pyscipopt") is not None
            # Preserve optionality and an actionable absent-dependency explanation.
            reason="optional PySCIPOpt installed" if available else "install uv sync --extra milp"
        # All matching methods need the matching library, while toroidal methods also use upstream primitives.
        elif name in {"planar_matching","toroidal_bound","toroidal_search","toroidal_window"}:
            # Both topology and signed matching are real implemented paths, with resource guards applied at solve time.
            available=importlib.util.find_spec("networkx") is not None and (name in {"planar_matching","toroidal_window"} or (ROOT/"external/MaxCutPlanarAndToroidal/toroid_lp_lib.py").is_file())
            # Avoid describing a missing checkout as a failed optimization result.
            reason="matching dependency/source available" if available else "install matching extra and obtain pinned toroidal source"
        # TESB uses the reviewed authors' CPU class and its separate optional imports.
        elif name=="tesb":
            # No generic SB implementation is substituted when the authors' code is missing.
            available=(ROOT/"external/TESB/tSB.py").is_file() and all(importlib.util.find_spec(p) is not None for p in ("scipy","pandas"))
            # Installation instructions remain distinct from local bSB/dSB numerical code.
            reason="authors CPU source/dependencies available" if available else "obtain pinned TESB source and install tesb extra"
        # The brief permits a precisely documented availability blocker for QuBowl.
        elif name=="qubowl":
            # Author correspondence states code was not publicly distributed; no current official downloadable source was obtained.
            available=False
            # Record only what source investigation establishes, not a claim that the code can never become available.
            reason="no obtainable official source identified; see docs/portfolio/EXTERNAL_BUILDS.md and paper manifest"
        # The runner additionally imposes a hard process deadline on every method.
        result[name]={**features,"available":available,"availability_reason":reason,"hard_time_limit":"run_solver.py child process; API checks vary by method"}
    # Return plain data rather than registering factories or mutating a global solver registry.
    return result


# BM is adapted around the existing implementation; its original public functions stay unchanged.
def solve_bm_adapter(graph,config,seed,budget,initial_assignment=None):
    """Run unchanged BM through the portfolio contract and preserve legacy defaults.

    config accepts max_sweeps=200,rounding_count=32,restarts=1,
    perturb_rounds=0,perturb_scale=.35 and the five settled core tolerances.
    seed local base seed, budget seconds (API checked before/after one core
    call), max_work optional pass ceiling that must cover M*(1+P). A strict
    wall deadline is provided by run_solver.py, not by editing old BM kernels.
    initial labels warm restart zero and remain retained. Return shared result
    plus complete original BM history, with upper_bound=None. No mutation/files.
    Example default no-incumbent solve returns exactly solve_bm's signs/cut.
    Sparse memory and cost match the existing solver; passing more work does
    not create an automatic multi-setting campaign.
    """
    # Timing wraps the old solver without consuming extra initialization random draws.
    started=perf_counter()
    # All original parameter meanings and numerical defaults remain explicit.
    cfg=settings(config,{"max_sweeps":200,"rounding_count":32,"restarts":1,"perturb_rounds":0,"perturb_scale":0.35,
                         "field_rtol":1e-12,"sweep_atol":1e-12,"sweep_rtol":1e-9,"gain_tolerance":1e-10,"projection_tolerance":1e-12})
    # A malformed outer pass budget cannot be converted into an uncounted partial experiment.
    if type(cfg["restarts"]) is not int or cfg["restarts"]<1 or type(cfg["perturb_rounds"]) is not int or cfg["perturb_rounds"]<0:
        # The existing extended API retains these same total/additional meanings.
        raise ValueError("invalid BM total restarts/additional rounds")
    # Actual complete passes are determined by configured starts and rounds.
    passes=cfg["restarts"]*(1+cfg["perturb_rounds"])
    # An explicit pass ceiling is enforced instead of silently ignored.
    if "max_work" in budget and budget["max_work"]<passes:
        # Callers can deliberately lower M/P to fit a smaller complete-pass budget.
        raise ValueError("BM max_work must cover configured M*(1+P) complete passes")
    # Shared validation supplies the coarse API deadline without changing the mathematical kernel.
    deadline=deadline_from(budget)
    # A zero-time request returns a validated incumbent without running an unbounded core pass.
    if perf_counter()>=deadline:
        # Initial labels remain meaningful even when no new work can be performed.
        initial=starting_signs(graph,np.random.default_rng(seed),initial_assignment)
        # No upper bound or optimality is claimed for this no-work result.
        return result_record("bm",graph,cfg,seed,budget,started,initial,status="time_limit",reason="before_BM_pass",counters={"passes":0})
    # Separate old core parameters from the outer-loop controls.
    core={key:value for key,value in cfg.items() if key not in {"restarts","perturb_rounds","perturb_scale"}}
    # Preserve the exact no-incumbent one-start path and its legacy RNG coupling.
    if passes==1 and initial_assignment is None:
        # This invokes the original public solver with identical settings and seed.
        signs,original_value,history=solve_bm(graph,seed=seed,**core)
    # Extended/warm use calls the existing validated implementation, not a duplicated solver.
    else:
        # Warm signs really participate in restart-zero refinement and global retention.
        signs,original_value,history=solve_bm_extended(graph,seed=seed,initial_signs=initial_assignment,
                                      restarts=cfg["restarts"],perturb_rounds=cfg["perturb_rounds"],perturb_scale=cfg["perturb_scale"],**core)
    # Execution status can be time-limited even when the completed core returned valid labels.
    result=result_record("bm",graph,cfg,seed,budget,started,signs,
                         status="time_limit" if perf_counter()>=deadline else "completed",
                         reason="API_time_checked_after_complete_call" if perf_counter()>=deadline else "configured_BM_passes",
                         counters={"passes":passes},implementation="preserved-project-rank-two-BM")
    # Complete original histories preserve coordinate/rounding/polishing and extension attempt evidence.
    result["bm_history"]=history
    # Its encountered relaxed objective never becomes a Max-Cut upper bound.
    return result


# Equivalent inputs enter one explicit dispatcher without solver discovery side effects.
def solve(graph,config,seed,budget,initial_assignment=None,solver="bm"):
    """Dispatch solve(graph,config,seed,budget,initial_assignment) by explicit solver.

    graph is fixed original-order sparse Graph; config dict is method-specific;
    seed nonnegative int; budget dict seconds/max_work where supported; optional
    +/-1 initial vector must be honored or explicitly rejected. solver defaults
    bm and must be a named implemented or blocked component. Return ordinary
    shared JSON dict. No automatic candidate selection, campaigns, evolution,
    dependency installs or input mutation. Example solver='exhaustive' on a
    +2 edge returns a verified optimum. Cost is the selected method's cost.
    """
    # Seed protocol must be reproducible and must not accidentally accept Boolean/fractional seeds.
    if type(seed) is not int or seed<0:
        # Native-specific ranges are validated by their individual adapter.
        raise ValueError("seed must be a nonnegative integer")
    # Reject unknown backend names before any work or file writes.
    if solver not in FEATURES:
        # Never substitute a generic method under a requested published name.
        raise ValueError("unknown solver name")
    if solver == "mixing":
        from portfolio_mixing import solve_mixing
        return solve_mixing(graph,config,seed,budget,initial_assignment)
    if solver == "pt_icm":
        from portfolio_tempering import solve_pt_icm
        return solve_pt_icm(graph,config,seed,budget,initial_assignment)
    if solver == "toroidal_window":
        from portfolio_window import solve_window
        return solve_window(graph,config,seed,budget,initial_assignment)
    # Basic discrete methods share only mathematical primitives, not their distinct search policies.
    if solver in {"exhaustive","tabu","bls","annealing"}:
        # Optional native dependencies are not imported for these project-owned solvers.
        from portfolio_search import solve_exhaustive,solve_tabu,solve_bls,solve_annealing
        # A plain local mapping selects an ordinary function, not a factory/plugin layer.
        function={"exhaustive":solve_exhaustive,"tabu":solve_tabu,"bls":solve_bls,"annealing":solve_annealing}[solver]
        # Equivalent graph/config/seed/budget/incumbent data reaches the selected implementation.
        return function(graph,config,seed,budget,initial_assignment)
    # Existing BM enters its preservation wrapper.
    if solver=="bm":
        # No mathematical kernel, baseline default or old CLI is rewritten.
        return solve_bm_adapter(graph,config,seed,budget,initial_assignment)
    # The generic exact edge-XOR MILP remains independent of SMS.
    if solver=="milp":
        # Import only the optional MILP wrapper requested by this user call.
        from portfolio_milp import solve_milp
        # The wrapper itself reports unavailable when PySCIPOpt is absent.
        return solve_milp(graph,config,seed,budget,initial_assignment)
    # Exact-neighborhood repair is a local controller, not a global exact-solver identity.
    if solver=="lns":
        # Conditional enumeration remains usable without optional SCIP.
        from portfolio_neighborhood import solve_lns
        # Warm labels determine the actual fixed outside boundary of released subsets.
        return solve_lns(graph,config,seed,budget,initial_assignment)
    # Local bifurcation methods use distinct primary formulations and one sparse numerical interface.
    if solver in {"bsb","dsb","gsb","sbqa"}:
        # No PyTorch or GPU package is required for the local CPU path.
        from portfolio_bifurcation import solve_bifurcation
        # The method argument selects actual equation/control differences, not merely a different label.
        return solve_bifurcation(graph,config,seed,budget,initial_assignment,method=solver)
    # TESB specifically invokes the authors' independently pinned CPU source.
    if solver=="tesb":
        # It is not silently mapped onto bSB plus the local discrete tabu search.
        from portfolio_tesb import solve_tesb
        # The adapter preserves optionality and rejects missing author sources honestly.
        return solve_tesb(graph,config,seed,budget,initial_assignment)
    # Native programs have separately validated conversions and process lifetimes.
    if solver in {"mqlib","scientific","biqbin","madam","biqcrunch"}:
        # Native configuration/seed/warm-start limitations remain explicit.
        from portfolio_external import solve_native
        # Pass the actual selected native identity into its thin adapter.
        return solve_native(graph,config,seed,budget,initial_assignment,method=solver)
    # General planar optimization and toroidal bound/search retain separate proof meanings.
    if solver in {"planar_matching","toroidal_bound","toroidal_search"}:
        # Matching imports are optional until this path is requested.
        from portfolio_topology import solve_planar,solve_toroidal
        # A valid planar embedding is proved by the actual planar algorithm.
        if solver=="planar_matching":
            # No wrap edges are removed to make a nonplanar input appear planar.
            return solve_planar(graph,config,seed,budget,initial_assignment)
        # Toroidal algorithms verify the original row-major periodic embedding before any bound claim.
        return solve_toroidal(graph,config,seed,budget,initial_assignment,method=solver)
    # QuBowl investigation is complete but a downloadable implementation was not obtained.
    started=perf_counter()
    # Reject arbitrary ignored settings even for an unavailable component.
    settings(config,{})
    # Unsupported QuBowl warm starts must not be accepted or silently ignored.
    if initial_assignment is not None:
        # No obtained native API exists to inject the requested incumbent.
        raise ValueError("QuBowl source unavailable; no warm-start interface is implemented")
    # An unavailable backend still obeys the shared budget-validation contract.
    deadline_from(budget)
    # No assignment, native upper bound or completed implementation is fabricated.
    return result_record("qubowl",graph,config,seed,budget,started,status="unavailable",reason=list_solvers()["qubowl"]["availability_reason"])
