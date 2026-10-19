from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from pathlib import Path

from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.examples.downloads import download_tech_demo_data

from reference import REFERENCE_FREQUENCIES_HZ, OFFICIAL_EXAMPLE_URL

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
RUN_DIR = HERE / ".mapdl_run"
OUT.mkdir(exist_ok=True)
RUN_DIR.mkdir(exist_ok=True)


def launch():
    kwargs = dict(
        run_location=str(RUN_DIR),
        jobname="pcb_demo",
        override=True,
        start_timeout=120,
        # Use shared-memory parallelism for this Windows demo.  This avoids
        # MPI/DMP communication failures that can terminate MAPDL during the
        # Block Lanczos solve on some local installations.
        additional_switches="-smp",
        nproc=4,
        # Give MAPDL an explicit workspace larger than the launcher default.
        ram=8192,
        mapdl_output=str(RUN_DIR / "pcb_demo_console.out"),
    )
    exe = os.environ.get("ANSYS_MAPDL_EXECUTABLE")
    if exe:
        kwargs["exec_file"] = exe
    return launch_mapdl(**kwargs)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_component_nodes(mapdl, component: str) -> int | None:
    try:
        mapdl.allsel()
        mapdl.cmsel("S", component)
        return int(mapdl.mesh.n_node)
    except Exception:
        return None
    finally:
        mapdl.allsel()


def extract_element_types(etlist_text: str) -> list[str]:
    names = []
    for line in etlist_text.splitlines():
        m = re.search(r"\b(?:BEAM|SOLID|SHELL|CONTA|TARGE|MASS|COMBIN|PIPE|ELBOW)\d+\b", line.upper())
        if m:
            names.append(m.group(0))
    return sorted(set(names))


def save_model_plot(mapdl, path: Path):
    # Keep the plot deliberately simple. The earlier benchmark demonstrated that
    # adding BC legends can trigger a PyVista/VTK crash on some Windows installs.
    mapdl.allsel()
    mapdl.eplot(
        background="white",
        show_edges=True,
        savefig=str(path),
    )


def get_modal_frequencies(mapdl, n_modes: int) -> list[float]:
    values = []
    mapdl.post1()
    for i in range(1, n_modes + 1):
        mapdl.set(1, i)
        val = float(mapdl.get("freq_tmp", "ACTIVE", 0, "SET", "FREQ"))
        values.append(val)
    return values


def main():
    print("[1/6] Launching MAPDL in SMP mode and downloading official PCB model...")
    mapdl = launch()
    try:
        cdb = Path(download_tech_demo_data("td-20", "pcb_mesh_file.cdb"))
        source_meta = {
            "source_file": cdb.name,
            "sha256": sha256_file(cdb),
            "official_example": OFFICIAL_EXAMPLE_URL,
        }

        print("[2/6] Importing single PCB and building 3-layer assembly...")
        mapdl.clear()
        mapdl.prep7()
        mapdl.cdread("COMB", str(cdb))
        mapdl.allsel()

        single_nodes = int(mapdl.mesh.n_node)
        single_elements = int(mapdl.mesh.n_elem)
        max_nodenum = int(mapdl.get("max_nodenum", "NODE", "", "NUM", "MAX"))

        # Official PyMAPDL Technology Showcase construction of a 3-layer PCB.
        mapdl.egen(3, max_nodenum, "ALL", dy=-20)

        mapdl.cmsel("S", "N_JOINT_BOARD")
        mapdl.cmsel("A", "N_JOINT_LEGS")
        mapdl.cmsel("A", "N_BASE")
        nb_selected_nodes = int(mapdl.mesh.n_node)

        current_node = 0
        q = mapdl.queries
        for _ in range(nb_selected_nodes):
            current_node = int(q.ndnext(current_node))
            if current_node <= 0:
                break
            mapdl.nsel("A", "NODE", "", current_node + max_nodenum)
            mapdl.nsel("A", "NODE", "", current_node + 2 * max_nodenum)

        mapdl.cpintf("ALL")
        cp_max = int(mapdl.get("cp_max", "CP", 0, "MAX"))
        if cp_max > 0:
            mapdl.nsel("U", "CP", "", 1, cp_max)
        mapdl.cm("N_BASE_EXCITE", "NODE")
        mapdl.d("ALL", "ALL")
        mapdl.allsel()
        mapdl.save("pcb_advanced_baseline")

        model_nodes = int(mapdl.mesh.n_node)
        model_elements = int(mapdl.mesh.n_elem)

        et_text = str(mapdl.etlist())
        (OUT / "element_type_listing.txt").write_text(et_text, encoding="utf-8", errors="ignore")
        element_types = extract_element_types(et_text)

        components = {}
        for comp in ["N_JOINT_BOARD", "N_JOINT_LEGS", "N_BASE", "N_BASE_EXCITE", "MY_MONITOR"]:
            components[comp] = count_component_nodes(mapdl, comp)

        summary = {
            "benchmark": "PyMAPDL Technology Showcase 20 - 3-layer PCB assembly",
            "single_board_nodes": single_nodes,
            "single_board_elements": single_elements,
            "assembled_nodes": model_nodes,
            "assembled_elements": model_elements,
            "element_types": element_types,
            "component_node_counts": components,
            **source_meta,
        }
        (OUT / "model_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

        print("[3/6] Saving complex-model image...")
        save_model_plot(mapdl, OUT / "01_complex_pcb_model.png")

        print("[4/6] Running model-interrogation queries...")
        query_lines = [
            f"Model size: {model_nodes:,} nodes; {model_elements:,} elements.",
            f"Element technologies found: {', '.join(element_types) if element_types else 'See element_type_listing.txt'}.",
            f"Base-excitation component N_BASE_EXCITE: {components.get('N_BASE_EXCITE')} nodes.",
            f"Monitor component MY_MONITOR: {components.get('MY_MONITOR')} node(s).",
            f"Joint-board component N_JOINT_BOARD: {components.get('N_JOINT_BOARD')} nodes.",
            f"Joint-legs component N_JOINT_LEGS: {components.get('N_JOINT_LEGS')} nodes.",
        ]
        (OUT / "query_summary.txt").write_text("\n".join(query_lines) + "\n", encoding="utf-8")
        (OUT / "query_results.json").write_text(
            json.dumps({"answers": query_lines, "components": components, "element_types": element_types}, indent=2),
            encoding="utf-8",
        )

        print("[5/6] Solving first 10 modes and checking against published reference...")
        mapdl.finish()
        mapdl.slashsolu()
        mapdl.antype("MODAL")
        mapdl.modopt("LANB", 10)
        mapdl.mxpand(10)
        mapdl.solve()
        mapdl.finish()

        actual = get_modal_frequencies(mapdl, 10)
        rows = []
        for i, (calc, ref) in enumerate(zip(actual, REFERENCE_FREQUENCIES_HZ), start=1):
            pct = 100.0 * (calc - ref) / ref
            rows.append((i, calc, ref, pct))

        with (OUT / "modal_check.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["mode", "calculated_hz", "published_reference_hz", "percent_difference"])
            w.writerows(rows)

        max_abs_pct = max(abs(r[3]) for r in rows)

        print("[6/6] Writing evidence report...")
        report = f"""# Advanced PCB Demo - Evidence Report

## Model

- Public source: PyMAPDL Technology Showcase 20
- Source file: `{cdb.name}`
- SHA-256: `{source_meta['sha256']}`
- Single-board mesh: {single_nodes:,} nodes / {single_elements:,} elements
- 3-layer assembly: {model_nodes:,} nodes / {model_elements:,} elements
- Element technologies detected: {', '.join(element_types) if element_types else 'See element_type_listing.txt'}

## Interrogation

{chr(10).join('- ' + x for x in query_lines)}

## Modal verification

- Modes solved: 10
- Maximum absolute difference from published reference: {max_abs_pct:.4f}%
- Detailed comparison: `modal_check.csv`

## Evidence package

- `01_complex_pcb_model.png`
- `model_summary.json`
- `element_type_listing.txt`
- `query_results.json`
- `query_summary.txt`
- `modal_check.csv`

## Source

{OFFICIAL_EXAMPLE_URL}
"""
        (OUT / "demo_report.md").write_text(report, encoding="utf-8")

        print("Done.")
        print(f"Open: {OUT / 'demo_report.md'}")
    finally:
        try:
            mapdl.exit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
