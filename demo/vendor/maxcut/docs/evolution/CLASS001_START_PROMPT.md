# Paste into the Codex session in the cluster checkout

```text
Read instruction_Tamim/CLASS001_CODEX_INSTRUCTIONS.md and
instruction_Tamim/CLASS001_CONTEXT.md, then docs/evolution/CLASS001.md.
Treat the first file as my project instructions and the second as context that
must be checked against this checkout and the actual cluster.

Prepare this class001 checkout for the six expensive graphs in
 evolve/configs/class001_large.json. Preserve the validated portfolio, official
inputs/scorer, public solutions, portable starting labels and previous evidence.
I have no sudo access. Computation, builds and numerical tests must run through
Bash Slurm jobs. CPU, memory and array concurrency are intentionally undecided:
inspect site limits with permitted lightweight commands, propose a resource plan,
and let me choose the values before submission. Do not infer an allocation from
host nproc/free output. No public jobs or live model checks until I request them.

First report the checkout state, missing dependencies and unverified conditions.
Make necessary deployment fixes, prepare resource-explicit Slurm commands and
bounded verification jobs, and keep failure logs/context updated. Do not weaken
sandbox/source checks or rewrite old manifests to make errors disappear. Do not
commit, push, tag or automatically combine/publish results; I will do that.
```

The files are explicitly named because they are handoff documents rather than
an automatically discovered repository `AGENTS.md`. For the instruction loading
convention, see the [official guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
