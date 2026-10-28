# Historical implementation map

This records the initial implementation. The user later requested concurrent
private campaigns, manual commits and explicit consolidation; see the
[current implementation/workflow](CONCURRENT_CAMPAIGNS.md).

# Implementation map — October 20, 2026

Starting checkout: `a19c758` (validated portfolio), with the supplied evolution brief as the only preexisting untracked file. Actual hashes and baseline test/scoring receipts are in `evidence/evolution/`. The original 61 tests were rerun successfully; the latest complete retained set was independently rescored. Existing official files, portfolio sources, configurations, upstream source and public assignments are preserved.

The framework will use plain modules: immutable candidates and capability filtering; exact target/archive/scoring helpers; a real structured-output Codex bridge; bounded isolated numerical evaluation; a persistent round controller with locks, write-ahead promotion/commit recovery; and `evolve_search.py`. Numerical workers import frozen portfolio snapshots. Candidate edits are limited to isolated research modules and validated configuration/policy changes. The controller, scorer and objective do not evolve.

Implementation order: snapshot/target/artifact primitives; bounded trial and Codex bridges; persistent round state and local commits; fixture recovery/selection tests; illustrated documentation and one bounded real Codex scratch integration. Public campaign launch is outside this implementation run. Local round commits in scratch verification repositories are authorized; remote pushes and milestone tags are not performed.

The installed Snap Codex CLI requires access to its normal runtime directory; the sandboxed version probe failed explicitly, while the authorized host probe succeeded at `codex-cli 0.114.0`. Its actual exec help supports stdin prompts, JSONL events, output schemas and final-message files. No API key or replacement model is invented. Candidate execution uses the available Bubblewrap filesystem sandbox and the portfolio's verified descendant cleanup.
