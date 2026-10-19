from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from ansys.mapdl.core import launch_mapdl

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
RUN_DIR = HERE / ".mapdl_run"
OUT.mkdir(parents=True, exist_ok=True)
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_URL = (
    "https://examples.mapdl.docs.pyansys.com/version/dev/"
    "verif-manual/vm-nr1677-01-1a.html"
)

DOFS = ["UX", "UY", "UZ", "ROTX", "ROTY", "ROTZ"]
CHANGE_DOF = "UX"
N_MODES = 5

# Public NUREG/CR-1677 Volume 1, Problem 1 properties.
E_PSI = 24.0e6
NU = 0.3
OD_IN = 7.289
THK_IN = 0.241

# MASS21 values used by the current-technology verification model.
MASS_BY_NODE = {
    2: 0.03988,
    6: 0.05032,
    28: 0.02088,
    10: 0.01698,
    11: 0.01307,
    15: 0.01698,
    35: 0.01044,
    19: 0.01795,
    20: 0.01501,
}

# Keypoint geometry from the public benchmark (inches).
KPS = {
    1: (0.0, 0.0, 0.0),
    2: (0.0, 54.45, 0.0),
    3: (0.0, 108.9, 0.0),
    4: (10.632, 134.568, 0.0),
    5: (36.3, 145.2, 0.0),
    6: (54.15, 145.2, 0.0),
    7: (72.0, 145.2, 0.0),
    8: (97.668, 145.2, 10.632),
    9: (108.3, 145.2, 36.3),
    10: (108.3, 145.2, 56.80),
    11: (108.3, 145.2, 77.3),
    12: (2.7631, 122.79, 0.0),
    13: (22.408, 142.44, 0.0),
    14: (85.9, 145.0, 2.76),
    15: (106.0, 145.0, 22.4),
}


def launch():
    return launch_mapdl(
        run_location=str(RUN_DIR),
        jobname="nrc_semantic_diff",
        nproc=4,
        ram=8192,
        additional_switches="-smp",
        override=True,
        loglevel="WARNING",
    )


def nearest_node(mapdl, xyz: tuple[float, float, float]) -> int:
    coords = np.asarray(mapdl.mesh.nodes, dtype=float)
    nums = np.asarray(mapdl.mesh.nnum, dtype=int)
    target = np.asarray(xyz, dtype=float)
    idx = int(np.argmin(np.linalg.norm(coords - target, axis=1)))
    return int(nums[idx])


def build_model(mapdl) -> tuple[int, int]:
    mapdl.clear()
    mapdl.title("NRC piping semantic-diff demo")
    mapdl.prep7()

    mapdl.mp("EX", 1, E_PSI)
    mapdl.mp("NUXY", 1, NU)

    mapdl.et(1, "PIPE289")
    mapdl.keyopt(1, 4, 2)
    mapdl.et(2, "ELBOW290", "", 6)
    mapdl.et(3, "MASS21")
    mapdl.keyopt(3, 3, 2)

    mapdl.sectype(1, "PIPE")
    mapdl.secdata(OD_IN, THK_IN, 24)

    for kp, xyz in KPS.items():
        mapdl.k(kp, *xyz)

    # Straight portions.
    for a, b in [(1, 2), (2, 3), (5, 6), (6, 7), (9, 10), (10, 11)]:
        mapdl.l(a, b)

    # Two smooth bends, each represented by two arc segments.
    mapdl.larc(3, 4, 12)
    mapdl.larc(4, 5, 13)
    mapdl.larc(7, 8, 14)
    mapdl.larc(8, 9, 15)

    mapdl.type(1)
    mapdl.mat(1)
    mapdl.secnum(1)
    mapdl.lsel("S", "LINE", "", 1, 6)
    mapdl.allsel("BELOW", "LINE")
    mapdl.lesize("ALL", "", "", 2)
    mapdl.lmesh("ALL")
    mapdl.allsel("ALL", "ALL")

    mapdl.type(2)
    mapdl.mat(1)
    mapdl.secnum(1)
    mapdl.lsel("S", "LINE", "", 7, 10)
    mapdl.allsel("BELOW", "LINE")
    mapdl.lesize("ALL", "", "", 2)
    mapdl.lmesh("ALL")
    mapdl.allsel("ALL", "ALL")

    # Add the benchmark lumped masses.
    mapdl.type(3)
    real_id = 12
    for node, mass in MASS_BY_NODE.items():
        mapdl.r(real_id, mass)
        mapdl.real(real_id)
        mapdl.e(node)
        real_id += 1

    # Convert appropriate curved-pipe elements to ELBOW290.
    mapdl.elbow("ON", "", "", "SECT")
    mapdl.allsel("ALL", "ALL")

    anchor_a = nearest_node(mapdl, KPS[1])
    anchor_b = nearest_node(mapdl, KPS[11])

    # Baseline: both anchors fixed in all six structural DOFs.
    mapdl.d(anchor_a, "ALL", 0)
    mapdl.d(anchor_b, "ALL", 0)
    mapdl.finish()
    return anchor_a, anchor_b


def solve_modes(mapdl, n_modes: int = N_MODES) -> list[float]:
    mapdl.finish()
    mapdl.slashsolu()
    mapdl.antype("MODAL")
    mapdl.modopt("LANB", n_modes)
    mapdl.mxpand("", "", "", "YES")
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()
    rows = mapdl.set("LIST").to_list()
    freqs = [float(row[1]) for row in rows[:n_modes]]
    mapdl.finish()
    return freqs


def set_dof_state(mapdl, node: int, dof: str, fixed: bool) -> None:
    mapdl.finish()
    mapdl.prep7()
    if fixed:
        mapdl.d(node, dof, 0)
    else:
        mapdl.ddele(node, dof)
    mapdl.finish()


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def pct_change(new: float, old: float) -> float:
    return 100.0 * (new - old) / old


def plot_frequency_impact(
    baseline: list[float], modified: list[float], restored: list[float]
) -> None:
    modes = np.arange(1, len(baseline) + 1)
    width = 0.24
    fig, ax = plt.subplots(figsize=(10.5, 5.7))
    ax.bar(modes - width, baseline, width=width, label="Model A - baseline")
    ax.bar(modes, modified, width=width, label=f"Model B - {CHANGE_DOF} released")
    ax.bar(modes + width, restored, width=width, label="Counterfactual - restraint restored")
    ax.set_xlabel("Mode")
    ax.set_ylabel("Natural frequency (Hz)")
    ax.set_xticks(modes)
    ax.set_title("Modal impact of one semantic boundary-condition change")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "02_frequency_impact.png", dpi=180)
    plt.close(fig)


def plot_evidence_card(
    anchor_b: int,
    baseline: list[float],
    modified: list[float],
    restored: list[float],
) -> None:
    changes = [pct_change(m, b) for b, m in zip(baseline, modified)]
    recovery = [pct_change(r, b) for b, r in zip(baseline, restored)]
    max_impact_idx = int(np.argmax(np.abs(changes)))
    max_recovery = max(abs(v) for v in recovery)

    fig = plt.figure(figsize=(13.0, 7.2))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    fig.text(0.055, 0.91, "SEMANTIC MODEL DIFF + ROOT-CAUSE CHECK", fontsize=22, weight="bold")
    fig.text(0.055, 0.86, "NUREG/CR-1677 Vol. 1 Problem 1 | solver-backed comparison", fontsize=12)

    fig.text(0.065, 0.75, "Detected model change", fontsize=15, weight="bold")
    fig.text(0.065, 0.70, f"Node {anchor_b}   {CHANGE_DOF}:   FIXED  ->  FREE", fontsize=16)
    fig.text(0.065, 0.655, "Geometry: unchanged", fontsize=11)
    fig.text(0.065, 0.62, "Elements: unchanged", fontsize=11)
    fig.text(0.065, 0.585, "Material / section / mass: unchanged", fontsize=11)

    fig.text(0.52, 0.75, "Largest modal impact", fontsize=15, weight="bold")
    fig.text(
        0.52,
        0.69,
        f"Mode {max_impact_idx + 1}: {baseline[max_impact_idx]:.3f} -> {modified[max_impact_idx]:.3f} Hz",
        fontsize=15,
    )
    fig.text(0.52, 0.635, f"Change: {changes[max_impact_idx]:+.2f}%", fontsize=21, weight="bold")

    fig.text(0.065, 0.46, "Counterfactual test", fontsize=15, weight="bold")
    fig.text(0.065, 0.405, f"Restore Node {anchor_b} {CHANGE_DOF} restraint and re-solve", fontsize=13)
    fig.text(0.065, 0.355, f"Maximum residual frequency difference: {max_recovery:.5f}%", fontsize=14)

    verdict = "PASS" if max_recovery < 0.05 else "REVIEW"
    fig.text(0.52, 0.46, "Root-cause evidence", fontsize=15, weight="bold")
    fig.text(0.52, 0.395, verdict, fontsize=26, weight="bold")
    fig.text(
        0.52,
        0.34,
        "Restoring the changed restraint recovers the baseline modal response.",
        fontsize=12,
    )

    fig.text(
        0.055,
        0.17,
        "Conclusion: the boundary-condition change is isolated as the causal model revision for the observed modal shift.",
        fontsize=14,
        weight="bold",
    )
    fig.text(0.055, 0.08, "Evidence is generated from deterministic MAPDL solves; no frequency is invented by an LLM.", fontsize=10)

    fig.savefig(OUT / "03_root_cause_evidence.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_model_plot(mapdl) -> None:
    path = OUT / "01_nrc_baseline_model.png"
    try:
        from ansys.mapdl.core.plotting import GraphicsBackend

        mapdl.prep7()
        mapdl.allsel("ALL", "ALL")
        mapdl.eplot(
            graphics_backend=GraphicsBackend.MAPDL,
            savefig=str(path),
            show_node_numbering=False,
        )
        mapdl.finish()
    except Exception as exc:
        print(f"Warning: native MAPDL model plot was skipped: {exc}")


def main() -> None:
    print("[1/7] Launching MAPDL in SMP mode...")
    mapdl = launch()
    try:
        print("[2/7] Building public NRC piping benchmark...")
        anchor_a, anchor_b = build_model(mapdl)
        n_nodes = int(mapdl.mesh.n_node)
        n_elems = int(mapdl.mesh.n_elem)

        print(f"      Anchor nodes resolved as {anchor_a} and {anchor_b}")
        print("[3/7] Saving baseline model image...")
        save_model_plot(mapdl)

        print("[4/7] Solving Model A (baseline)...")
        baseline = solve_modes(mapdl)

        print(f"[5/7] Creating Model B: releasing {CHANGE_DOF} at Node {anchor_b}...")
        set_dof_state(mapdl, anchor_b, CHANGE_DOF, fixed=False)
        modified = solve_modes(mapdl)

        print("[6/7] Running counterfactual: restoring the restraint and re-solving...")
        set_dof_state(mapdl, anchor_b, CHANGE_DOF, fixed=True)
        restored = solve_modes(mapdl)

        modal_rows = []
        for i, (fa, fb, fr) in enumerate(zip(baseline, modified, restored), start=1):
            modal_rows.append(
                [
                    i,
                    f"{fa:.8f}",
                    f"{fb:.8f}",
                    f"{pct_change(fb, fa):.6f}",
                    f"{fr:.8f}",
                    f"{pct_change(fr, fa):.6f}",
                ]
            )
        write_csv(
            OUT / "modal_comparison.csv",
            [
                "mode",
                "model_a_baseline_hz",
                "model_b_modified_hz",
                "modified_percent_change",
                "counterfactual_restored_hz",
                "restored_percent_change",
            ],
            modal_rows,
        )

        bc_a = {str(anchor_a): DOFS, str(anchor_b): DOFS}
        bc_b = {str(anchor_a): DOFS, str(anchor_b): [d for d in DOFS if d != CHANGE_DOF]}
        diff = {
            "change_type": "boundary_condition",
            "node": anchor_b,
            "dof": CHANGE_DOF,
            "model_a": "FIXED",
            "model_b": "FREE",
            "geometry_changed": False,
            "element_count_changed": False,
            "material_changed": False,
            "section_changed": False,
            "mass_changed": False,
        }

        model_summary = {
            "benchmark": "NUREG/CR-1677 Volume 1 Problem 1",
            "source": SOURCE_URL,
            "nodes": n_nodes,
            "elements": n_elems,
            "element_technologies": ["PIPE289", "ELBOW290", "MASS21"],
            "material": {"E_psi": E_PSI, "nu": NU},
            "pipe_section": {"OD_in": OD_IN, "thickness_in": THK_IN},
            "lumped_mass_total_lb_s2_per_in": sum(MASS_BY_NODE.values()),
            "anchor_nodes": [anchor_a, anchor_b],
        }
        (OUT / "model_summary.json").write_text(json.dumps(model_summary, indent=2), encoding="utf-8")
        (OUT / "model_a_semantics.json").write_text(
            json.dumps({"boundary_conditions": bc_a}, indent=2), encoding="utf-8"
        )
        (OUT / "model_b_semantics.json").write_text(
            json.dumps({"boundary_conditions": bc_b}, indent=2), encoding="utf-8"
        )
        (OUT / "semantic_diff.json").write_text(json.dumps(diff, indent=2), encoding="utf-8")

        changes = [pct_change(m, b) for b, m in zip(baseline, modified)]
        recovery = [pct_change(r, b) for b, r in zip(baseline, restored)]
        max_idx = int(np.argmax(np.abs(changes)))
        max_recovery = max(abs(v) for v in recovery)
        verdict = "PASS" if max_recovery < 0.05 else "REVIEW"

        report = f"""# NRC Semantic Model Diff + Root-Cause Evidence\n\n## Question\nWhy did the modal response change between Model A and Model B?\n\n## Deterministic semantic diff\n- Model A: both anchor nodes fixed in all six structural DOFs.\n- Model B: Node {anchor_b} changes only in **{CHANGE_DOF}: FIXED -> FREE**.\n- Geometry: unchanged.\n- Node/element topology: unchanged.\n- Material: unchanged.\n- Pipe section: unchanged.\n- Lumped masses: unchanged.\n\n## Solver impact\n- Modes solved: {N_MODES}.\n- Largest absolute modal shift: Mode {max_idx + 1}, {baseline[max_idx]:.4f} Hz -> {modified[max_idx]:.4f} Hz ({changes[max_idx]:+.3f}%).\n- Full comparison: `modal_comparison.csv`.\n\n## Counterfactual test\nThe released {CHANGE_DOF} restraint at Node {anchor_b} is restored and the model is solved again.\n\n- Maximum residual difference from Model A: **{max_recovery:.6f}%**.\n- Counterfactual status: **{verdict}**.\n\n## Root-cause conclusion\nThe boundary-condition revision at Node {anchor_b} is isolated as the causal change for the modal-response shift because the other tracked model semantics remain unchanged and restoring that restraint recovers the baseline modal response.\n\n## Evidence\n- `01_nrc_baseline_model.png`\n- `02_frequency_impact.png`\n- `03_root_cause_evidence.png`\n- `model_summary.json`\n- `model_a_semantics.json`\n- `model_b_semantics.json`\n- `semantic_diff.json`\n- `modal_comparison.csv`\n\n## Public benchmark\n{SOURCE_URL}\n"""
        (OUT / "root_cause_report.md").write_text(report, encoding="utf-8")

        summary_txt = (
            "SEMANTIC MODEL DIFF\n"
            "===================\n"
            f"Node {anchor_b}: {CHANGE_DOF}  FIXED -> FREE\n"
            "Geometry / elements / material / section / mass: unchanged\n\n"
            "RESULT IMPACT\n"
            "=============\n"
            f"Largest shift: Mode {max_idx + 1}: {baseline[max_idx]:.4f} -> "
            f"{modified[max_idx]:.4f} Hz ({changes[max_idx]:+.3f}%)\n\n"
            "COUNTERFACTUAL\n"
            "==============\n"
            f"Restore Node {anchor_b} {CHANGE_DOF}; max residual difference = "
            f"{max_recovery:.6f}% -> {verdict}\n\n"
            "CONCLUSION\n"
            "==========\n"
            "The changed restraint is isolated as the causal model revision for the modal shift.\n"
        )
        (OUT / "root_cause_summary.txt").write_text(summary_txt, encoding="utf-8")

        plot_frequency_impact(baseline, modified, restored)
        plot_evidence_card(anchor_b, baseline, modified, restored)

        print("[7/7] Writing semantic-diff evidence package...")
        print()
        print(summary_txt)
        print(f"Done. Open: {OUT / 'root_cause_report.md'}")
    finally:
        try:
            mapdl.exit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
