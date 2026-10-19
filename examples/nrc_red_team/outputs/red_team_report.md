# AI Red Team for FEA — Robustness Evidence

## Question
Try to prove the model is fragile: which challenged modeling assumption most strongly changes the first 5 modal frequencies?

## Baseline
- Public benchmark: NUREG/CR-1677 Volume 1 Problem 1
- Nodes: 41
- Elements: 29
- Baseline modes: 28.5149, 56.4409, 82.9473, 144.1393, 166.2637 Hz

## Deterministic challenge library
- Elastic modulus: -20%, +20%
- Pipe wall thickness: -10%, +10%
- Lumped masses: -20%, +20%
- Boundary condition: release UX at the second anchor (Node 24)

## Ranking
1. **Anchor UX released** — max |Δf| = 47.039% (Mode 2)
2. **Lumped masses -20%** — max |Δf| = 11.803% (Mode 4)
3. **Elastic modulus -20%** — max |Δf| = 10.557% (Mode 4)
4. **Elastic modulus +20%** — max |Δf| = 9.545% (Mode 1)
5. **Lumped masses +20%** — max |Δf| = 8.713% (Mode 5)
6. **Wall thickness -10%** — max |Δf| = 6.382% (Mode 2)
7. **Wall thickness +10%** — max |Δf| = 6.004% (Mode 2)

## Interpretation
This demonstration does not ask an LLM to calculate structural response. Each challenge rebuilds the FE model, MAPDL solves it, and the harness ranks the resulting changes. A future LLM layer can propose additional engineering hypotheses and decide which challenge to run next, while the solver remains authoritative.

## Evidence
- `01_baseline_model.png`
- `02_robustness_heatmap.png`
- `03_sensitivity_ranking.png`
- `04_red_team_evidence.png`
- `challenge_results.csv`
- `ranked_assumptions.csv`
- `baseline_summary.json`
- `challenge_definitions.json`
- `red_team_results.json`

## Public benchmark
https://examples.mapdl.docs.pyansys.com/version/dev/verif-manual/vm-nr1677-01-1a.html
