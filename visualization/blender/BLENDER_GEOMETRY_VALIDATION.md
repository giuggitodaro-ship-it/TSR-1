# Blender geometry validation

Measured inside Blender on world-space geometry / joint datums. Unit: metres unless shown. Ground datum Z=0. Repository baseline commit `95f06abd408712dffba3958a1003227ca7db70d2`. Bounds include hardware and exclude presentation, hidden internal allocation boxes, and deployed remote cables. Functioning arms/crane naturally enlarge the operating envelope.

| Property | Repository value | Blender measured value | Error | PASS/FAIL | Note |
|---|---:|---:|---:|---|---|
| TRAVERSE overall length [m] | 3.600000 | 3.600000 | -0.000000 | PASS |  |
| TRAVERSE overall width [m] | 2.400000 | 2.400000 | +0.000000 | PASS |  |
| TRAVERSE top above ground [m] | 2.200000 | 2.200000 | +0.000000 | PASS |  |
| TRAVERSE chassis ground clearance [m] | 0.450000 | 0.450000 | +0.000000 | PASS |  |
| chassis length [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |
| chassis width [m] | 1.500000 | 1.500000 | +0.000000 | PASS |  |
| chassis height [m] | 0.450000 | 0.450000 | -0.000000 | PASS |  |
| wheelbase [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |
| track [m] | 2.000000 | 2.000000 | +0.000000 | PASS |  |
| wheel tip diameter [m] | 0.900000 | 0.900080 | +0.000080 | PASS | C06: radial tip diameter; .43 tread + .02 grouser |
| wheel width [m] | 0.400000 | 0.400000 | +0.000000 | PASS |  |
| mast tube [m] | 1.200000 | 1.200000 | +0.000000 | PASS |  |
| stereo optical baseline [m] | 0.250000 | 0.250000 | +0.000000 | PASS |  |
| radiator gross area [m2] | 1.642944 | 1.642943 | -0.000000 | PASS |  |
| spine X footprint [m] | 0.900000 | 0.900000 | +0.000000 | PASS |  |
| spine Y footprint [m] | 1.350000 | 1.350000 | +0.000000 | PASS |  |
| solar L length [m] | 1.500000 | 1.500000 | +0.000000 | PASS |  |
| solar L height [m] | 0.500000 | 0.500000 | +0.000000 | PASS |  |
| solar R length [m] | 1.500000 | 1.500000 | +0.000000 | PASS |  |
| solar R height [m] | 0.500000 | 0.500000 | +0.000000 | PASS |  |
| TRAVERSE armL upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| TRAVERSE armL forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| TRAVERSE armL wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| TRAVERSE armR upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| TRAVERSE armR forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| TRAVERSE armR wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| TRAVERSE crane boom [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |
| SERVICING chassis ground clearance [m] | 0.100000 | 0.100000 | -0.000000 | PASS |  |
| SERVICING armL upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| SERVICING armL forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| SERVICING armL wrist [m] | 0.150000 | 0.150000 | +0.000000 | PASS |  |
| SERVICING armR upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| SERVICING armR forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| SERVICING armR wrist [m] | 0.150000 | 0.150000 | +0.000000 | PASS |  |
| SERVICING crane boom [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |
| RECOVERY chassis ground clearance [m] | 0.100000 | 0.100000 | -0.000000 | PASS |  |
| RECOVERY armL upper [m] | 0.750000 | 0.750000 | -0.000000 | PASS |  |
| RECOVERY armL forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| RECOVERY armL wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| RECOVERY armR upper [m] | 0.750000 | 0.750000 | -0.000000 | PASS |  |
| RECOVERY armR forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| RECOVERY armR wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| RECOVERY crane boom [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |
| recovery working fairlead height [m] | 0.250000 | 0.250000 | +0.000000 | PASS |  |
| EMERGENCY_POWER chassis ground clearance [m] | 0.450000 | 0.450000 | +0.000000 | PASS |  |
| EMERGENCY_POWER armL upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| EMERGENCY_POWER armL forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| EMERGENCY_POWER armL wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| EMERGENCY_POWER armR upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| EMERGENCY_POWER armR forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| EMERGENCY_POWER armR wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| EMERGENCY_POWER crane boom [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |
| LANDER_STOW overall length [m] | 3.600000 | 3.600000 | -0.000000 | PASS |  |
| LANDER_STOW overall width [m] | 2.400000 | 2.400000 | +0.000000 | PASS |  |
| LANDER_STOW top above ground [m] | 1.750000 | 1.750000 | +0.000000 | PASS |  |
| LANDER_STOW chassis ground clearance [m] | 0.450000 | 0.450000 | +0.000000 | PASS |  |
| LANDER_STOW armL upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| LANDER_STOW armL forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| LANDER_STOW armL wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| LANDER_STOW armR upper [m] | 0.750000 | 0.750000 | +0.000000 | PASS |  |
| LANDER_STOW armR forearm [m] | 0.700000 | 0.700000 | -0.000000 | PASS |  |
| LANDER_STOW armR wrist [m] | 0.150000 | 0.150000 | -0.000000 | PASS |  |
| LANDER_STOW crane boom [m] | 2.600000 | 2.600000 | -0.000000 | PASS |  |

PASS is dimensional conformity under documented interpretations, not engineering certification. C04 fairlead height applies only in lowered recovery. C06 wheel diameter includes grousers. Internal material density/mass budgets are not recalculated by this visualization. Full motion collision certification is not claimed.
