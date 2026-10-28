# Appendix: architecture and API {#appendix .appendix-section}

## Server architecture {#system-flow .appendix data-seconds="45"}

::: {.question}
**What coordinates the browser, numerical search and model?**
:::

::: {.block .visual}
![Only the model worker contacts TAMU.](figures/architecture-overview.svg){width=100%}
:::

::: {.block}
One loopback server owns run state and workers, serves every teaching page, and streams events to the browser.
:::

::: {.answer}
**The server orchestrates; workers execute; events explain.** The API key stays in the server-side client.
:::

::: {.notes}
The diagram shows responsibilities, not a collection of independently deployed services. HTTP requests use a standard-library ThreadingHTTPServer on 127.0.0.1:8766. Manager permits one active run. A Run thread owns its sequence of serial numerical trials and model calls. Numerical and model workers are bounded child subprocesses with PID/start-tick ownership. Original-edge checking happens both inside the numerical adapter and again in the controller; the scorer box is not a separate network service.

The browser never directly calls TAMU. It creates a run, starts it, advances explicit round gates and subscribes to server-sent events. The same server hosts presentation, demo, guide, exact exchange, architecture and teaching notes. Switching views or reconnecting only reads existing state; it cannot start another paid request. The separate architecture document maps every route, module, message and trust boundary in more detail.
:::

## The API request and context {#api-context .appendix data-seconds="60"}

::: {.question}
**What is actually sent when we press “Send parents to Luna”?**
:::

::: {.block}
```text
model: protected.gpt-5.6-luna
messages:
  system: instructions + response schema
  user: serialized round context
stream: true; tools: []
```
:::

::: {.block}
Context: up to three genomes and trial evidence; failures and tried IDs; algorithm defaults, bounds and remaining budget. The worker adds HTTPS authorization separately.
:::

::: {.answer}
**The context carries measured search memory.** Solution vectors, reference answers and the API key are excluded from the model's context.
:::

::: {.notes}
At an explicit round gate, Run.propose selects the measured survivors and constructs a JSON context through proposals.context. Parent records contain normalized stages, median, minimum and three trial records, including elapsed numerical time, stage counters and completeness. The context also includes attempted genome identities, actual validation or incomplete-trial failures, initial solver selection, graph size and signedness, the raw-start rule, allowed defaults, parameter bounds, stage work caps and remaining wall time.

The model receives two Chat Completions messages: a system message with instructions plus the required JSON schema, and a user message containing that context. The TAMU client sends a streamed HTTPS POST to https://chat-api.tamu.ai/api/chat/completions with the protected Luna model, max_completion_tokens=2400, low reasoning effort and no tools. Authorization is a server-side header, not part of the displayed body. The proposer is not given the assignment vectors, stored numerical preset, replay, benchmark name or reference target. The exact-exchange page displays the actual recorded request body and public return, rather than a reconstructed example.
:::

## Response and loop closure {#api-return .appendix data-seconds="50"}

::: {.question}
**When does streamed text become a candidate that can survive?**
:::

::: {.block}
Public chunks → completed JSON → known parent IDs → schema, bounds and duplicate checks → admitted stage program.
:::

::: {.block}
Owned numerical trials → independent original-edge scores → complete-candidate ranking → new survivors and failure feedback for the next request.
:::

::: {.answer}
**Text is a proposal until validated and measured.** Server-sent events expose progress; selection supplies the next mutation context.
:::

::: {.notes}
model_worker.py projects public content and completion metadata from the provider stream, excluding hidden reasoning fields and authorization. A watcher emits actual public deltas to the browser. A completed response must be valid JSON with the required round ID, known parent IDs, hypothesis, mutation category, up to two children and any plateau reason. Each child is checked independently; invalid parameters and duplicate normalized genomes are rejected without a silent fix or free retry.

Admitted children run through backend.py in owned processes. The controller checks their graph hash and independently rescored witnesses. Incomplete candidates cannot enter the survivor ranking, even when their best witness is valid. Each event is appended to an ignored run log and streamed by SSE with a sequence number. Reconnection uses an event cursor and never launches paid work. A genuine recorded replay reproduces these events, keeps a persistent replay label, and reveals its public response only when the recorded timeline reaches that response.
:::

