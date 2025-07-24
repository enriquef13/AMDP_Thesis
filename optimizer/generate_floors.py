from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore

def obtain_APB_limits(cap):
    x_min = cap.APB_min_width
    x_max = min(cap.APB_max_width, cap.max_sheet_width - 6)
    y_min = cap.APB_min_length
    y_max = min(cap.APB_max_length, cap.max_sheet_length - 6)

    # Apply diagonal constraint
    max_diagonal = cap.APB_max_flat_diagonal
    if x_max**2 + y_max**2 > max_diagonal**2:
        x_max = min(x_max, math.sqrt(max_diagonal**2 - y_min**2))
        y_max = min(y_max, math.sqrt(max_diagonal**2 - x_min**2))

    # Apply mass constraint
    max_mass = cap.APB_max_mass / cap.density[cap.gauge_material]
    if x_max * y_max > max_mass:
        x_max = min(x_max, max_mass / y_min)
        y_max = min(y_max, max_mass / x_min)

    if cap.gauge == 16 or cap.gauge_material == "14_GLV" or cap.gauge_material == "12_GLV":
        return x_min, x_max, y_min, y_max - 5  # Ensure minimum dimensions

    # Ensure minimum dimensions
    return x_min, x_max, y_min, y_max

def obtain_MPB_limits(cap):
    x_min = 0
    x_max = cap.max_sheet_width
    y_min = 0
    y_max = cap.MPB_max_dim
    return x_min, x_max, y_min, y_max

def fill_floor_with_panels(floor_width, floor_length, x_min, x_max, y_min, y_max):
    """
    Fill a floor area with the smallest number of panels, ensuring the entire area is covered.
    Panels can be rotated to minimize the number of panels.

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        x_min (float): Minimum width of a panel.
        x_max (float): Maximum width of a panel.
        y_min (float): Minimum length of a panel.
        y_max (float): Maximum length of a panel.

    Returns:
        list: List of panel dimensions [(width, length), ...].
    """
    short_dim = min(x_min, y_min)
    long_dim = max(x_max, y_max)
    n_bottom_panels = math.ceil(floor_width / short_dim)

    bottom_length = floor_length - short_dim 
    bottom_width = floor_width / n_bottom_panels    

    n_top_panels = math.ceil(floor_width / long_dim)

    top_length = short_dim
    top_width = floor_width / n_top_panels

    panels = []
    for _ in range(n_bottom_panels):
        panels.append((bottom_width, bottom_length))
    for _ in range(n_top_panels):
        panels.append((top_width, top_length))

    return panels

def visualize_filled_floor(floor_width, floor_length, panels):
    """
    Visualize the filled floor area with panels based on the backtracking algorithm's placement logic.

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        panels (list): List of panel dimensions [(width, length), ...].
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Draw the floor boundary
    ax.set_xlim(0, floor_width)
    ax.set_ylim(0, floor_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("Floor Area Filled with Panels")
    ax.set_xlabel("Width")
    ax.set_ylabel("Length")
    
    # Place panels following the same logic as in the backtracking algorithm

    
    # Show the plot
    plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

cap = Capabilities(gd.SST, 12)
x_min, x_max, y_min, y_max = obtain_APB_limits(cap)
print(f"APB Limits: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

floor_width = cfg.x_in
floor_length = cfg.y_in
print(f"Floor dimensions: width={floor_width}, length={floor_length}")

x_min, x_max, y_min, y_max = obtain_APB_limits(cap)

panels = fill_floor_with_panels(floor_width, floor_length, x_min, x_max, y_min, y_max)

print(f"Number of panels: {len(panels)}")
print("Panel dimensions:")
for r, panel in enumerate(panels):
    print(f"Panel {r+1}: Width: {panel[0]}, Length: {panel[1]}")

# Visualize the filled floor
# visualize_filled_floor(floor_width, floor_length, panels)