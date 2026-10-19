# NRC Semantic Model Diff + Root-Cause Evidence

## Question
Why did the modal response change between Model A and Model B?

## Deterministic semantic diff
- Model A: both anchor nodes fixed in all six structural DOFs.
- Model B: Node 24 changes only in **UX: FIXED -> FREE**.
- Geometry: unchanged.
- Node/element topology: unchanged.
- Material: unchanged.
- Pipe section: unchanged.
- Lumped masses: unchanged.

## Solver impact
- Modes solved: 5.
- Largest absolute modal shift: Mode 2, 56.4409 Hz -> 29.8916 Hz (-47.039%).
- Full comparison: `modal_comparison.csv`.

## Counterfactual test
The released UX restraint at Node 24 is restored and the model is solved again.

- Maximum residual difference from Model A: **0.000000%**.
- Counterfactual status: **PASS**.

## Root-cause conclusion
The boundary-condition revision at Node 24 is isolated as the causal change for the modal-response shift because the other tracked model semantics remain unchanged and restoring that restraint recovers the baseline modal response.

## Evidence
- `01_nrc_baseline_model.png`
- `02_frequency_impact.png`
- `03_root_cause_evidence.png`
- `model_summary.json`
- `model_a_semantics.json`
- `model_b_semantics.json`
- `semantic_diff.json`
- `modal_comparison.csv`

## Public benchmark
https://examples.mapdl.docs.pyansys.com/version/dev/verif-manual/vm-nr1677-01-1a.html
