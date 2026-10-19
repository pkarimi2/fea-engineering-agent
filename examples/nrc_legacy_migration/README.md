# NRC Legacy ANSYS -> Current-Technology Migration Demo

This demo is designed for the presentation story:

> **Do not just convert the file. Demonstrate that the engineering behavior is preserved.**

It uses the public NUREG/CR-1677 Volume 1, Problem 1 piping benchmark in two implementations:

- **Legacy technology:** PIPE16 + PIPE18 + MASS21
- **Current technology:** PIPE289 + ELBOW290 + MASS21

Current Mechanical APDL documentation classifies PIPE16 and PIPE18 as archived technologies. The current NRC benchmark uses PIPE289 and ELBOW290.

## Main run - MAPDL 2025

From the repository root with the existing virtual environment activated:

```bat
python examples\nrc_legacy_migration\run_demo.py
```

The workflow:

1. Builds and solves the legacy element formulation.
2. Detects archived element technologies.
3. Writes a deterministic migration plan.
4. Builds the current-technology counterpart.
5. Re-solves the model.
6. Checks preserved model semantics and modal equivalence.
7. Produces presentation-ready evidence.

## Presentation-ready outputs

The `outputs` folder will contain:

- `01_legacy_model.png`
- `02_modern_model.png`
- `03_modal_equivalence.png`
- `04_migration_evidence.png`
- `legacy_inventory.json`
- `migration_plan.json`
- `modern_inventory.json`
- `migration_modal_comparison.csv`
- `equivalence_check.json`
- `migration_summary.txt`
- `migration_report.md`
- `legacy_technology_model.db`
- `modernized_model.db`

## Optional - create a real ANSYS 11 DB and resume it in 2025

To make the provenance demonstration literal rather than only element-technology based:

1. Open **ANSYS 11 / Mechanical APDL 11**.
2. Read `legacy_ansys11.inp` as an input file.
3. It creates `legacy_ansys11.db` and solves the first five modes.
4. Copy `legacy_ansys11.db` into this demo folder if ANSYS wrote it elsewhere.
5. In the current Python environment run:

```bat
python examples\nrc_legacy_migration\resume_ansys11_db.py
```

That creates evidence showing that the actual ANSYS 11 database was resumed and re-solved in MAPDL 2025.

## Engineering interpretation

This is **not** a requirement for identical node or element counts. The current technology intentionally changes element formulation and mesh density. The verification target is the preserved engineering intent:

- material properties
- pipe dimensions
- support/anchor semantics
- lumped mass
- modal behavior within a defined demo tolerance

For complex production models, the same concept should be extended to mass by direction, reactions, displacements, selected element forces, mode-shape MAC, and other project-specific acceptance criteria.

## Public references

- Ansys Mechanical APDL Verification Manual, NUREG/CR-1677 Volume 1 Problem 1, legacy formulation using PIPE16 / PIPE18 / MASS21.
- Ansys Mechanical APDL Verification Manual, current-technology formulation using PIPE289 / ELBOW290 / MASS21.
- Ansys Feature Archive: PIPE16 is archived; current documentation recommends current-technology pipe elements. PIPE18 is archived; current documentation recommends ELBOW290.
