"""Immutable candidate artifacts, narrow research-code admission and real capability checks."""
# Static inspection rejects executable top-level payloads and protected I/O imports.
import ast
# Raw source SHA identifies exact saved module bytes independently of its semantic identity.
import hashlib
# Tokenization distinguishes real inline comments from hash characters inside strings.
import io
# Content metadata stays ordinary finite JSON.
import json
# Shape/topology guards use integer arithmetic, not filename guesses.
import math
# Explicit paths and copies isolate inherited artifacts from their parents.
from pathlib import Path
# Baseline snapshot copies do not modify the validated portfolio.
import shutil
# Python's lexer identifies comments without evaluating candidate source.
import tokenize
# NumPy stores copied node/angle state in the trusted worker.
import numpy as np
# Current portfolio metadata is authoritative for availability and actual warm support.
from solver_portfolio import list_solvers
# Exact integer conversion and topology validation reuse settled code.
from portfolio_common import integer_weights
# The actual embedding verifier rejects missing wraps/odd node mappings.
from portfolio_topology import torus_faces
# Shared identities and atomic immutable publication require no inheritance framework.
from evolution_common import CampaignError, identity, immutable_json
# Existing file hashes identify the actual source bytes.
from run_bm import atomic_json, file_sha256

# Research hooks can use numerical primitives but never controller/scorer/process/filesystem imports.
IMPORTS={'numpy':None,'math':None,'bm_solver':{'compute_flip_gains','flip_node','cut_value','local_search','angles_from_signs','solve_from_angles','round_angles'},
         'portfolio_perturbations':{'select_subset','perturb_binary','perturb_selected_angles','adaptive_strength'}}
# These escape/I/O operations have no algorithmic purpose within an admitted numerical hook.
FORBIDDEN={'open','exec','eval','compile','__import__','getattr','setattr','globals','locals','vars','breakpoint',
           'load','save','savez','savetxt','loadtxt','fromfile','tofile','memmap','ctypeslib','ctypes','system','popen'}

# Snapshots pin actual working source bytes rather than requiring a historical commit reset.
def snapshot(root,campaign):
    """Copy core/config prerequisites to campaign/base; return its manifest hash.

    Args root/campaign Paths; writes only a fresh base snapshot, never parents.
    Example snapshot(root,campaign). External original builds are read-only linked
    prerequisites, with selected source/binary identities checked separately.
    """
    # Existing campaign bases are immutable recovery inputs.
    base=campaign/'base'
    # Creation must be exclusive so a stale snapshot cannot masquerade as current code.
    base.mkdir(exist_ok=False)
    # Root Python modules retain ordinary relative imports within the pinned snapshot.
    for path in root.glob('*.py'):
        # Copy bytes, not a mutable link to project-owned source.
        shutil.copyfile(path,base/path.name)
    # Method defaults are part of the source/config identity.
    shutil.copytree(root/'configs/portfolio',base/'configs/portfolio')
    # Native/TESB/toroidal prerequisites remain separately pinned upstream builds.
    if (root/'external').exists():
        # Filesystem sandbox makes this linked prerequisite tree read-only during candidate execution.
        (base/'external').symlink_to(root/'external',target_is_directory=True)
    # All copied core/config bytes are covered, excluding separately linked upstream directories.
    manifest={str(path.relative_to(base)):file_sha256(path) for path in base.rglob('*') if path.is_file() and 'external' not in path.relative_to(base).parts}
    # Persist source identity before any artifact or candidate import can occur.
    immutable_json(campaign/'base_manifest.json',manifest)
    # Native implementation identities are part of the parent's recoverable provenance.
    return identity(manifest)

def initial_configurations(root,backend,config):
    """Yield unique explicit initial configurations, including declared native variants."""
    defaults=json.loads((root/'configs/portfolio'/f'{backend}.json').read_text())
    primary={**defaults,**config['candidate_configs'].get(backend,{})}
    seen=set()
    for changes in [None,*config.get('candidate_variants',{}).get(backend,[])]:
        value=primary if changes is None else {**primary,**changes}
        key=identity(value)
        if key not in seen:
            seen.add(key)
            yield value

# Actual resource and topology checks precede solver execution or code generation.
def eligibility(graph,backend,config,campaign_config):
    """Return (eligible,reason) for real capabilities/guards; read-only, no optimization.

    Example a 100000-node graph excludes dense SDP and expanded toroidal matching.
    Optional planar checking computes an embedding but no cut. Never lifts guards implicitly.
    """
    # Availability is discovered, not copied from an earlier status report.
    features=list_solvers().get(backend)
    # Unknown/unavailable entries cannot be substituted with a different solver.
    if not features or not features['available']:
        # Return the actual absence reason where available.
        return False,features['availability_reason'] if features else 'unknown backend'
    # Defaults come from the actual portfolio's declared explicit configurations.
    defaults=json.loads((Path(__file__).parent/'configs/portfolio'/f'{backend}.json').read_text())
    # A child must use implemented option names, never an ignored work directory or proof flag.
    if set(config)-set(defaults):
        # Reject before importing a candidate or launching a backend.
        return False,'unknown/forbidden backend configuration keys'
    # Preserve explicit default option types; bool is not an integer solver control.
    for key,value in config.items():
        # Null defaults accept backend-defined optional values, checked by the actual solver.
        default=defaults[key]
        # Numeric controls cannot contain strings, NaN, infinity or accidental booleans.
        if isinstance(default,(int,float)) and not isinstance(default,bool) and (type(value) not in (int,float) or not np.isfinite(value) or type(default) is int and type(value) is not int):
            # Reject malformed controls before native or local execution.
            return False,'invalid numeric backend option: '+key
        # Boolean and string options keep their actual declared interface types.
        if isinstance(default,(bool,str)) and type(value) is not type(default):
            # Do not coerce truthy strings into policy changes.
            return False,'invalid backend option type: '+key
    # Implicit resource-guard changes are forbidden by default.
    for key in ('max_nodes','max_expanded_nodes','max_defects'):
        # Raising a guard requires a campaign-level explicit opt-in as well as proposal evidence.
        if key in config and key in defaults and config[key]>defaults[key] and not campaign_config['lift_backend_guards']:
            # This prevents a model from densifying a large sparse graph under an innocuous parameter change.
            return False,'backend guard increase not authorized'
    # Each actual numerical path applies its graph-size guard before running.
    if backend=='exhaustive' and graph.node_count>min(26,config.get('max_nodes',defaults.get('max_nodes',24))):
        # Work/time budgets do not override the independent exponential size guard.
        return False,'exhaustive n guard'
    # Dense native SDP/model guards are honored explicitly.
    if backend in ('biqbin','madam','biqcrunch','milp','scientific','mqlib') and graph.node_count>config.get('max_nodes',defaults.get('max_nodes',100000)):
        # Large graphs remain excluded rather than allocated speculatively.
        return False,'native/model max_nodes guard'
    # Integer-only backends must preserve every finite-decimal weight.
    if backend in ('biqbin','madam','biqcrunch','exhaustive','planar_matching','toroidal_bound','toroidal_search'):
        # Unsupported precision/range is a documented incompatibility, not a rounded problem.
        try:
            # Native integer range is stricter than the Python oracle's arithmetic.
            weights,scale=integer_weights(graph,max_integer=2**45 if backend in ('biqbin','madam','biqcrunch') else 2**50)
            # Upstream C edge coefficients need a conservative signed-integer guard.
            if backend in ('biqbin','madam','biqcrunch') and any(abs(weight)>2**30 for weight in weights):
                # Keep exact input identity rather than clip edges.
                return False,'scaled native integer edge range'
        # Failure retains the exact observed unsupported conversion reason.
        except (ValueError,OverflowError) as error:
            # An excluded backend consumes no solver-call budget.
            return False,str(error)
    # Toroidal expanded matching cannot be inferred from the basename alone.
    if backend.startswith('toroidal'):
        # Guard before constructing any expanded dual matrix.
        if backend != 'toroidal_window' and 4*graph.node_count>config.get('max_expanded_nodes',defaults.get('max_expanded_nodes',4096)):
            # Side-100 and side-316 public tori are excluded by the default 4096 guard.
            return False,'expanded torus exceeds max_expanded_nodes'
        # The actual graph must retain both modulo wrap directions and row-major original IDs.
        try:
            # No optimization is performed by this topology validator.
            torus_faces(graph)
        # Missing wraps or unsupported L=2 parallel aliases are explicit exclusions.
        except ValueError as error:
            # No planarized substitute is scheduled.
            return False,str(error)
    # Signed planar optimization requires an actual planar graph.
    if backend=='planar_matching':
        # A simple planar necessary condition cheaply rejects most dense instances.
        if graph.node_count>=3 and len(graph.edges)>3*graph.node_count-6:
            # No dense graph adjacency is allocated for this rejection.
            return False,'nonplanar edge-count obstruction'
        # Import optional graph tooling only for the requested installed path.
        import networkx as nx
        # Sparse topology preserves isolates through explicit node insertion.
        topology=nx.Graph()
        # Isolated original IDs must remain part of the embedding.
        topology.add_nodes_from(range(graph.node_count))
        # No edge weight is changed by the topology test.
        topology.add_edges_from((i,j) for i,j,w in graph.edges)
        # This verifies planarity without computing any assignment or matching bound.
        if not nx.check_planarity(topology)[0]:
            # Nonplanar graphs cannot use the exact planar algorithm.
            return False,'verified nonplanar topology'
    # Successful eligibility is separate from performance on this graph.
    return True,'compatible with discovered capabilities/guards'

# A complete module is easier to recover/audit than a patch against an unknown checkout.
def validate_source(source):
    """Validate narrow variant.py source; return AST, no execution/mutation.

    Accept choose_nodes and/or search hooks, numerical imports and constants.
    Example choose_nodes returns [1] for a controlled perturbation. Invalid syntax,
    filesystem/process imports, dunder escapes or protected edits raise ValueError.
    """
    # Size limits prevent accidentally embedding unrelated repository dumps.
    if len(source.encode())>32000:
        # The brief calls for small readable algorithmic variants.
        raise ValueError('research source exceeds 32KB')
    # Parse before saving or importing executable candidate code.
    tree=ast.parse(source)
    # Model code is never allowed to execute arbitrary initialization at import time.
    for node in tree.body:
        # Only declarative imports, numerical constants, functions and a module docstring are permitted.
        if not isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.Assign,ast.Expr)):
            # Controllers/scorers/process management cannot be smuggled into a hook.
            raise ValueError('unsupported top-level research statement')
        # Top-level expressions must be explanatory text rather than a function call.
        if isinstance(node,ast.Expr) and not isinstance(node.value,ast.Constant):
            # Do not allow import-time solver work outside its trial budget.
            raise ValueError('top-level executable expression forbidden')
        # Constants are literal data, never imports, calls or comprehensions.
        if isinstance(node,ast.Assign):
            # literal_eval rejects hidden side effects without evaluating them.
            ast.literal_eval(node.value)
    # At least one implemented hook is necessary for an algorithm-code proposal.
    if not any(isinstance(node,ast.FunctionDef) and node.name in ('choose_nodes','search') for node in tree.body):
        # Merely changing a filename/docstring is not a new algorithm.
        raise ValueError('variant must define choose_nodes or search')
    # AST-level restrictions complement the independent read-only filesystem sandbox.
    for node in ast.walk(tree):
        # Decorators/default argument calls could execute before the bounded numerical call.
        if isinstance(node,ast.FunctionDef) and (node.decorator_list or any(not isinstance(value,(ast.Constant,ast.Tuple)) for value in node.args.defaults)):
            # Simple numeric hooks need no executable import-time decorators/defaults.
            raise ValueError('executable decorators/default arguments forbidden')
        # Direct imports must be reviewed numerical libraries only.
        if isinstance(node,ast.Import):
            # Root module matching does not permit numpy.ctypeslib submodule imports.
            if any(alias.name not in IMPORTS for alias in node.names):
                # Process, networking and filesystem modules are outside mutation scope.
                raise ValueError('unapproved numerical import')
        # From-import lists preserve a narrow settled-kernel interface.
        if isinstance(node,ast.ImportFrom):
            # Relative imports or wildcard imports make source resolution ambiguous.
            if node.level or node.module not in IMPORTS or any(alias.name=='*' or alias.name.startswith('_') or IMPORTS[node.module] is not None and alias.name not in IMPORTS[node.module] for alias in node.names):
                # Objective/validation/process wrappers cannot evolve through a candidate import.
                raise ValueError('unapproved numerical from-import')
        # Dunder reflection and known I/O names are not legitimate numerical perturbation tools.
        if isinstance(node,(ast.Name,ast.Attribute)):
            # Both direct calls and library attributes are inspected.
            name=node.id if isinstance(node,ast.Name) else node.attr
            # Private internal attributes are unnecessary for these explicit hooks.
            if name in FORBIDDEN or name.startswith('__'):
                # Reject before any candidate import can occur.
                raise ValueError('forbidden I/O/reflection operation: '+name)
    # Require adjacent explanatory comments and function documentation for authored mutation code too.
    lines=source.splitlines()
    # A string containing '#' is not an explanatory comment; only lexer COMMENT tokens qualify.
    comments={token.start[0]:token for token in tokenize.generate_tokens(io.StringIO(source).readline)
              if token.type==tokenize.COMMENT and token.string[1:].strip()}
    # These static checks make candidate research as readable as the trusted framework.
    for node in ast.walk(tree):
        # Every numerical hook needs purpose/arguments/return/failure explanation.
        if isinstance(node,ast.FunctionDef) and not ast.get_docstring(node):
            # Invalid artifacts are not admitted for numerical comparison.
            raise ValueError('candidate function needs a teaching docstring')
        # Docstrings are explanatory text, not a second executable statement needing a comment.
        if isinstance(node,ast.stmt) and not (isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str)):
            # Look only across whitespace, not unrelated statements.
            previous=node.lineno-2
            # Blank lines do not detach a preceding explanation.
            while previous>=0 and not lines[previous].strip():
                # Do not skip executable text.
                previous-=1
            # A preceding comment must be a real standalone comment, not text within a string.
            preceding=previous>=0 and previous+1 in comments and lines[previous].lstrip().startswith('#')
            # Compound statements need their own header explanation, not a comment in a nested body.
            body=getattr(node,'body',None)
            # Simple statements may span several lines; closing-line comments describe that statement too.
            last=max(node.lineno,body[0].lineno-1) if isinstance(body,list) and body else node.end_lineno
            # Accept either established preceding comments or real comments on the statement/header lines.
            inline=any(line in comments for line in range(node.lineno,last+1))
            # Detailed diagnostics let the single correction fix the actual missing explanation.
            if not preceding and not inline:
                # Source text is bounded and comes only from this already captured candidate.
                raise ValueError(f'candidate statement at line {node.lineno} lacks explanatory comment; '
                                 f'use a preceding or inline # comment: {lines[node.lineno-1].strip()[:120]}')
    # The caller persists exact source bytes, never a reserialized AST.
    return tree

# Candidate content identity excludes filenames, trial seeds, parents and prose-only code edits.
def artifact(base_identity,backend,config,policy,stages,source=''):
    """Return canonical candidate dict with semantic content hash; no files.

    Args explicit backend/config/policy/stages/source and baseline hash. Example
    parameter-only tenure change yields a distinct artifact; renaming a file does
    not. AST identity omits comments/docstrings while exact source SHA is retained.
    """
    # Source syntax is validated before its semantic identity is used.
    tree=validate_source(source) if source else None
    # Docstrings do not create fictitious algorithm novelty.
    if tree is not None:
        # Remove only explanatory string nodes from the identity tree, never from saved source bytes.
        for node in ast.walk(tree):
            # Function/module bodies can start with a docstring.
            if hasattr(node,'body') and isinstance(node.body,list):
                # Numerical expressions and literal assignments remain part of identity.
                node.body=[child for child in node.body if not (isinstance(child,ast.Expr) and isinstance(child.value,ast.Constant) and isinstance(child.value.value,str))]
    # Full resolved config prevents omitted-default spelling from creating a new candidate.
    defaults=json.loads((Path(__file__).parent/'configs/portfolio'/f'{backend}.json').read_text())
    # Native work directories and actual runtime measurements are never candidate controls.
    resolved={**defaults,**config}
    # Only declared representation policies can change initialization.
    if set(policy)-{'representation','rule','count','nodes','strength','adaptive'} or policy.get('representation','none') not in ('none','binary','angles'):
        # Reject ignored policy fields or undocumented dynamical-state perturbation.
        raise ValueError('invalid perturbation policy')
    # Angular policies apply only to the BM refinement-center representation.
    if policy.get('representation')=='angles' and backend!='bm':
        # Replica axes/momenta cannot silently become BM angles.
        raise ValueError('angular perturbation is supported only for BM')
    # A disabled policy has one canonical identity, with no ignored keys creating fictitious novelty.
    if policy.get('representation','none')=='none':
        # Extra disabled controls would have no executable effect.
        if set(policy)-{'representation'}:
            # Reject filename/config spelling changes disguised as new strategies.
            raise ValueError('disabled perturbation cannot contain ignored controls')
        # Canonical spelling matches all baseline artifacts.
        policy={'representation':'none'}
    # Unsupported native interfaces cannot silently ignore a supplied perturbed state.
    if policy.get('representation')!='none' and list_solvers()[backend]['warm_start']=='unsupported':
        # A genuinely fresh-start native competitor has no state-policy injection pathway.
        raise ValueError('backend does not support a perturbed warm start')
    # A staged child cannot silently ignore its own declared perturbation in an unsupported first stage.
    if stages and policy.get('representation')!='none' and list_solvers()[stages[0]['backend']]['warm_start']=='unsupported':
        # Such a child must explicitly remove the policy or choose a genuinely warm first stage.
        raise ValueError('first stage does not support the declared perturbed warm state')
    # BM angular initialization cannot be reinterpreted as signs for a different first backend.
    if stages and policy.get('representation')=='angles' and stages[0]['backend']!='bm':
        # Keep the actual numerical representation explicit throughout the initial stage.
        raise ValueError('angular initialization requires a BM first stage')
    # Custom searches remain local heuristic variants, not relabeled exact/native implementations.
    if tree is not None and any(isinstance(node,ast.FunctionDef) and node.name=='search' for node in tree.body):
        # Native/model identities must continue to execute their own inspected interfaces.
        if backend not in ('bm','tabu','bls','annealing','lns','bsb','dsb','gsb','sbqa') or stages:
            # Recombination must retain actual stage backend semantics.
            raise ValueError('custom search is local-heuristic-only and cannot override a native/multistage identity')
    # A node-selector-only module needs an enabled declared perturbation policy.
    if tree is not None and policy.get('representation')=='none' and not any(isinstance(node,ast.FunctionDef) and node.name=='search' for node in tree.body):
        # Dead source is not an algorithmic novelty claim.
        raise ValueError('choose_nodes hook needs an enabled perturbation')
    # Fixed/dynamic selection controls have explicit finite cardinality/strength semantics.
    if type(policy.get('count',0)) is not int or policy.get('count',0)<0 or not np.isfinite(policy.get('strength',0)) or policy.get('strength',0)<0:
        # Invalid policies fail admission rather than becoming a no-op.
        raise ValueError('invalid perturbation cardinality/strength')
    # Semantics are immutable; lineage/rationale are added by the controller as provenance only.
    content={'base_identity':base_identity,'backend':backend,'config':resolved,'policy':policy,'stages':stages,
             'semantic_source':ast.dump(tree,include_attributes=False) if tree else None}
    # Full identity, not a filename change or seed change, defines an evolved artifact.
    digest=identity(content)
    # Raw source hash independently identifies comments and exact reconstructable bytes.
    return {'id':'c-'+digest[:24],'content_hash':digest,'content':content,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'source':source}

# Artifact files are immutable and included in each round's evidence/commit.
def save_artifact(campaign,record,parents,round_id,category,hypothesis):
    """Save new artifact plus lineage once, return its ID; never mutate parents.

    Example parameter child with parents=[parent_id]. Existing semantic identities
    are duplicate proposals, not novel filenames. Full source/prerequisites persist.
    """
    # Candidate paths are derived from validated content hashes only.
    directory=campaign/'candidates'/record['id']
    # Duplicate identities are not admitted as new descendants.
    if directory.exists():
        # The controller records this rejected proposal and can request one correction.
        raise ValueError('duplicate candidate content identity')
    # Fresh directory prevents an inherited module from aliasing a mutable parent file.
    directory.mkdir(parents=True,exist_ok=False)
    # Exact module bytes are stored only inside the candidate-owned namespace.
    if record['source']:
        # Model output cannot select a filesystem path beyond this variant filename.
        (directory/'variant.py').write_text(record['source'])
    # Identity and provenance are separate so parent IDs do not fabricate novelty.
    immutable_json(directory/'artifact.json',{**record,'parents':parents,'creation_round':round_id,'category':category,'hypothesis':hypothesis})
    # The artifact can now be referenced by a durable round proposal.
    return record['id']

# Read every identity back before it is allowed to run or become a parent.
def load_artifact(campaign,candidate_id):
    """Return verified artifact dict; no mutation, malformed IDs/hashes raise integrity_error.

    Example load_artifact(campaign,'c-...'); checks semantic and exact source bytes.
    """
    # A content-derived basename cannot escape its own artifact directory.
    if not candidate_id.startswith('c-') or len(candidate_id)!=26 or any(char not in '0123456789abcdef' for char in candidate_id[2:]):
        # Parent IDs are validated against membership separately by the controller.
        raise CampaignError('integrity_error','invalid candidate ID')
    # Artifact metadata is immutable input, not a trusted backend result.
    directory=campaign/'candidates'/candidate_id
    # Read declared identity and exact source provenance.
    record=json.loads((directory/'artifact.json').read_text())
    # Semantic corruption and exact-source replacement are independently rejected.
    if identity(record['content'])!=record['content_hash'] or candidate_id!='c-'+record['content_hash'][:24] or hashlib.sha256(record['source'].encode()).hexdigest()!=record['source_sha256']:
        # Do not execute or select a corrupted research artifact.
        raise CampaignError('integrity_error','candidate metadata hash mismatch')
    # Source must be byte-identical to the captured module, not a mutable global checkout.
    if record['source'] and (directory/'variant.py').read_text()!=record['source']:
        # Preserve the altered file for diagnosis rather than silently restore it.
        raise CampaignError('integrity_error','candidate module bytes changed')
    # Recompute semantic identity from actual module bytes; updating only the raw-source hash cannot hide changed code.
    rebuilt=artifact(record['content']['base_identity'],record['content']['backend'],record['content']['config'],record['content']['policy'],record['content']['stages'],record['source'])
    # Source/config/policy must describe exactly the content-derived immutable artifact ID.
    if rebuilt['content_hash']!=record['content_hash']:
        # This rejects semantically changed source even if an attacker also edited its byte-hash field.
        raise CampaignError('integrity_error','candidate source semantic identity changed')
    # Recheck allowed source syntax/imports even on recovered artifacts.
    if record['source']:
        # Serialized metadata cannot bypass current protected mutation scope.
        validate_source(record['source'])
    # Callers receive ordinary immutable-by-convention metadata and owned worker copies.
    return record
