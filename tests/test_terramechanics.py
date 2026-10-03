import math

import numpy as np
import pytest

from tsr1.common import units as U
from tsr1.environment.lunar import soil_conservative, soil_nominal
from tsr1.mobility.terramechanics import (Wheel, _integrals, bekker_sinkage_closed_form, contact_pressure,
                                          solve)
from tsr1.mobility.vehicle import (Vehicle, axle_loads, drive_state, lrv_calibration, max_slope,
                                   max_tow_force)

W = Wheel(0.40, 0.30, 0.015)


def test_pressure_sinkage_dimensions():
    n = 1
    k_eq = U.N / U.L ** (n + 2)              # k_c/b + k_phi
    sigma = k_eq * U.L ** n                  # [r (cos - cos)]^n
    assert sigma == U.Pa
    tau = U.Pa                               # c + sigma tan(phi)
    torque = U.L * tau * U.L ** 2            # b r_s^2 ∫τ dθ
    assert torque == U.N * U.L


def test_vertical_equilibrium_is_satisfied():
    st = solve(W, soil_nominal(), 400.0, 0.2)
    Wv, H, Rr, T = _integrals(W, soil_nominal(), st.theta1, 0.2)
    assert Wv == pytest.approx(400.0, rel=1e-6)
    assert st.dp == pytest.approx(H - Rr)


def test_numeric_sinkage_close_to_bekker_closed_form():
    for load in (200.0, 400.0, 800.0):
        z_num = solve(W, soil_nominal(), load, 0.05).sinkage
        z_cf = bekker_sinkage_closed_form(W, soil_nominal(), load)
        assert 0.7 < z_num / z_cf < 1.5


def test_drawbar_pull_increases_with_slip_and_friction():
    s = soil_nominal()
    dps = [solve(W, s, 400.0, i).dp for i in (0.05, 0.1, 0.2, 0.4)]
    assert all(np.diff(dps) > 0)
    weak = s.scaled(phi=math.radians(30))
    assert solve(W, weak, 400.0, 0.2).dp < solve(W, s, 400.0, 0.2).dp


def test_conservative_soil_sinks_more_and_pulls_less():
    a = solve(W, soil_nominal(), 400.0, 0.2)
    b = solve(W, soil_conservative(), 400.0, 0.2)
    assert b.sinkage > a.sinkage * 1.2
    assert b.dp < a.dp


def test_sinkage_increases_with_load_and_pressure_reasonable():
    z = [solve(W, soil_nominal(), L, 0.2).sinkage for L in (200, 400, 800)]
    assert z[0] < z[1] < z[2]
    st = solve(W, soil_nominal(), 400.0, 0.2)
    assert 2e3 < contact_pressure(st, W) < 3e4


def test_axle_loads_static_equilibrium():
    v = Vehicle(1400.0, W, (1.2, 0.0, -1.2), h_cg=0.7)
    th = math.radians(15)
    loads = axle_loads(v, th, f_tow=200.0, h_tow=0.3)
    assert loads.sum() == pytest.approx(v.weight * math.cos(th))
    x = np.array(v.axle_x) - v.x_cg
    assert (x * loads).sum() == pytest.approx(-v.weight * math.sin(th) * 0.7 - 200.0 * 0.3)


def test_slope_capability_and_towing_monotonic():
    v = Vehicle(1400.0, W, (1.2, 0.0, -1.2), h_cg=0.7)
    s = soil_nominal()
    th0 = max_slope(v, s)
    assert math.radians(10) < th0 < math.radians(35)
    assert max_slope(v, s, f_tow=300.0) < th0
    assert max_slope(v, s, failed_wheels=1) < th0
    assert max_tow_force(v, s, math.radians(10)) < max_tow_force(v, s, 0.0)
    assert drive_state(v, s, math.radians(5)).feasible


def test_lrv_calibration_factor_plausible():
    k = lrv_calibration()
    assert 0.3 < k < 1.5
