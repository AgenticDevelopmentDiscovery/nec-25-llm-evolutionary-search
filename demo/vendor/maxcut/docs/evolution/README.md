# Independent single-graph evolutionary campaigns

Start with the [current concurrent campaign workflow](CONCURRENT_CAMPAIGNS.md).
New campaigns keep results/logs private, share no branch/index mutation, and make
no automatic commits. Different IDs may run concurrently in one checkout, either
from multiple terminals or through the bounded `batch` launcher. Public solution
consolidation is an explicit separate command.

Use `scripts/evolve_campaigns.py run` or `batch` for
[automatic resume of existing IDs](AUTO_RESUME.md). It reports already-running
controllers without disturbing them and preserves their pinned execution engine.

The framework evolves solver strategies for **one graph selected by the user**. A solver candidate and its best assignment are different objects: candidates compete and inherit code/configuration; the archive keeps every verified improvement, including useful witnesses from candidates that are not selected.

Implementation is additive. The validated portfolio at starting HEAD `a19c75865983911186e26af417519e8dfd5d6f84`, official files, upstream implementations and existing public solutions are preserved. No public campaign was launched during framework development.

Read the guides in this order:

1. [Architecture and responsibilities](ARCHITECTURE.md).
2. [Objective, target, proof and ladder mathematics](MATHEMATICS.md).
3. [Actual discovered capabilities](CAPABILITIES.md).
4. [Selection, seeds, budgets and stagnation](POLICIES.md).
5. [Inherited mutation examples and scope](MUTATIONS.md).
6. [Launch, inspect, stop and resume](TUTORIAL.md).
7. [Durability, commits, transcripts and recovery](RECOVERY.md).
8. [Measured verification and live integration](VERIFICATION.md).
9. [Class001 resource-explicit Slurm deployment and pending remote checks](CLASS001.md).
   [Cluster Codex start prompt](CLASS001_START_PROMPT.md) loads the instructions/context handoff.
10. [Comment/duplicate admission fixes and pinned campaign compatibility](ADMISSION_FIXES.md).
11. [Concurrent runs, manual commits and explicit consolidation](CONCURRENT_CAMPAIGNS.md).
12. [Automatic ID reuse without disrupting active campaigns](AUTO_RESUME.md).
13. [Permanent scoring timing fix and explicit source migration](SCORING_TIMING_FIX.md).

The bounded real integration now **passes with Codex CLI 0.163.0**, after the user upgraded from the incompatible Snap build. One actual model call proposed three inherited parameter/state-policy variants; numerical checks and evaluation reached verified cut 10 on the scratch trap and committed the round. The original failed attempts remain preserved. Fixture runs stay separately labeled `fixture-test`. See the [live check report](../../evidence/evolution/cli_update_0163/README.md) and [verification report](VERIFICATION.md). Public campaigns remain for separate user launches.

Current numerical source upgrade: [suite v3](../portfolio/SUITE_V3.md). Use the
updated local manifest and fresh class001 IDs, with longer equal-budget screening
and inherited local campaign expenditure. Old bases and round evidence stay intact.
