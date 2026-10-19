"""Small deterministic natural-language front end for the first demo.

This is intentionally *not* an LLM yet.  It converts three simple prompt shapes
into deterministic solver queries so the first public demo is reproducible.
The later MCP/LLM layer will call the same query functions as tools.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from ansys.mapdl.core import launch_mapdl

from model import build_model
from query_tools import connected_elements, elements_using_material, node_restraints


def route_query(mapdl, prompt: str):
    text = prompt.strip().lower()

    node_match = re.search(r"node\s+(\d+)", text)
    material_match = re.search(r"material\s+(\d+)", text)

    if node_match and any(word in text for word in ["connect", "attached", "element"]):
        return connected_elements(mapdl, int(node_match.group(1)))

    if material_match and any(word in text for word in ["use", "using", "element"]):
        return elements_using_material(mapdl, int(material_match.group(1)))

    if node_match and any(word in text for word in ["restraint", "constraint", "fixed", "dof"]):
        return node_restraints(mapdl, int(node_match.group(1)))

    raise ValueError(
        "Demo parser did not recognize the prompt. Try one of:\n"
        "  What elements are connected to node 2?\n"
        "  Which elements use material 1?\n"
        "  Show restraints at node 1."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="+", help="Question to ask the MAPDL model")
    parser.add_argument("--run-location", default=".mapdl_run")
    args = parser.parse_args()

    prompt = " ".join(args.prompt)
    run_location = Path(args.run_location).resolve()
    run_location.mkdir(parents=True, exist_ok=True)

    mapdl = launch_mapdl(
        run_location=str(run_location),
        jobname="nrc_ask",
        loglevel="WARNING",
        cleanup_on_exit=True,
    )
    try:
        build_model(mapdl)
        result = route_query(mapdl, prompt)
        print(json.dumps(result.to_dict(), indent=2))
    finally:
        mapdl.exit()


if __name__ == "__main__":
    main()
