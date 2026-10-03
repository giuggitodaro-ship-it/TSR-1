"""TS-03 manipulator architecture trade (directive §6A, §12).

Architectures are sized with the same arm/crane models; capability is scored against a task catalogue
derived from the DRMs. Task weights are the expected fraction of TSR-1 work content per task, derived
from the fault-type mix (A-09) and DRM step content — not arbitrary preferences. Capability per task
is a rule-based engineering judgement (documented in ``CAPABILITY_RULES``):
    1.0 feasible as specified; 0.75 feasible with a fixture/crane work-around (longer time);
    0.5 feasible only for a subset of cases; 0.0 infeasible.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from tsr1.manipulation.arm import ArmSpec, size_arm
from tsr1.manipulation.crane import CraneSpec, size_crane

# task: (weight, description, needs)
# needs keys: m = handled mass [kg], precise = needs fine positioning, bimanual = needs simultaneous hold,
#             force = sustained push/pull [N], reach = horizontal reach from deck [m]
TASKS = {
    "T01 small ORU swap (≤20 kg) with connectors": (0.20, dict(m=20, precise=True)),
    "T02 medium ORU swap (20–50 kg)": (0.08, dict(m=50, precise=True)),
    "T03 heavy ORU swap (50–150 kg)": (0.04, dict(m=150, precise=True)),
    "T04 open and hold access panel while working": (0.06, dict(m=10, bimanual=True)),
    "T05 connector mate/demate (≤150 N)": (0.10, dict(m=2, precise=True, force=150)),
    "T06 fastener operations (≤50 N m, tool-reacted)": (0.08, dict(m=3, precise=True)),
    "T07 cable/tether manipulation": (0.05, dict(m=2, precise=True, bimanual=True)),
    "T08 electrical diagnostic probing": (0.07, dict(m=1.5, precise=True)),
    "T09 dust cleaning of surfaces (brush/EDS wand)": (0.10, dict(m=3, reach=1.5)),
    "T10 support/stabilise damaged equipment (50–150 kg)": (0.03, dict(m=150)),
    "T11 lift wheel corner of immobilised rover (≤150 kg)": (0.03, dict(m=150)),
    "T12 rig tow line / shackle": (0.04, dict(m=2, precise=True)),
    "T13 install helical anchors (30 N m, 200 N crowd)": (0.04, dict(m=6, force=200)),
    "T14 heavy push/pull on structure (200–300 N)": (0.02, dict(force=300)),
    "T15 close-range inspection (macro, IR)": (0.06, dict(m=0.5, precise=True)),
}


@dataclass
class Architecture:
    name: str
    dex: bool = False          # one dexterous 7-DOF arm (20 kg)
    dex2: bool = False         # second identical dexterous arm
    heavy: bool = False        # heavy 6-DOF arm (150 kg)
    general: bool = False      # single general-purpose 7-DOF arm (100 kg, stiff)
    crane: bool = False        # cable-stayed crane boom (150 kg)
    fixtures: bool = False     # passive fixtures (vice, prop rod, ORU cradle) on service spine


ARCHITECTURES = [
    Architecture("A1 one general-purpose 7-DOF arm (100 kg)", general=True),
    Architecture("A2 two identical dexterous arms", dex=True, dex2=True),
    Architecture("A3 asymmetric heavy arm + dexterous arm", dex=True, heavy=True),
    Architecture("A4 dexterous arm + crane boom", dex=True, crane=True),
    Architecture("A5 dexterous arm + passive fixtures", dex=True, fixtures=True),
    Architecture("A6 dexterous arm + crane boom + passive fixtures", dex=True, crane=True, fixtures=True),
    Architecture("A7 two dexterous arms + crane boom", dex=True, dex2=True, crane=True),
]


def capability(a: Architecture, needs: dict) -> float:
    """Rule set (CAPABILITY_RULES)."""
    m = needs.get("m", 0.0)
    precise = needs.get("precise", False)
    bim = needs.get("bimanual", False)
    force = needs.get("force", 0.0)
    dex_like = a.dex or a.general
    two_arms = (a.dex and a.dex2) or (a.dex and a.heavy)
    score = 1.0
    # mass handling
    if m > 20:
        if a.general and m <= 100:
            pass
        elif a.heavy:
            pass
        elif a.crane and dex_like:
            score = min(score, 0.9 if precise else 1.0)     # crane carries, arm guides (cooperative)
        elif a.crane:
            score = min(score, 0.5)
        elif a.general and m > 100:
            score = min(score, 0.0)
        else:
            return 0.0
    # precision
    if precise and not dex_like:
        return 0.0
    # bimanual
    if bim:
        if two_arms:
            pass
        elif a.fixtures or a.crane:
            score = min(score, 0.75)
        else:
            score = min(score, 0.4)
    # sustained force
    if force > 0:
        cap = 0.0
        if a.general or a.heavy:
            cap = 400.0
        elif a.dex:
            cap = 150.0            # dexterous arm tip force at full reach (rating/arm length, conservative)
        if force <= cap:
            pass
        elif a.crane and force <= 300:
            score = min(score, 0.6)    # line pull via crane/winch rigging
        else:
            score = min(score, 0.25)
    return score


def evaluate() -> list[dict]:
    dex = size_arm(ArmSpec("dexterous", (0.75, 0.70, 0.15), 20.0, 0.003, 7, 3, 6.0, 3.0, math.radians(5)))
    heavy = size_arm(ArmSpec("heavy", (1.1, 1.0, 0.2), 150.0, 0.010, 6, 3, 10.0, 0.0, math.radians(2)))
    gen = size_arm(ArmSpec("general", (1.1, 1.0, 0.2), 100.0, 0.003, 7, 3, 10.0, 3.0, math.radians(3)))
    crane = size_crane(CraneSpec(boom_length=2.6, payload=150.0))
    out = []
    for a in ARCHITECTURES:
        mass = (dex.mass if a.dex else 0) + (dex.mass if a.dex2 else 0) + (heavy.mass if a.heavy else 0) + \
               (gen.mass if a.general else 0) + (crane.mass if a.crane else 0) + (8.0 if a.fixtures else 0)
        n_joints = 7 * (a.dex + a.dex2 + a.general) + 6 * a.heavy + 3 * a.crane
        power = (dex.power_move if a.dex else 0) + (heavy.power_move if a.heavy else 0) + \
                (gen.power_move if a.general else 0) + (crane.power_hoist if a.crane else 0)
        base_moment = max(dex.base_moment if a.dex else 0, heavy.base_moment if a.heavy else 0,
                          gen.base_moment if a.general else 0)
        cov = sum(w * capability(a, needs) for w, needs in TASKS.values())
        wsum = sum(w for w, _ in TASKS.values())
        per_task = {k: capability(a, n) for k, (w, n) in TASKS.items()}
        # degraded capability if the primary dexterous element fails (single-point-failure indicator)
        if a.dex and (a.dex2 or a.general):
            backup = 1.0
        elif a.dex and a.heavy:
            backup = sum(w * capability(Architecture("x", general=True), n) for w, n in TASKS.values()) / wsum * 0.6
        else:
            backup = 0.0
        out.append(dict(architecture=a.name, mass_kg=mass, joints=n_joints, move_power_W=power,
                        max_base_moment_Nm=base_moment, weighted_coverage=cov / wsum,
                        coverage_per_kg=cov / wsum / mass, backup_after_primary_arm_failure=backup,
                        per_task=per_task))
    return out
