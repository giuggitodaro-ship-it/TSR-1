"""Deck layout of TSR-1 (plan view) — the single geometric definition used by the mass/CoM model, the stability
crane geometry, the GEOM closure checks, figure fig03 and the visual render specification (CDR-21).

Frame: x forward, y left, origin at the deck centre; the deck is the top of the chassis torque box
(wheelbase × deck width). Every deck item is an axis-aligned rectangle (x0, x1, y0, y1) [m].

Allocation logic (DESIGN DECISION, CDR-21):
* the zenith radiator needs an unobstructed upward view, so it takes the full deck width at the rear;
* the service spine is a 2 × 3 grid of 0.45 m slots (6 slots) in the middle;
* the front strip carries what must be at the front for reach and sensing: the two dexterous-arm bases at the
  corners, the crane turntable on the centre line between them and the sensor mast;
* tools hang in holsters on the chassis front face, inside both arms' workspace;
* arms stow upright at the front corners (candle stow); the crane boom stows rearward over the spine.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

SLOT = 0.45            # spine slot pitch (module footprint ≤ 0.45 × 0.45 m per slot, II-01)
SLOT_ROWS, SLOT_COLS = 2, 3
EDGE_GAP = 0.03        # clearance between deck items


@dataclass(frozen=True)
class Item:
    name: str
    x0: float
    x1: float
    y0: float
    y1: float
    z_top: float = 0.0          # height of the item above the deck top in stowed configuration [m]

    @property
    def area(self) -> float:
        return (self.x1 - self.x0) * (self.y1 - self.y0)

    @property
    def centre(self) -> tuple[float, float]:
        return 0.5 * (self.x0 + self.x1), 0.5 * (self.y0 + self.y1)

    def overlaps(self, o: "Item") -> bool:
        return min(self.x1, o.x1) - max(self.x0, o.x0) > 1e-9 and min(self.y1, o.y1) - max(self.y0, o.y0) > 1e-9


def deck_layout(wheelbase: float, deck_width: float, a_rad: float, upper_arm: float = 0.75) -> dict[str, Item]:
    L, W = wheelbase, deck_width
    xr0, yr = -L / 2, W / 2
    rad_len = a_rad / W
    rad = Item("radiator", xr0, xr0 + rad_len, -yr, yr, 0.02)
    sp_len, sp_w = SLOT_ROWS * SLOT, SLOT_COLS * SLOT
    sp_x0 = rad.x1 + EDGE_GAP
    spine = Item("service_spine", sp_x0, sp_x0 + sp_len, -sp_w / 2, sp_w / 2, 0.45)
    fx0 = spine.x1 + EDGE_GAP            # front strip
    arm_w = 0.30
    arm_r = Item("dex_arm_R_base", L / 2 - arm_w, L / 2, -yr, -yr + arm_w, upper_arm + 0.10)
    arm_l = Item("dex_arm_L_base", L / 2 - arm_w, L / 2, yr - arm_w, yr, upper_arm + 0.10)
    crane = Item("crane_turntable", max(fx0, L / 2 - 0.45), L / 2, -0.20, 0.20, 0.25)
    mast = Item("sensor_mast_base", fx0, fx0 + 0.20, 0.22, 0.42, 0.30)
    return {i.name: i for i in (rad, spine, crane, mast, arm_r, arm_l)}


def tool_rack(wheelbase: float, deck_width: float) -> Item:
    """Tool holsters on the chassis front face (x = L/2), described as a strip in y (not a deck item)."""
    return Item("tool_rack_front_face", wheelbase / 2, wheelbase / 2 + 0.08, -0.55, 0.55, 0.0)


def check_layout(items: dict[str, Item], wheelbase: float, deck_width: float) -> dict:
    """Containment and pairwise non-overlap of all deck items (closure GEOM-5)."""
    L, W = wheelbase, deck_width
    outside = [i.name for i in items.values()
               if i.x0 < -L / 2 - 1e-9 or i.x1 > L / 2 + 1e-9 or i.y0 < -W / 2 - 1e-9 or i.y1 > W / 2 + 1e-9]
    names = list(items)
    overlaps = [(a, b) for k, a in enumerate(names) for b in names[k + 1:] if items[a].overlaps(items[b])]
    used = sum(i.area for i in items.values())
    return dict(ok=not outside and not overlaps, outside=outside, overlaps=overlaps, used_area=used,
                deck_area=L * W, free_area=L * W - used)


def boom_radiator_shading(items: dict[str, Item], boom_length: float, boom_od: float) -> float:
    """Fraction of the radiator's plan area covered by the rearward-stowed crane boom (projected, conservative)."""
    rad, crane = items["radiator"], items["crane_turntable"]
    x_base = crane.centre[0]
    x_tip = x_base - boom_length
    cover = max(0.0, min(rad.x1, x_base) - max(rad.x0, x_tip)) * boom_od
    return cover / rad.area


def stowed_height(deck_top: float, items: dict[str, Item]) -> float:
    return deck_top + max(i.z_top for i in items.values())


def crane_base(items: dict[str, Item], z: float = 1.05) -> tuple[float, float, float]:
    x, y = items["crane_turntable"].centre
    return (x, y, z)


def reach_to_point(base: tuple[float, float, float], x: float, y: float) -> float:
    return math.hypot(x - base[0], y - base[1])
