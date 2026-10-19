# NRC Semantic Model Diff + Root-Cause Demo

This demo extends the public NUREG/CR-1677 Volume 1, Problem 1 piping benchmark into a controlled model-revision investigation.

It creates:

- **Model A** — baseline NRC piping model with both anchors fixed.
- **Model B** — the same model with one support DOF released.
- **Counterfactual** — the changed DOF is restored and the model is re-solved.

The workflow records the semantic model change, compares modal frequencies, and tests whether restoring the changed assumption recovers the baseline behavior.

## Run

From the repository root with the existing virtual environment activated:

```bat
python examples\nrc_semantic_diff\run_demo.py
```

## Presentation-ready outputs

The `outputs` folder contains:

- `01_nrc_baseline_model.png`
- `02_frequency_impact.png`
- `03_root_cause_evidence.png`
- `modal_comparison.csv`
- `semantic_diff.json`
- `model_a_semantics.json`
- `model_b_semantics.json`
- `model_summary.json`
- `root_cause_report.md`
- `root_cause_summary.txt`

## Public source

ANSYS / PyMAPDL verification example: NUREG/CR-1677 Volume 1, Problem 1.

https://examples.mapdl.docs.pyansys.com/version/dev/verif-manual/vm-nr1677-01-1a.html
