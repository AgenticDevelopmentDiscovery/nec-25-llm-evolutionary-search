"""Real bounded Codex CLI bridge with structured decisions and lossless raw streams."""
# Lossless compression preserves raw agent bytes rather than an edited narrative.
import gzip
# SHA256 identifies exact prompt/event/stderr bytes.
import hashlib
# JSON is parsed against a small explicit supported schema subset.
import json
# Existing user authentication/profile is inherited through an environment copy.
import os
# Paths reserve one unique call record and read the actual final-message file.
from pathlib import Path
# CLI discovery never installs or substitutes an authentication system.
import shutil
# Read-only help/version inspection uses checked local subprocesses.
import subprocess
# Time stamps supplement actual elapsed process timings.
import time
# Protected owned-process cleanup includes interrupted Codex descendants.
from evolution_common import CampaignError,immutable_json,owned_process
# Atomic finite metadata preserves every observed invocation outcome.
from run_bm import atomic_json

# Strict JSON objects enumerate every field so the CLI can enforce structured output.
def object_schema(properties):
    """Return strict object schema; no mutation; e.g. object_schema({'id':{'type':'string'}})."""
    # All declared fields are required; optional meanings use explicit empty strings/arrays.
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}

# Strings and arrays stay ordinary explicit schema fragments, not a plugin framework.
STRING={'type':'string'}
# Bounded children have real parent lineage, complete source bytes and declared regression expectations.
CHILD=object_schema({'proposal_id':STRING,'parent_ids':{'type':'array','items':STRING,'minItems':1,'maxItems':2},
    'category':{'type':'string','enum':['parameter','algorithm_policy','state_policy','backend_switch','recombination']},
    'backend':STRING,'config_json':STRING,'policy_json':STRING,'stages_json':STRING,'source_path':STRING,'source_code':STRING,
    'changed_keys':{'type':'array','items':STRING},'hypothesis':STRING,'expected_effect':STRING,
    'required_checks':{'type':'array','items':{'type':'string','enum':['signed_examples','ownership','trap','perturbation_scope']},'minItems':1},
    'resource_estimate':STRING})
# Plan fields are instructions for the deterministic controller, never measurements or success proofs.
SCHEMA=object_schema({'round_id':{'type':'integer'},'graph_sha256':STRING,'evidence_summary':STRING,'rationale':STRING,
    'children':{'type':'array','items':CHILD,'maxItems':3},
    'evaluation_plan':object_schema({'order':{'type':'array','items':STRING},'seconds':{'type':'number'},'repeats':{'type':'integer'}}),
    'diversity_slot':{'type':'boolean'},'diversification_reason':STRING,
    'stop_reason':{'type':'string','enum':['continue','plateau']}})

# Local schema checking never trusts model self-reported validation.
def validate_schema(value,schema=SCHEMA):
    """Raise ValueError on malformed schema values; return None, no mutation.

    Supports this explicit object/array/scalar schema only; e.g. a missing
    graph_sha256 fails. Independent semantic/path/lineage checks follow later.
    """
    # Boolean is not an integer/number in the explicit controller protocol.
    kind=schema['type']
    # Object fields are all required and no extras are accepted.
    if kind=='object':
        # A quoted JSON blob must not masquerade as an outer decision object.
        if not isinstance(value,dict) or set(value)!=set(schema['properties']):
            # Exact key equality catches both missing and protected/unknown fields.
            raise ValueError('decision object fields do not match schema')
        # Validate each declared field recursively, without executing it.
        for key,child in schema['properties'].items():
            # The same narrow validator also covers nested evaluation plans/children.
            validate_schema(value[key],child)
    # Arrays have bounded cardinalities where the schema declares them.
    elif kind=='array':
        # No implicit scalar-to-list coercion is permitted.
        if not isinstance(value,list) or len(value)<schema.get('minItems',0) or len(value)>schema.get('maxItems',10000):
            # Limits are validated before a child can reserve compute work.
            raise ValueError('invalid decision array cardinality')
        # Every item has the declared type and allowed enum.
        for item in value:
            # Child code remains a string until separate static admission.
            validate_schema(item,schema['items'])
    # Primitive fields have exact Python JSON-compatible types.
    else:
        # Number accepts integer or float but excludes bool and nonfinite values.
        valid=isinstance(value,str) if kind=='string' else type(value) is bool if kind=='boolean' else type(value) is int if kind=='integer' else type(value) in (int,float) and abs(value)!=float('inf') and value==value
        # Enumerated stop/mutation/check types cannot be silently remapped.
        if not valid or 'enum' in schema and value not in schema['enum']:
            # Semantic failures get at most one bounded correction attempt.
            raise ValueError('invalid decision scalar/enum')

# Read-only doctor inspection checks real installed flags and actual Snap startup behavior.
def inspect_codex(executable='codex'):
    """Return real version/help/support or exact blocked reason; no model call.

    Example inspect_codex('codex'). Two probes have ten-second limits, inherit
    authentication without reading/printing secrets, and never install packages.
    """
    # PATH discovery preserves the user's installed CLI instead of inventing one.
    path=shutil.which(executable)
    # Missing executables are an honest live-integration blocker.
    if path is None:
        # Deterministic infrastructure remains usable with the explicitly named test provider.
        return {'available':False,'reason':'Codex executable not found','executable':executable}
    # Actual probes can fail under a filesystem policy even when a binary is present.
    try:
        # Bounded local version inspection makes no model request.
        version=subprocess.run([path,'--version'],capture_output=True,text=True,timeout=10)
        # Supported exec flags are checked locally before constructing production argv.
        help_result=subprocess.run([path,'exec','--help'],capture_output=True,text=True,timeout=10)
        # Require the exact noninteractive features used by this implementation.
        supported=all(flag in help_result.stdout for flag in ('--json','--output-schema','--output-last-message','--cd','--sandbox'))
        # A Snap/runtime/auth environment failure remains a concrete reason, not a fake success.
        return {'available':version.returncode==0 and help_result.returncode==0 and supported,'version':version.stdout.strip(),
                'executable':path,'supported_flags':supported,'reason':(version.stderr+help_result.stderr).strip(),
                'help':help_result.stdout}
    # A crashed/unlaunchable help probe is distinct from unavailable authentication.
    except (OSError,subprocess.TimeoutExpired) as error:
        # Preserve only diagnostic text, not credential material.
        return {'available':False,'executable':path,'reason':f'{type(error).__name__}: {error}'}

# Prompts explain the actual contract, source scope and measured round evidence.
def prompt_bytes(context,correction=None):
    """Return raw UTF-8 round prompt; dict input, no files or mutation.

    Example prior trial outcomes plus frozen parent sources. Graph summaries
    exclude large edge lists; small fixture edges may be included explicitly.
    """
    # JSON context contains immutable identities, not a claimed future improvement.
    rules='''You are the bounded reasoning/mutation operator for ONE Max-Cut campaign.
Return ONLY the requested schema JSON. Do not run Codex, controllers, numerical
campaigns, subprocesses, networking, git, or edit files. All implementation changes
must be emitted as complete source_code for the isolated variant.py (or explicit
config/policy JSON). The Python controller will execute, verify and store them privately; the user commits manually.
Preserve fixed original weights/objective, verification, proof status and budgets.
Every child inherits one or two listed actual parents. A new seed or filename is
not a novel artifact. known_candidates lists ALL existing candidates, including
discarded offspring and baseline backends. Compare resolved backend/config/policy/
stages and inherited source against that catalogue before proposing a child.
Do not recreate a known candidate or repeat a sibling. One or two useful novel
children are preferable to filling three slots with duplicates. An all-duplicate
plan is rejected; mixed plans keep only novel children and record skipped handles.
If no justified novel continuation exists, report plateau with no children.
For plateau, evaluation_plan has seconds=0, repeats=0, and order=[] (no work).
A parameter-only change is category parameter: change config only, inheriting
policy/source and using stages_json=[]. A state_policy change alters the policy
without changing source; leave source_path/source_code empty to inherit code.
Use algorithm_policy for a new choose_nodes/search function or changed executable
source/scheduling. A backend switch is backend_switch. Do not claim measurements
or optimality from a proposal.
config_json is an object of backend parameter changes merged with the first
parent (or new backend defaults on switch). policy_json is the FULL desired
perturbation policy object ({} inherits); stages_json is [] for one stage or
[{"backend":...,"config":...,"fraction":...},...] for up to two real stages.
Total fractions <=1, with the same aggregate budget as a parent. Explicit
backend guard increases require prior campaign opt-in and a resource estimate.
source_path must be exactly variant.py when emitting new source, otherwise empty.
Empty source_code inherits a parent's code unless switching backend. Allowed
hooks: choose_nodes(graph, signs, rng, policy) -> unique original int indices;
search(graph, config, seed, budget, initial_assignment) -> +/-1 assignment or
{"assignment": signs, "cut": independently correct optional cut, "work_counters":...}.
No proof/status/upper-bound fields may come from research code. Numerical imports:
math, numpy, or from bm_solver import compute_flip_gains,flip_node,cut_value,
local_search,angles_from_signs,solve_from_angles,round_angles; or from
portfolio_perturbations import select_subset,perturb_binary,perturb_selected_angles,
adaptive_strength. No file/process/reflection imports or operations. Top-level
code is docstrings, literal constants, approved imports and functions only.
Every executable source statement needs a meaningful preceding OR inline # comment
(including function/branch/loop headers). A '#' inside a string is not a comment;
comments inside a nested body do not document its containing header. Every
function needs a teaching docstring with inputs/return/ownership/failures/example.
A choose_nodes hook needs policy representation binary or angles and count. Policy
keys: representation none/binary/angles, count, rule uniform/connected/violated/mixed,
nodes optional fixed original IDs, strength radians, adaptive optional min/max/
multiplier/threshold names from the existing adaptive_strength helper. Angles are
BM-only and currently one pass (restarts=1,perturb_rounds=0). No unsupported warm
start; do not change replica axes. Ensure policies work on n=2,3,4 correctness
fixtures as well as this target. Do not hardcode returned assignment length.
changed_keys lists EXACT backend config keys changed from its declared baseline;
policy/code changes are represented by their own fields, not fake config keys.
required_checks includes signed_examples and ownership (plus trap/scope if useful).
Use proposal IDs child1/child2/child3. evaluation_plan.order must include all actual
parent IDs and all proposal IDs once. Its one shared seconds/repeats may not exceed
campaign limits. During >=3 nonimproving rounds propose explicit justified stronger
diversification, without increasing budgets, or honestly stop_reason plateau.
A requested diversity slot is declared BEFORE results and needs a rationale.
Target achievement is checked by Python; do not ask to continue after success.
'''
    # A malformed first response can be corrected once under the same recorded evidence/budgets.
    addition='' if correction is None else '\nThe previous proposal was rejected. Correct this concrete error: '+str(correction)+'\n'
    # Preserve input bytes exactly for raw transcript verification.
    return (rules+addition+'\nROUND CONTEXT:\n'+json.dumps(context,indent=2,allow_nan=False)).encode()

# Production uses real CLI calls; the test provider is always separately labeled.
def request_plan(config,context,directory,timeout,fixture_index=0,correction=None,stop_path=None):
    """Run one real Codex or explicit fixture-test call; return parsed plan/metadata.

    Fresh directory, finite timeout, config and immutable context are inputs.
    Saves prompt/schema/argv, raw stdout/stderr/final file, gzip/hash receipts,
    session/usage when available. Errors return exact rejected/blocked evidence;
    no implicit mocks, shell interpolation or model substitution.
    """
    # Recursive controllers/model mutation calls are forbidden even from a child shell.
    if os.environ.get('MAXCUT_EVOLUTION_CODEX_CHILD') or os.environ.get('MAXCUT_EVOLUTION_WORKER'):
        # The installed CLI is an operator, never an orchestrator that spawns itself.
        raise CampaignError('awaiting_codex','recursive Codex/controller invocation refused')
    # Unique call folders preserve invalid and correction attempts separately.
    directory.mkdir(parents=True,exist_ok=False)
    # Raw prompt bytes are created once, never normalized after capture.
    prompt=prompt_bytes(context,correction)
    # Plain raw input and its gzip version permit byte-for-byte verification.
    (directory/'prompt.stdin').write_bytes(prompt)
    # This exact schema is also enforced independently after parsing.
    immutable_json(directory/'schema.json',SCHEMA)
    # Provider identity is part of every receipt and is never inferred from schema compliance.
    provider=config['provider']
    # A test provider does not make a real model request and cannot be mistaken for one.
    if provider=='fixture-test':
        # Test plans are explicitly predeclared JSON in fixture configuration.
        decisions=config['fixture_decisions']
        # Exhausted fixtures are an honest blocked state, not random substitute mutations.
        if fixture_index>=len(decisions):
            # Capture a real unavailable-provider outcome in the same evidence structure.
            raw=b''
            # Distinct stderr makes this impossible to present as a live Codex transcript.
            error=b'fixture-test provider has no further declared decisions\n'
            # No successful CLI execution is fabricated.
            outcome={'exit_code':2,'elapsed_seconds':0.0,'timed_out':False,'stopped':False}
        # Fixture records use the SAME semantic plan validation as real responses.
        else:
            # Context-specific placeholders are resolved only for the explicitly labeled fixture protocol.
            decision=json.dumps(decisions[fixture_index]).replace('@GRAPH@',context['graph_sha256']).replace('"@ROUND@"',str(context['round_id']))
            # Parent placeholders are deterministic fixture helpers, not LLM claims.
            for index,parent in enumerate(context['parents']):
                # IDs are real immutable campaign artifact identities.
                decision=decision.replace('@PARENT'+str(index)+'@',parent['id'])
            # Raw fixture bytes remain clearly labeled rather than forged JSONL model events.
            raw=(decision+'\n').encode()
            # No live stderr/usage/session is invented.
            error=b'fixture-test provider; NOT a live Codex call\n'
            # Simulated execution is explicit in provider and argv fields below.
            outcome={'exit_code':0,'elapsed_seconds':0.0,'timed_out':False,'stopped':False}
            # Final file is an exact copy of the fixture response, not a manually repaired parse result.
            (directory/'final.json').write_bytes(raw)
        # There is no executable/model identity for a fixture provider.
        argv=['fixture-test',str(fixture_index)]
        # Preserve both raw streams unchanged.
        (directory/'stdout.raw').write_bytes(raw)
        # This diagnostic is never relabeled as actual Codex stderr.
        (directory/'stderr.raw').write_bytes(error)
    # Production never silently switches away from the requested installed CLI/profile.
    else:
        # Local CLI inspection is read-only and bounded, before constructing argv.
        info=inspect_codex(config['codex_executable'])
        # Missing/unsupported CLI still produces a raw error record and an honest await state.
        if not info['available']:
            # Empty stdout is actual absence of a call, not an edited successful transcript.
            (directory/'stdout.raw').write_bytes(b'')
            # Store the observed reason without reading authentication tokens.
            (directory/'stderr.raw').write_text(info['reason'])
            # No fake successful call is emitted when the executable cannot launch.
            outcome={'exit_code':127,'elapsed_seconds':0.0,'timed_out':False,'stopped':False}
            # An attempted probe is explicit; no alternate binary is chosen.
            argv=[config['codex_executable'],'exec']
        # Actual CLI JSONL and final-message support were verified locally.
        else:
            # The numerical mutation response is complete JSON; tools need no write access.
            argv=[info['executable'],'exec','--json','--sandbox','read-only','--cd',str(directory),
                  '--output-schema',str(directory/'schema.json'),'--output-last-message',str(directory/'final.json')]
            # Profiles/models/reasoning settings are inherited unless explicitly overridden.
            if config['codex_profile'] is not None:
                # Never invent a paid API account or substitute a different profile.
                argv+=['--profile',config['codex_profile']]
            # A requested model is passed unchanged.
            if config['codex_model'] is not None:
                # No default hardcoded model name appears in the framework.
                argv+=['--model',config['codex_model']]
            # Reasoning override is an actual local -c option, not an inferred model family.
            if config['codex_reasoning'] is not None:
                # JSON quoting is valid TOML string quoting for this scalar CLI setting.
                argv+=['-c','model_reasoning_effort='+json.dumps(config['codex_reasoning'])]
            # A dash requests exact stdin prompt consumption.
            argv+=['-']
            # Child environment inherits existing authentication without exposing its contents.
            environment=os.environ.copy()
            # The guard prevents generated commands from recursively invoking our controller/bridge.
            environment['MAXCUT_EVOLUTION_CODEX_CHILD']='1'
            # Bounded owned execution captures real raw events, not private internal reasoning.
            outcome=owned_process(argv,directory,timeout,directory/'stdout.raw',directory/'stderr.raw',stdin=prompt,
                                  environment=environment,registration=directory/'active_process.json',stop_path=stop_path)
    # Actual argv is durable even on missing CLI/timeout/invalid output.
    immutable_json(directory/'argv.json',argv)
    # Every raw stream is losslessly gzipped, with original bytes hashed independently.
    streams={}
    # Prompt, JSONL events and stderr are separate media/provenance objects.
    for name in ('prompt.stdin','stdout.raw','stderr.raw'):
        # Read only bytes captured for this particular call.
        data=(directory/name).read_bytes()
        # Deterministic gzip metadata avoids timestamp-only byte differences.
        (directory/(name+'.gz')).write_bytes(gzip.compress(data,mtime=0))
        # A decompression check verifies the artifact really contains the unedited original stream.
        if gzip.decompress((directory/(name+'.gz')).read_bytes())!=data:
            # Corrupt transcript capture is an integrity error, never a summary-only replacement.
            raise CampaignError('integrity_error','raw stream gzip mismatch')
        # SHA is over the original payload, not the compressed wrapper.
        streams[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'gzip':name+'.gz'}
    # Session/model/token fields are extracted when actually present, not invented from account plans.
    events=[]
    # Malformed/truncated event lines remain in raw bytes even when not parseable.
    for line in (directory/'stdout.raw').read_bytes().splitlines():
        # Fixture JSON is explicitly separate from actual Codex JSONL event streams.
        try:
            # Parsing reads public event data only; no access to hidden internal reasoning is claimed.
            events.append(json.loads(line))
        # Partial JSONL at a timeout does not become a successful model response.
        except ValueError:
            # Raw line remains exactly preserved in the compressed stream.
            pass
    # Complete portable metadata survives whether the final JSON parses or not.
    receipt={'provider':provider,'live_codex_call':provider=='codex' and len(argv)>2,'process':outcome,'streams':streams,
             'session_ids':[event.get('thread_id') for event in events if isinstance(event,dict) and event.get('thread_id')],
             'usage':[event['usage'] for event in events if isinstance(event,dict) and 'usage' in event],
             'requested_model':config['codex_model'],'requested_reasoning':config['codex_reasoning'],'monetary_cost':None,
             'capture_scope':'CLI input, emitted public JSONL events, stderr and final response only; not private internal reasoning'}
    # Expose a bounded actionable error without copying enormous server configuration dumps into status.
    diagnostic=[]
    # Read only the raw public stderr emitted by the actual CLI process.
    for line in (directory/'stderr.raw').read_text(errors='replace').splitlines():
        # Model catalog/API/auth errors matter; ordinary progress warnings stay only in raw evidence.
        if any(word in line.lower() for word in ('error','unauthorized','unsupported','not found')):
            # Server response bodies remain unedited in raw gzip, outside concise status fields.
            diagnostic.append(line.split('; body:',1)[0][:600])
    # No diagnostic is invented when the process produced no stderr.
    receipt['runtime_diagnostic']=diagnostic[:3]
    # Final response is never reconstructed from a cleaned stdout narrative.
    try:
        # A timeout/interruption cannot be treated as a completed proposal even if a file appeared.
        if outcome['exit_code']!=0 or outcome['timed_out'] or outcome['stopped']:
            # Preserve honest operational failure and avoid fake mutation plans.
            raise ValueError('Codex/fixture execution did not complete successfully')
        # The real final-message file is authoritative for structured output.
        plan=json.loads((directory/'final.json').read_text())
        # Independent strict-schema validation precedes semantic admission.
        validate_schema(plan)
        # A syntactically valid decision is not yet an admitted algorithm or measured improvement.
        receipt['parsed']=True
    # All malformed/unsupported outputs remain rejected artifacts for the one correction attempt.
    except (OSError,ValueError,TypeError) as error:
        # A missing CLI, timeout and invalid JSON have explicit diagnostic receipts.
        plan=None
        # Error text is separate from unedited raw streams.
        receipt.update(parsed=False,rejection=f'{type(error).__name__}: {error}')
    # The controller records calls and applies semantic/correction/stop budgets.
    atomic_json(directory/'receipt.json',receipt)
    # Parsed plan and authentic provenance remain separate return values.
    return plan,receipt
