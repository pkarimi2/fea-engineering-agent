# Legacy ANSYS Technology Migration - Evidence Report

## Objective
Demonstrate a controlled migration of the public NUREG/CR-1677 Volume 1, Problem 1 piping benchmark from archived ANSYS pipe technology to current-technology elements, then verify that the engineering behavior remains acceptably close under a defined demo criterion.

## Legacy model audit
- Elements: **PIPE16, PIPE18, MASS21**.
- PIPE16 and PIPE18 are archived element technologies in current Mechanical APDL documentation.
- Nodes: **11**.
- Elements: **19**.
- Lumped mass total: **0.20151 lb-sec^2/in**.
- Anchors: end nodes fixed in all structural DOFs.

## Migration plan
- Straight pipe: legacy PIPE16 -> current PIPE289 for this demo, matching the official current-technology NRC benchmark.
- Curved pipe: legacy PIPE18 -> ELBOW290.
- MASS21 retained.
- Material, wall thickness, lumped mass, and support intent preserved.
- Mesh refinement near bends is intentional; identical node/element counts are **not** required.

## Equivalence check
- First 5 modes compared.
- Maximum absolute frequency difference: **2.117%**.
- Demo acceptance criterion: **3.0%**.
- Status: **PASS**.

Detailed results: `migration_modal_comparison.csv`.

## Important engineering interpretation
This is not a byte-for-byte or element-count conversion. The purpose of modernization is to preserve the physical model intent while moving from archived element technology to current technology. Because the element formulation and mesh are intentionally different, verification focuses on semantic invariants and solver response.

## Outputs
- `01_legacy_model.png`
- `02_modern_model.png`
- `03_modal_equivalence.png`
- `04_migration_evidence.png`
- `legacy_inventory.json`
- `migration_plan.json`
- `modern_inventory.json`
- `migration_modal_comparison.csv`
- `equivalence_check.json`
- `legacy_technology_model.db`
- `modernized_model.db`

## Public references
- NUREG/CR-1677 Volume 1, Problem 1.
- Ansys Mechanical APDL Verification Manual legacy formulation: PIPE16 / PIPE18 / MASS21.
- Ansys Mechanical APDL Verification Manual current-technology formulation: PIPE289 / ELBOW290 / MASS21.
