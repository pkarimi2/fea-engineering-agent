# NRC Piping Benchmark — Public Demo Model

This example is intended to be the first public demonstration model for the FEA Engineering Agent.

## Source

Official PyMAPDL verification example:

https://examples.mapdl.docs.pyansys.com/version/dev/verif-manual/vm-nr1677-01-1a.html

Reference benchmark:

P. Bezler, M. Hartzman, and M. Reich, *Dynamic Analysis of Uniform Support Motion Response Spectrum Method*, NUREG/CR-1677, Brookhaven National Laboratory, 1980, Volume 1, Problem 1.

## Why this benchmark

The model is a compact but meaningful piping system with:

- three straight pipe segments,
- two bends,
- two fixed anchors,
- lumped structural masses,
- modal analysis,
- response-spectrum analysis,
- three excitation directions,
- GRP modal combination,
- published reference values.

The PyMAPDL implementation uses modern element technologies including `PIPE289`, `ELBOW290`, and `MASS21`.

## Reference modal frequencies

The official verification example compares the first five frequencies to approximately:

| Mode | Reference frequency (Hz) |
|---:|---:|
| 1 | 28.515 |
| 2 | 56.441 |
| 3 | 82.947 |
| 4 | 144.140 |
| 5 | 166.260 |

These values provide an objective regression target for automated verification.

## Planned demos

### Demo 1 — Model interrogation

```text
What elements are connected to this node?
Which elements are PIPE289 vs ELBOW290?
Where are the fixed anchors?
Show every MASS21 element.
```

### Demo 2 — Semantic model diff

Create a controlled revision, for example:

- change one support DOF,
- change one material stiffness,
- relocate one lumped mass,
- modify a pipe section.

Then ask:

```text
Compare baseline and modified models and explain the engineering differences.
```

### Demo 3 — Root-cause investigation

```text
The first frequency changed between Model A and Model B. Why?
```

The agent should compare mass, stiffness, connectivity, and boundary conditions and then run a controlled counterfactual case to test the leading hypothesis.

### Demo 4 — Continuous verification

A GitHub workflow can rerun the benchmark after a model/code change and compare:

- frequencies,
- selected nodal displacements,
- selected rotations,
- element forces / moments,
- reactions.

## Important note

The official PyMAPDL page labels this as a **verification run**. The example is appropriate for regression testing and demonstration; it is not a production design model.
