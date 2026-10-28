# Formal definition and transfer

## The agentic evolutionary framework {#definition data-seconds="60"}

::: {.question}
**Can we now name the five choices we implemented?**
:::

::: {.block}
$(\mathcal A,f,\mu,\sigma,P_0)$: artifact space, fitness, mutation, selection and initial population. Checkboxes choose $P_0$; they do not change $\mathcal A$.
:::

::: {.block}
$$Q_t\sim\mu(\cdot\mid P_t,H_t,B_t),\quad P_{t+1}=\sigma(P_t\cup E(Q_t)).$$

$H_t$: measured history. $B_t$: remaining budget. $E$: validation and complete evaluation.
:::

::: {.answer}
**The LLM is the mutation operator inside an externally measured evolutionary loop.** For the course minimization convention, $f(a)=-\operatorname{median}_j C_G(A_a(G,z_j))$.
:::

::: {.notes}
This instantiates Chapter 10, Definition 10.2, after the audience has encountered both ordinary evolutionary search and the LLM variant. The artifact space contains validated programs of one to three trusted stages. Its interpreter maps graph G and shared raw start z_j into signs under the seeded numerical protocol. Negative median cut turns maximization into the course's lower-is-better fitness convention. The implementation supplements that primary scalar with minimum cut, stage count and stable identity tie-breaks.

The chapter presents an artifact-to-artifact mutation operator. The operational notation here makes context, stochasticity and budget explicit: one tool-free call may refer to up to three selected parents and return at most two children. Q_t is the proposed set; E(Q_t) retains only admitted, completely evaluated children. Selected programs and their measured histories inform the next request. The model's parameters remain fixed; learning during the run is carried by external context and population memory.

Elitism preserves observed measured strategies under this protocol, not global optimality, diversity or unseen-instance quality. Initial population design and allowed artifact-space design are separate levers. In this tutorial all checked and unchecked trusted kernels remain available to mutation in every comparison.
:::

## Applying the framework to research {#transfer data-seconds="40"}

::: {.question}
**Which component would be hardest to supply honestly for your own research problem?**
:::

::: {.block}
Specify the artifact, automatic evaluator, mutation context, survivor rule and initial population. Declare budgets and a success criterion before running.
:::

::: {.block}
Use domain knowledge, compare strong numerical baselines, and test unseen instances before claiming generalization.
:::

::: {.answer}
**Build trustworthy measurement and inspectable data flow first.** Then decide where a language-model mutator earns its cost.
:::

::: {.notes}
Transfer the framework by replacing components deliberately. A scientific expression may be scored by prediction error and complexity; an experimental protocol still needs a definition of executable evidence. If no reliable automatic evaluation exists, measurement design is the next task. The algorithm guide and separate architecture document let a researcher inspect the system before adapting it.

FunSearch supplies a prominent program-search example [@funsearch2024]. AlphaEvolve operates at a broader algorithm-evolution scope [@alphaevolve2025], while OpenEvolve is an independent open-source implementation [@openevolve]. This classroom interpreter evolves configurations and compositions of existing kernels. It demonstrates the mechanism without claiming new kernel synthesis, broad model superiority or global convergence. The teaching sequence follows Chapter 10, especially Definition 10.2, Figures 10.1–10.2 and its discussions of context, elitism, diversity and cost.
:::
