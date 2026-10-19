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

N_MODES = 5
E_PSI = 24.0e6
NU = 0.3
OD_IN = 7.289
THK_IN = 0.241

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

CHALLENGES = [
    {
        "id": "E_MINUS_20",
        "label": "Elastic modulus -20%",
        "category": "material",
        "e_scale": 0.80,
    },
    {
        "id": "E_PLUS_20",
        "label": "Elastic modulus +20%",
        "category": "material",
        "e_scale": 1.20,
    },
    {
        "id": "THK_MINUS_10",
        "label": "Wall thickness -10%",
        "category": "section",
        "thk_scale": 0.90,
    },
    {
        "id": "THK_PLUS_10",
        "label": "Wall thickness +10%",
        "category": "section",
        "thk_scale": 1.10,
    },
    {
        "id": "MASS_MINUS_20",
        "label": "Lumped masses -20%",
        "category": "mass",
        "mass_scale": 0.80,
    },
    {
        "id": "MASS_PLUS_20",
        "label": "Lumped masses +20%",
        "category": "mass",
        "mass_scale": 1.20,
    },
    {
        "id": "ANCHOR_UX_RELEASE",
        "label": "Anchor UX released",
        "category": "boundary condition",
        "release_anchor_ux": True,
    },
]


def launch():
    return launch_mapdl(
        run_location=str(RUN_DIR),
        jobname="nrc_red_team",
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


def build_model(
    mapdl,
    *,
    e_scale: float = 1.0,
    thk_scale: float = 1.0,
    mass_scale: float = 1.0,
    release_anchor_ux: bool = False,
) -> tuple[int, int]:
    mapdl.clear()
    mapdl.title("NRC piping AI-red-team robustness demo")
    mapdl.prep7()

    mapdl.mp("EX", 1, E_PSI * e_scale)
    mapdl.mp("NUXY", 1, NU)

    mapdl.et(1, "PIPE289")
    mapdl.keyopt(1, 4, 2)
    mapdl.et(2, "ELBOW290", "", 6)
    mapdl.et(3, "MASS21")
    mapdl.keyopt(3, 3, 2)

    mapdl.sectype(1, "PIPE")
    mapdl.secdata(OD_IN, THK_IN * thk_scale, 24)

    for kp, xyz in KPS.items():
        mapdl.k(kp, *xyz)

    for a, b in [(1, 2), (2, 3), (5, 6), (6, 7), (9, 10), (10, 11)]:
        mapdl.l(a, b)

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

    mapdl.type(3)
    real_id = 12
    for node, mass in MASS_BY_NODE.items():
        mapdl.r(real_id, mass * mass_scale)
        mapdl.real(real_id)
        mapdl.e(node)
        real_id += 1

    mapdl.elbow("ON", "", "", "SECT")
    mapdl.allsel("ALL", "ALL")

    anchor_a = nearest_node(mapdl, KPS[1])
    anchor_b = nearest_node(mapdl, KPS[11])

    mapdl.d(anchor_a, "ALL", 0)
    mapdl.d(anchor_b, "ALL", 0)
    if release_anchor_ux:
        mapdl.ddele(anchor_b, "UX")

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


def pct_change(new: float, old: float) -> float:
    return 100.0 * (new - old) / old


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def save_model_plot(mapdl) -> None:
    path = OUT / "01_baseline_model.png"
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


def plot_heatmap(labels: list[str], matrix: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.3))
    im = ax.imshow(matrix, aspect="auto")
    ax.set_xticks(np.arange(N_MODES))
    ax.set_xticklabels([f"Mode {i}" for i in range(1, N_MODES + 1)])
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Modal response")
    ax.set_title("Red-team robustness map: frequency change from baseline (%)")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Frequency change (%)")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:+.1f}", ha="center", va="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "02_robustness_heatmap.png", dpi=180)
    plt.close(fig)


def plot_ranking(labels: list[str], max_impacts: list[float]) -> None:
    order = np.argsort(max_impacts)
    labels_sorted = [labels[i] for i in order]
    impacts_sorted = [max_impacts[i] for i in order]

    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    y = np.arange(len(labels_sorted))
    ax.barh(y, impacts_sorted)
    ax.set_yticks(y)
    ax.set_yticklabels(labels_sorted)
    ax.set_xlabel("Maximum absolute modal-frequency shift (%)")
    ax.set_title("Which challenged assumption matters most?")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "03_sensitivity_ranking.png", dpi=180)
    plt.close(fig)


def plot_evidence_card(
    baseline: list[float],
    ranked_rows: list[dict[str, object]],
    anchor_b: int,
) -> None:
    top = ranked_rows[0]
    runner = ranked_rows[1]

    fig = plt.figure(figsize=(13.0, 7.2))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    fig.text(0.055, 0.91, "AI RED TEAM FOR FEA — ROBUSTNESS CHALLENGE", fontsize=22, weight="bold")
    fig.text(0.055, 0.86, "Question: Which modeling assumption can most strongly change the predicted dynamics?", fontsize=12)

    fig.text(0.065, 0.74, "Baseline", fontsize=15, weight="bold")
    fig.text(0.065, 0.69, f"Modes 1–5: {', '.join(f'{v:.2f}' for v in baseline)} Hz", fontsize=12)
    fig.text(0.065, 0.645, "Public NRC piping benchmark | deterministic MAPDL solves", fontsize=11)

    fig.text(0.52, 0.74, "Top challenged assumption", fontsize=15, weight="bold")
    fig.text(0.52, 0.685, str(top["label"]), fontsize=17, weight="bold")
    fig.text(0.52, 0.625, f"Maximum modal shift: {float(top['max_abs_change']):.2f}%", fontsize=20, weight="bold")

    fig.text(0.065, 0.49, "Challenge set", fontsize=15, weight="bold")
    fig.text(0.065, 0.44, "Material stiffness ±20%", fontsize=12)
    fig.text(0.065, 0.40, "Pipe wall thickness ±10%", fontsize=12)
    fig.text(0.065, 0.36, "Lumped mass ±20%", fontsize=12)
    fig.text(0.065, 0.32, f"Boundary condition: release UX at anchor Node {anchor_b}", fontsize=12)

    fig.text(0.52, 0.49, "Next most influential", fontsize=15, weight="bold")
    fig.text(0.52, 0.435, str(runner["label"]), fontsize=14, weight="bold")
    fig.text(0.52, 0.385, f"Maximum modal shift: {float(runner['max_abs_change']):.2f}%", fontsize=16)

    fig.text(
        0.055,
        0.18,
        "Engineering use: rank assumptions by solver-observed consequence before spending review effort everywhere equally.",
        fontsize=14,
        weight="bold",
    )
    fig.text(
        0.055,
        0.085,
        "This demo uses a deterministic challenge library. An LLM can later propose and prioritize additional tests; MAPDL still generates the numbers.",
        fontsize=10,
    )

    fig.savefig(OUT / "04_red_team_evidence.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    print("[1/7] Launching MAPDL 2025 in SMP mode...")
    mapdl = launch()
    try:
        print("[2/7] Building and solving baseline NRC model...")
        anchor_a, anchor_b = build_model(mapdl)
        baseline = solve_modes(mapdl)
        n_nodes = int(mapdl.mesh.n_node)
        n_elems = int(mapdl.mesh.n_elem)
        save_model_plot(mapdl)

        print("[3/7] Running red-team challenge library...")
        results = []
        matrix = []

        for i, challenge in enumerate(CHALLENGES, start=1):
            print(f"      [{i}/{len(CHALLENGES)}] {challenge['label']}")
            build_model(
                mapdl,
                e_scale=float(challenge.get("e_scale", 1.0)),
                thk_scale=float(challenge.get("thk_scale", 1.0)),
                mass_scale=float(challenge.get("mass_scale", 1.0)),
                release_anchor_ux=bool(challenge.get("release_anchor_ux", False)),
            )
            freqs = solve_modes(mapdl)
            changes = [pct_change(f, b) for b, f in zip(baseline, freqs)]
            matrix.append(changes)
            max_idx = int(np.argmax(np.abs(changes)))
            results.append(
                {
                    "id": challenge["id"],
                    "label": challenge["label"],
                    "category": challenge["category"],
                    "frequencies_hz": freqs,
                    "percent_changes": changes,
                    "max_abs_change": float(abs(changes[max_idx])),
                    "controlling_mode": max_idx + 1,
                }
            )

        print("[4/7] Ranking challenged assumptions...")
        ranked = sorted(results, key=lambda x: float(x["max_abs_change"]), reverse=True)

        challenge_rows = []
        for r in results:
            row = [r["id"], r["label"], r["category"]]
            row += [f"{v:.8f}" for v in r["frequencies_hz"]]
            row += [f"{v:.6f}" for v in r["percent_changes"]]
            row += [r["controlling_mode"], f"{float(r['max_abs_change']):.6f}"]
            challenge_rows.append(row)

        headers = ["challenge_id", "challenge", "category"]
        headers += [f"mode_{i}_hz" for i in range(1, N_MODES + 1)]
        headers += [f"mode_{i}_percent_change" for i in range(1, N_MODES + 1)]
        headers += ["controlling_mode", "max_abs_percent_change"]
        write_csv(OUT / "challenge_results.csv", headers, challenge_rows)

        ranked_rows_csv = [
            [i, r["id"], r["label"], r["category"], r["controlling_mode"], f"{float(r['max_abs_change']):.6f}"]
            for i, r in enumerate(ranked, start=1)
        ]
        write_csv(
            OUT / "ranked_assumptions.csv",
            ["rank", "challenge_id", "challenge", "category", "controlling_mode", "max_abs_percent_change"],
            ranked_rows_csv,
        )

        print("[5/7] Generating robustness visuals...")
        labels = [str(r["label"]) for r in results]
        matrix_np = np.asarray(matrix, dtype=float)
        plot_heatmap(labels, matrix_np)
        plot_ranking(labels, [float(r["max_abs_change"]) for r in results])
        plot_evidence_card(baseline, ranked, anchor_b)

        print("[6/7] Writing machine-readable evidence...")
        baseline_summary = {
            "benchmark": "NUREG/CR-1677 Volume 1 Problem 1",
            "source": SOURCE_URL,
            "nodes": n_nodes,
            "elements": n_elems,
            "anchor_nodes": [anchor_a, anchor_b],
            "baseline_modes_hz": baseline,
            "element_technologies": ["PIPE289", "ELBOW290", "MASS21"],
        }
        (OUT / "baseline_summary.json").write_text(json.dumps(baseline_summary, indent=2), encoding="utf-8")
        (OUT / "challenge_definitions.json").write_text(json.dumps(CHALLENGES, indent=2), encoding="utf-8")
        (OUT / "red_team_results.json").write_text(json.dumps({"results": results, "ranking": ranked}, indent=2), encoding="utf-8")

        top = ranked[0]
        runner = ranked[1]
        summary = (
            "AI RED TEAM / ROBUSTNESS CHALLENGE\n"
            "==================================\n"
            f"Baseline modes (Hz): {', '.join(f'{v:.4f}' for v in baseline)}\n"
            f"Challenges executed: {len(CHALLENGES)}\n\n"
            "MOST INFLUENTIAL CHALLENGE\n"
            "==========================\n"
            f"{top['label']}\n"
            f"Controlling mode: {top['controlling_mode']}\n"
            f"Maximum absolute modal shift: {float(top['max_abs_change']):.3f}%\n\n"
            "SECOND MOST INFLUENTIAL\n"
            "=======================\n"
            f"{runner['label']}\n"
            f"Controlling mode: {runner['controlling_mode']}\n"
            f"Maximum absolute modal shift: {float(runner['max_abs_change']):.3f}%\n\n"
            "ENGINEERING CONCLUSION\n"
            "======================\n"
            "The challenge library ranks modeling assumptions by solver-observed consequence.\n"
            "This is deterministic sensitivity evidence; it does not rely on an LLM to invent results.\n"
        )
        (OUT / "red_team_summary.txt").write_text(summary, encoding="utf-8")

        ranking_md = "\n".join(
            f"{i}. **{r['label']}** — max |Δf| = {float(r['max_abs_change']):.3f}% (Mode {r['controlling_mode']})"
            for i, r in enumerate(ranked, start=1)
        )
        report = f"""# AI Red Team for FEA — Robustness Evidence\n\n## Question\nTry to prove the model is fragile: which challenged modeling assumption most strongly changes the first {N_MODES} modal frequencies?\n\n## Baseline\n- Public benchmark: NUREG/CR-1677 Volume 1 Problem 1\n- Nodes: {n_nodes}\n- Elements: {n_elems}\n- Baseline modes: {', '.join(f'{v:.4f}' for v in baseline)} Hz\n\n## Deterministic challenge library\n- Elastic modulus: -20%, +20%\n- Pipe wall thickness: -10%, +10%\n- Lumped masses: -20%, +20%\n- Boundary condition: release UX at the second anchor (Node {anchor_b})\n\n## Ranking\n{ranking_md}\n\n## Interpretation\nThis demonstration does not ask an LLM to calculate structural response. Each challenge rebuilds the FE model, MAPDL solves it, and the harness ranks the resulting changes. A future LLM layer can propose additional engineering hypotheses and decide which challenge to run next, while the solver remains authoritative.\n\n## Evidence\n- `01_baseline_model.png`\n- `02_robustness_heatmap.png`\n- `03_sensitivity_ranking.png`\n- `04_red_team_evidence.png`\n- `challenge_results.csv`\n- `ranked_assumptions.csv`\n- `baseline_summary.json`\n- `challenge_definitions.json`\n- `red_team_results.json`\n\n## Public benchmark\n{SOURCE_URL}\n"""
        (OUT / "red_team_report.md").write_text(report, encoding="utf-8")

        print("[7/7] Red-team evidence package complete.")
        print()
        print(summary)
        print(f"Done. Open: {OUT / 'red_team_report.md'}")
    finally:
        try:
            mapdl.exit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
