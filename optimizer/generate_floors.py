from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
from structural_panels import calculate_floor_gauge, calculate_wall_gauge
import numpy as np

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

def plot_panel_thicknesses(max_width, max_length, step_size=1, water_height_in=cfg.water_height_in, material=cfg.material):
    """
    Plots heatmaps showing the required panel thickness and gauge for a range of panel dimensions,
    given a water height and material. Useful for visualizing how panel size affects required gauge and thickness.

    Parameters:
        water_height_in (float): Height of water inside the panel (inches).
        material (str): Material type (e.g., SST or GLV).

    Returns:
        None
    """
    min_gauge = min(gd.GAUGES[material].values())
    max_gauge = max(gd.GAUGES[material].values())

    # Initialize 2D arrays to store gauge and thickness values
    thickness_array, gauge_array = get_thickness_and_gauge_array(max_width=max_width, max_length=max_length, 
                                                                 step_size=step_size, water_height_in=water_height_in, 
                                                                 material=material)
    
    thickness_array = np.transpose(thickness_array)
    gauge_array = np.transpose(gauge_array)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    title_font_size = 16
    label_font_size = 14
    axes_font_size = 12

    # Plot thickness heatmap
    ax1 = axes[0]
    im1 = ax1.imshow(thickness_array, origin='lower', cmap='viridis',
                     extent=[1, max_width, 1, max_length], aspect='auto')
    ax1.set_title(f'Heatmap of Required Thickness.\nMaterial: {material}, Water Level: {water_height_in}\"', 
                  fontsize=title_font_size, fontweight='bold')
    ax1.set_xlabel('Floor Width (inches)', fontsize=label_font_size)
    ax1.set_ylabel('Floor Length (inches)', fontsize=label_font_size)
    ax1.tick_params(axis='both', labelsize=axes_font_size)
    cbar1 = fig.colorbar(im1, ax=ax1)
    cbar1.set_label('Thickness (inches)', fontsize=label_font_size)
    cbar1.ax.tick_params(labelsize=axes_font_size)

    # Plot gauge heatmap
    ax2 = axes[1]
    im2 = ax2.imshow(gauge_array, origin='lower', cmap='viridis',
                     extent=[1, max_width, 1, max_length], vmin=min_gauge, vmax=max_gauge, aspect='auto')
    ax2.set_title(f'Heatmap of Gauge Required.\nMaterial: {material}, Water Level: {water_height_in}\"', 
                  fontsize=title_font_size, fontweight='bold')
    ax2.set_xlabel('Floor Width (inches)', fontsize=label_font_size)
    ax2.set_ylabel('Floor Length (inches)', fontsize=label_font_size)
    ax2.tick_params(axis='both', labelsize=axes_font_size)
    cbar2 = fig.colorbar(im2, ax=ax2)
    cbar2.set_label('Gauge', fontsize=label_font_size)
    cbar2.ax.tick_params(labelsize=axes_font_size)

    plt.tight_layout()
    plt.show()

def get_thickness_and_gauge_array(max_width, max_length, step_size=1, water_height_in=cfg.water_height_in, material=cfg.material):
    """
    Generate a 2D array of required thickness and gauge for a range of panel dimensions.

    Parameters:
        max_width (float): Maximum width of the panel (inches).
        max_length (float): Maximum length of the panel (inches).
        step_size (float): Step size for generating dimensions.
        water_height_in (float): Height of water inside the panel (inches).
        material (str): Material type (e.g., SST or GLV).

    Returns:
        tuple: Two 2D numpy arrays for thickness and gauge.
    """
    gauge_matrix = []
    thickness_matrix = []

    min_gauge = min(gd.GAUGES[material].values())

    for i in np.arange(1, max_width + step_size, step_size):
        gauge_row = []
        thickness_row = []
        for j in np.arange(1, max_length + step_size, step_size):
            thickness_required, gauge_required = calculate_floor_gauge(i, j, water_height_in, material)
            # Append NaN for gauge if below 8, but always append thickness
            gauge_row.append(gauge_required if gauge_required and gauge_required >= min_gauge else float('nan'))
            thickness_row.append(thickness_required if thickness_required else float('nan'))

        gauge_matrix.append(gauge_row)
        thickness_matrix.append(thickness_row)

    thickness_array = np.array(thickness_matrix)
    gauge_array = np.array(gauge_matrix)

    return thickness_array, gauge_array

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
    ax.set_title("Floor Area Filled with Panels.\nMaterial: {}, Gauge: {}".format(material, gauge), fontsize=14, fontweight='bold')
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

thickness_array, gauge_array = get_thickness_and_gauge_array(max_width=cfg.x_in, max_length=cfg.y_in, 
                                                             step_size=1)



for material in [gd.SST, gd.GLV]:
    for gauge in [10, 12, 14, 16]:
        cap = Capabilities(material, gauge)



        floor_width = cfg.x_in
        floor_length = cfg.y_in

        panels = fill_floor_with_panels(floor_width, floor_length, cap, only_vertical=False)
        visualize_filled_floor(floor_width, floor_length, panels, cap)

plot_panel_thicknesses(max_width=cfg.x_in, max_length=cfg.y_in, step_size=1)