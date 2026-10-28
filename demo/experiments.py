"""Public matched experiment presets. Checkboxes seed populations, not search spaces."""
SCENARIOS = {
 'contrast_limited': {'label':'1 · Limited suite / 1,000-vertex signed graph','instance':'rand_pm_1000_s23.txt','seed':3,'initial_solvers':['tabu','annealing']},
 'contrast_informed': {'label':'2 · Informed suite / same signed graph','instance':'rand_pm_1000_s23.txt','seed':3,'initial_solvers':['tabu','bls','bm']},
 'harder': {'label':'3 · Dense real-weight stress case','instance':'dense_gauss_100_s14.txt','seed':3,'initial_solvers':['tabu','annealing','bls','bm']},
}


def progress_metrics(events, reference):
    calls=0; median_match=None; robust_match=None; witness_match=None
    numerical=0; best_median=None; initial_median=None; best_cut=None
    for e in events:
        kind=e['type']
        if kind=='model_started':calls+=1
        if kind=='trial_scored':numerical+=e.get('elapsed_seconds',0)
        if kind=='best_updated':
            best_cut=e['best']['cut']
            if best_cut>=reference-1e-9 and witness_match is None:witness_match={'seconds':e['elapsed'],'calls':calls}
        if kind=='candidate_ranked' and e['candidate']['complete']:
            c=e['candidate'];best_median=max(best_median,c['median']) if best_median is not None else c['median']
            if c['round_id']==0:initial_median=max(initial_median,c['median']) if initial_median is not None else c['median']
            if c['median']>=reference-1e-9 and median_match is None:median_match={'seconds':e['elapsed'],'calls':calls}
            if c['minimum']>=reference-1e-9 and robust_match is None:robust_match={'seconds':e['elapsed'],'calls':calls}
    return {'reference':reference,'initial_best_median':initial_median,'best_median':best_median,'best_cut':best_cut,
      'median_reference':median_match,'all_trials_reference':robust_match,'witness_reference':witness_match,
      'numerical_seconds':numerical,'model_calls':calls}
