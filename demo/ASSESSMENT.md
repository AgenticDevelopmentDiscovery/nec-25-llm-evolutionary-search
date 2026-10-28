# Assessment of the existing tutorial

Reviewed on October 26, 2026 on branch `Tamim-dev`; no pre-existing tutorial
file was edited during the transfer. The starting checkout was clean.

## Preserve

- The WHAT / WHY / HOW / WHAT ELSE arc is coherent.
- One source produces document, slides and site; keep the existing Pandoc/Metropolis
  16:9 workflow and paired concept sidecars.
- Round 001 correctly identified the missing visible loop and concrete trace.
  Retain those original reports as historical feedback; do not rewrite them.
- Its emphasis on independent evaluation, diversity and evaluator exploitation
  is useful for this example.

## Change before class

1. **Replace the old worked example everywhere.** `topic.md`, context/content/
   conclusion prose and `03-content.concepts.md` still promise symbolic regression,
   five generations, held-out equation error and a complexity penalty. None of
   those is implemented here. Replace them with the actual strategy genome,
   graph, objective, fair seed comparisons and measured trace. Keep the lessons
   about validation, but do not call semantic toy tests evidence of generalization.
2. **Reduce the deck.** `output/slides.pdf` has 19 actual pages: title, four section
   dividers and fourteen content frames. The main loop slide is one paragraph;
   its rendered page 11 was inspected. Use a loop diagram and one visible parent/
   child trace instead. Suppress redundant divider frames if needed and verify
   rendered page count, rather than counting only Markdown headings.
3. **Replace bibliography placeholders.** `references.bib` contains only an example
   article and no substantive citations. FunSearch appeared online in December
   2023 and in Nature volume 625 (2024); distinguish those dates. Describe LLM
   mutation as biased proposals, not guaranteed superior mutations. Avoid implying
   AlphaEvolve and a small local strategy demo have the same scale or capability.
4. **Use the new measured example.** Seed 3 on the signed 10x10 torus gives parent
   58 and the tested tabu comparison 68. State that this is measured numerical
   headroom; only real model-run records can establish live evolutionary success.
5. **Make selection visible.** Show the child diff, same-budget comparison and
   survivor reason, including rejected or equal children. A rising cut curve
   alone can also come from restarts without an LLM.
6. **Keep scope teachable.** Introduce one elite pool, not islands + MAP-Elites +
   novelty search as three implemented claims. Leave those as optional further
   reading. Define strategy, solution and fitness as distinct objects.
7. **Separate modes.** Numerical smoke, live LLM and recorded real replay get
   persistent labels. A hard deadline, unavailable model or plateau is a valid
   observed outcome. Do not promise a global optimum or guaranteed live response.

## Sources to add, verified against primary pages

- Romera-Paredes et al., *Mathematical discoveries from program search with large
  language models*, Nature 625, 468-475 (2024), DOI 10.1038/s41586-023-06924-6.
  Primary full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145/
- Google DeepMind, *AlphaEvolve: A Gemini-powered coding agent for designing
  advanced algorithms*, May 14, 2025:
  https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- The actual OpenEvolve project (independent open-source implementation):
  https://github.com/algorithmicsuperintelligence/openevolve

These sources motivate the architecture; they do not validate this demo's runtime
or results. The ten-seed measurements and future real-model rehearsals do that.
