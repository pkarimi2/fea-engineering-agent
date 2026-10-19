# Demo 1 - Advanced PCB Assembly

This demo uses the public **PyMAPDL Technology Showcase 20** printed-circuit-board model to test the engineering-agent workflow at a much higher level of model complexity than Demo 0.

The source model contains solids, shells, beams, and bonded/flexible contact definitions. The script imports the official public CDB, constructs the documented three-layer PCB assembly, creates the base-excitation support set, performs model-interrogation queries, solves the first 10 modes, and compares the frequencies against the published PyMAPDL example values.

## Why this demo exists

Demo 0 proves the full workflow on a compact NRC piping benchmark. Demo 1 asks whether the same workflow still works on a much larger mixed-element model with tens of thousands of nodes/elements and multiple element technologies.

## Run

From the repository root, with the virtual environment active:

```bat
python examples\pcb_advanced\run_demo.py
```

The first run downloads the public `pcb_mesh_file.cdb` through the PyMAPDL examples data helper.

## Expected outputs

```text
examples/pcb_advanced/outputs/
  01_complex_pcb_model.png
  demo_report.md
  element_type_listing.txt
  modal_check.csv
  model_summary.json
  query_results.json
  query_summary.txt
```

## Public source

PyMAPDL Technology Showcase 20 - Dynamic simulation of a printed circuit board assembly:

https://examples.mapdl.docs.pyansys.com/technology_showcase_examples/techdemo-20/ex_20-tecPCB.html
