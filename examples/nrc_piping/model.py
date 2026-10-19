"""Public NRC piping benchmark model used by the FEA Engineering Agent demo.

The geometry and reference values follow the public PyMAPDL verification example
for NUREG/CR-1677, Volume 1, Problem 1.  This module intentionally focuses on
model construction and the first five modal frequencies so the demo stays fast
and easy to inspect.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

REFERENCE_FREQUENCIES_HZ = np.array(
    [28.515, 56.441, 82.947, 144.140, 166.260], dtype=float
)


@dataclass(frozen=True)
class ModalCheck:
    mode: int
    reference_hz: float
    computed_hz: float
    difference_pct: float


def build_model(mapdl) -> None:
    """Build the public NRC piping benchmark in the active MAPDL session."""
    mapdl.clear()
    mapdl.title("NRC Piping Benchmark - NUREG/CR-1677 Vol. 1 Problem 1")
    mapdl.prep7()

    # Material and element technologies.
    mapdl.mp("EX", 1, 24.0e6)
    mapdl.mp("NUXY", 1, 0.3)

    mapdl.et(1, "PIPE289")
    mapdl.keyopt(1, 4, 2)
    mapdl.et(2, "ELBOW290", "", 6)
    mapdl.et(3, "MASS21")
    mapdl.keyopt(3, 3, 2)

    # Pipe section: OD, wall thickness, circumferential integration points.
    mapdl.sectype(1, "PIPE")
    mapdl.secdata(7.289, 0.241, 24)

    # Lumped masses, lb-sec^2/in, at the benchmark nodes.
    lumped_masses = {
        12: 0.03988,
        13: 0.05032,
        14: 0.02088,
        15: 0.01698,
        16: 0.01307,
        17: 0.01698,
        18: 0.01044,
        19: 0.01795,
        20: 0.01501,
    }
    for real_id, mass in lumped_masses.items():
        mapdl.r(real_id, mass)

    # Geometry keypoints.
    keypoints = {
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
    for kid, xyz in keypoints.items():
        mapdl.k(kid, *xyz)

    # Six straight lines.
    for i, j in [(1, 2), (2, 3), (5, 6), (6, 7), (9, 10), (10, 11)]:
        mapdl.l(i, j)

    # Four curved segments forming two bends.
    mapdl.larc(3, 4, 12)
    mapdl.larc(4, 5, 13)
    mapdl.larc(7, 8, 14)
    mapdl.larc(8, 9, 15)

    # Straight-pipe mesh.
    mapdl.type(1)
    mapdl.mat(1)
    mapdl.secnum(1)
    mapdl.real(1)
    mapdl.lsel("S", "LINE", "", 1, 6)
    mapdl.allsel("BELOW", "LINE")
    mapdl.lesize("ALL", "", "", 2)
    mapdl.lmesh("ALL")
    mapdl.allsel("ALL")

    # Bend mesh.  ELBOW later converts the appropriate pipe elements to ELBOW290.
    mapdl.type(2)
    mapdl.secnum(1)
    mapdl.mat(1)
    mapdl.lsel("S", "LINE", "", 7, 14)
    mapdl.allsel("BELOW", "LINE")
    mapdl.lesize("ALL", "", "", 2)
    mapdl.lmesh("ALL")
    mapdl.allsel("ALL")

    # Point masses at benchmark nodes.  The node numbering follows the public
    # verification example because the same geometry/mesh sequence is used.
    mass_nodes = {
        12: 2,
        13: 6,
        14: 28,
        15: 10,
        16: 11,
        17: 15,
        18: 35,
        19: 19,
        20: 20,
    }
    mapdl.type(3)
    for real_id, node_id in mass_nodes.items():
        mapdl.real(real_id)
        mapdl.e(node_id)

    mapdl.elbow("ON", "", "", "SECT")
    mapdl.allsel("ALL")

    # Two fixed anchors at end keypoints.
    mapdl.dk(1, "ALL", 0)
    mapdl.dk(11, "ALL", 0)
    mapdl.allsel("ALL")
    mapdl.finish()


def solve_modal(mapdl, nmodes: int = 5) -> list[float]:
    """Solve the first ``nmodes`` modes and return their frequencies in Hz."""
    mapdl.slashsolu()
    mapdl.antype("MODAL")
    mapdl.modopt("LANB", nmodes)
    mapdl.mxpand("", "", "", "YES")
    mapdl.solve()
    mapdl.finish()

    mapdl.post1()
    rows = mapdl.set("LIST").to_list()
    frequencies = [float(row[1]) for row in rows[:nmodes]]
    mapdl.finish()
    return frequencies


def compare_frequencies(computed: Iterable[float]) -> list[ModalCheck]:
    """Compare computed modal frequencies with the published benchmark values."""
    computed_array = np.asarray(list(computed), dtype=float)
    n = min(len(computed_array), len(REFERENCE_FREQUENCIES_HZ))
    checks: list[ModalCheck] = []
    for idx in range(n):
        ref = float(REFERENCE_FREQUENCIES_HZ[idx])
        calc = float(computed_array[idx])
        checks.append(
            ModalCheck(
                mode=idx + 1,
                reference_hz=ref,
                computed_hz=calc,
                difference_pct=100.0 * (calc - ref) / ref,
            )
        )
    return checks


def save_baseline_database(mapdl, path: Path) -> None:
    """Save a database copy for later interrogation/model-diff demos."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mapdl.save(str(path.with_suffix("")), "db")
