# Simulated Bifurcation Quantum Annealing

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver sbqa --features`.

## 2. Intuition

Couple different replicas of the SAME node along a periodic replica ring. Independent restarts alone do not implement this model.

## 3. Formulation and conventions

$\Gamma(t)=\Gamma_0(1-t/T)^\alpha+10^{-5}$, $J_\perp=-\log[\tanh(\beta\Gamma/R)]/(2\beta)$. Use $\dot q_{ik}=p_{ik}/R$ and $\dot p_{ik}=-(1-a(t))q_{ik}/R+c_0\sum_jJ_{ij}f(q_{jk})/R+J_\perp(q_{i,k-1}+q_{i,k+1})$, periodic k. Here $f(q)=0$ for $|q|\le.7t/T$, else sign(q).

## 4. Algorithm steps

Initialize n×R positions/momenta near zero. Evaluate the regularized schedule; activate old node coordinates at the current threshold; add sparse within-replica interactions divided by R and periodic neighbor-replica force. Momentum-first symplectic Euler then updates position with another 1/R factor. Apply inelastic walls and extract final signs.

## 5. Fully worked small example

One edgeless node with R=3 positions (.1,.2,−.3), y=0, beta=Gamma0=alpha=1 at t=0 has $J_\perp=-\log\tanh[(1+10^{-5})/3]/2$. Replica 0 force is $-.1/3+J_\perp(-.3+.2)$. For dt=.1, new momentum is .1 times that force and new position is $.1+.1p^{new}/3$. Wrong-axis rolling or missing 1/R fails this test.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Simulated Bifurcation Quantum Annealing illustration](figures/replicas.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

replicas=8 (must be >=2), beta=1, gamma_initial=1, alpha=1, regularization=1e-5, replica_coupling=True. dt=.25 and c0 auto RMS are explicit CPU defaults. Coupling=False is a named ablation; it does not turn SBQA into the bSB equations because R scaling/activation remain.

Copyable config: [`configs/portfolio/sbqa.json`](../../configs/portfolio/sbqa.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

$O(nR+m)$ memory and $O(steps\,(n+m)R)$ CPU work, including replica-axis rolls. Interactions wrap from replica R−1 to 0 for every graph node.

## 9. Exactness and certification limits

A classical dynamical heuristic, not a quantum optimality certificate. No upper bound. Raw and optionally polished results are separated. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_bifurcation.replica_coupling / dynamics_step sbqa; Pawłowski et al. arXiv:2604.01050v1 Eqs.(5)–(8), full Methods reviewed including regularization.

Primary source records: [`sbqa`](../../papers/README.md#sbqa). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver sbqa \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/sbqa.json --seed 1 \
  --time-limit 10 --output runs/sbqa_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Fixed explicit beta/alpha/Gamma and CPU symplectic Euler are the project configuration; paper auto-tuning, adaptive integration/performance claims and GPU experiments are not reproduced. The implemented interacting model is kept distinct from independent replicas.
