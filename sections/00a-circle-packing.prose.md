# The circle-packing problem

## Circle packing: the problem {#packing-26 data-seconds="45"}

::: {.question}
**What are we trying to arrange?**
:::

::: {.block}
:::: {.columns}
::: {.column width="58%"}
Place **26 or 32 circles** inside a square with side length 1. Choose each circle's **center** (its location) and **radius** (half its width). The radii may differ.
:::
::: {.column width="38%"}
![Four circles illustrate the rules.](figures/packing-rules.svg){width=100%}
:::
::::
:::

::: {.block}
Every circle must stay inside the square. Circles may touch each other and the boundary, but they must **not overlap**.
:::

::: {.answer}
**A valid packing satisfies these rules for every circle.** The number of circles stays fixed within each problem.
:::

::: {.notes}
Begin with the geometry before introducing an algorithm. A center is the point in the middle of a circle. A radius is the distance from that center to its edge, so the diameter is twice the radius. A unit square has side length one. In each problem the number of circles is fixed: 26 for Demo 1 and 32 for Demo 2. Their sizes can differ. We choose both their centers and their radii.

The picture shows four circles so the rules are easy to see. It is an illustration, not the 26- or 32-circle demo output. The dot marks one center and the segment labeled r runs from that center to the circle's edge. Its plotted center/radius triples are (0.22,0.22,0.22), (0.74,0.22,0.18), (0.25,0.72,0.18), and (0.72,0.72,0.25). All circles fit inside the square and their interiors are disjoint.

A packing is valid only if every circle lies entirely inside the square and no two circle interiors overlap. Touching is allowed. For a center $c_i=(x_i,y_i)$ and radius $r_i$, these rules are $r_i\ge0$, $r_i\le x_i\le1-r_i$, $r_i\le y_i\le1-r_i$, and $\|c_i-c_j\|_2\ge r_i+r_j$ for each distinct pair. Zero radii are allowed under the demonstration's contract and remain visible in its reports. The next frame introduces the score, separately from these validity rules.

The two cases use the mathematical formulation in AlphaEvolve Appendix B.12 [@alphaevolve2025]. The local initial methods, controller, Luna model and compute budget are our classroom implementation. No published answer coordinates are hidden in the initial arrangements.
:::

## Circle packing: the goal {#packing-goal data-seconds="45"}

::: {.question}
**Which valid packing is better?**
:::

::: {.block}
**Packing score:** $S=r_1+\cdots+r_N$, the sum of all radii. **Larger is better.**
:::

::: {.block .visual}
![Same four centers, different radii. Both packings are valid.](figures/packing-comparison.svg){width=85%}
:::

::: {.answer}
**B has the larger score.** Circle positions limit how large the radii can be. We need a strategy to search for better packings.
:::

::: {.notes}
Ask students to add the radii before revealing the conclusion. Point to the visible space around A's circles and then to the touching circles in B. Four times 0.15 is 0.60. Four times 0.25 is 1.00. Both drawings use centers (0.25,0.25), (0.75,0.25), (0.25,0.75) and (0.75,0.75). Arrangement B touches the boundary and neighboring circles, which the rules allow. These exact-coordinate drawings are teaching illustrations, not measured results from either demonstration or a claim about the best possible four-circle packing.

The score is the sum of radii. Covered area would use π times the sum of squared radii, which is a different objective. We also keep the number of circles fixed when comparing scores. A raw sum for 32 circles cannot establish improvement over a run with 26 circles.

This simple example improves by increasing radii at fixed centers. In a crowded arrangement, further changes can require moving centers: making room for one circle can reduce the room available for others. Finding a good arrangement therefore involves interacting choices. We will use an evolutionary framework to improve the Python programs that search for packings. A program is the method; a packing is the arrangement it produces. We check and score the arrangement to evaluate the method. This strategy can find better constructions without certifying a global optimum.
:::
