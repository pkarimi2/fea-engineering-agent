# Advanced PCB Demo - Evidence Report

## Model

- Public source: PyMAPDL Technology Showcase 20
- Source file: `pcb_mesh_file.cdb`
- SHA-256: `aca96794b31d823b8504a30917564afbb93b92b32998066edbc458b3c4ddc0dc`
- Single-board mesh: 14,699 nodes / 8,682 elements
- 3-layer assembly: 43,897 nodes / 26,046 elements
- Element technologies detected: BEAM188, CONTA174, SHELL181, SOLID186, TARGE170

## Interrogation

- Model size: 43,897 nodes; 26,046 elements.
- Element technologies found: BEAM188, CONTA174, SHELL181, SOLID186, TARGE170.
- Base-excitation component N_BASE_EXCITE: 5 nodes.
- Monitor component MY_MONITOR: 1 node(s).
- Joint-board component N_JOINT_BOARD: 5 nodes.
- Joint-legs component N_JOINT_LEGS: 5 nodes.

## Modal verification

- Modes solved: 10
- Maximum absolute difference from published reference: 2.1296%
- Detailed comparison: `modal_check.csv`

## Evidence package

- `01_complex_pcb_model.png`
- `model_summary.json`
- `element_type_listing.txt`
- `query_results.json`
- `query_summary.txt`
- `modal_check.csv`

## Source

https://examples.mapdl.docs.pyansys.com/technology_showcase_examples/techdemo-20/ex_20-tecPCB.html
