"""
Code to calculate the required sheet thickness and channel spacing for a wall based on hydrostatic and wind loads using 
Allowable Stress Design (ASD) principles.

Walls assumed to have 1 fixed edge (floor), 2 simply supported edges (walls), and 1 free edge (top).
Floor assumed to have 4 fixed edges.

Safety Factor applied to yield strength of materials.

Min. Wind Pressure Rating per Zone Category:
- Non-Tropical Cyclone (NTC): 40 psf
- Tropical Cyclone (TC): 45 psf
- Tropical Cyclone Missile (TCM): 60 psf

SST & GLV properties: Global Structural Design Manual Rev 6. p.p. 23-24
Wind Pressure Rating: Structural Design Standard - North America, Jan 2022. p.p. 71
Plate bending formulas: https://jackson.engr.tamu.edu/wp-content/uploads/sites/229/2023/03/Roarks-formulas-for-stress-and-strain.pdf, p.p. 511
"""

import numpy as np # type: ignore
from general_data import MATERIALS, GAUGES, BETA_FLOOR, ALPHA_FLOOR, BETA_WALL, GAMMA_WALL, WIND_PRESSURE_RATINGS, SF
from general_data import WIND_NTC, WIND_TC, WIND_TCM, SST, GLV
from config import z_in

def calculate_wall_gauge(width_in, height_in, water_height_in, wind_zone="NTC", material="SST-M3", display=False):
    """
    Calculate required sheet thickness for a wall.

    width_in: Width of the wall (inches).
    height_in: Height of the wall (inches).
    water_height_in: Height of water inside (inches).
    wind_zone: NTC (Non-Tropical Cyclone), TC (Tropical Cyclone), or TCM (Tropical Cyclone Missile) for wind pressure rating.
    material: "SST-M3" or "GLV-M5".
    """

    # Calculate allowable stress based on material properties
    props = MATERIALS[material]
    S_allow = props["yield_strength"] / SF  # psi (safety factor of 2.5)

    # Obtain wind pressure rating and convert to psi
    wind_pressure_psi = (WIND_PRESSURE_RATINGS[wind_zone] / 144) * 1.15  # psi (1.15 is a safety factor for wind pressure)

    # Hydrostatic pressure at bottom of wall (psi)
    gamma_water = 0.03603  # lbf/in³ (P = rho * g * h -> gamma = rho * g; rho = 62.4 lb/ft³, g = 32.2 ft/s²)
    water_pressure_psi = gamma_water * water_height_in # psi

    if display:
        print(f"Water pressure: {water_pressure_psi:.3f} psi for water height {water_height_in}\"")
        print(f"Wind pressure: {wind_pressure_psi:.3f} psi for wind zone {wind_zone}")

    # Total pressure on wall
    total_pressure_psi = max(water_pressure_psi, wind_pressure_psi)

    # Find closest aspect ratio to match BETA_WALL table indices
    a_b = width_in / height_in  # Aspect ratio of the wall
    a_b = min(BETA_WALL.keys(), 
              key=lambda x: abs(x - a_b) if x >= a_b else float('inf')
             ) if a_b <= max(BETA_WALL.keys()) else max(BETA_WALL.keys())
    beta = BETA_WALL[a_b]

    # Calculate required thickness using plate bending formula
    t_required_in = np.sqrt((beta * total_pressure_psi * height_in**2) / (S_allow))
    if display: print(f"Required thickness: {t_required_in:.3f}\"")

    # Find closest (upper) gauge thickness
    gauge_dict = GAUGES[material]
    thickness_warning = t_required_in >= max(gauge_dict.keys())
    t_closest_in = min(gauge_dict.keys(), 
                       key=lambda x: abs(x - t_required_in) if x >= t_required_in else float('inf')
                      ) if not thickness_warning else max(gauge_dict.keys())
    
    if display:
        if thickness_warning:
            print(f"WARNING! Required thickness {t_required_in:.3f}\" exceeds maximum thickness {max(gauge_dict.keys()):.3f}\" for {material}.")
        else:
            print(f"Recommended thickness: {t_closest_in:.3f}\" ({gauge_dict[t_closest_in]} gauge {material})")

    return gauge_dict[t_closest_in]


def calculate_floor_gauge(width_in, length_in, water_height_in, material="SST-M3", display=False):
    """
    Calculate required thickness for a floor panel.

    width_in: Width of the floor panel (inches).
    length_in: Length of the floor panel (inches).
    water_height_in: Height of water inside (inches).
    material: "SST" or "GLV".
    """

    # Obtain allowable stress and elastic modulus
    props = MATERIALS[material]
    S_allow = props["yield_strength"] / SF # psi
    E = props["elastic_mod"]  # psi

    # Hydrostatic pressure at bottom of floor (psi)
    gamma_water = 0.03603  # lbf/in³ (P = rho * g * h -> gamma = rho * g; rho = 62.4 lb/ft³, g = 32.2 ft/s²)
    water_pressure_psi = gamma_water * water_height_in  # psi

    if display: print(f"Water pressure: {water_pressure_psi:.3f} psi for water height {water_height_in}\"")

    a = max(width_in, length_in)
    b = min(width_in, length_in)
    a_b = a / b  # Aspect ratio of the floor
    a_b = min(BETA_FLOOR.keys(), 
              key=lambda x: abs(x - a_b) if x >= a_b else float('inf')
             ) if a_b <= max(BETA_FLOOR.keys()) else max(BETA_FLOOR.keys())
    beta = BETA_FLOOR[a_b]
    alpha = ALPHA_FLOOR[a_b]

    # Calculate required thickness using allowable stress
    t_prevent_yield_in = np.sqrt((beta * water_pressure_psi * b**2) / (S_allow))
    if display: print(f"Thickness to avoid yield: {t_prevent_yield_in:.3f}\"")

    # Calculate thickness to avoid deflection
    deflection_limit = 0.5 # inches
    t_avoid_deflection_in = np.power((alpha * water_pressure_psi * b**4) / (E * deflection_limit), 1/3)
    if display: print(f"Thickness to avoid {deflection_limit}\" deflection: {t_avoid_deflection_in:.3f}\"")

    # Required thickness is the maximum of the two
    t_required_in = max(t_prevent_yield_in, t_avoid_deflection_in)

    # Find closest (upper) gauge thickness
    gauge_dict = GAUGES[material]
    thickness_warning = t_required_in >= max(gauge_dict.keys())
    t_closest_in = min(gauge_dict.keys(), 
                       key=lambda x: abs(x - t_required_in) if x >= t_required_in else float('inf')
                      ) if not thickness_warning else max(gauge_dict.keys())
    
    if display:
        if thickness_warning:
            print(f"WARNING! Required thickness {t_required_in:.3f}\" exceeds maximum thickness {max(gauge_dict.keys()):.3f}\" for {material}.")
        else:
            print(f"Recommended thickness: {t_closest_in:.3f}\" ({gauge_dict[t_closest_in]} gauge {material})")

    return gauge_dict[t_closest_in]


display = True
calculate_wall_gauge(
    width_in=13,              
    height_in=z_in,             
    water_height_in=10,       
    wind_zone=WIND_NTC,
    material=SST,
    display=display
)

print(" ")

calculate_floor_gauge(
    width_in=50,              
    length_in=31,             
    water_height_in=14,     
    material=SST,
    display=display
)