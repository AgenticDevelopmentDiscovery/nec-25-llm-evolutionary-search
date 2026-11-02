# Frozen before validation; original live run 8e4ad862eb9e4a64afc01e888551f894; program 692f84a9f165aa3b.
def solve(initial, seed, steps):
    rng = np.random.default_rng(seed)
    centers = np.array(initial, dtype=float, copy=True)
    current_r = radii(centers)
    current_score = float(current_r.sum())
    best_centers = centers.copy()
    best_r = current_r.copy()
    best_score = current_score
    report(np.column_stack((best_centers, best_r)))
    n = len(centers)
    for k in range(int(steps)):
        proposal = centers.copy()
        frac = k / max(1, int(steps) - 1)
        scale = 0.045 * (1.0 - frac) ** 1.4 + 0.0015
        if n > 1 and rng.random() < 0.16:
            ids = rng.choice(n, size=2, replace=False)
            proposal[ids] += rng.normal(0.0, scale, (2, 2))
        else:
            i = int(rng.integers(n))
            proposal[i] += rng.normal(0.0, scale, 2)
        proposal = np.clip(proposal, 1e-7, 1.0 - 1e-7)
        rr = radii(proposal)
        value = float(rr.sum())
        if value > current_score:
            centers = proposal
            current_r = rr
            current_score = value
        if value > best_score:
            best_score = value
            best_centers = proposal.copy()
            best_r = rr.copy()
            report(np.column_stack((best_centers, best_r)))
    return np.column_stack((best_centers, best_r))