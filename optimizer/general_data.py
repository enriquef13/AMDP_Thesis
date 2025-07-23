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
SF = 1.5

MATERIALS = {
    SST: {"yield_strength": 35000, "elastic_mod": 28000000, "youngs_mod": 28000000},  # psi
    GLV: {"yield_strength": 33000, "elastic_mod": 29500000, "youngs_mod": 29500000}  # psi
}

GAUGES = {
    SST: {0.047: 18, 0.059: 16, 0.075: 14, 0.101: 12, 0.128: 10, 0.158: 8},
    GLV: {0.042: 18, 0.053: 16, 0.066: 14, 0.096: 12, 0.129: 10, 0.157: 8}
}

BETA_FLOOR = {
    1.0: 0.3078, 1.2: 0.3834, 1.4: 0.4356, 1.6: 0.4680, 1.8: 0.4872, 2.0: 0.4974, 3.0: 0.5000
}

ALPHA_FLOOR = {
    1.0: 0.0138, 1.2: 0.0188, 1.4: 0.0226, 1.6: 0.0251, 1.8: 0.0267, 2.0: 0.0277, 3.0: 0.0284
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