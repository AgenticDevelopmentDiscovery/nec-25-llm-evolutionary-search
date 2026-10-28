"""One measured bounded session, never retries or changes mode on failure."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from controller import Manager, PROFILE, HERE
from server import verify_snapshot
from settings import REAL_PROVIDERS


def summary(run):
    events=run.events
    proposals=[e for e in events if e['type']=='proposal_received' and e.get('provider') in REAL_PROVIDERS]
    matches=[e for e in events if e['type']=='best_updated' and e['best']['reference_matched']]
    ranked=[e['candidate'] for e in events if e['type']=='candidate_ranked']
    return {'date_utc':datetime.now(timezone.utc).isoformat(), 'run_id':run.id,'mode':run.mode,'status':run.status,
            'scenario':run.scenario,'initial_solvers':run.initial_solvers,'population_protocol':'shared_raw' if run.population_protocol else 'legacy_frozen_parent',
            'seed':run.seed,'trial_seeds':run.seeds,'wall_seconds':run.elapsed(),'model_calls':run.calls,
            'time_to_first_real_proposal':proposals[0]['elapsed'] if proposals else None,
            'time_to_reference_match':matches[0]['elapsed'] if matches else None,
            'best_cut':run.best['cut'] if run.best else None,
            'baseline_construction':[{'seed':e['trial_seed'],'cut':e['cut']} for e in events if e['type']=='baseline_scored'],
            'candidates':[{k:c[k] for k in ('id','strategy','parent_ids','hypothesis','diff','complete','median','minimum','trials')} for c in ranked],
            'terminal_reason':events[-1].get('reason'), 'raw_records':f'demo/runs/{run.id}/',
            'replay_eligible':run.id in run.manager.recordings(),
            'caps':{k:PROFILE[k] for k in ('total_seconds','stop_and_save_by_seconds','max_model_calls','max_rounds','children_per_round')},
            'human_aloud_presentation_rehearsal':False}


def main():
    from settings import load_local_env
    load_local_env()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['numerical','live','replay'],default='numerical')
    parser.add_argument('--seed',type=int,default=3)
    parser.add_argument('--replay',help='verified source run ID, for replay only')
    parser.add_argument('--speed',type=int,choices=[1,2,4],default=1)
    parser.add_argument('--rounds',type=int,choices=[1,2,3],default=3,help='tighten round and model-call caps')
    parser.add_argument('--solvers',nargs='+',choices=['tabu','annealing','bls','bm'])
    parser.add_argument('--scenario',choices=['easy_limited','easy_informed','harder','custom'],default='custom')
    parser.add_argument('--instance',choices=['torus_pm_10_s11.txt','dense_gauss_100_s14.txt'],default='dense_gauss_100_s14.txt')
    parser.add_argument('--stop-on-model-stream',action='store_true',help='test Stop once real API response headers/public stream arrive')
    args=parser.parse_args()
    PROFILE['max_rounds'] = args.rounds
    PROFILE['max_model_calls'] = args.rounds
    verify_snapshot()
    manager=Manager(instance=args.instance)
    run=manager.create({'mode':args.mode,'seed':args.seed,'replay':args.replay,'speed':args.speed,**({'initial_solvers':args.solvers,'scenario':args.scenario} if args.solvers else {})})
    manager.start(run)
    try:
        deadline=time.monotonic()+PROFILE['total_seconds']+1
        while run.thread.is_alive() and time.monotonic()<deadline:
            if args.stop_on_model_stream and list(run.path.glob('model-*/public-stream.jsonl')):
                run.stop()
                break
            run.thread.join(.05)
        if run.thread.is_alive():run.stop()
    except KeyboardInterrupt:run.stop()
    result=summary(run)
    path=HERE/'evidence'/f'rehearsal-{run.id}.json'
    with path.open('x') as stream:json.dump(result,stream,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in result.items() if k not in ('candidates','baseline_construction','caps')},indent=2))
    if run.status!='finished':raise SystemExit(1)


if __name__=='__main__':main()
