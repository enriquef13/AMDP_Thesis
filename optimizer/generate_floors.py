from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore

def obtain_APB_limits(cap):
    x_min = cap.APB_min_width
    x_max = min(cap.APB_max_width, cap.max_sheet_width - 10)
    y_min = cap.APB_min_length
    y_max = min(cap.APB_max_length, cap.max_sheet_length - 10)

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

def fill_floor_with_panels(floor_width, floor_length, cap):
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

    x_min, x_max, y_min, y_max = obtain_APB_limits(cap)

    panels = []

    n_bottom_panels = math.ceil(floor_width / x_max)
    bottom_space = floor_length if floor_length <= y_max else y_max
    top_space = floor_length - bottom_space

    bottom_length = bottom_space if top_space >= y_min or top_space <= 0 else bottom_space - (y_min - top_space)
    bottom_width = floor_width / n_bottom_panels    

    for _ in range(n_bottom_panels):
        panels.append((bottom_width, bottom_length))

    if top_space > 0:
        top_orientation = 'horizontal' if top_space >= x_min and top_space <= x_max else 'vertical'
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

for material in [gd.SST, gd.GLV]:
    for gauge in [10, 12, 14, 16]:
        cap = Capabilities(material, gauge)
    
        floor_width = cfg.x_in
        floor_length = cfg.y_in

        panels = fill_floor_with_panels(floor_width, floor_length, cap)
        visualize_filled_floor(floor_width, floor_length, panels, cap)