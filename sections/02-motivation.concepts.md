# Motivation — spine

## Purpose

Say WHY the topic is important for agentic development, and bound where it applies.

## Claims

- LLM-driven evolutionary search gives an agentic system a measurable search loop that can improve code or equations across generations.
- Good evaluation design is the selective pressure and therefore the highest-leverage design choice.
- The method should be used when a fitness function can capture useful signal, but it is unsafe where evaluation is ambiguous or easily gamed.

## Decisions

- The motivation section ties the topic directly to the course’s agentic-development pattern rather than discussing it as a general AI topic.
- The failure mode is framed through eval hacking rather than a vague loss of reliability.

## Open questions

- How much of the task should be described in the prompt versus encoded in the evaluator?
- What interface between code execution and fitness scoring is most stable for classroom workflows?

## Not doing

- We are not claiming that every LLM search problem should use an archive or island strategy.
- We are not presenting the method as a universal replacement for normal debugging or software engineering.
