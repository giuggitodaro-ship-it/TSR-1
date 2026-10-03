import math

import pytest

from tsr1.environment.lunar import G_MOON, overburden_stress, insitu_profile, soil_nominal
from tsr1.mobility.terramechanics import Wheel
from tsr1.power.electrical import size_battery, size_cable
from tsr1.recovery.towing import (Restraint, Target, helical_anchor_capacity, kp, max_recoverable_mass,
                                  restraint_capacity, spade_capacity, spade_insertion_force, target_resistance)
from tsr1.structures.chassis import FACE_MATERIALS, size_chassis
from tsr1.thermal.lumped import cold_leak, radiator_area


def test_rankine_kp():
    assert kp(math.radians(30)) == pytest.approx(3.0, rel=1e-9)


def test_overburden_uses_lunar_gravity():
    s = overburden_stress(0.15, insitu_profile())
    assert s == pytest.approx(1500 * G_MOON * 0.15)


def test_spade_capacity_grows_with_depth_and_strength():
    a, b = spade_capacity(0.6, 0.2), spade_capacity(0.6, 0.3)
    assert b > a > 0
    assert spade_capacity(0.6, 0.3, strength_factor=0.5) < b
    assert spade_insertion_force(0.6, 0.4) > spade_insertion_force(0.6, 0.3)


def test_anchor_capacity_positive_and_monotonic():
    assert helical_anchor_capacity(0.15, 0.6) > helical_anchor_capacity(0.15, 0.4) > 0


def test_restraint_ordering():
    s, w = soil_nominal(), Wheel(0.4, 0.3, 0.015)
    caps = [restraint_capacity(1100, 0.0, c, s, w, 6) for c in
            (Restraint("b"), Restraint("b+s", n_spades=2), Restraint("b+s+a", n_spades=2, n_anchors=2))]
    assert caps[0] < caps[1] < caps[2]
    assert restraint_capacity(1100, math.radians(15), Restraint("b"), s, w, 6) < caps[0]


def test_target_resistance_cases():
    free = target_resistance(Target("f", 450.0), 0.0)
    locked = target_resistance(Target("l", 450.0, brakes_locked=True), 0.0)
    sunk = target_resistance(Target("s", 450.0, sinkage=0.15), 0.0)
    assert free < locked < sunk
    assert target_resistance(Target("f", 450.0), math.radians(10)) > free


def test_max_recoverable_mass_decreases_with_slope():
    m = [max_recoverable_mass(4000.0, math.radians(d), 0.2) for d in (0, 10, 20)]
    assert m[0] > m[1] > m[2] > 0


def test_cable_voltage_drop_meets_spec():
    c = size_cable(3000.0, 25.0, drop_frac=0.03)
    assert c.drop_v == pytest.approx(0.03 * 120.0, rel=1e-6)
    assert c.loss_w == pytest.approx(3000.0 / 120.0 * c.drop_v, rel=1e-6)


def test_battery_meets_usable_eol_energy():
    b = size_battery(14.0)
    assert b.nameplate_kwh * 0.8 * 0.8 >= 14.0 - 1e-9
    assert b.n_cells == b.n_series * b.n_parallel


def test_radiator_area_linear_and_leak_positive():
    a1, _ = radiator_area(200.0)
    a2, _ = radiator_area(400.0)
    assert a2 == pytest.approx(2 * a1)
    assert cold_leak(3.0, 1.0) > 0


def test_chassis_meets_frequency_and_strength():
    for mat in FACE_MATERIALS:
        r = size_chassis(1200.0, material=mat)
        assert r.f1 >= 35.0 - 1e-6
        assert r.margin_strength >= 0
