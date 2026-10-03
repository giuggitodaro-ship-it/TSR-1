"""Electrical power system sizing (directive §6C, §18).

Architecture (selected in TS-06): Li-ion battery (PPR 18650-class pack) behind a bidirectional
buck-boost regulator producing a regulated **120 VDC** primary bus (ISPSIS, S011); 28 VDC secondary
bus via isolated converters for avionics; a galvanically isolated bidirectional **power-transfer
module (PTM)** for charging from infrastructure and emergency power delivery at 120 VDC through a
tethered dust-tolerant connector (exchange distance < 100 m, S012).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from tsr1.common.params import REGISTRY as R

SUB = "power"
R.define("bus_voltage", "V_bus", 120.0, "V", "SOURCE", "S011", SUB, "ISPSIS interoperability bus voltage")
R.define("cu_resistivity", "ρ_Cu", 1.72e-8, "ohm m", "SOURCE", "L023 (CRC handbook, 20 C, LITERATURE-RECALL)", SUB,
         "copper resistivity at 20 C")
R.define("cu_alpha", "α_Cu", 0.00393, "1/K", "SOURCE", "L023 (LITERATURE-RECALL)", SUB, "temperature coefficient")
R.define("cu_density", "ρ_m,Cu", 8960.0, "kg/m^3", "SOURCE", "L023", SUB, "copper density")
R.define("batt_spec_energy", "e_bat", 160.0, "Wh/kg", "ASSUMPTION", "A-15 (S070: 150-170 Wh/kg PPR today)", SUB,
         "pack-level specific energy incl. PPR features", low=130.0, high=200.0)
R.define("batt_dod", "DoD", 0.80, "-", "ASSUMPTION", "A-16", SUB, "usable depth of discharge, nominal", low=0.70, high=0.90)
R.define("batt_eol_fade", "f_fade", 0.20, "-", "ASSUMPTION", "A-16", SUB,
         "capacity loss at end of 10-yr life (~3000 moderate-DoD cycles + calendar)", low=0.10, high=0.30)
R.define("conv_eff", "η_conv", 0.95, "-", "ASSUMPTION", "A-17", SUB, "DC-DC converter efficiency", low=0.92, high=0.97)
R.define("conv_spec_power", "p_conv", 300.0, "W/kg", "ESTIMATE", "L007 (space power-conditioning units, LITERATURE-RECALL)",
         SUB, "specific power of space DC-DC converters incl. housing/thermal mount", low=150.0, high=500.0)
R.define("cell_energy_wh", "E_cell", 12.6, "Wh", "SOURCE", "S070 (18650 class: 3.5 Ah x 3.6 V)", SUB,
         "nominal 18650 cell energy", low=11.0, high=13.5)
R.define("cell_v_nom", "V_cell", 3.6, "V", "SOURCE", "S070 (Li-ion NCA/NMC nominal)", SUB, "cell nominal voltage")


@dataclass
class Cable:
    area_mm2: float
    resistance: float      # loop resistance [ohm]
    loss_w: float
    drop_v: float
    mass: float


def size_cable(power: float, length: float, voltage: float | None = None, drop_frac: float = 0.03,
               temp_c: float = 60.0, n_cond: int = 2, jacket_factor: float = 1.6) -> Cable:
    """Two-wire DC cable sized for a fractional voltage drop at conductor temperature ``temp_c``.
    Mass includes insulation/jacket/shield via ``jacket_factor`` (ESTIMATE)."""
    voltage = R.v("bus_voltage") if voltage is None else voltage
    I = power / voltage
    rho = R.v("cu_resistivity") * (1 + R.v("cu_alpha") * (temp_c - 20.0))
    r_max = drop_frac * voltage / I
    area = rho * (n_cond * length) / r_max
    # minimum mechanical/ampacity floor: 1.0 mm² (≈AWG 17) in vacuum for ≤ 10 A class (A)
    area = max(area, 1.0e-6)
    res = rho * n_cond * length / area
    mass = R.v("cu_density") * area * n_cond * length * jacket_factor
    return Cable(area * 1e6, res, I * I * res, I * res, mass)


@dataclass
class Battery:
    usable_eol_kwh: float
    nameplate_kwh: float
    mass: float
    n_cells: int
    n_series: int
    n_parallel: int
    v_nominal: float


def size_battery(usable_eol_kwh: float, n_series: int = 28) -> Battery:
    """Nameplate energy such that usable energy at end of life meets the requirement."""
    dod, fade = R.v("batt_dod"), R.v("batt_eol_fade")
    nameplate = usable_eol_kwh / (dod * (1 - fade))
    n_par = math.ceil(nameplate * 1000 / (R.v("cell_energy_wh") * n_series))
    n_cells = n_par * n_series
    nameplate_real = n_cells * R.v("cell_energy_wh") / 1000
    mass = nameplate_real * 1000 / R.v("batt_spec_energy")
    return Battery(usable_eol_kwh, nameplate_real, mass, n_cells, n_series, n_par, n_series * R.v("cell_v_nom"))


def converter_mass(power_w: float) -> float:
    return power_w / R.v("conv_spec_power")
