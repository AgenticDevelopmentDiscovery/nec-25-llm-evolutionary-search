# 10.3 Selection and population management

## Elitism protects measured progress {#elitism data-seconds="55"}

::: {.question}
**If a mutation is worse, must the current champion disappear?**
:::

::: {.block}
Pool parents with the new child. Retain the best complete programs under the declared fitness rule.
:::

::: {.block}
For a maximized quality, elitism makes the observed best stay level or improve **under comparable evaluation conditions**.
:::

::: {.answer}
**A failed mutation need not erase a useful parent.** Preserve the best valid packing separately from program fitness.
:::

::: {.notes}
Chapter 10.3.1 describes carrying elite candidates forward. The lower-is-better course fitness is monotonically non-increasing when the same deterministic measured fitness is used. Equivalently, maximized observed quality is non-decreasing. This is a property of retaining a measured incumbent, not a theorem of global convergence or future quality on new instances.

Our default uses inherited packing banks. At each round, freeze the same incoming packings for the parents and the child, re-evaluate the parents, and select within that bank. An old program median from a different bank is not directly comparable. The cumulative best valid construction is a separate monotone curve because its verified geometry is retained. A valid progress packing can survive in that archive even when a program later times out and receives no eligible fitness.
:::

## Selection pressure and population collapse {#selection data-seconds="55"}

::: {.question}
**Why can keeping only the highest scores make search stagnate?**
:::

::: {.block}
**Top-$k$:** rank everyone and retain the best $k$. **Tournament:** sample a group and retain its best; smaller tournaments can preserve more alternatives.
:::

::: {.block}
Collapse: several survivors become small rewrites of the same search. Current fitness does not reveal every parent’s future descendants.
:::

::: {.answer}
**Strong selection exploits evidence but can discard useful routes.** Our top-three rule does not guarantee diversity.
:::

::: {.notes}
Chapter 10.3.2 compares top-k and tournament selection; 10.3.3 identifies population collapse. Our implemented rule is deterministic: all three trials must complete and pass geometry checks; then rank by median sum of radii, minimum sum, and stable source identity. A child below the champion may still survive if it belongs among the three best programs. Do not teach elitism as a rule that rejects every nonchampion.

Programs with different IDs may have nearly identical behavior. Normalizing syntax prevents comments alone from creating another genome, but it is not a semantic diversity measure. Several schedules differing only in a constant can still explore the same region. The guide names our three initial mechanisms so students can inspect their differences before deciding whether the population is varied enough. Tournament selection is explained here but is not implemented as a hidden classroom feature.
:::
