# Frozen before validation; original live run d59faeb94cce415f8677b0c7ea39190d; program fb222085fbc31e19.
def solve(initial, seed, steps):
    """Move one center at a time and accept only a larger sum of radii."""
    rng = np.random.default_rng(seed)
    centers = np.array(initial, dtype=float)
    rs = radii(centers)
    best = float(rs.sum())
    report(np.column_stack((centers, rs)))
    for k in range(steps):
        proposal = centers.copy()
        i = int(rng.integers(len(centers)))
        scale = 0.04 * (1 - k / max(1, steps)) + 0.002
        proposal[i] = np.clip(proposal[i] + rng.normal(0, scale, 2), 0.001, 0.999)
        rr = radii(proposal)
        if float(rr.sum()) > best:
            centers, rs, best = proposal, rr, float(rr.sum())
            report(np.column_stack((centers, rs)))
    return np.column_stack((centers, rs))
