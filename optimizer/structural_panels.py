"""
Code to calculate the required sheet thickness and channel spacing for a wall based on hydrostatic and wind loads using 
Allowable Stress Design (ASD) principles.

Walls assumed to have 1 fixed edge (floor), 2 simply supported edges (walls), and 1 free edge (top).
Floor assumed to have 4 simply supported edges.

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
import general_data as gd

def _interpolate_key(a_b, dictionary):
    d_keys = sorted(dictionary.keys())
    if a_b < d_keys[0]:
        # Interpolate between the smallest key's value and 0
        return dictionary[d_keys[0]] * (a_b / d_keys[0])
    elif a_b >= d_keys[-1]:
        # If a_b is equal to the largest key, use the corresponding value
        return dictionary[d_keys[-1]]
    else:
        # Find the two closest keys for interpolation
        lower_key = max(k for k in d_keys if k <= a_b)
        upper_key = min(k for k in d_keys if k > a_b)
        lower_value = dictionary[lower_key]
        upper_value = dictionary[upper_key]
        # Linear interpolation
        return lower_value + (upper_value - lower_value) * ((a_b - lower_key) / (upper_key - lower_key))

def calculate_wall_gauge(width_in, height_in, water_height_in, material=gd.SST, display=False):
    """
    Calculate required sheet thickness for a wall.

    width_in: Width of the wall (inches).
    height_in: Height of the wall (inches).
    water_height_in: Height of water inside (inches).
    material: "SST-M3" or "GLV-M5".
    """

    # Calculate allowable stress based on material properties
    props = gd.MATERIALS[material]
    S_allow = props["yield_strength"] / gd.YIELD_SF  # psi (safety factor of 2.5)

    # Obtain wind pressure rating and convert to psi
    wind_pressure_psi = (gd.WIND_PRESSURE_RATING / 144) * gd.WIND_RESISTANCE_FACTOR

    # Hydrostatic pressure at bottom of wall (psi)
    gamma_water = 0.03603  # lbf/in³ (P = rho * g * h -> gamma = rho * g; rho = 62.4 lb/ft³, g = 32.2 ft/s²)
    water_pressure_psi = gamma_water * water_height_in # psi

    if display:
        print(f"Water pressure: {water_pressure_psi:.3f} psi for water height {water_height_in}\"")
        print(f"Wind pressure: {wind_pressure_psi:.3f} psi")

    # Total pressure on wall
    total_pressure_psi = max(water_pressure_psi, wind_pressure_psi)

    # Find closest aspect ratio to match BETA_WALL table indices
    a_b = width_in / height_in  # Aspect ratio of the wall
    if a_b > max(gd.BETA_WALL.keys()):
        if display:
            print(f"Aspect ratio {a_b:.2f} exceeds maximum of {max(gd.BETA_WALL.keys()):.2f}. Returning None.")
        return None, None

    beta = _interpolate_key(a_b, gd.BETA_WALL)

    # Calculate required thickness using plate bending formula
    t_required_in = np.sqrt((beta * total_pressure_psi * height_in**2) / (S_allow))
    if display: print(f"Required thickness: {t_required_in:.3f}\"")

    # Find closest (upper) gauge thickness
    gauge_dict = gd.GAUGES[material]
    thickness_warning = t_required_in >= max(gauge_dict.keys())
    t_closest_in = min(gauge_dict.keys(), 
                       key=lambda x: abs(x - t_required_in) if x >= t_required_in else float('inf')
                      ) if not thickness_warning else max(gauge_dict.keys())
    
    if thickness_warning:
        if display:
            print(f"WARNING! Required thickness {t_required_in:.3f}\" exceeds maximum thickness {max(gauge_dict.keys()):.3f}\" for {material}.")
        return t_required_in, None
    
    if display:
        print(f"Recommended thickness: {t_closest_in:.3f}\" ({gauge_dict[t_closest_in]} gauge {material})")

    return t_required_in, gauge_dict[t_closest_in]


def calculate_floor_gauge(width_in, length_in, water_height_in, material=gd.SST, display=False):
    """
    Calculate required thickness for a floor panel.

    width_in: Width of the floor panel (inches).
    length_in: Length of the floor panel (inches).
    water_height_in: Height of water inside (inches).
    material: "SST" or "GLV".
    """

    # Obtain allowable stress and elastic modulus
    props = gd.MATERIALS[material]
    S_allow = props["yield_strength"] / gd.YIELD_SF # psi
    E = props["elastic_mod"]  # psi

    # Hydrostatic pressure at bottom of floor (psi)
    gamma_water = 0.03603  # lbf/in³ (P = rho * g * h -> gamma = rho * g; rho = 62.4 lb/ft³, g = 32.2 ft/s²)
    water_pressure_psi = gamma_water * water_height_in  # psi

    if display: print(f"Water pressure: {water_pressure_psi:.3f} psi for water height {water_height_in}\"")

    a = max(width_in, length_in)
    b = min(width_in, length_in)
    a_b = a / b  # Aspect ratio of the floor    
    beta = _interpolate_key(a_b, gd.BETA_FLOOR)
    alpha = _interpolate_key(a_b, gd.ALPHA_FLOOR)

    # Calculate required thickness using allowable stress
    t_prevent_yield_in = np.sqrt((beta * water_pressure_psi * b**2) / (S_allow))
    if display: print(f"Thickness to avoid yield: {t_prevent_yield_in:.3f}\"")

    # Calculate thickness to avoid deflection
    deflection_limit_factor = gd.DEFLECTION_LIMIT
    deflection_limit = a * deflection_limit_factor # inches
    t_avoid_deflection_in = np.power((alpha * water_pressure_psi * b**4) / (E * deflection_limit), 1/3)
    if display: print(f"Thickness to avoid {deflection_limit:.2f}\" L/{1/deflection_limit_factor:.0f} deflection: {t_avoid_deflection_in:.3f}\"")

    # Required thickness is the maximum of the two
    t_required_in = max(t_prevent_yield_in, t_avoid_deflection_in)

    # Find closest (upper) gauge thickness
    gauge_dict = gd.GAUGES[material]
    thickness_warning = t_required_in >= max(gauge_dict.keys())
    t_closest_in = min(gauge_dict.keys(), 
                       key=lambda x: abs(x - t_required_in) if x >= t_required_in else float('inf')
                      ) if not thickness_warning else max(gauge_dict.keys())
    if thickness_warning:
        if display:
            print(f"WARNING! Required thickness {t_required_in:.3f}\" exceeds maximum thickness {max(gauge_dict.keys()):.3f}\" for {material}.")
        return t_required_in, None
    
    if display:
        print(f"Recommended thickness: {t_closest_in:.3f}\" ({gauge_dict[t_closest_in]} gauge {material})")

    return t_required_in, gauge_dict[t_closest_in]