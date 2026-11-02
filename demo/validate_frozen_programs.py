"""Post-search numerical validation of frozen programs. No provider requests."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import packing
from packing_controller import PackingManager
from packing_sandbox import availability

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'evidence/packing_heldout_validation.json')
    args=parser.parse_args()
    ready=availability()
    if not ready['available']:raise ValueError(ready['reason'])
    manifest=json.loads((HERE/'evidence/packing_validation_sources.json').read_text())
    seeds=manifest['validation_seeds']
    manager=PackingManager(HERE/'runs'/'validation')
    cases=[]
    try:
        for case in manifest['cases']:
            run=manager.create(dict(mode='numerical',n=case['n'],seed=seeds[0],starts='fixed'))
            assert run.seeds==seeds
            run.started=time.monotonic();run.status='running';run.phase='post-search validation'
            summaries=[]
            for program in case['programs']:
                path=HERE/program['file']
                if hashlib.sha256(path.read_bytes()).hexdigest()!=program['sha256']:
                    raise ValueError('frozen source changed: '+str(path))
                source=path.read_text()
                if packing.source_identity(source)[0]!=program['id']:raise ValueError('source identity changed')
                result=run.evaluate(source,[],0,program['name'])
                summaries.append({**program,**{k:result[k] for k in ('complete','median','minimum','trials','bank_id')}})
            run.finish('finished' if all(p['complete'] for p in summaries) else 'failed',
                       'frozen-program numerical validation; zero model calls')
            cases.append(dict(n=case['n'],source_run=case['source_run'],validation_run=run.id,
                              elapsed_seconds=run.elapsed(),programs=summaries))
        toys=[]
        for name,circles in [('valid_pair',[[.25,.5,.25],[.75,.5,.25]]),
                             ('overlapping_pair',[[.3,.5,.3],[.7,.5,.3]])]:
            try:
                packing.verify(circles,n=2);valid=True;reason='feasible'
            except ValueError as error:valid=False;reason=str(error)
            toys.append(dict(name=name,circles=circles,flawed_score=sum(c[2] for c in circles),
                             checked_valid=valid,checked_result=reason))
        complete=all(p['complete'] for c in cases for p in c['programs'])
        report=dict(mode='numerical_only',model_calls=0,all_complete=complete,task_version=packing.VERSION,
            validation_seeds=seeds,requested_steps=packing.STEPS,trial_seconds=packing.TRIAL_SECONDS,
            source_selection=manifest['selection_rule'],starts=manifest['starts'],cases=cases,
            scorer_counterexample=toys,
            limitations=['These seeds were not used in the original mutation/evaluation rounds.',
                         'Post-search fixed-start checks are separate from inherited-bank evolution.',
                         'Three starts per case do not establish broad generalization.',
                         'A fixed valid construction is legitimate for a fixed packing task; hard-coding alone is not proof of evaluator exploitation.'])
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'mode':'numerical_only','model_calls':0,'seeds':seeds,
            'cases':[dict(n=c['n'],programs=[dict(role=p['role'],median=p['median'],complete=p['complete'])
                                            for p in c['programs']]) for c in cases]},indent=2))
        return 0 if complete else 1
    finally:manager.close()


if __name__=='__main__':raise SystemExit(main())
