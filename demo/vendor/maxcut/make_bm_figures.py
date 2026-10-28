"""Generate settled and optional extension SVGs using standard-library geometry and recorded history."""

# argparse supplies explicit history/output paths and --help.
import argparse
# escape keeps labels such as 'gain < tolerance' valid XML text.
from html import escape
# json reads measured solver output instead of inventing progress data.
import json
# math supplies scalar circle geometry in radians and accurate analytic example values.
import math
# Path handles the chosen JSON input and SVG output directory.
from pathlib import Path


# Text labels are ordinary SVG elements, keeping figures inspectable without a plotting dependency.
def text(parts, x, y, label, size=16, color="#172334", anchor="start"):
    """Figures for Steps 1–9: append one XML-safe label; return None.

    parts is a mutable list[str]; x/y are pixel floats (e.g. 30,40);
    label is str; size is pixel font size (16); color is CSS str;
    anchor is 'start'/'middle'/'end'. Mutates parts only. escape(label)
    protects XML characters. Example text(parts,30,40,'A = +1'). O(label length).
    """
    # Escape the user-visible string, leaving the numerical pixel coordinates unchanged.
    safe = escape(str(label))
    # append adds a single SVG text element; the font is inherited from the document.
    parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{safe}</text>')


# A line may represent an undirected graph edge, an axis, a boundary, or a geometric vector.
def line(parts, x1, y1, x2, y2, color="#7b8794", width=2, arrow=False, dashed=False):
    """Figures: append a segment; all x/y arguments are pixels, color CSS str,
    width pixels, arrow/dashed bools. parts is list[str], mutated; return None.
    arrow=True is reserved for geometric vectors, NEVER graph edges.
    Example line(parts,10,20,40,20,arrow=True). O(1) aside from formatting.
    """
    # A dash pattern distinguishes a boundary or old arrow independently of color.
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    # Append the exact segment endpoints; equal x/y scales are supplied by callers for geometry.
    parts.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"{dash}/>')
    # Draw explicit arrowhead geometry so older SVG renderers need no marker support.
    if arrow:
        # hypot measures the pixel segment length without changing its mathematical endpoint.
        length = math.hypot(x2 - x1, y2 - y1)
        # A zero-length segment has no meaningful direction or arrowhead.
        if length > 0:
            # Divide the horizontal pixel displacement by length to get the unit tangent.
            ux = (x2 - x1) / length
            # The vertical tangent uses screen coordinates consistently with the segment.
            uy = (y2 - y1) / length
            # The first base corner lies nine pixels behind the tip and four pixels to one side.
            base1 = (x2 - 9 * ux - 4 * uy, y2 - 9 * uy + 4 * ux)
            # The other base corner lies the same distance behind and on the opposite side.
            base2 = (x2 - 9 * ux + 4 * uy, y2 - 9 * uy - 4 * ux)
            # The arrow tip is exactly the plotted vector endpoint; no vector is shortened or rescaled.
            parts.append(f'<polygon points="{x2:.3f},{y2:.3f} {base1[0]:.3f},{base1[1]:.3f} {base2[0]:.3f},{base2[1]:.3f}" fill="{color}"/>')


# All geometric vector panels share one explicit equal-axis unit conversion.
def plane(parts, center_x, center_y, scale, extent=1.3):
    """Steps 3–7 figures: draw axes and a true unit circle; return None.

    parts is mutated list[str]; center_x/y are origin pixels; scale is pixels
    per mathematical unit (e.g. 90); extent is positive axis radius in units
    (1.3). x maps right and y maps UP using center_y-scale*y. No input graph
    mutation. Example plane(parts,250,240,90) gives radius 90 pixels. O(1).
    """
    # The circle's radius is exactly one mathematical unit in the chosen pixel scale.
    parts.append(f'<circle cx="{center_x}" cy="{center_y}" r="{scale}" fill="none" stroke="#ccd4df"/>')
    # Horizontal axis endpoints use the same scale as the unit circle.
    line(parts, center_x - extent * scale, center_y, center_x + extent * scale, center_y)
    # Vertical coordinates invert screen y so positive mathematical y points upward.
    line(parts, center_x, center_y + extent * scale, center_x, center_y - extent * scale)
    # Axis labels define the coordinates as vector components rather than graph locations.
    text(parts, center_x + extent * scale + 8, center_y + 5, "x", size=14)
    # This y label sits above the equal-scale vertical reference axis.
    text(parts, center_x + 6, center_y - extent * scale - 8, "y", size=14)
    # The unit tick explicitly identifies the circle radius in vector units.
    text(parts, center_x + scale, center_y + 18, "1", size=12)
    # Origin labeling reinforces that every geometric arrow starts at the same point.
    text(parts, center_x - 12, center_y + 16, "0", size=12)


# Vector endpoints use the same coordinate map as axes and circles.
def vector(parts, cx, cy, scale, vx, vy, label, color="#1765ae", dx=8, dy=-8, dashed=False):
    """Steps 3–7: draw origin-to-(vx,vy) arrow; return None; mutate parts only.

    cx/cy are origin pixels, scale pixels/unit, vx/vy real components, label
    str, color CSS str, dx/dy pixel label offsets, dashed bool. Example
    vector(parts,250,240,80,2,1,'h=(2,1)') has length sqrt(5), not one.
    Coordinate mapping is (cx+scale*vx,cy-scale*vy). O(1).
    """
    # The endpoint's horizontal component uses the panel's common unit scale.
    x = cx + scale * vx
    # Screen y increases downward, so invert the mathematical vertical component.
    y = cy - scale * vy
    # Only geometric vectors receive arrowheads; length is never normalized implicitly.
    line(parts, cx, cy, x, y, color=color, width=3, arrow=True, dashed=dashed)
    # Place a persistent name/value label beside that exact endpoint.
    text(parts, x + dx, y + dy, label, size=15, color=color)


# Each output is standalone SVG with accessibility metadata and an explicit caption.
def save_svg(path, title, description, parts, height=500):
    """Figures: save an accessible 1100-by-height SVG; return None.

    path is selected Path (e.g. docs/figures/bm_scoring.svg), title/description
    are str, parts is list[str] drawing elements, height is pixel int (500).
    Inputs unchanged; writes that file. <title>/<desc> provide alt metadata;
    the caption is also visible. O(total SVG text size).
    """
    # Include role/img linkage so SVG viewers can expose its title and description.
    header = f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-labelledby="title desc">'
    # XML-escape metadata independently of the SVG drawing commands.
    metadata = f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
    # Set a readable white canvas and inherited system font, with no external assets.
    opening = '<rect width="1100" height="100%" fill="white"/><g font-family="DejaVu Sans, sans-serif">'
    # The title and caption become ordinary visible labels too.
    labels = []
    # The title is positioned consistently across all six figures.
    text(labels, 30, 35, title, size=23)
    # The caption uses a known bottom margin, outside the drawing panels.
    text(labels, 30, height - 18, description, size=14)
    # Join returns one complete XML string; input parts are not modified.
    content = "\n".join([header, metadata, opening] + labels + parts + ["</g></svg>"])
    # write_text writes UTF-8, preserving minus signs and angle symbols in labels.
    path.write_text(content + "\n", encoding="utf-8")


# The graph-scoring panels deliberately use undirected segments without arrowheads.
def triangle(parts, offset, signs):
    """Steps 1/2/8 figure helper: weighted triangle AB=5,BC=3,AC=1.

    parts is mutable list[str]; offset is horizontal pixel displacement
    (e.g. 0); signs is three ±1 ints in A,B,C order. Return None. Draw fixed
    weight labels and variable cut contributions; never mutate signs. O(1).
    Example triangle(parts,0,[1,-1,1]) shows contributions 5,3,0.
    """
    # Pixel positions are a graph layout, not geometric spin-arrow directions.
    points = [(100 + offset, 250), (260 + offset, 110), (420 + offset, 250)]
    # Persistent names identify original graph nodes across panels.
    names = ["A", "B", "C"]
    # These immutable weights are identical in every assignment panel.
    edges = [(0, 1, 5), (1, 2, 3), (0, 2, 1)]
    # Explicit edges provide both fixed weight and assignment-dependent contribution labels.
    for i, j, weight in edges:
        # Fetch this undirected segment's endpoints from the chosen layout.
        x1, y1 = points[i]
        # The other node's location is independent of its binary label.
        x2, y2 = points[j]
        # Draw a segment WITHOUT arrow=True: the input graph is undirected.
        line(parts, x1, y1, x2, y2, width=3)
        # A same-group edge contributes zero; its displayed weight still remains weight.
        contribution = weight if signs[i] != signs[j] else 0
        # Midpoint labels distinguish these two different quantities explicitly.
        text(parts, (x1 + x2) / 2, (y1 + y2) / 2 - 10, f"w={weight}; term={contribution}", size=14, anchor="middle")
    # Node colors reinforce, rather than replace, the written sign labels.
    for node, position in enumerate(points):
        # Unpack the selected layout coordinate for this original node.
        x, y = position
        # Both colors have visible dark sign labels, so meaning does not depend on hue alone.
        color = "#eaf4ff" if signs[node] > 0 else "#fff0da"
        # The node is a circle, never an arrow on an input edge.
        parts.append(f'<circle cx="{x}" cy="{y}" r="27" fill="{color}" stroke="#172334"/>')
        # +d prints an explicit +1/-1 label next to the persistent node name.
        text(parts, x, y + 5, f"{names[node]} {signs[node]:+d}", size=14, anchor="middle")


# The progress plot reads only measured arrays from a selected solver run.
def plot_series(parts, rect, series, labels, x_label, y_label):
    """Steps 6/9 figure helper: plot measured scalar series with true affine axes.

    parts is mutable list[str]; rect=(left,top,width,height) in pixels;
    series is list[list[(x,y)]], labels is matching list[str]; x/y labels are
    str with units. No source data mutation; return None. Example one series
    [(0,1.2),(1,1.5)] draws those actual samples. O(number of samples).
    """
    # Rectangular chart bounds need not have equal units because axes are explicitly labeled.
    left, top, width, height = rect
    # Collect axis coordinates independently from all measured series.
    xs = []
    # A separate list supports a common y scale within this plot only.
    ys = []
    # Every sample influences the labeled plot bounds.
    for values in series:
        # Values are (index or normal angle, measured objective) pairs.
        for x, y in values:
            # append records the actual x coordinate without imposing equal sample intervals.
            xs.append(x)
            # append records the actual observed y value.
            ys.append(y)
    # min/max return the actual extrema; the x range is padded only if all x values coincide.
    xmin = min(xs)
    # Keep a unit-wide nondegenerate x axis for a single-sample run.
    xmax = max(max(xs), xmin + 1e-12)
    # Objective extrema determine y bounds, with a visible margin below and above.
    ymin = min(ys)
    # A flat series gets a one-unit range instead of a division by zero.
    span = max(max(ys) - ymin, 1.0)
    # Ten percent of that span separates data markers from the chart frame.
    ymin = ymin - 0.1 * span
    # Use the original maximum plus the same padding.
    ymax = max(ys) + 0.1 * span
    # Draw horizontal axis without implying a vector direction or monotonic improvement.
    line(parts, left, top + height, left + width, top + height)
    # Draw the independently labeled vertical objective axis.
    line(parts, left, top, left, top + height)
    # Five grid labels make the affine data scale inspectable.
    for tick in range(5):
        # A fraction from zero to one sets a common tick position on either axis.
        fraction = tick / 4
        # Interpolate actual x units, not merely pixel positions.
        xvalue = xmin + fraction * (xmax - xmin)
        # Place each tick label under the corresponding chart coordinate.
        text(parts, left + fraction * width, top + height + 23, f"{xvalue:.3g}", size=12, anchor="middle")
        # Y values increase upward, so labels invert screen direction.
        yvalue = ymin + fraction * (ymax - ymin)
        # Include numerical objective ticks in weight units.
        text(parts, left - 8, top + height - fraction * height + 4, f"{yvalue:.5g}", size=12, anchor="end")
    # Each chart's x label specifies either sweeps or normal radians.
    text(parts, left + width / 2, top + height + 48, x_label, size=15, anchor="middle")
    # The y-axis quantity is written above the plot, avoiding a rotated hard-to-read label.
    text(parts, left, top - 15, y_label, size=16)
    # The palettes are reinforced by persistent legend labels and different dash styles.
    colors = ["#1765ae", "#b24c00"]
    # Plot each source series separately; never join R and F into a single series.
    for index, values in enumerate(series):
        # The point string will hold measured data mapped onto this chart's own axes.
        points = []
        # Every original sample contributes one position without smoothing.
        for x, y in values:
            # Map x linearly from actual data units into the plot width.
            px = left + (x - xmin) * width / (xmax - xmin)
            # Map objective upward from its explicitly labeled minimum/maximum.
            py = top + height - (y - ymin) * height / (ymax - ymin)
            # Retain adequate pixel precision for the affine mapping.
            points.append(f"{px:.3f},{py:.3f}")
            # Visible small markers distinguish actual samples from interpolating segments.
            parts.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="2.5" fill="{colors[index]}"/>')
        # The second series is dashed, so the raw/polished distinction also survives grayscale.
        dash = ' stroke-dasharray="6 4"' if index == 1 else ""
        # join makes SVG's coordinate list, without changing any source measurement.
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{colors[index]}" stroke-width="2"{dash}/>')
        # The legend explicitly names the objective series rather than relying on color.
        text(parts, left + index * 200, top + height + 78, labels[index], color=colors[index], size=14)


# Rectangles represent orchestration states, not graph nodes or unit-vector geometry.
def state_box(parts, x, y, width, height, labels, color="#eaf4ff"):
    """Steps 11–12 figure: append a labeled flow box; return None, mutate parts only.

    x/y/width/height are pixel scalars, labels is list[str], color CSS str.
    Example state_box(parts,30,80,220,90,['Fresh angles','independent stream']).
    Each label gets a separate line inside the rectangle. O(number of labels).
    """
    # SVG rect creates an explicit flow-state region with no implied graph adjacency.
    parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" fill="{color}" stroke="#65778b"/>')
    # Persistent text explains this state without relying on color alone.
    for index, label in enumerate(labels):
        # Use one connected label per line, with fixed readable spacing.
        text(parts, x + 12, y + 24 + 21 * index, label, size=14)


# Four-node graph panels preserve original node names and undirected weights.
def extension_trap_panel(parts, offset, signs):
    """Step 10 figure: append fixed K4 weights with the supplied four signs.

    parts is mutable list[str], offset horizontal pixels (0 or 540), signs is
    list of four +/-1 in A,B,C,D order. Return exact integer cut and draw no
    arrowheads on graph edges. No sign/weight mutation. O(1) graph size.
    """
    # A square is a graph layout, not a diagram of angular vector directions.
    points = [(115 + offset, 190), (375 + offset, 190), (115 + offset, 395), (375 + offset, 395)]
    # Separate label positions avoid the two diagonal weights crossing each other.
    edges = [(0, 1, 3, 245, 160), (2, 3, 3, 245, 435), (0, 2, 2, 80, 295),
             (1, 3, 2, 415, 295), (0, 3, 2, 192, 240), (1, 2, 2, 300, 240)]
    # Compute each stated assignment's actual cut rather than inventing a trajectory measurement.
    value = 0
    # All six undirected edges retain the same weights across the two panels.
    for i, j, weight, label_x, label_y in edges:
        # A crossing contributes its fixed weight; a same-label pair contributes zero.
        crossing = signs[i] != signs[j]
        # Draw undirected segments with distinct colors for the submitted cut membership.
        line(parts, *points[i], *points[j], color="#1765ae" if crossing else "#aeb8c4", width=3)
        # Label the FIXED weight at an uncluttered location near its edge.
        text(parts, label_x + offset, label_y, f"w={weight}", size=14, anchor="middle")
        # The exact score is the sum of weights of the stated crossing edges.
        if crossing:
            # Keep integer arithmetic for this analytic example only.
            value += weight
    # Draw original graph nodes, never geometrical arrows at their positions.
    for node, point in enumerate(points):
        # Label colors are redundant with the explicit +/-1 annotation.
        color = "#eaf4ff" if signs[node] == 1 else "#fff0da"
        # Node circles have a readable fixed radius on the square graph layout.
        parts.append(f'<circle cx="{point[0]}" cy="{point[1]}" r="28" fill="{color}" stroke="#172334"/>')
        # chr maps 0..3 to persistent A..D identifiers in the original node order.
        text(parts, point[0], point[1] + 5, f"{chr(65 + node)} {signs[node]:+d}", size=14, anchor="middle")
    # Return the exact F for caption checks, without claiming a solver transition.
    return value


# Separate raw-improvement and runtime axes avoid unexplained normalization of different quantities.
def measured_bars(parts, rect, rows, field, ylabel):
    """Step 13 figure: draw actual nonnegative measurement bars with categorical labels.

    parts is mutated list[str], rect=(left,top,width,height) pixels; rows are
    measured comparison dicts, field is 'difference' or 'wall_seconds', ylabel
    is a unit-bearing str. Return None; no input mutation. B/P/R/C prefixes
    label profile and explicit seed. Cost O(number of measured rows).
    """
    # Both charts have their own explicit numerical units and affine scales.
    left, top, width, height = rect
    # Actual observed values determine the vertical range; zero bars remain zero.
    values = [float(row[field]) for row in rows]
    # These retained-output comparisons should not produce negative gains or times.
    if not values or min(values) < 0:
        # Refuse unsupported/missing data instead of inventing replacement bars.
        raise ValueError("comparison bars require recorded nonnegative values")
    # A flat zero plot gets a finite unit range without fabricating nonzero measurements.
    maximum = max(max(values) * 1.15, 1e-6)
    # Draw the horizontal zero baseline independently of the chosen quantity's scale.
    line(parts, left, top + height, left + width, top + height)
    # The vertical axis is explicitly labeled in raw weight units or elapsed seconds.
    line(parts, left, top, left, top + height)
    # Short categorical names fit eight explicit profile/seed combinations legibly.
    prefixes = {"baseline": "B", "perturb_only": "P", "restart_only": "R", "combined": "C"}
    # Five ticks show the actual vertical measurement scale.
    for tick in range(5):
        # Fractions create evenly spaced tick positions, not invented data points.
        fraction = tick / 4
        # Numeric tick labels state the actual raw-unit axis conversion.
        text(parts, left - 7, top + height - fraction * height + 4, f"{fraction * maximum:.3g}", size=12, anchor="end")
    # Identify the quantity above the chart instead of rotating a hard-to-read label.
    text(parts, left, top - 18, ylabel, size=17)
    # Each measured record receives its own visible bar and profile/seed identity.
    for index, row in enumerate(rows):
        # One slot per actual record prevents plots of missing seeds or graphs.
        slot = width / len(rows)
        # Bars use this chart's numerical maximum; another chart may have different units.
        bar_height = float(row[field]) / maximum * height
        # The left margin separates adjacent measured categorical values.
        x = left + index * slot + slot * .2
        # SVG y grows downward, so higher measurements extend upward from zero.
        y = top + height - bar_height
        # Blue encodes actual bars, with numerical labels retaining accessible meaning.
        parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{slot*.6:.3f}" height="{bar_height:.3f}" fill="#1765ae"/>')
        # Compact names identify both profile and the actual explicit seed.
        label = prefixes[row["profile"]] + ":" + str(row["seed"])
        # Label every bar, including a genuine zero-height result.
        text(parts, left + (index + .5) * slot, top + height + 22, label, size=12, anchor="middle")


# Extension diagrams combine exact geometry with two explicitly selected measured evidence files.
def make_extension_figures(output_dir, attempt_report, comparison):
    """Steps 10–13: write five accessible SVGs from equations and actual pilot records.

    output_dir is selected Path; attempt_report is an actual run_bm JSON dict
    containing solver.attempts; comparison is an actual compare_bm JSON dict.
    Return None. Inputs untouched; write bm_extension_*.svg only. Geometry
    uses the specified deterministic offsets; measured traces use only recorded
    F/time samples. Example source pilot/restart_only/seed_0/histories/pilot8.json.
    O(attempt records + selected profile results); standard library only.
    """
    # A measured figure must have real recorded attempts rather than an illustrative fabricated trace.
    attempts = attempt_report["solver"]["attempts"]
    # Missing experiment results are errors, never zero placeholders on a chart.
    if not attempts or not comparison["results"]:
        # Keep figures honest when a pilot has not yet completed.
        raise ValueError("extension figures require completed attempt and comparison records")
    # Geometry uses four explicitly prescribed offsets, not a claim about a sampled random run.
    offsets = [-.35, .35, -.30, .30]
    # These binary signs match the worked example's original graph-node order.
    signs = [1, 1, -1, -1]
    # Compose independent SVG elements with the shared established primitives.
    parts = []
    # Persistent text specifies physical units and separates vectors from graph locations.
    text(parts, 35, 78, "Four graph nodes represented by separate unit-arrow panels; sigma = 0.35 radians.", size=17)
    # Each node gets identical equal x/y scales before and after angular perturbation.
    for node in range(4):
        # Centers are spaced uniformly so labels cannot overlap adjacent panels.
        cx = 155 + node * 260
        # Binary embedding is exact at zero or pi radians.
        base = 0.0 if signs[node] == 1 else math.pi
        # Modulo wraps negative offsets into the documented [0,2*pi) interval.
        angle = (base + offsets[node]) % math.tau
        # Name and sign belong to this graph node, not to an additional geometric point.
        text(parts, cx, 125, f"Node {chr(65+node)}: {signs[node]:+d}", size=18, anchor="middle")
        # A radius of 62 pixels equals one vector unit on both axes.
        plane(parts, cx, 245, 62)
        # The base arrow's direction is the exact binary angle, not a plotted graph edge.
        vector(parts, cx, 245, 62, math.cos(base), math.sin(base), chr(65+node), dx=10, dy=-12)
        # Put numerical angles outside the circle to avoid overlapping arrowheads.
        text(parts, cx, 360, f"base = {base:.6f} rad", size=15, anchor="middle")
        # The perturbed panel preserves exactly the same vector-unit scale.
        plane(parts, cx, 520, 62)
        # Noise changes direction only; every displayed arrow remains length one.
        vector(parts, cx, 520, 62, math.cos(angle), math.sin(angle), chr(65+node), color="#267953", dx=10, dy=23 if node == 0 else -12)
        # Display the explicit illustration offset, not a mislabeled random noise sample.
        text(parts, cx, 625, f"offset = {offsets[node]:+.2f} rad", size=15, anchor="middle")
        # Six decimals reproduce the specified worked example to its stated precision.
        text(parts, cx, 653, f"start = {angle:.6f} rad", size=15, anchor="middle")
    # Rounding uses the normal angle alpha=0, giving the unchanged original signs here.
    text(parts, 40, 707, "Immediate alpha=0 rounding: (+1,+1,-1,-1). Moving an arrow need not flip its binary label.", size=17)
    # The caption labels this as a deterministic geometric example rather than empirical improvement.
    save_svg(output_dir / "bm_extension_geometry.svg", "Step 10: binary embedding and angular perturbation", "Exact worked offsets; equal x/y scales. Sigma is a uniform angular half-width, not a flip fraction.", parts, 770)
    # Show two exact assignments of one unchanged graph, without a claimed stochastic trajectory.
    parts = []
    # The left assignment is the prescribed single-node local optimum.
    value8 = extension_trap_panel(parts, 0, [1, 1, -1, -1])
    # The right assignment groups A,C together and B,D together.
    value10 = extension_trap_panel(parts, 540, [1, -1, 1, -1])
    # Every exact cut label was computed from the displayed fixed edges.
    text(parts, 80, 95, f"{{A,B}} | {{C,D}}: F={value8}", size=20)
    # The exact optimum is a separate assignment, not the asserted next step of a noise run.
    text(parts, 620, 95, f"{{A,C}} | {{B,D}}: F={value10}", size=20)
    # All four local gains of the left assignment are exactly negative one.
    text(parts, 75, 490, "Left: gains=(-1,-1,-1,-1); greedy accepts zero flips. Exact optimum on four nodes is 10.", size=17)
    # A truthful attribution prevents treating the polished baseline's success as perturbation-only escape.
    text(parts, 75, 530, "Our settled all-plus polishing already finds 10 on this graph; these panels are not a noise trajectory.", size=16)
    # Graph segments remain undirected and both panels use the identical fixed weights.
    save_svg(output_dir / "bm_extension_trap.svg", "Step 10: a real greedy trap and a better assignment", "Exact assignments, not a guaranteed perturbation result. AB=CD=3; all four cross-pair weights are 2.", parts, 590)
    # Distinct restart-local states feed a shared global comparator; there is no reverse global-to-local shortcut.
    parts = []
    # Flow boxes describe orchestration and are distinct from geometric arrows and graph nodes.
    for restart, y in [(0, 145), (1, 435)]:
        # Each restart samples fresh angles, including the preserved original stream at index zero.
        state_box(parts, 35, y, 225, 90, [f"Restart {restart}: fresh angles", "independent initialization", "shared Steps 5-9 core"])
        # Only this restart's own best signs become its perturbation center.
        state_box(parts, 335, y, 235, 90, [f"Restart {restart} LOCAL best", "owned signs; direct F", "replace only if improved"], "#e9f6ef")
        # This loop explicitly performs P additional attempts rather than P total starts.
        state_box(parts, 320, y + 125, 265, 90, ["Rounds 1..P of this restart", "local signs -> 0/pi -> noise", "shared Steps 5-9 -> compare"], "#fff0da")
        # Initialization enters its own local comparison before refinement.
        line(parts, 260, y + 45, 335, y + 45, arrow=True)
        # A local best supplies the current restart's next noisy starting angles.
        line(parts, 405, y + 90, 405, y + 125, arrow=True)
        # The return arrow updates only the local best on strict improvement.
        line(parts, 545, y + 125, 545, y + 90, arrow=True)
        # Each local path can update a distinct shared global comparator.
        line(parts, 570, y + 45, 800, 340, arrow=True)
    # A global output is shared across all candidates but does not reset a different restart's local center.
    state_box(parts, 800, 290, 265, 110, ["GLOBAL best across starts", "and supplied old output", "owned signs; direct F", "strict improvements only"], "#e9f6ef")
    # A supplied incumbent may seed only restart zero's refinement center.
    text(parts, 35, 700, "Supplied signs may seed restart 0. A new restart never initializes from another restart's global best.", size=16)
    # The count is derived from the shown nested loops, not an undocumented extra baseline call.
    save_svg(output_dir / "bm_extension_loops.svg", "Steps 10-11: independent starts and restart-local refinement", "M=2, P=2 means 2*(1+2)=6 complete passes. Baseline polishing is inside each pass, not another start.", parts, 755)
    # Recorded candidates and retained global best are distinct series with an explicitly measured source.
    parts = []
    # Use only actual candidate cuts; the initial warm cut supplies a separate incumbent point when present.
    candidates = []
    # Start the retained series with the actual supplied cut if this was a warm continuation.
    globals_ = []
    # An absent old incumbent remains absent instead of a fabricated measurement at attempt zero.
    if attempt_report["solver"]["initial_cut"] is not None:
        # This point is the actually recomputed supplied assignment, before new attempts.
        globals_.append((0, attempt_report["solver"]["initial_cut"]))
    # Each chronological record carries actual restart/round identities and its own candidate F.
    for index, attempt in enumerate(attempts, start=1):
        # Candidate quality may fall; do not replace it by a cumulative maximum.
        candidates.append((index, attempt["candidate_cut"]))
        # Global quality comes from the recorded retained state, not recalculated smoothing.
        globals_.append((index, attempt["global_best_cut"]))
    # The two plotted quantities share real F units, unlike a relaxed/discrete mixture.
    plot_series(parts, (105, 160, 875, 260), [candidates, globals_], ["Actual candidate F", "Retained global-best F"], "Completed attempt (not sweeps)", "Discrete F (weight units)")
    # Name the actual toy input and seed so the reader can reproduce these exact attempts.
    text(parts, 50, 91, f"Input: {Path(attempt_report['instance']).name}; seed={attempt_report['solver']['seed']}; M={attempt_report['solver']['restarts']}, P={attempt_report['solver']['perturb_rounds']}.", size=18)
    # Keep the full finite measured cut list visible even when series overlap.
    text(parts, 50, 550, "Actual candidate F: " + ", ".join(f"{r['candidate_cut']:.6g}" for r in attempts), size=16)
    # Persistent values distinguish constant ties from a supposed hidden improvement sequence.
    text(parts, 50, 585, "Actual global F: " + ", ".join(f"{r['global_best_cut']:.6g}" for r in attempts), size=16)
    # Explicit ties on this bounded run must not be presented as a guaranteed perturbation success.
    text(parts, 50, 620, "These are recorded observations. Equal cuts are honest ties; other inputs/seeds may behave differently.", size=16)
    # The source is an actual saved CLI history, not the supplied package's schematic candidate sequence.
    save_svg(output_dir / "bm_extension_retention.svg", "Steps 11-12: actual candidates versus retained incumbent", "Measured toy history: candidates are never smoothed; only the retained best must be nondecreasing.", parts, 680)
    # Raw improvement and elapsed time are plotted separately for every actually compared toy input.
    parts = []
    # Each case is a selected graph from the actual comparison, not an invented missing public result.
    for case_index, case in enumerate(comparison["cases"]):
        # Match only this graph's explicit profile/seed rows.
        rows = [row for row in comparison["results"] if row["instance"] == case["instance_key"]]
        # Keep profile insertion and seed order from the recorded experiment.
        top = 180 + case_index * 330
        # The per-instance title prevents comparing raw cuts across different graph scales.
        text(parts, 40, top - 65, f"{case['instance_key']}; common F={case['common_cut']:.6g}; seeds={comparison['seeds']}", size=18)
        # Left bars report raw F increase, with an explicitly labeled weight-unit axis.
        measured_bars(parts, (90, top, 420, 155), rows, "difference", "Raw improvement in F (weight units)")
        # Right bars measure full subprocess wall time with independent numerical scaling in seconds.
        measured_bars(parts, (650, top, 400, 155), rows, "wall_seconds", "Measured subprocess wall time (seconds)")
    # Common legend identifies each profile's exact complete-pass budget.
    foot_y = 180 + len(comparison["cases"]) * 330
    # B is deliberately not described as an equal-work competitor to the three four-pass profiles.
    text(parts, 40, foot_y - 20, "B=baseline (1 pass); P=perturb_only (4); R=restart_only (4); C=combined (4). Labels include seed.", size=16)
    # Wall times include child startup and verification; fixed passes never imply matched elapsed time.
    text(parts, 40, foot_y + 20, "Fixed pass counts, NOT matched time. Tiny wall timings include startup/I/O and do not establish a speed ranking.", size=15)
    # Reference availability comes from the actual records, including future selected real-graph comparisons.
    available = sum(row["score"] is not None for row in comparison["results"])
    # Missing references stay explicitly unavailable rather than an invented normalized plot.
    reference_label = "Reference scores: not_available in these records." if available == 0 else f"Fixed reference scores available for {available} recorded calls."
    # Neither case is mislabeled as a full-ladder result.
    text(parts, 40, foot_y + 55, reference_label + " Selected inputs only; no full-ladder aggregate.", size=16)
    # Dynamic height reserves separate chart and caption regions for every actually present case.
    save_svg(output_dir / "bm_extension_comparison.svg", "Step 13: recorded selected-instance improvement and runtime", "Actual pilot values on separate raw-F and seconds axes; no missing graph results or fabricated normalizations.", parts, foot_y + 115)


# Main composes six standalone explanatory artifacts from equations and measured history.
def main(argv=None):
    """Figures for Steps 1–9: argv list[str] or None; return None.

    Read --history (default evidence/bm_smoke.json) and write six SVGs under
    --output-dir (default docs/figures). Optional --extension-history plus
    --comparison adds five measured extension diagrams; --extension-only
    skips the original six. No graph or history input is mutated.
    Geometry uses the specified analytic examples; progress uses only saved
    run values. Example: python make_bm_figures.py. O(history size).
    """
    # ArgumentParser constructs user-readable help for the figure generator.
    parser = argparse.ArgumentParser(description="Create six standard-library SVG figures from equations and measured solver history.")
    # The default is the bounded smoke run recorded by run_bm.py, not fabricated sample numbers.
    parser.add_argument("--history", type=Path, default=Path("evidence/bm_smoke.json"), help="Recorded run_bm.py JSON history (default: evidence/bm_smoke.json).")
    # The output directory is explicit and separate from official inputs and solutions.
    parser.add_argument("--output-dir", type=Path, default=Path("docs/figures"), help="Directory for bm_*.svg (default: docs/figures).")
    # These optional measured inputs enable five additional extension figures without changing old defaults.
    parser.add_argument("--extension-history", type=Path, help="Actual extended CLI JSON with per-attempt F; used with --comparison.")
    # The comparison plot uses actual selected-profile measurements, not synthetic values.
    parser.add_argument("--comparison", type=Path, help="Actual compare_bm.py comparison.json.")
    # Existing six-figure regeneration can be skipped explicitly when only extension artifacts are needed.
    parser.add_argument("--extension-only", action="store_true", help="Require both extension inputs and generate only five extension SVGs.")
    # parse_args uses a supplied list or shell arguments when argv is None.
    args = parser.parse_args(argv)
    # A partial extension input pair would otherwise risk a plot with missing evidence.
    if (args.extension_history is None) != (args.comparison is None):
        # Require both measured data sources before writing any figure.
        parser.error("--extension-history and --comparison must be supplied together")
    # Explicit extension-only calls do not require the original smoke history.
    if args.extension_only:
        # Missing evidence is an error, not permission to invent a measured trace.
        if args.extension_history is None:
            # Explain which measured inputs are necessary for the five extension diagrams.
            parser.error("--extension-only requires --extension-history and --comparison")
        # Create only the selected figure directory.
        args.output_dir.mkdir(parents=True, exist_ok=True)
        # Read actual finite JSON histories and pass their measured scalar records to the generator.
        make_extension_figures(args.output_dir, json.loads(args.extension_history.read_text()), json.loads(args.comparison.read_text()))
        # Preserve the old six figures untouched on this extension-only path.
        return
    # read_text reads the recorded UTF-8 report; loads converts JSON into dict/list/scalar data.
    report = json.loads(args.history.read_text(encoding="utf-8"))
    # Select the deterministic solver trace, excluding CLI runtime from plot coordinates.
    history = report["solver"]
    # An extended CLI history still contains the settled first-pass trace for the original six diagrams.
    core_scope = None
    # Do not mistake one restart's progress for a whole extended-run trajectory.
    if "attempts" in history:
        # Explicitly select the original restart-zero initialization's recorded core, without resampling.
        history = history["attempts"][0]["core"]
        # Label the scope if its best differs from the actual saved global incumbent.
        core_scope = f"This chart: restart 0 initial pass only. Whole-run saved F={report['reloaded_cut']:.12g}."
    # Create the selected artifact directory; existing figure files at these selected names are regenerated.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # Start the graph/scoring figure with an empty sequence of SVG elements.
    parts = []
    # The required labels give crossing terms 5 and 3, and internal term zero.
    triangle(parts, 0, [1, -1, 1])
    # Give the neighbor list its own region, outside the graph layout.
    text(parts, 560, 100, "Fixed adjacency (0-based internally)", size=19)
    # The two entries for A correspond to the once-per-edge list AB and AC.
    text(parts, 560, 145, "A [0]: (B,5), (C,1)")
    # B's symmetric entries carry the same fixed edge weights.
    text(parts, 560, 185, "B [1]: (A,5), (C,3)")
    # C's adjacency completes the undirected representation.
    text(parts, 560, 225, "C [2]: (A,1), (B,3)")
    # The sum uses edge contributions, not the entire sum of weights 9.
    text(parts, 560, 295, "F = 5 + 3 + 0 = 8", size=22)
    # The internal edge's weight remains one even while its contribution is zero.
    text(parts, 70, 345, "AC keeps w=1; its term is 0 because A and C share a group.")
    # Save with a caption that identifies graph edges as undirected.
    save_svg(args.output_dir / "bm_scoring.svg", "Steps 1–2: fixed weights and the binary cut", "Undirected edges: weight stays fixed; only the cut term changes with labels.", parts, 420)
    # A fresh list prevents unrelated elements from leaking into another figure.
    parts = []
    # Left panel shows the two allowed binary arrow directions.
    plane(parts, 240, 240, 90)
    # The panel title includes angle units.
    text(parts, 70, 80, "Binary: angles 0 or pi radians", size=19)
    # The right-pointing arrow corresponds to sign +1.
    vector(parts, 240, 240, 90, 1, 0, "+1: 0 rad", dy=-15)
    # The left-pointing arrow corresponds to sign -1.
    vector(parts, 240, 240, 90, -1, 0, "-1: pi rad", dx=-95, dy=-15)
    # Right panel has exactly the same vector unit scale and reference axes.
    plane(parts, 780, 240, 90)
    # Its title explicitly separates relaxed arrows from submitted labels.
    text(parts, 590, 80, "Relaxed: arbitrary unit arrows", size=19)
    # The required nonbinary example has three distinct angular directions.
    for name, angle in [("A: 20 deg", math.radians(20)), ("B: 130 deg", math.radians(130)), ("C: 250 deg", math.radians(250))]:
        # cos/sin take radians and give exact plotted horizontal/vertical components.
        vector(parts, 780, 240, 90, math.cos(angle), math.sin(angle), name)
    # State the angle conversion before assuming knowledge of radians.
    text(parts, 60, 395, "One turn = 2*pi radians = 360 degrees. Every vector starts at the shared origin.")
    # The caption reinforces that arbitrary angles must be rounded before output.
    save_svg(args.output_dir / "bm_arrows.svg", "Steps 3–4: binary signs become unit-circle directions", "Right panel is a relaxed representation, not a valid assignment file.", parts)
    # Coordinate geometry requires a larger visible range for h=(2,1).
    parts = []
    # Extent 2.6 and scale 75 ensure the length-sqrt(5) field fits at its true scale.
    plane(parts, 290, 260, 75, extent=2.6)
    # The neighbor arrows have unit lengths on the same axes as the field.
    vector(parts, 290, 260, 75, 1, 0, "v_B=(1,0)", dy=23)
    # C supplies the vertical weighted-neighbor component.
    vector(parts, 290, 260, 75, 0, 1, "v_C=(0,1)", dx=-130)
    # The field is NOT normalized: its endpoint is (2,1) on this exact scale.
    vector(parts, 290, 260, 75, 2, 1, "h_A=(2,1)", color="#b24c00")
    # The original A arrow points at 45 degrees and is dashed for persistent identification.
    vector(parts, 290, 260, 75, 1 / math.sqrt(2), 1 / math.sqrt(2), "old A: 45 deg", dx=16, dy=20, dashed=True)
    # The new A is the unit arrow opposite the weighted field.
    vector(parts, 290, 260, 75, -2 / math.sqrt(5), -1 / math.sqrt(5), "new A", dx=-70, dy=25, color="#267953")
    # Derivation labels specify the exact two-edge graph for this coordinate step.
    text(parts, 580, 100, "Only edges AB (w=2), AC (w=1)", size=19)
    # The field is a weighted sum, not another graph node's position.
    text(parts, 580, 145, "h_A = 2*v_B + v_C = (2,1)")
    # The vector norm is computed with hypot's x/y argument convention.
    text(parts, 580, 185, f"|h_A| = sqrt(5) = {math.hypot(2, 1):.6f}")
    # atan2's y-first argument order is explicitly visible next to the geometry.
    text(parts, 580, 225, "theta_new = atan2(-1,-2) mod 2*pi")
    # degrees converts the updated radian angle for the requested numerical label.
    text(parts, 580, 265, f"theta_new = {math.degrees(math.atan2(-1, -2) % math.tau):.6f} deg")
    # Calculate, rather than hard-code, the required initial incident objective.
    text(parts, 580, 320, f"R_A before = 1.5 - 3/(2*sqrt(2)) = {1.5 - 3 / (2 * math.sqrt(2)):.6f}")
    # The maximized dot product expression gives the exact analytic after value.
    text(parts, 580, 360, f"R_A after = 1.5 + sqrt(5)/2 = {1.5 + math.sqrt(5) / 2:.6f}")
    # The caption states the common unit scale so h cannot be mistaken for a unit vector.
    save_svg(args.output_dir / "bm_coordinate.svg", "Steps 5–6: an exact single-coordinate ascent update", "Equal x/y scales: one vector unit = 75 pixels. Field length is sqrt(5), not one.", parts, 520)
    # Rounding panels share an origin-to-arrow drawing convention, not a triangle graph layout.
    parts = []
    # These are the specified 0/120/240-degree angular node representations.
    angles = [0., 2 * math.pi / 3, 4 * math.pi / 3]
    # Both panels use the same unit scale while the normal and boundary rotate.
    for cx, alpha in [(250, 0.), (790, math.pi / 3)]:
        # Reference axes and circle establish the shared vector coordinate system.
        plane(parts, cx, 240, 90)
        # The chosen alpha is a normal angle, always in radians in the algorithm.
        text(parts, cx - 180, 80, f"normal alpha = {math.degrees(alpha):.0f} deg", size=19)
        # A perpendicular unit direction (-sin(alpha),cos(alpha)) spans the boundary line.
        bx = -math.sin(alpha)
        # This companion component keeps the boundary's dot product with r equal to zero.
        by = math.cos(alpha)
        # Extend the boundary beyond the unit circle using the same 90-pixel scale.
        line(parts, cx - 1.4 * 90 * bx, 240 + 1.4 * 90 * by,
             cx + 1.4 * 90 * bx, 240 - 1.4 * 90 * by, color="#b24c00", dashed=True)
        # Place a persistent boundary label away from the unit-arrow endpoint labels.
        text(parts, cx - 190, 405, "Dashed boundary: x dot r = 0", color="#b24c00", size=15)
        # Draw the normal r at exactly unit length on the same scale as the node arrows.
        vector(parts, cx, 240, 90, math.cos(alpha), math.sin(alpha), "r NORMAL", color="#b24c00", dy=27)
        # Calculate each arrow's projected sign with exactly the solver's tie policy.
        signs = []
        # Enumerate provides persistent A/B/C labels at their angular endpoints.
        for node, angle in enumerate(angles):
            # Scalar projection is the dot product of two unit arrows.
            projection = math.cos(angle - alpha)
            # Unitless tolerance 1e-12 assigns boundary and near-boundary projections to +1.
            sign = -1 if projection < -1e-12 else 1
            # Retain the calculated sign for the explicit panel label.
            signs.append(sign)
            # chr(65+node) maps indices 0,1,2 to A,B,C without changing their positions.
            vector(parts, cx, 240, 90, math.cos(angle), math.sin(angle), f"{chr(65 + node)} {sign:+d}", dx=8, dy=-12)
        # List exact analytic dot products rather than rounding them to zero or changing the graph.
        dots = "(1, -1/2, -1/2)" if alpha == 0 else "(1/2, 1/2, -1)"
        # These three numbers explain the sign of every arrow projection in the panel.
        text(parts, cx - 185, 380, "Dot products: " + dots, size=16)
        # The two selected groupings each cut two fixed +1 triangle edges.
        text(parts, cx - 185, 440, "Fixed graph: AB=BC=AC=+1; F=2", size=15)
    # Distinguish a line direction from its perpendicular normal using an explicit example.
    text(parts, 40, 490, "At alpha=0: (0,1) lies ON the dividing line; (1,0) points ALONG its normal r.", size=16)
    # The relaxed value is explicitly separated from the two valid cut values.
    text(parts, 40, 525, "R = 2.25 is NOT a valid discrete cut. Tie policy: |projection| <= 1e-12 gives +1.", size=16)
    # The caption describes all arrows as sharing one origin and avoids claiming exhaustive rounding.
    save_svg(args.output_dir / "bm_rounding.svg", "Step 7: round by the sign of projection onto the normal", "Vectors start at one origin. The dashed dividing line is perpendicular to r in each panel.", parts, 580)
    # Before/after graph panels preserve the same weights but change only node C's label.
    parts = []
    # The initial signs cross AB and AC for cut 6.
    triangle(parts, 0, [-1, 1, 1])
    # The flipped signs cross AB and BC for cut 8.
    triangle(parts, 540, [-1, 1, -1])
    # Each panel states its actual binary objective independently.
    text(parts, 100, 80, "Before: F=6; gains=(-6,-2,+2)", size=18)
    # Updated gains use the old sign of C, not its new negative label.
    text(parts, 640, 80, "After flipping C: F=8", size=18)
    # The explicit edge changes explain the gain as a net improvement.
    text(parts, 80, 335, "BC gains 3; AC loses 1; gain(C)=+2.", size=18)
    # Show neighbor gain corrections with old s_C=+1 and unchanged neighbor labels.
    text(parts, 80, 380, "OLD s_C=+1: g_A=-6 - 2*1*(+1)*(-1)=-4; g_B=-2 - 2*3*(+1)*(+1)=-8.", size=16)
    # The flipped node's own gain becomes the negative of its old gain.
    text(parts, 80, 420, "g_C becomes -2. Updated gains=(-4,-8,-2); no improving single-node flip remains.", size=16)
    # A clear caption prevents graph edges from being mistaken for directed vectors.
    save_svg(args.output_dir / "bm_local_search.svg", "Step 8: binary best-improvement using the OLD flipped sign", "Graph edges are undirected. All fixed weights are identical in the before/after panels.", parts, 490)
    # Progress is generated entirely from the selected measured JSON trace.
    parts = []
    # Sweep zero is the measured initial relaxed value before any optimization.
    relaxed_points = [(0., history["continuous"]["initial_value"])]
    # Append the measured after value for every recorded sweep, with no cumulative maximum.
    for sweep in history["continuous"]["sweeps"]:
        # Store the actual sweep number and its actual R measurement.
        relaxed_points.append((float(sweep["sweep"]), sweep["after"]))
    # Raw/polished F traces use their true direction angles, not fake time coordinates.
    raw_points = []
    # A separate series records discrete local-search improvement after each rounding.
    polished_points = []
    # All directions in the measured run appear once in each F series.
    for direction in history["roundings"]:
        # Raw F is computed before binary local search for this normal.
        raw_points.append((direction["alpha_radians"], direction["raw_cut"]))
        # Polished F is computed after Step 8 for the same normal.
        polished_points.append((direction["alpha_radians"], direction["polished_cut"]))
    # The left plot's y axis measures relaxed R in the graph's weight units.
    plot_series(parts, (85, 120, 400, 230), [relaxed_points], ["Measured relaxed R"], "Sweep number (0 = initialization)", "R (weight units; not a submitted cut)")
    # The right plot independently measures discrete F; it is not a continuation of the R series.
    plot_series(parts, (635, 120, 400, 230), [raw_points, polished_points], ["Raw rounded F", "Polished F"], "Normal alpha (radians)", "F (actual discrete cut, weight units)")
    # Report the retained source exactly, including baseline retention if all candidate values tied.
    retained = history["retained"]
    # The baseline is a legitimate earlier incumbent and may win every exact tie.
    if retained == "baseline":
        # This message does not invent a winning rounding direction.
        retained_label = "Retained: polished baseline (earlier incumbent on exact ties)."
    # Otherwise the saved index identifies one measured direction record.
    else:
        # Read the actual normal and score from its recorded direction index.
        direction = history["roundings"][retained]
        # Format the selected angle in radians with enough digits to identify it.
        retained_label = f"Retained: direction k={retained}, alpha={direction['alpha_radians']:.6f} rad, F={history['best_cut']:.17g}."
    # A textual marker identifies the retained candidate even for overlapping plotted points.
    text(parts, 50, 480, retained_label, size=17)
    # State source, seed, and stopping reason instead of presenting illustrative values as measurements.
    text(parts, 50, 520, f"Source: {Path(report['instance']).name}; seed={history['seed']}; stop={history['continuous']['stop_reason']}.", size=15)
    # The baseline measurement remains separately labeled rather than blended into a direction series.
    text(parts, 50, 555, f"Polished zero baseline F={history['baseline']['polished_cut']:.17g}. Exact F ties keep the earlier incumbent.", size=15)
    # Extended inputs need a visible distinction between this core chart and the saved global result.
    if core_scope is not None:
        # Existing legacy SVG output is unchanged because this extra label is only for extended histories.
        text(parts, 50, 585, core_scope, size=14)
    # Save separate axes and named objectives in a single overview artifact.
    save_svg(args.output_dir / "bm_progress.svg", "Steps 6 and 9: measured relaxed progress and discrete retention", "Separate plots: R by sweep; raw/polished F by normal direction. F across directions need not increase.", parts, 620)

    # Optional measured extension inputs add five diagrams while preserving the original six outputs.
    if args.extension_history is not None:
        # Both files were required as a pair before any drawing began.
        make_extension_figures(args.output_dir, json.loads(args.extension_history.read_text()), json.loads(args.comparison.read_text()))


# Imports are side-effect free; writing happens only when the script is executed.
if __name__ == "__main__":
    # None means the documented CLI reads the process's shell arguments.
    main()
