# Tutorial 25: LLM-driven evolutionary search

A 20–25-minute Chapter 10 tutorial with two live circle-packing demonstrations:
26 and 32 variable-radius circles in the unit square, maximizing summed radii,
as in AlphaEvolve Appendix B.12. Luna evolves actual Python search programs;
an isolated interpreter executes them and an independent checker scores geometry.

Start with [Student and agent setup](STUDENT_SETUP.md). After installing
`demo/requirements.txt` and Bubblewrap on Linux/WSL, run:

```bash
python demo/server.py --port 8766
```

Open http://127.0.0.1:8766/ for the presentation or /packing for the demo.
`just demo 8767` selects another port. The server hosts frames, live demonstration,
algorithm examples, exact public Luna exchange, notes, architecture and PDFs.
Numerical-only mode needs no API key. For live mode, each student puts their own
TAMU key in ignored demo/.env; only the blank example is public.

The mathematical problems match the paper. This bounded Luna implementation is
not the unpublished AlphaEvolve engine or a reproduction of its reported record.
See [demo/README.md](demo/README.md), [architecture](demo/ARCHITECTURE.md),
[presentation plan](demo/PRESENTATION_PLAN.md), and [actual readiness](demo/READINESS.md).

## Editing and building

Read [CLAUDE.md](CLAUDE.md) for the document method. Each sections/*.prose.md
has a matching concepts sidecar. Saved prose updates browser frames and notes;
`just build` regenerates document, final-state handout and site. `just overlays`
exports every reveal. Keep architecture/API detail in the optional appendix.

Chapter 10.1–10.5 use 2/3/2/1/2 conceptual frames, plus title and two demo sequences.
Past teaching sources, critiques, evidence and the hashed reference snapshot are
preserved as history. Do not commit, push, deploy or invoke the reviewer panel
without an explicit instruction. For a new session, read [the handoff](DEMO_REDESIGN_HANDOFF.md).
