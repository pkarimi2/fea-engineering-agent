# NRC AI Red Team / Robustness Demo

This public-model demonstration challenges a known NRC piping benchmark with a deterministic library of engineering perturbations and ranks them by their effect on the first five natural frequencies.

## What it demonstrates

- Solver-backed robustness testing rather than LLM-generated numbers.
- A reproducible challenge library for material, section, mass, and boundary-condition assumptions.
- Automatic ranking of assumptions by maximum modal-frequency consequence.
- Presentation-ready robustness heatmap and evidence summary.

## Run

From the repository root with the existing virtual environment active:

```bat
python examples\nrc_red_team\run_demo.py
```

## Outputs

- `01_baseline_model.png`
- `02_robustness_heatmap.png`
- `03_sensitivity_ranking.png`
- `04_red_team_evidence.png`
- `challenge_results.csv`
- `ranked_assumptions.csv`
- `baseline_summary.json`
- `challenge_definitions.json`
- `red_team_results.json`
- `red_team_summary.txt`
- `red_team_report.md`

## Important interpretation

The phrase **AI Red Team** describes the engineering workflow we are building toward: challenge the model instead of merely accepting its answer. This demo keeps the challenge set deterministic and reproducible. A future LLM layer can propose additional hypotheses or select the next test, but MAPDL remains the numerical authority.
