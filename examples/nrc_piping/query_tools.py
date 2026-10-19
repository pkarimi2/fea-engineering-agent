"""Deterministic model-interrogation tools for the NRC piping demo.

These functions deliberately use MAPDL selection commands and solver/database
information rather than asking an LLM to guess model facts.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class QueryResult:
    query_type: str
    entity_id: int
    answer: dict[str, Any]
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def connected_elements(mapdl, node_id: int) -> QueryResult:
    """Return elements attached to a node using NSEL + ESLN."""
    mapdl.allsel("ALL")
    mapdl.nsel("S", "NODE", "", node_id)
    mapdl.esln("S")
    element_ids = [int(v) for v in mapdl.mesh.enum.tolist()]
    coord = {
        "x": float(mapdl.queries.nx(node_id)),
        "y": float(mapdl.queries.ny(node_id)),
        "z": float(mapdl.queries.nz(node_id)),
    }
    result = QueryResult(
        query_type="connected_elements",
        entity_id=node_id,
        answer={"elements": element_ids, "count": len(element_ids)},
        evidence={
            "mapdl_selection": f"NSEL,S,NODE,,{node_id} -> ESLN,S",
            "node_coordinates": coord,
        },
    )
    mapdl.allsel("ALL")
    return result


def elements_using_material(mapdl, material_id: int) -> QueryResult:
    """Return all currently defined elements using a material number."""
    mapdl.allsel("ALL")
    mapdl.esel("S", "MAT", "", material_id)
    element_ids = [int(v) for v in mapdl.mesh.enum.tolist()]
    result = QueryResult(
        query_type="elements_using_material",
        entity_id=material_id,
        answer={"elements": element_ids, "count": len(element_ids)},
        evidence={"mapdl_selection": f"ESEL,S,MAT,,{material_id}"},
    )
    mapdl.allsel("ALL")
    return result


def node_restraints(mapdl, node_id: int) -> QueryResult:
    """List DOF constraints for one node and return the raw MAPDL evidence."""
    mapdl.allsel("ALL")
    mapdl.nsel("S", "NODE", "", node_id)
    listing = mapdl.dlist().to_list()
    # Keep the raw table rows because this is evidence from MAPDL, not an LLM summary.
    result = QueryResult(
        query_type="node_restraints",
        entity_id=node_id,
        answer={"constraint_rows": listing, "constrained": bool(listing)},
        evidence={"mapdl_command": "DLIST", "selected_node": node_id},
    )
    mapdl.allsel("ALL")
    return result


def _save_eplot(mapdl, output: Path, **kwargs) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        mapdl.eplot(savefig=str(output), **kwargs)
    except (TypeError, ValueError):
        # PyMAPDL/PyVista combinations can reject an optional plotting
        # keyword, or can fail when a BC legend is requested but no legend
        # labels were created. Retry without the legend before falling back
        # to a plain element plot.
        fallback = dict(kwargs)
        fallback.pop("plot_bc_legend", None)
        try:
            mapdl.eplot(savefig=str(output), **fallback)
        except (TypeError, ValueError):
            mapdl.eplot(savefig=str(output))


def plot_connected_elements(mapdl, node_id: int, output: Path) -> None:
    mapdl.allsel("ALL")
    mapdl.nsel("S", "NODE", "", node_id)
    mapdl.esln("S")
    _save_eplot(mapdl, output, show_node_numbering=True)
    mapdl.allsel("ALL")


def plot_material_elements(mapdl, material_id: int, output: Path) -> None:
    mapdl.allsel("ALL")
    mapdl.esel("S", "MAT", "", material_id)
    _save_eplot(mapdl, output, show_node_numbering=False)
    mapdl.allsel("ALL")


def plot_model_with_bcs(mapdl, output: Path) -> None:
    mapdl.allsel("ALL")
    _save_eplot(
        mapdl,
        output,
        show_node_numbering=False,
        plot_bc=True,
        plot_bc_legend=False,
    )
