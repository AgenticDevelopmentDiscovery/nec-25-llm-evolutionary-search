"""Draw a solution two ways: the color map and the frustration map.

  colours      -- what the solver decided. Each node drawn as one of two
                  colors: large single-color regions, the walls between
                  them, a clean global split or a patchwork.

  frustration  -- what the solver could not achieve. A positive edge whose
                  endpoints agree, or a negative edge whose endpoints differ,
                  is frustrated and is drawn hot.

Usage::

    uv run --extra viz viz.py both --instance instances/public/torus_pm_32_s21.txt \
                                   --assignment solutions/torus_pm_32_s21.txt

``colours`` and ``frustration`` draw one panel each; ``both`` draws them side by
side. ``torus_pm`` instances are drawn on their L x L grid, everything else as
a node-link diagram (up to 300 nodes). Override with ``--layout grid|graph``.
Figures land in ``figures/``.
"""

from __future__ import annotations

import argparse
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from evaluate import cut_value, load_instance, load_solution  # noqa: E402

FIGURE_DIR = "figures"

# Okabe-Ito blue / orange for the two sides; vermillion for broken edges.
SIDE_COLORS = {-1: "#0072B2", +1: "#E69F00"}
HOT = "#D55E00"
FAINT = "#BBBBBB"


def frustrated(i, j, w, s):
    """Mask of the edges this coloring violates."""
    agree = s[i] == s[j]
    return ((w > 0) & agree) | ((w < 0) & ~agree)


def line_widths(w):
    """Width by |w|, so a heavy broken edge reads as more expensive."""
    a = np.abs(w)
    return 0.8 + 2.2 * a / a.max() if a.size else a


def grid_image(ax, n, s, alpha=1.0):
    L = math.isqrt(n)
    cmap = ListedColormap([SIDE_COLORS[-1], SIDE_COLORS[+1]])
    ax.imshow(s.reshape(L, L), cmap=cmap, vmin=-1, vmax=1, alpha=alpha,
              interpolation="nearest")


def grid_seams(n, i, j):
    """Segments between the two cells of each grid edge (wrap edges on the border)."""
    L = math.isqrt(n)
    segs = []
    for a, b in zip(i.tolist(), j.tolist()):
        (ra, ca), (rb, cb) = divmod(a, L), divmod(b, L)
        if ra == rb:  # horizontal neighbors: vertical seam right of the left cell
            c = ca if (ca + 1) % L == cb else cb
            segs.append([(c + 0.5, ra - 0.5), (c + 0.5, ra + 0.5)])
        else:  # vertical neighbors: horizontal seam below the upper cell
            r = ra if (ra + 1) % L == rb else rb
            segs.append([(ca - 0.5, r + 0.5), (ca + 0.5, r + 0.5)])
    return segs


def spring_positions(n, i, j, seed=0, iterations=300):
    """Force-directed layout, hand-rolled in numpy. Refuses above 300 nodes."""
    if n > 300:
        raise SystemExit(f"node-link layout is for n <= 300, got n={n}; "
                         "use --layout grid on a torus instance")
    pos = np.random.default_rng(seed).random((n, 2))
    k = 1.0 / math.sqrt(n)  # ideal edge length
    src, dst = np.concatenate([i, j]), np.concatenate([j, i])
    for it in range(iterations):
        delta = pos[:, None, :] - pos[None, :, :]
        d2 = np.maximum((delta ** 2).sum(axis=2), 1e-6)
        disp = (k * k * delta / d2[:, :, None]).sum(axis=1)  # repulsion
        e = pos[src] - pos[dst]
        np.add.at(disp, src, -e * np.linalg.norm(e, axis=1, keepdims=True) / k)
        step = 0.1 * (1.0 - it / iterations)  # linear cooling
        length = np.maximum(np.linalg.norm(disp, axis=1, keepdims=True), 1e-9)
        pos += disp / length * np.minimum(length, step)
    return pos


def draw_colours(ax, n, i, j, w, s, layout):
    if layout == "grid":
        grid_image(ax, n, s)
    else:
        pos = spring_positions(n, i, j)
        ax.add_collection(LineCollection(np.stack([pos[i], pos[j]], axis=1),
                                         colors=FAINT, linewidths=0.5, alpha=0.6))
        ax.scatter(pos[:, 0], pos[:, 1], s=max(8, 2000 / n), zorder=2,
                   c=[SIDE_COLORS[int(v)] for v in s], edgecolors="white", linewidths=0.5)
    ax.set_title(f"colors: cut = {cut_value(i, j, w, s):g} (total weight {w.sum():g})")
    ax.legend(handles=[Patch(color=SIDE_COLORS[v], label=f"s = {v:+d}") for v in (-1, 1)],
              loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2,
              fontsize=9, frameon=False)
    ax.set_aspect("equal")
    ax.set_axis_off()


def draw_frustration(ax, n, i, j, w, s, layout):
    bad = frustrated(i, j, w, s)
    if layout == "grid":
        L = math.isqrt(n)
        grid_image(ax, n, s, alpha=0.2)  # faint context, so seams sit on domain walls
        ax.add_collection(LineCollection(grid_seams(n, i[bad], j[bad]), colors=HOT,
                                         linewidths=line_widths(w[bad])))
        ax.set_xlim(-0.5, L - 0.5)
        ax.set_ylim(L - 0.5, -0.5)
    else:
        pos = spring_positions(n, i, j)
        ax.add_collection(LineCollection(np.stack([pos[i], pos[j]], axis=1),
                                         colors=FAINT, linewidths=0.5, alpha=0.4))
        if bad.any():
            ax.add_collection(LineCollection(np.stack([pos[i[bad]], pos[j[bad]]], axis=1),
                                             colors=HOT, linewidths=line_widths(w[bad])))
        ax.scatter(pos[:, 0], pos[:, 1], s=max(4, 800 / n), c="#555555", zorder=2)
    ax.set_title(f"frustration: {bad.sum()} edges broken, weight {np.abs(w[bad]).sum():g}")
    ax.set_aspect("equal")
    ax.set_axis_off()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command", choices=["colours", "frustration", "both"])
    p.add_argument("--instance", required=True)
    p.add_argument("--assignment", required=True, help="solution file: one -1 or +1 per line")
    p.add_argument("--layout", choices=["grid", "graph"], help="default: from the instance family")
    p.add_argument("--out")
    args = p.parse_args(argv)

    n, i, j, w = load_instance(args.instance)
    s, message = load_solution(args.assignment, n)
    if s is None:
        raise SystemExit(f"{args.assignment}: {message}")
    is_torus = os.path.basename(args.instance).startswith("torus") and math.isqrt(n) ** 2 == n
    layout = args.layout or ("grid" if is_torus else "graph")
    panels = {"colours": [draw_colours], "frustration": [draw_frustration],
              "both": [draw_colours, draw_frustration]}[args.command]

    fig, axes = plt.subplots(1, len(panels), figsize=(6 * len(panels), 6.5), squeeze=False)
    for ax, draw in zip(axes[0], panels):
        draw(ax, n, i, j, w, s, layout)
    stem = os.path.splitext(os.path.basename(args.instance))[0]
    fig.suptitle(f"{stem}  ({os.path.basename(args.assignment)})")
    out = args.out or os.path.join(FIGURE_DIR, f"{stem}_{args.command}.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
