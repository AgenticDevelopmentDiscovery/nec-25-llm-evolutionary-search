# Class001 publication and remote reconciliation

The user explicitly authorized updating real solutions, a proper session summary,
commit, fetch, deliberate combination and push. Publication means `solutions/`;
GitHub repository visibility is unchanged. Earlier search-time prohibitions on
automatic publication and Git actions do not override this explicit handoff.

## Preservation before updating

A verified private backup outside the checkout retained 87034 original local-work
files, the tracked binary patch, original HEAD and status. Its uncompressed tar
is 20.2GB. Environments, native prerequisites and credentials were left in place;
no reset --hard, clean, source-hash rewrite or deletion was used. Raw cluster
campaigns, model transcripts, runtime copies and failed generated snapshots stay
local. The commit includes source adaptations/overlays, scripts, tests, selected
receipts, published labels and the session account.

## Integration decisions

1. Slurm 59864 first updated the real solutions directory, before remote work,
   as specifically requested. Official overall 0.9830097949799796. The previous
   public files and sidecars were backed up with the selection/scorer receipts.
2. Commit `53d5068c` records the publication and cluster work. Commit `af26213a`
   adds the three newly generated large-graph identity sidecars.
3. Fetch advanced origin/main from `0ecbfc21` to `d4954e3f`, one laptop commit.
   Authentication used the existing user-owned class001 SSH agent; no new key,
   credential helper, token or credential file was created or exposed.
4. The incoming change adds extensive saved campaign evidence, an independent
   calibrated-SA driver and five tests, documentation/process history, and two
   public Torus results. It does not alter root solver/controller code, official
   input graphs, references or scorer. Existing cluster adaptations therefore
   remain intact without selecting a whole local/incoming code file.
5. A non-fast-forward merge stopped before committing and reported zero
   conflicts. An exact incoming solution snapshot was retained alongside the
   first cluster publication. No label file was chosen merely because it was
   local, incoming or textually mergeable.
6. Slurm 59865 ran four new publication tests, five incoming SA generated tests
   and the existing consolidation regression. The publisher reran its four
   gates before the final write. All passed. Numerical tests stayed inside the
   allocation: one node, two task slots times five CPUs, 15 GiB, 15min hard limit.
7. Final consolidation considered both branch snapshots and the incoming
   retained-label set plus the retained cluster archives. Exact objective checks
   and the unchanged official scorer reproduced **0.9879417376062763** on all 18
   real assignments. Seven cuts improve over the pre-session public folder,
   none degrade; the Torus100/Torus32 laptop gains are preserved alongside all
   five cluster gains. Zero candidate sources were rejected. No public solver
   or model ran. Cluster frozen campaign/source snapshots and original local verification reports remain intact.

The verified writer intentionally preserves existing bytes on exact ties; `1`
and canonical `+1` labels can thus have different hashes despite identical values.
Old selection receipts describe their canonical snapshots and were not rewritten.
The [released inventory](../../evidence/class001/session-20261021/released_assignments.json)
records actual public file hashes and existing metadata hashes separately.

## Validation and operational limits

- [Final official scores](../../evidence/class001/publication-59865.qq796u/consolidated/public_scores.json)
- [Publication receipt](../../evidence/class001/publication-59865.qq796u/consolidated/publication_receipt.json)
- [Integration test receipt](../../evidence/class001/integrated-publication-59865.LfQvrh/verification.json)
- [First cluster publication and backups](../../evidence/class001/publication-59864.TFQvbW/consolidated/)
- [Incoming exact solution snapshot](../../evidence/class001/remote-d4954e3f/)
- [Full session summary](CLASS001_SESSION_RESULTS.md)

Static checks parsed 84 project Python files and configuration JSON, checked Bash
syntax, and verified the original official inputs/references/scorer are unchanged.
Source/documentation whitespace checks passed. Historical raw log whitespace is
preserved exactly. The positive minimum-budget source remains unverified; this
handoff does not imply a successful new search or extend the expired 22:30 window.

Git spawned automatic background repacking during the early commit/fetch.
The exact user-owned gc/repack group was identified and terminated after it was
found consuming CPUs outside Slurm. Existing Git objects and all worktree files
were retained. Repository-local `gc.auto=0` prevents further automatic housekeeping;
heavy maintenance can be performed later inside an explicitly allocated job.
The final push is an ordinary fast-forward update of origin/main, without force,
tags, rewritten remote history or a repository visibility change.
