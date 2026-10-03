"""Lunar south-polar environment model (directive §9).

Values are registered in the central parameter register with uncertainty ranges. Where the
environment naturally has a distribution, a range or sampler is provided rather than a single value.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from tsr1.common.params import REGISTRY as R

SUB = "environment"

# --- physical constants -------------------------------------------------------------------------
G_MOON = R.define("g_moon", "g_m", 1.62, "m/s^2", "SOURCE", "L018", SUB,
                  "NSSDC Moon fact sheet surface gravity")
G_EARTH = R.define("g_earth", "g_0", 9.80665, "m/s^2", "SOURCE", "L023", SUB, "standard gravity")
SIGMA_SB = R.define("sigma_sb", "σ", 5.670374419e-8, "W/(m^2 K^4)", "SOURCE", "L023", SUB,
                    "CODATA 2018 Stefan-Boltzmann constant")
SOLAR_CONST = R.define("solar_constant", "S", 1361.0, "W/m^2", "SOURCE", "L017", SUB,
                       "TSI 1360.8 W/m2 (Kopp & Lean 2011); ±3.4 % annual from orbit eccentricity",
                       low=1315.0, high=1408.0)

# --- regolith: disturbed-surface trafficability parameters (Lunar Sourcebook Table 9.14, S023) ---
R.define("soil_c", "c", 170.0, "Pa", "SOURCE", "S023", SUB,
         "Table 9.14 trafficability cohesion; range 0.1-1 kPa (S023)", low=100.0, high=1000.0)
R.define("soil_phi_deg", "φ", 35.0, "deg", "SOURCE", "S023", SUB,
         "Table 9.14 friction angle; range 30-46 deg (S023 depth table)", low=30.0, high=46.0)
R.define("soil_kc", "k_c", 1400.0, "N/m^(n+1)", "SOURCE", "S023", SUB,
         "Table 9.14 (0.14 N/cm2); range x0.5-x2 is ASSUMPTION A-03", low=700.0, high=2800.0)
R.define("soil_kphi", "k_φ", 820e3, "N/m^(n+2)", "SOURCE", "S023", SUB,
         "Table 9.14 (0.82 N/cm3); range x0.5-x2 is ASSUMPTION A-03", low=410e3, high=1640e3)
R.define("soil_n", "n", 1.0, "-", "SOURCE", "S023", SUB, "Table 9.14; range ASSUMPTION A-03",
         low=0.8, high=1.2)
R.define("soil_K", "K", 0.0178, "m", "SOURCE", "S023", SUB, "Table 9.14 shear deformation modulus 1.78 cm",
         low=0.010, high=0.025)
R.define("soil_rho_surface", "ρ_0-15", 1500.0, "kg/m^3", "SOURCE", "S023", SUB, "0-15 cm average",
         low=1450.0, high=1550.0)
R.define("soil_rho_0_30", "ρ_0-30", 1580.0, "kg/m^3", "SOURCE", "S023", SUB, "0-30 cm average",
         low=1530.0, high=1630.0)
R.define("soil_rho_30_60", "ρ_30-60", 1740.0, "kg/m^3", "SOURCE", "S023", SUB, "30-60 cm average",
         low=1690.0, high=1790.0)
# in-situ (undisturbed) strength by depth, used for anchors and ground-reaction spades
R.define("soil_c_0_15", "c_0-15", 520.0, "Pa", "SOURCE", "S023", SUB, "in-situ 0-15 cm", low=440.0, high=620.0)
R.define("soil_phi_0_15_deg", "φ_0-15", 42.0, "deg", "SOURCE", "S023", SUB, "in-situ 0-15 cm",
         low=41.0, high=43.0)
R.define("soil_c_0_30", "c_0-30", 900.0, "Pa", "SOURCE", "S023", SUB, "in-situ 0-30 cm", low=740.0, high=1100.0)
R.define("soil_phi_0_30_deg", "φ_0-30", 46.0, "deg", "SOURCE", "S023", SUB, "in-situ 0-30 cm",
         low=44.0, high=47.0)
R.define("soil_c_30_60", "c_30-60", 3000.0, "Pa", "SOURCE", "S023", SUB,
         "in-situ 30-60 cm (LITERATURE-RECALL of S023 depth table: 2.4-3.8 kPa)", low=2400.0, high=3800.0)
R.define("soil_phi_30_60_deg", "φ_30-60", 54.0, "deg", "SOURCE", "S023", SUB,
         "in-situ 30-60 cm (LITERATURE-RECALL of S023: 52-55 deg)", low=52.0, high=55.0)
R.define("lowg_dp_factor", "f_DP,g", 0.80, "-", "SOURCE", "S043", SUB,
         "lunar-g drawbar-pull reduction vs 1-g test (~20 %); applied in conservative case only (A-03b)",
         low=0.70, high=1.0)
R.define("lowg_sinkage_factor", "f_z,g", 1.40, "-", "SOURCE", "S043", SUB,
         "lunar-g sinkage increase up to 40 %; conservative case only (A-03b)", low=1.0, high=1.5)
R.define("contact_pressure_limit", "p_lim", 7000.0, "Pa", "SOURCE", "S023", SUB,
         "satisfactory mobility if ground pressure <= 7-10 kPa; lower bound adopted", low=7000.0, high=10000.0)

# --- illumination, communication geometry -------------------------------------------------------
R.define("illum_frac_best_2m", "f_ill,2m", 0.9227, "-", "SOURCE", "S030", SUB, "best ridge site, 2 m height")
R.define("illum_frac_best_10m", "f_ill,10m", 0.9565, "-", "SOURCE", "S030", SUB, "best ridge site, 10 m")
R.define("dark_max_best_site_h", "t_dark", 120.0, "h", "SOURCE", "S030", SUB,
         "longest continuous darkness typically 3-5 days at best sites (upper value)", low=72.0, high=120.0)
R.define("sun_elev_max_deg", "β_max", 1.54, "deg", "SOURCE", "L009", SUB,
         "lunar obliquity to ecliptic 1.54 deg -> max solar elevation at pole (+ local topography)")
R.define("dte_availability", "f_DTE", 0.51, "-", "SOURCE", "S073", SUB, "average south-pole DTE availability")

# --- thermal environment ------------------------------------------------------------------------
R.define("T_psr", "T_PSR", 40.0, "K", "SOURCE", "S032", SUB, "PSR floor temperatures < 40 K; cold bound 28 K",
         low=28.0, high=60.0)
R.define("T_sunlit_rim_max", "T_rim", 300.0, "K", "SOURCE", "S032", SUB,
         "sunlit polar rims often > 223 K, peaks ~300 K (secondary)", low=223.0, high=300.0)
R.define("T_sink_zenith", "T_sink", 70.0, "K", "ASSUMPTION", "A-29", SUB,
         "effective radiative sink for zenith-facing radiator incl. terrain view", low=30.0, high=150.0)

# --- radiation, micrometeoroids -----------------------------------------------------------------
R.define("dose_rate_gcr_si", "Ḋ_GCR", 13.2e-6, "Gy/h", "SOURCE", "S033", SUB, "Chang'e-4 LND, Si",
         low=12.2e-6, high=14.2e-6)
R.define("tid_design_krad", "TID_d", 10.0, "krad(Si)", "ASSUMPTION", "A-24", SUB,
         "10-yr incl. SPE behind 3 mm Al", low=3.0, high=30.0)
R.define("mm_flux_pole", "Φ_mm", 15000.0 / (100 * 100 + 4 * 100 * 10), "1/(m^2 yr)", "CALCULATED",
         "S061", SUB, "15 000 impacts/yr over 14 000 m2 exposed area of 100x100x10 m base (10^-6..10 g)")


@dataclass(frozen=True)
class Soil:
    """Bekker/Janosi-Hanamoto soil parameter set (SI)."""
    c: float
    phi: float      # rad
    kc: float
    kphi: float
    n: float
    K: float
    dp_factor: float = 1.0       # multiplicative drawbar-pull factor (reduced-g paradox)
    k_factor: float = 1.0        # multiplicative factor on kc, kphi (reduced-g sinkage increase)

    def scaled(self, **kw) -> "Soil":
        return replace(self, **kw)


def soil_nominal() -> Soil:
    return Soil(c=R.v("soil_c"), phi=math.radians(R.v("soil_phi_deg")), kc=R.v("soil_kc"),
                kphi=R.v("soil_kphi"), n=R.v("soil_n"), K=R.v("soil_K"))


def soil_conservative() -> Soil:
    """Nominal parameters with the reduced-gravity penalty applied (A-03b)."""
    fz = R.v("lowg_sinkage_factor")
    s = soil_nominal()
    n = s.n
    # sinkage ∝ k^(-2/(2n+1)) for a rigid wheel (Bekker closed form) -> choose k_factor for z x fz
    k_factor = fz ** (-(2 * n + 1) / 2)
    return s.scaled(dp_factor=R.v("lowg_dp_factor"), k_factor=k_factor)


def soil_weak() -> Soil:
    """Low-strength bound (c, phi at lower range limits; k at x0.5) with reduced-g penalty."""
    lo = lambda k: R.rng(k)[0]
    s = soil_conservative()
    return s.scaled(c=lo("soil_c"), phi=math.radians(lo("soil_phi_deg")), kc=lo("soil_kc"),
                    kphi=lo("soil_kphi"))


def sample_soils(n: int, rng: np.random.Generator) -> list[Soil]:
    """Monte Carlo sampler: uniform within registered ranges; lunar-g penalty sampled uniformly
    between none and full (A-03b)."""
    out = []
    for _ in range(n):
        u = lambda k: rng.uniform(*R.rng(k))
        g_pen = rng.uniform(0.0, 1.0)
        dp = 1.0 - g_pen * (1.0 - R.v("lowg_dp_factor"))
        fz = 1.0 + g_pen * (R.v("lowg_sinkage_factor") - 1.0)
        nn = u("soil_n")
        out.append(Soil(c=u("soil_c"), phi=math.radians(u("soil_phi_deg")), kc=u("soil_kc"),
                        kphi=u("soil_kphi"), n=nn, K=u("soil_K"), dp_factor=dp,
                        k_factor=fz ** (-(2 * nn + 1) / 2)))
    return out


@dataclass(frozen=True)
class InSituLayer:
    """Undisturbed regolith layer for anchor / spade analysis."""
    z_top: float
    z_bot: float
    rho: float
    c: float
    phi: float   # rad


def insitu_profile(strength_factor: float = 1.0) -> list[InSituLayer]:
    """Depth profile from S023 (A-26). ``strength_factor`` scales cohesion and tan(phi)."""
    def ph(name):
        return math.atan(math.tan(math.radians(R.v(name))) * strength_factor)
    return [
        InSituLayer(0.00, 0.15, R.v("soil_rho_surface"), R.v("soil_c_0_15") * strength_factor,
                    ph("soil_phi_0_15_deg")),
        InSituLayer(0.15, 0.30, R.v("soil_rho_0_30"), R.v("soil_c_0_30") * strength_factor,
                    ph("soil_phi_0_30_deg")),
        InSituLayer(0.30, 0.60, R.v("soil_rho_30_60"), R.v("soil_c_30_60") * strength_factor,
                    ph("soil_phi_30_60_deg")),
    ]


def layer_at(z: float, profile: list[InSituLayer]) -> InSituLayer:
    for lay in profile:
        if lay.z_top <= z < lay.z_bot:
            return lay
    return profile[-1]


def overburden_stress(z: float, profile: list[InSituLayer], g: float = G_MOON) -> float:
    """Vertical effective stress σ_v(z) = ∫ρ g dz [Pa]."""
    s = 0.0
    for lay in profile:
        if z <= lay.z_top:
            break
        dz = min(z, lay.z_bot) - lay.z_top
        s += lay.rho * g * dz
    if z > profile[-1].z_bot:
        s += profile[-1].rho * g * (z - profile[-1].z_bot)
    return s


def gcr_tid_krad(years: float) -> float:
    """GCR-only total ionizing dose in krad(Si) for a surface exposure of ``years``."""
    gy = R.v("dose_rate_gcr_si") * years * 365.25 * 24
    return gy * 0.1  # 1 Gy = 100 rad = 0.1 krad


def micrometeoroid_impacts(area_m2: float, years: float) -> float:
    return R.v("mm_flux_pole") * area_m2 * years
