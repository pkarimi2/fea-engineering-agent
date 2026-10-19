"""Optional provenance step: resume a DB created by ANSYS 11 in MAPDL 2025.

First run `legacy_ansys11.inp` in ANSYS 11 so that `legacy_ansys11.db`
exists in this folder. Then run this script from the repo root.
"""
from __future__ import annotations

import json
from pathlib import Path

from ansys.mapdl.core import launch_mapdl

HERE = Path(__file__).resolve().parent
RUN = HERE / ".mapdl_resume_run"
OUT = HERE / "outputs"
DB = HERE / "legacy_ansys11.db"


def main() -> None:
    if not DB.exists():
        raise FileNotFoundError(
            f"Missing {DB.name}. First run legacy_ansys11.inp in ANSYS 11 and place the resulting DB here."
        )

    RUN.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    mapdl = launch_mapdl(
        run_location=str(RUN),
        jobname="resume_ansys11_db",
        nproc=4,
        ram=8192,
        additional_switches="-smp",
        override=True,
        loglevel="WARNING",
    )
    try:
        print("[1/4] Resuming real ANSYS 11 database in MAPDL 2025...")
        mapdl.resume(str(DB.with_suffix("")), "db")
        summary = {
            "source_database": DB.name,
            "resumed_in": "MAPDL 2025",
            "nodes": int(mapdl.mesh.n_node),
            "elements": int(mapdl.mesh.n_elem),
            "expected_legacy_element_technologies": ["PIPE16", "PIPE18", "MASS21"],
        }

        print("[2/4] Re-solving first five modes in MAPDL 2025...")
        mapdl.finish()
        mapdl.slashsolu()
        mapdl.antype("MODAL")
        mapdl.modopt("LANB", 5)
        mapdl.mxpand("", "", "", "YES")
        mapdl.solve()
        mapdl.finish()
        mapdl.post1()
        rows = mapdl.set("LIST").to_list()
        freqs = [float(row[1]) for row in rows[:5]]
        mapdl.finish()
        summary["frequencies_hz"] = freqs

        print("[3/4] Writing provenance evidence...")
        (OUT / "ansys11_db_resumed_in_2025.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        txt = (
            "REAL LEGACY DATABASE PROVENANCE CHECK\n"
            "=====================================\n"
            f"Source DB: {DB.name}\n"
            "Created by: ANSYS 11 (when legacy_ansys11.inp is executed there)\n"
            "Resumed by: MAPDL 2025\n"
            f"Nodes: {summary['nodes']}\n"
            f"Elements: {summary['elements']}\n"
            "First five re-solved frequencies (Hz): "
            + ", ".join(f"{v:.5f}" for v in freqs)
            + "\n"
        )
        (OUT / "ansys11_db_resume_summary.txt").write_text(txt, encoding="utf-8")

        print("[4/4] Done.")
        print(txt)
    finally:
        try:
            mapdl.exit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
