from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
from matplotlib.lines import Line2D # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
import matplotlib.patches as mpatches # type: ignore
from structural_panels import calculate_floor_gauge, calculate_wall_gauge
import numpy as np # type: ignore
import math

def fill_floor_with_panels(floor_width, floor_length, cap, n_sols=5, only_vertical=False, display=False):
    """
    Fill a floor area with the smallest number of panels, ensuring the entire area is covered.
    Panels can be rotated to minimize the number of panels. (Max. floor length: 165) 

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        cap (Capabilities): Panel capabilities including dimensions and constraints.

    Returns:
        list: List of panel setups, each containing panel dimensions [(width, length), ...].
    """
    x_min, x_max, y_min, y_max = cap.obtain_APB_limits()
    if display: print(f"APB limits: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

    solutions = []  # List to store all panel setups

    # Initial panel setup
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

    # Store the initial panel setup
    solutions.append(panels)

    # Incrementally add panels to both top and bottom rows
    for increment in range(1, n_sols + 1):
        panels = []  # Reset panels for each increment

        # Increase bottom panels
        n_bottom_panels += increment
        bottom_width = floor_width / n_bottom_panels
        for _ in range(n_bottom_panels):
            panels.append((bottom_width, bottom_length))

        # Increase top panels
        if top_space > 0:
            n_top_panels += increment
            top_width = floor_width / n_top_panels
            for _ in range(n_top_panels):
                panels.append((top_width, top_length))

        # Store the new panel setup
        solutions.append(panels)

    return solutions

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

    for i in np.arange(step_size, max_width + step_size, step_size):
        gauge_row = []
        thickness_row = []
        for j in np.arange(step_size, max_length + step_size, step_size):
            thickness_required, gauge_required = calculate_floor_gauge(i, j, water_height_in, material)
            # Append NaN for gauge if below 8, but always append thickness
            gauge_row.append(gauge_required if gauge_required and gauge_required >= min_gauge else float('nan'))
            thickness_row.append(thickness_required if thickness_required else float('nan'))

        gauge_matrix.append(gauge_row)
        thickness_matrix.append(thickness_row)

    thickness_array = np.array(thickness_matrix)
    gauge_array = np.array(gauge_matrix)

    return thickness_array, gauge_array

def visualize_filled_floor(floor_width, floor_length, panels, cap, channel_spacing=None, vertical=True):
    """
    Visualize the filled floor area with panels based on the backtracking algorithm's placement logic.
    Optionally, add evenly spaced channels (vertical or horizontal) within individual panels.

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        panels (list): List of panel dimensions [(width, length), ...].
        cap (Capabilities): Panel capabilities including material and gauge.
        channel_spacing (float): Spacing between channels (inches). If None, no channels are added.
        vertical (bool): If True, channels are added vertically; otherwise, horizontally.
    """
    material = cap.material
    gauge = cap.gauge
    channel_width = 4  # Width of each channel in inches

    fig, ax = plt.subplots(figsize=(10, 6))

    # Draw the floor boundary
    ax.set_xlim(0, floor_width)
    ax.set_ylim(0, floor_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("Floor Area Filled with Panels.\nMaterial: {}, Gauge: {}".format(material, gauge), fontsize=14, fontweight='bold')
    ax.set_xlabel("Width (inches)")
    ax.set_ylabel("Length (inches)")
    
    # Place panels and add channels within each panel
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
        rect = patches.Rectangle((current_x, current_y), panel_width, panel_length, linewidth=3, 
                                  edgecolor='blue', facecolor='lightblue', alpha=0.25, linestyle='-')
        ax.add_patch(rect)
        
        # Add text to the center of the rectangle showing its dimensions
        center_x = current_x + panel_width / 2
        center_y = current_y + panel_length / 2
        if panel_width > panel_length:
            ax.text(center_x, center_y, f"{panel_width:.0f} x {panel_length:.0f}", 
                    ha='center', va='center', fontsize=16, color='black', fontweight='bold')
        else:
            ax.text(center_x, center_y, f"{panel_width:.0f} x {panel_length:.0f}", 
                    ha='center', va='center', fontsize=16, color='black', rotation=90, fontweight='bold')
        
        # Add channels within the panel if channel_spacing is provided
        if channel_spacing is not None:
            if vertical:
                # Calculate the number of vertical channels and their positions
                usable_width = panel_width - channel_width * math.ceil(panel_width / channel_spacing)
                adjusted_spacing = usable_width / math.ceil(panel_width / channel_spacing)
                for i in range(1, math.ceil(panel_width / channel_spacing)):
                    x = current_x + i * adjusted_spacing + i * channel_width
                    # Ensure channels are not placed on the panel edges
                    if x < current_x + panel_width:
                        ax.axvline(x=x, ymin=current_y / floor_length, ymax=(current_y + panel_length) / floor_length,
                                   color='red', linestyle='-', linewidth=10, alpha=0.15)
            else:
                # Calculate the number of horizontal channels and their positions
                usable_length = panel_length - channel_width * math.ceil(panel_length / channel_spacing)
                adjusted_spacing = usable_length / math.ceil(panel_length / channel_spacing)
                for i in range(1, math.ceil(panel_length / channel_spacing)):
                    y = current_y + i * adjusted_spacing + i * channel_width
                    # Ensure channels are not placed on the panel edges or seams
                    if y > current_y and y < current_y + panel_length:
                        ax.axhline(y=y, xmin=current_x / floor_width, xmax=(current_x + panel_width) / floor_width,
                                   color='red', linestyle='-', linewidth=10, alpha=0.15)

        # Move the x position for the next panel
        current_x += panel_width
        last_panel_length = panel_length

    # Add legend manually using 2D lines
    panel_legend = Line2D([0], [0], color='blue', alpha=0.5, lw=2, label='Panel')
    channel_legend = Line2D([0], [0], color='red', alpha=0.5, linestyle='--', lw=2, label='Channel')
    ax.legend(handles=[panel_legend, channel_legend], loc='upper right', fontsize=12)

    # Show the plot
    plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

def get_beam_spacing(gauge, gauge_array):
    """
    Calculate the vertical spacing for a given gauge based on the gauge array.
    This function finds the first occurrence of the specified gauge in the last row of the gauge array
    and returns the spacing in inches.

    Parameters:
        gauge (int): The gauge for which to find the vertical spacing.
        gauge_array (list): The 2D array of gauges.
        vertical (bool): If True, calculates vertical spacing; if False, horizontal spacing.

    Returns:
        int: The vertical spacing in inches for the specified gauge.
    """

    spacing = 0
    step_size = 1 / (len(gauge_array[0]) / cfg.y_in)

    for i in range(len(gauge_array)):
        curr_gauge = gauge_array[i][len(gauge_array[0]) - 1]
        if curr_gauge == gauge and spacing < i + 1:
            spacing = (i + 1) * step_size

    return spacing

thickness_array, gauge_array = get_thickness_and_gauge_array(max_width=cfg.x_in, max_length=cfg.y_in, 
                                                             step_size=1)


for gauge in [10, 12, 14, 16]:
    cap = Capabilities(cfg.material, gauge)

    spacing = get_beam_spacing(gauge, gauge_array) # Account for 3 inches of channel width

    print(f"Gauge: {gauge}, Spacing: {spacing} inches")
    floor_width = cfg.x_in
    floor_length = cfg.y_in

    solutions = fill_floor_with_panels(floor_width, floor_length, cap, only_vertical=True)
    vertical = True
    for _ in range(2):
        if vertical:
            for panels in solutions:
                visualize_filled_floor(floor_width, floor_length, panels, cap, channel_spacing=spacing, vertical=vertical)
        else:
            visualize_filled_floor(floor_width, floor_length, solutions[0], cap, channel_spacing=spacing, vertical=vertical)
        vertical = not vertical

plot_panel_thicknesses(max_width=25, max_length=160, step_size=0.1)