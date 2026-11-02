# Frozen before validation; original live run d59faeb94cce415f8677b0c7ea39190d; program 322a2bde034f929b.
def solve(initial, seed, steps):
    rng = np.random.default_rng(seed)
    centers = np.array(initial, dtype=float, copy=True)
    n = len(centers)
    rs = radii(centers)
    score = float(rs.sum())
    best_centers = centers.copy()
    best_rs = rs.copy()
    best = score
    report(np.column_stack((best_centers, best_rs)))
    total = max(1, int(steps))
    for k in range(total):
        frac = k / max(1, total - 1)
        scale = 0.038 * (1.0 - frac) + 0.0012
        if k % 19 == 18:
            scale *= 2.2
        for attempt in range(2):
            proposal = centers.copy()
            q = rng.random()
            if q < 0.16:
                count = 3
            elif q < 0.43:
                count = 2
            else:
                count = 1
            ids = rng.choice(n, size=count, replace=False)
            delta = rng.normal(0.0, scale, size=(count, 2))
            if count == 2 and rng.random() < 0.35:
                delta[1] = -delta[0] * rng.uniform(0.45, 1.0)
            proposal[ids] = np.clip(proposal[ids] + delta, 1e-8, 1.0 - 1e-8)
            rr = radii(proposal)
            trial = float(rr.sum())
            if trial > best:
                best = trial
                best_centers = proposal.copy()
                best_rs = rr.copy()
                report(np.column_stack((best_centers, best_rs)))
            temperature = 0.0038 * (1.0 - frac) + 0.000025
            accept = trial >= score
            if not accept and rng.random() < math.exp(max(-60.0, (trial - score) / temperature)):
                accept = True
            if accept:
                centers, rs, score = proposal, rr, trial
    return np.column_stack((best_centers, best_rs))