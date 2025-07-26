# Forming Methods
FORM_APB = 'Auto Panel Bender'
FORM_MPB = 'Manual Press Brake'
FORM_RF = 'Roll Form (outsourced)'

# Cutting Methods
CUT_APS = 'Auto Punch Shear'
CUT_MSP = 'Manual Shear Punch'
CUT_MSL = 'Manual Shear Laser'
CUT_TL = 'Auto Tube Laser'

# Materials
GLV = 'GLV-M5'
SST = 'SST-M3'

# Structure Types
WALL = 'Wall'
FLOOR = 'Floor'

# Safety Factor (for yield strength in walls and floors)
SF = 2

MATERIALS = {
    SST: {"yield_strength": 35000, "elastic_mod": 28000000, "youngs_mod": 28000000},  # psi
    GLV: {"yield_strength": 33000, "elastic_mod": 29500000, "youngs_mod": 29500000}  # psi
}

GAUGES = {
    SST: {0.047: 18, 0.059: 16, 0.075: 14, 0.101: 12, 0.128: 10, 0.158: 8},
    GLV: {0.042: 18, 0.053: 16, 0.066: 14, 0.096: 12, 0.129: 10, 0.157: 8}
}

BETA_FLOOR = {
    1.0: 0.2874, 1.2: 0.3762, 1.4: 0.4530, 1.6: 0.5172, 1.8: 0.5688, 2.0: 0.6102, 3.0: 0.7134, 
    4.0: 0.7410, 5.0: 0.7476, 6.0: 0.7500 # 6 applies to infinite aspect ratio
}

ALPHA_FLOOR = {
    1.0: 0.0444, 1.2: 0.0616, 1.4: 0.0770, 1.6: 0.0906, 1.8: 0.1017, 2.0: 0.1110, 3.0: 0.1335, 
    4.0: 0.1400, 5.0: 0.1417, 6.0: 0.1421 # 6 applies to infinite aspect ratio
}

BETA_WALL = {
    0.25: 0.037, 0.50: 0.120, 0.75: 0.212, 1.0: 0.321, 1.5: 0.523, 2.0: 0.677, 3.0: 0.866
}

GAMMA_WALL = {
    0.25: 0.159, 0.5: 0.275, 0.75: 0.354, 1.0: 0.413, 1.5: 0.482, 2.0: 0.509, 3.0: 0.517
}

WIND_TC = 'TC'  # Tropical Cyclone
WIND_NTC = 'NTC'  # Non-Tropical Cyclone
WIND_TCM = 'TCM'  # Tropical Cyclone Missile

WIND_PRESSURE_RATINGS = {
    WIND_NTC: 40,  # psf
    WIND_TC: 45,   # psf
    WIND_TCM: 60   # psf
}