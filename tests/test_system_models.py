import math

import numpy as np
import pytest

from tsr1.budgets.scenarios import drm_library, evaluate
from tsr1.design.configuration import MODES, Options, build
from tsr1.reliability.servicing import LEVELS, TASKS, success_table
from tsr1.reliability.tsr_reliability import simulate_tsr
from tsr1.reliability.value_model import Scenario, monte_carlo, run_pair


@pytest.fixture(scope="module")
def cfg():
    return build(Options())


def test_mass_closure(cfg):
    assert cfg.cbe() == pytest.approx(sum(c.cbe * c.qty for c in cfg.comps))
    assert cfg.predicted() == pytest.approx(sum(t[2] for t in cfg.subsystem_table()))
    assert cfg.dry_mass_allocation > cfg.predicted() > cfg.cbe()
    # iteration converged: vehicle mass used for sizing equals operational mass
    assert cfg.vehicle.mass == pytest.approx(cfg.operational_mass, rel=1e-6)


def test_com_inside_footprint(cfg):
    c = cfg.com()
    assert abs(c[0]) < cfg.opts.wheelbase / 2 and abs(c[1]) < cfg.opts.track / 2 and 0.3 < c[2] < 1.5


def test_mode_power_positive(cfg):
    for m in MODES:
        assert cfg.mode_power(m) >= 0
    assert cfg.mode_power("M3_driving") > cfg.mode_power("M1_dormant")


def test_drm_energy_is_sum_of_phases(cfg):
    for drm in drm_library(cfg, 10.0):
        r = evaluate(cfg, drm)
        assert r.energy_kwh == pytest.approx(sum(row[5] for row in r.phase_energy))
        assert r.duration_h == pytest.approx(sum(p.hours for p in drm.phases))


def test_servicing_success_monotonic_in_level():
    st = success_table()
    for t in TASKS:
        vals = [st.robot[t][L] for L in LEVELS]
        assert all(np.diff(vals) >= 0)


def test_value_model_reproducible_and_bounded():
    a = run_pair(Scenario(n_assets=10), 5)
    b = run_pair(Scenario(n_assets=10), 5)
    assert a[0].availability == b[0].availability and a[1].availability == b[1].availability
    for m in a:
        assert 0.0 <= m.availability <= 1.0


def test_no_failures_gives_full_availability():
    m0, m1 = run_pair(Scenario(n_assets=5, mtbf_yr=1e9), 3)
    assert m0.availability == pytest.approx(1.0) and m1.availability == pytest.approx(1.0)
    assert m0.lost == 0


def test_tsr_improves_mean_availability():
    res = monte_carlo(Scenario(n_assets=20), n=40, sample=False)
    assert np.mean(res["dA"]) > 0
    assert np.mean(res["lost1"]) <= np.mean(res["lost0"])


def test_tsr_self_reliability_redundancy_helps():
    with_rep = simulate_tsr(n_runs=300, seed=3)
    no_rep = simulate_tsr(n_runs=300, seed=3, p_spare_tsr=0.0)
    assert with_rep.p_capable_10yr > no_rep.p_capable_10yr
