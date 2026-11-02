def solve(initial, seed, steps):
    """Disclosed constructor: allocate radii for the common perturbed grid."""
    centers = np.array(initial, dtype=float)
    result = np.column_stack((centers, radii(centers)))
    report(result)
    return result
