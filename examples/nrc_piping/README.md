# NRC Piping Benchmark Demo

This is the first **real solver-backed demonstration** for the FEA Engineering Agent project.

It uses the public Ansys/PyMAPDL implementation of the NRC piping benchmark from **NUREG/CR-1677, Volume 1, Problem 1** as the engineering reference.  The model contains straight pipe, elbows, lumped masses, fixed anchors, modal analysis, and published reference frequencies.

Official benchmark page:
https://examples.mapdl.docs.pyansys.com/version/dev/verif-manual/vm-nr1677-01-1a.html

## What the demo does

`run_demo.py`:

1. launches a local MAPDL session through PyMAPDL,
2. rebuilds the public piping benchmark,
3. saves a baseline database,
4. solves the first five modes,
5. compares them with the published reference frequencies,
6. asks deterministic model-interrogation questions,
7. saves actual MAPDL/PyMAPDL screenshots and JSON/CSV evidence,
8. writes a GitHub-friendly report at `outputs/demo_report.md`.

The initial questions are deliberately simple:

```text
What elements are connected to node 2?
Which elements use material 1?
Show restraints at node 1.
```

The important point is that the answers come from MAPDL selections/listings, not from an LLM guessing the model state.

## Requirements

- Windows machine with a supported local Ansys MAPDL installation/license
- Python 3.10+ recommended
- For the database/query workflow, a modern MAPDL release is recommended; the public PyMAPDL database API supports MAPDL 2021 R1 and later (with a documented exception for 2023 R1).

This repository is being developed against a modern MAPDL installation; **Ansys 2025 R1 is an appropriate target for this demo**.

## Setup on Windows

From the repository root:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PyMAPDL finds your Ansys installation automatically, run:

```bat
python examples\nrc_piping\run_demo.py
```

If MAPDL is not auto-detected, set its executable first.  Example for a typical 2025 R1 install:

```bat
set ANSYS_MAPDL_EXECUTABLE=C:\Program Files\ANSYS Inc\v251\ansys\bin\winx64\ANSYS251.exe
python examples\nrc_piping\run_demo.py
```

Adjust the path if your Ansys installation is elsewhere.

## Expected reference frequencies

The official verification example reports approximately:

| Mode | Reference frequency (Hz) |
|---:|---:|
| 1 | 28.515 |
| 2 | 56.441 |
| 3 | 82.947 |
| 4 | 144.140 |
| 5 | 166.260 |

Your generated `outputs/modal_check.csv` records the computed values and percent differences.

## Ask the model from the command line

The first natural-language front end is intentionally deterministic rather than LLM-based.  It proves the solver-query layer first.

```bat
cd examples\nrc_piping
python ask_model.py What elements are connected to node 2?
python ask_model.py Which elements use material 1?
python ask_model.py Show restraints at node 1.
```

Later, the MCP/LLM layer will call the same query functions as tools.

## Generated evidence

After a successful run, the `outputs/` folder contains:

```text
01_model_with_bcs.png
02_node_2_connected_elements.png
03_material_1_elements.png
model_summary.json
modal_check.csv
query_results.json
demo_report.md
```

Those are the files to use for the first presentation screenshots and the GitHub README.

## Presentation story

This demo supports a simple claim:

> **The LLM does not invent the finite-element answer. It decides what to ask; MAPDL provides the model fact; the evidence is preserved.**
