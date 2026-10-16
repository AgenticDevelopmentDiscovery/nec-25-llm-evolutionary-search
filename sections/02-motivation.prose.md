# Motivation

## Why it matters for agentic development

LLM-driven evolutionary search matters for agentic development because it forms a closed loop around generation, evaluation, and selection that an agentic system can run repeatedly without human intervention. The generator is the LLM, the evaluator is the harness, and the selection rule is a fitness function that decides which candidates survive. In the capstone setting, this is the method that fuses prior threads: generated code, objective scoring, sandboxed execution, and search orchestration into one working pattern.

## What goes wrong without it

Without a well-designed fitness loop, an agentic system can produce plausible-looking code that never actually improves the real task. A candidate may exploit the visible evaluator, fit the scoring shortcut, or optimize for a traceable artifact rather than a robust objective. The failure is not merely that the search is slow. It is that a weak selective pressure turns the entire system into an optimizer of the wrong thing.

## When to reach for it

Reach for LLM-driven evolutionary search when the task is program synthesis, symbolic regression, or algorithm improvement and an objective can be evaluated automatically. It is a good fit when the search space is too large for exhaustive enumeration and a reasonable numeric or test-based fitness function can be scored. It is the wrong tool when evaluation is subjective, expensive, low signal, or not separable from the agent’s own behavior, because then the loop cannot reliably tell whether it is improving the right target.
