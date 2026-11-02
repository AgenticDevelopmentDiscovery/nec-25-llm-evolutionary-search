# Appendix: architecture and data flow {#appendix .appendix-section}

## One server coordinates the experiment {#system-flow .appendix data-seconds="45"}

::: {.question}
**Who owns the population, execution and measurements?**
:::

::: {.block .visual}
![The server coordinates isolated execution and a separate provider worker.](figures/architecture-overview.svg){width=100%}
:::

::: {.answer}
**The controller owns the loop.** Only the model worker contacts TAMU; a separate isolated worker executes generated Python.
:::

::: {.notes}
The same loopback server serves the presentation, demo, algorithm guide, exchange, notes and PDFs. Browser controls create a run, start numerical evaluations and explicitly release each model gate. Server-sent events expose actual progress and support reconnect without repeating work. The model worker alone receives the configured provider credential. The generated program runs inside Bubblewrap with read-only runtime code, no host network and no repository, run-log or private-home mounts. Geometry is checked again in the server outside that code.
:::

## Request, context and source response {#api-context .appendix data-seconds="60"}

::: {.question}
**What crosses the model API boundary?**
:::

::: {.block}
Send the task, parent source, current-bank trial results, history and limits. Authorization is a separate HTTPS header.
:::

::: {.block}
Return JSON: `round_id`, `parent_ids`, `hypothesis`, `source`. The source defines `solve(initial, seed, steps)`.
:::

::: {.answer}
**A source string is executable code after admission.** The hypothesis is an explanation, never the authoritative score.
:::

::: {.notes}
The TAMU transport uses protected.gpt-5.6-luna, public streaming and no tools. It sends system instructions plus a JSON response schema and serialized context. The actual body is displayed on the demo page; the key is never part of it. Source identity is normalized syntax plus executor version. An inherited proposal must name actual surviving parent IDs. An independent proposal must use an empty parent list. The controller rejects duplicates and malformed responses without silent retries.
:::

## Execution, checking and feedback {#api-return .appendix data-seconds="50"}

::: {.question}
**When can a returned program become a survivor?**
:::

::: {.block}
Validate source → isolated trials → verify every circle and pair → aggregate three complete scores → select within the current packing bank.
:::

::: {.block}
Keep exact request/response records, valid witnesses and failures. The next context carries the measured history.
:::

::: {.answer}
**Execution turns a proposal into evidence.** Live LLM, numerical-only and recorded replay remain distinct throughout.
:::

::: {.notes}
Each numerical trial has an eight-second hard wall cap, including its isolated startup. Each model request has a 35-second cap, and the run has a 240-second deadline with bounded owned-process cleanup. Stop and Reset cancel the owned worker tree, not unrelated processes. Missing isolation or dependencies blocks execution instead of falling back to unsafe or fabricated work.

The numerical-only mode evaluates disclosed initial source programs without contacting Luna. Live mode performs real requests only at explicit gates. Replay is registered only from genuine provider records with matching task, source identities, geometry and transcript provenance. It reproduces recorded events, and reveals responses only as its timeline reaches them. Replay is not a new measured result under a changed executor.
:::
