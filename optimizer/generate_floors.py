from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
from structural_panels import calculate_floor_gauge

def fill_floor_with_panels(floor_width, floor_length, cap, only_vertical=False):
    """
    Fill a floor area with the smallest number of panels, ensuring the entire area is covered.
    Panels can be rotated to minimize the number of panels. (Max. floor length: 165) 

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        cap (Capabilities): Panel capabilities including dimensions and constraints.

    Returns:
        list: List of panel dimensions [(width, length), ...].
    """

    x_min, x_max, y_min, y_max = cap.obtain_APB_limits()
    print(f"APB limits: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

    panels = []

    n_bottom_panels = math.ceil(floor_width / x_max)
    bottom_space = floor_length if floor_length <= y_max else y_max
    top_space = floor_length - bottom_space

    bottom_length = bottom_space if top_space >= y_min or top_space <= 0 else bottom_space - (y_min - top_space)
    bottom_width = floor_width / n_bottom_panels    

    for _ in range(n_bottom_panels):
        panels.append((bottom_width, bottom_length))

    if top_space > 0:
        top_space = floor_length - bottom_length
        top_orientation = 'horizontal' if top_space >= x_min and top_space <= x_max else 'vertical'
        if only_vertical: top_orientation = 'vertical'
        if top_orientation == 'horizontal':
            n_top_panels = math.ceil(floor_width / y_max)
            top_length = top_space if top_space >= x_min and top_space <= x_max else x_max
            top_width = floor_width / n_top_panels
        else:
            n_top_panels = math.ceil(floor_width / x_max)
            top_length = top_space if top_space >= y_min and top_space <= y_max else y_max
            top_width = floor_width / n_top_panels

        for _ in range(n_top_panels):
            panels.append((top_width, top_length))

    return panels

def max_panel_length_for_gauge(water_height_in, material=gd.SST, gauge=16):
    """
    Get the maximum panel dimensions for a given gauge and water height.

    Parameters:
        water_height_in (float): Height of water inside the panel (inches).
        material (str): Material type (SST or GLV).
        gauge (int): Gauge number.

    Returns:
        tuple: Maximum panel dimensions (width, length) in inches.
    """
    min_width = 1
    min_length = 1
    max_width = 50
    max_length = 500

    last_gauge = 100
    max_panel_length = 0
    max_panel_width = 0
    for i in range(min_length, max_length + 1):
        for j in range(min_width, max_width + 1):
            gauge_required = calculate_floor_gauge(j, i, water_height_in, material)
            last_gauge = gauge_required if gauge_required else last_gauge
            if max_panel_length < i: max_panel_length = i
            if max_panel_width < j: max_panel_width = j
            if gauge > last_gauge:
                print(f"Maximum panel dimensions for gauge {gauge} and water height {water_height_in}: {max_panel_width} x {max_panel_length}")
                return (max_panel_width, max_panel_length)

    return None


def visualize_filled_floor(floor_width, floor_length, panels, cap):
    """
    Visualize the filled floor area with panels based on the backtracking algorithm's placement logic.

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        panels (list): List of panel dimensions [(width, length), ...].
    """
    material = cap.material
    gauge = cap.gauge

    fig, ax = plt.subplots(figsize=(10, 6))

    # Draw the floor boundary
    ax.set_xlim(0, floor_width)
    ax.set_ylim(0, floor_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("Floor Area Filled with Panels. Material: {}, Gauge: {}".format(material, gauge), fontsize=14, fontweight='bold')
    ax.set_xlabel("Width")
    ax.set_ylabel("Length")
    
    # Place panels following the same logic as in the backtracking algorithm
    current_x = 0
    current_y = 0
    for panel in panels:
        panel_width, panel_length = panel
        
        # Check if the panel fits in the current row
        if current_x + panel_width > floor_width:
            # Move to the next row
            current_x = 0
            current_y += last_panel_length

        # Draw the panel as a rectangle
        rect = patches.Rectangle((current_x, current_y), panel_width, panel_length, linewidth=1, 
                     edgecolor='blue', facecolor='lightblue', alpha=0.5)
        ax.add_patch(rect)
        
        # Add text to the center of the rectangle showing its dimensions
        center_x = current_x + panel_width / 2
        center_y = current_y + panel_length / 2
        if panel_width > panel_length:
            ax.text(center_x, center_y, f"{panel_width:.0f} x {panel_length:.0f}", 
                ha='center', va='center', fontsize=16, color='black')
        else:
            ax.text(center_x, center_y, f"{panel_width:.0f} x {panel_length:.0f}", 
                ha='center', va='center', fontsize=16, color='black', rotation=90)
        
        # Move the x position for the next panel
        current_x += panel_width
        last_panel_length = panel_length
    
    # Show the plot
    plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

# for material in [gd.SST, gd.GLV]:
#     for gauge in [10, 12, 14, 16]:
#         # material = cfg.material
#         # gauge = 16
#         cap = Capabilities(material, gauge)

#         floor_width = cfg.x_in
#         floor_length = cfg.y_in

#         panels = fill_floor_with_panels(floor_width, floor_length, cap, only_vertical=True)
#         visualize_filled_floor(floor_width, floor_length, panels, cap)

max_panel_length_for_gauge(cfg.water_height_in, material=cfg.material, gauge=10)
calculate_floor_gauge(101, 24, cfg.water_height_in, material=cfg.material, display=True)