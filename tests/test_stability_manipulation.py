import math

import numpy as np
import pytest

from tsr1.environment.lunar import G_MOON
from tsr1.manipulation.arm import ArmSpec, size_arm
from tsr1.manipulation.crane import CraneSpec, size_crane
from tsr1.stability.static_stability import Load, evaluate, gravity_vector, rectangle, weight


def test_cop_equals_com_for_single_weight():
    sup = rectangle(2.0, 1.0)
    r = evaluate([weight(100.0, (0.3, -0.2, 0.8))], sup)
    assert r.cop == pytest.approx([0.3, -0.2])
    assert r.margin == pytest.approx(0.3)   # nearest edge y=-0.5
    assert math.isinf(r.tip_factor)


def test_tip_factor_unity_at_balance():
    sup = rectangle(2.0, 2.0)
    # 100 kg at centre, 100 kg hanging 1 m outside the +x edge -> balanced about edge x=1
    loads = [weight(100.0, (0, 0, 0.5)), weight(100.0, (2.0, 0, 0.5))]
    r = evaluate(loads, sup)
    assert r.tip_factor == pytest.approx(1.0, rel=1e-9)
    assert abs(r.margin) < 1e-9


def test_gravity_vector_slope_signs():
    g = gravity_vector(math.radians(10), 0.0)
    assert g[0] < 0 and g[2] < 0          # nose up -> gravity pulls rearward
    g = gravity_vector(0.0, math.radians(10))
    assert g[1] < 0                       # left side up -> gravity pulls to the right
    assert np.linalg.norm(gravity_vector(0.3, 0.2)) == pytest.approx(G_MOON * math.sqrt(
        math.cos(0.2) ** 2 * math.cos(0.3) ** 2 + math.sin(0.3) ** 2 + math.sin(0.2) ** 2 * math.cos(0.3) ** 2))


def test_horizontal_push_overturns():
    sup = rectangle(2.0, 2.0)
    loads = [weight(100.0, (0, 0, 0.5)), Load(np.array([-1000.0, 0, 0]), np.array([0, 0, 1.0]))]
    r = evaluate(loads, sup)
    # overturning about x=-1 edge: 1000*1.0 = 1000 N m vs restoring 162 N m
    assert r.tip_factor < 1.0


def test_arm_shoulder_torque_matches_hand_calc():
    spec = ArmSpec("t", (1.0, 1.0, 0.1), 50.0, 0.01, 6, 3, 5.0)
    r = size_arm(spec)
    # shoulder torque >= payload+EE moment alone
    assert r.joint_torque[0] >= (50 + 5) * G_MOON * 2.1 * spec.dynamic_factor
    assert r.joint_torque[0] > r.joint_torque[1] > r.joint_torque[2]
    assert r.tip_deflection <= spec.tip_deflection * 1.0001
    assert r.mass > 0


def test_arm_mass_grows_with_payload():
    m = [size_arm(ArmSpec("t", (1.0, 0.9, 0.2), p, 0.01, 6, 3, 8.0)).mass for p in (25, 50, 100, 150)]
    assert all(np.diff(m) > 0)


def test_crane_lighter_than_equivalent_heavy_arm():
    crane = size_crane(CraneSpec(boom_length=2.6, payload=150.0))
    arm = size_arm(ArmSpec("heavy", (1.1, 1.0, 0.2), 150.0, 0.01, 6, 3, 10.0))
    assert crane.mass < 0.5 * arm.mass
    assert crane.t_luff > 0 and crane.boom_comp > 0


def test_deck_layout_fits_and_does_not_overlap():
    from tsr1.design.layout import boom_radiator_shading, check_layout, deck_layout, stowed_height
    lay = deck_layout(2.6, 1.5, 1.64)
    chk = check_layout(lay, 2.6, 1.5)
    assert chk["ok"] and not chk["overlaps"] and not chk["outside"]
    assert lay["radiator"].area == pytest.approx(1.64, rel=1e-6)
    assert lay["service_spine"].area == pytest.approx(0.9 * 1.35)
    assert 0.0 < boom_radiator_shading(lay, 2.6, 0.05) < 0.05
    assert stowed_height(0.9, lay) <= 2.0
    # an oversized radiator must be detected as an overlap with the spine
    assert not check_layout(deck_layout(2.6, 1.5, 2.6), 2.6, 1.5)["ok"]
