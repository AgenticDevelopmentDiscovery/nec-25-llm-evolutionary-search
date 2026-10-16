# Context

## What this is

LLM-driven evolutionary search keeps the evolutionary skeleton of search — a population or archive of candidate programs, a fitness function, and a selection mechanism — but replaces the random mutation or crossover operator of classic genetic programming with an LLM. Instead of editing code at random, the model reads one or more high-scoring parents and proposes a new program variant that is more likely to improve the objective. The result is an evolutionary loop in which the language model behaves like a learned mutation operator over code.

## Where it came from

The idea grew out of the long tradition of genetic programming, where mutation and crossover are usually random edits over symbolic trees or strings. FunSearch, introduced by Romera-Paredes et al. in Nature in 2023, showed that an LLM could act as a program mutation operator and discover improved solutions by iterating search and scoring. AlphaEvolve generalized the pattern to richer codebases and more complex objectives, and OpenEvolve now provides an open-source reimplementation that is easier to run and study.

## What this tutorial covers

This tutorial introduces the conceptual loop, the role of the fitness function, and the methods used to keep search from collapsing into a single narrow solution. The motivation section explains why this method matters for agentic development. The content section turns the abstraction into a worked symbolic-regression example with an LLM proposing equations, an evaluator scoring them, and held-out checks revealing eval hacking. The conclusion then states the capabilities the reader can carry forward: designing a small generate → evaluate → select → mutate workflow and reasoning about the fitness function that shapes it.
