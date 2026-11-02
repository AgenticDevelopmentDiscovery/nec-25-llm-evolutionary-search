def solve(initial, seed, steps):
    """Accept some temporary losses while retaining the best valid packing."""
    rng = np.random.default_rng(seed)
    centers = np.array(initial, dtype=float)
    rs = radii(centers)
    score = float(rs.sum())
    best, answer = score, np.column_stack((centers, rs))
    report(answer)
    for k in range(steps):
        proposal = centers.copy()
        indices = rng.choice(len(centers), size=2, replace=False)
        fraction = k / max(1, steps)
        proposal[indices] = np.clip(proposal[indices] + rng.normal(0, 0.03 * (1-fraction) + 0.002, (2, 2)), 0.001, 0.999)
        rr = radii(proposal)
        trial = float(rr.sum())
        temperature = 0.015 * (1-fraction) + 0.0001
        if trial > score or rng.random() < math.exp(min(0, (trial-score)/temperature)):
            centers, score = proposal, trial
        if trial > best:
            best, answer = trial, np.column_stack((proposal, rr))
            report(answer)
    return answer
