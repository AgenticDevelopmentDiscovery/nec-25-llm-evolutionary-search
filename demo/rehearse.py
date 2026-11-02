"""Bounded circle-packing rehearsal. Live mode explicitly spends up to --rounds calls."""
import argparse
import json
from pathlib import Path
import sys
import time
from packing_controller import PackingManager
from settings import load_local_env


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['numerical','live','replay'],default='numerical')
    parser.add_argument('--n',type=int,choices=[26,32],default=26)
    parser.add_argument('--seed',type=int,default=3)
    parser.add_argument('--rounds',type=int,choices=[1,2,3],default=3)
    parser.add_argument('--replay')
    parser.add_argument('--starts',choices=['fixed','inherited'],default='inherited')
    parser.add_argument('--summary',type=Path)
    args=parser.parse_args();load_local_env()
    manager=PackingManager()
    body=dict(mode=args.mode,n=args.n,seed=args.seed,rounds=args.rounds,starts=args.starts)
    if args.replay:body['replay']=args.replay
    run=manager.create(body);manager.start(run)
    try:
        cursor=0
        while run.status not in ('finished','failed','stopped'):
            for event in run.events[cursor:]:
                cursor=event['seq']
                if event['type'] in ('model_started','candidate_rejected','round_closed','survivors_selected'):
                    print(json.dumps(event),flush=True)
            if run.waiting_round is not None:
                # --mode live is the explicit CLI request to release paid gates.
                run.continue_round()
            time.sleep(.05)
        snapshot=run.snapshot()
        summary=dict(mode=run.mode,n=run.n,run_id=run.id,status=run.status,
            elapsed_seconds=run.elapsed(),model_calls=run.calls,
            best_sum=run.best['score'] if run.best else None,
            programs=[{k:c[k] for k in ('id','name','round_id','bank_id','complete','median','minimum','trials')}
                      for c in run.candidates], failures=run.failures)
        print(json.dumps(summary,indent=2))
        if args.summary:args.summary.write_text(json.dumps(summary,indent=2)+'\n')
        return 0 if run.status=='finished' else 1
    finally:manager.close()


if __name__=='__main__':sys.exit(main())
