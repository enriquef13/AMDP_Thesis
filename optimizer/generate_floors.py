from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
from matplotlib.lines import Line2D # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
from structural_panels import calculate_floor_gauge, calculate_wall_gauge
import numpy as np # type: ignore
import math

def fill_floor_with_panels(gauge, floor_width=cfg.x_in, floor_length=cfg.y_in, n_sols=1, display=False):
    """
    Fill a floor area with the smallest number of panels, ensuring the entire area is covered.
    Panels can be rotated to minimize the number of panels. (Max. floor length: 165) 

    Parameters:
        gauge (float): Panel gauge.
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        n_sols (int): Number of solutions to generate.
        display (bool): If True, displays the filled floor area.

    Returns:
        list: List of panel setups, each containing panel dimensions [(width, length), ...].
    """
    cap = Capabilities(cfg.material, gauge)
    x_min, x_max, y_min, y_max = cap.obtain_APB_limits()
    if display: print(f"APB limits: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

    panel_setups = []
    panels = []

    n_bottom_panels = math.ceil(floor_width / x_max)
    bottom_space = floor_length if floor_length <= y_max else y_max
    top_space = floor_length - bottom_space

    bottom_length = bottom_space if top_space >= y_min or top_space <= 0 else bottom_space - (y_min - top_space)
    bottom_width = floor_width / n_bottom_panels
    panel_weight = bottom_width * bottom_length * cap.density[cap.gauge_material]    

    for _ in range(n_bottom_panels):
        panels.append((bottom_width, bottom_length, panel_weight))

    if top_space > 0:
        top_space = floor_length - bottom_length
        n_top_panels = math.ceil(floor_width / x_max)
        top_length = top_space if top_space >= y_min and top_space <= y_max else y_max
        top_width = floor_width / n_top_panels
        panel_weight = top_width * top_length * cap.density[cap.gauge_material]

        for _ in range(n_top_panels):
            panels.append((top_width, top_length, panel_weight))

    # Store the initial panel setup
    panel_setups.append(panels)

    # Incrementally add panels to both top and bottom rows
    for _ in range(1, n_sols + 1):
        panels = []  # Reset panels for each increment

        # Increase bottom panels
        n_bottom_panels += 1
        bottom_width = floor_width / n_bottom_panels
        panel_weight = bottom_width * bottom_length * cap.density[cap.gauge_material]
        if bottom_width < x_min:
            continue
        
        for _ in range(n_bottom_panels):
            panels.append((bottom_width, bottom_length, panel_weight))

        if top_space > 0:
            n_top_panels += 1
            top_width = floor_width / n_top_panels
            panel_weight = top_width * top_length * cap.density[cap.gauge_material]
            for _ in range(n_top_panels):
                panels.append((top_width, top_length, panel_weight))

        # Store the new panel setup
        panel_setups.append(panels)

    top_solutions = []
    for panels in panel_setups:
        channels = _obtain_channels(panels=panels, gauge=cap.gauge, vertical=True)
        top_solutions.append({
            'panels': panels,
            'channels': channels,
            'cap': cap
        })

    return top_solutions if n_sols > 1 else top_solutions[0]

def plot_panel_thicknesses(max_width=cfg.x_in, max_length=cfg.y_in, step_size=1, 
                           water_height_in=cfg.water_height_in, material=cfg.material,
                           floor=True):
    """
    Plots heatmaps showing the required panel thickness and gauge for a range of panel dimensions,
    given a water height and material. Useful for visualizing how panel size affects required gauge and thickness.

    Parameters:
        max_width (float): Maximum width of the panel (inches).
        max_length (float): Maximum length of the panel (inches).
        step_size (float): Step size for generating dimensions.
        water_height_in (float): Height of water inside the panel (inches).
        material (str): Material type (e.g., SST-M3 or GLV-M5).

    Returns:
        None
    """
    min_gauge = min(gd.GAUGES[material].values())
    max_gauge = max(gd.GAUGES[material].values())

    # Initialize 2D arrays to store gauge and thickness values
    thickness_array, gauge_array = _get_thickness_and_gauge_array(max_width=max_width, max_length=max_length, 
                                                                 step_size=step_size, water_height_in=water_height_in, 
                                                                 material=material, floor=floor)
    
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

def _get_thickness_and_gauge_array(max_width=cfg.x_in, max_length=cfg.y_in, step_size=1, 
                                  water_height_in=cfg.water_height_in, material=cfg.material,
                                  floor=True):
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
            if floor:
                thickness_required, gauge_required = calculate_floor_gauge(i, j, water_height_in, material)
            else:
                thickness_required, gauge_required = calculate_wall_gauge(i, j, water_height_in, wind_zone=cfg.wind_zone, material=material)
            gauge_row.append(gauge_required if gauge_required and gauge_required >= min_gauge else float('nan'))
            thickness_row.append(thickness_required if thickness_required else float('nan'))

        gauge_matrix.append(gauge_row)
        thickness_matrix.append(thickness_row)

    thickness_array = np.array(thickness_matrix)
    gauge_array = np.array(gauge_matrix)

    return thickness_array, gauge_array

def _obtain_channels(panels, gauge, floor_width=cfg.x_in, floor_length=cfg.y_in, step_size=1, vertical=True):
    channel_width = gd.FLOOR_BEAMS.profile['b']
    channel_perimeter = gd.FLOOR_BEAMS.perimeter
    c_cap = Capabilities(material=gd.FLOOR_BEAMS.material, gauge=gauge)
    channel_density = c_cap.density[c_cap.gauge_material]

    _, gauge_array = _get_thickness_and_gauge_array(max_width=floor_width, 
                                                   max_length=floor_length, 
                                                   step_size=step_size)
    
    spacing = 0
    for i in range(len(gauge_array)):
        curr_gauge = gauge_array[i][len(gauge_array[0]) - 1]
        if curr_gauge == gauge and spacing < i + 1:
            spacing = (i + 1) * step_size

    current_x = 0
    current_y = 0
    last_panel_length = 0

    channels = []
    for panel in panels:
        panel_width, panel_length, panel_weight = panel

        if current_x + panel_width > floor_width + 0.01:  # Allow a small tolerance for floating point errors
            current_x = 0
            current_y += last_panel_length
        
        if vertical and current_y == 0:
            # Calculate the number of vertical channels and their positions
            usable_width = panel_width - channel_width * math.ceil(panel_width / spacing)
            adjusted_spacing = usable_width / math.ceil(panel_width / spacing)
            for i in range(1, math.ceil(panel_width / spacing)):
                x = current_x + i * adjusted_spacing + i * channel_width
                # Ensure channels are not placed on the panel edges
                if x < current_x + panel_width:
                    channel_weight = channel_perimeter * floor_length * channel_density
                    channels.append([x, floor_length, channel_weight])
                
        elif not vertical and current_x == 0:
            # Calculate the number of horizontal channels and their positions
            usable_length = panel_length - channel_width * math.ceil(panel_length / spacing)
            adjusted_spacing = usable_length / math.ceil(panel_length / spacing)
            for i in range(1, math.ceil(panel_length / spacing)):
                y = current_y + i * adjusted_spacing + i * channel_width
                # Ensure channels are not placed on the panel edges or seams
                if y > current_y and y < current_y + panel_length:
                    channel_weight = channel_perimeter * floor_width * channel_density
                    channels.append([y, floor_width, channel_weight])

        current_x += panel_width
        last_panel_length = panel_length

    return channels

def _get_panel_and_channel_weights(panels, channels):
    """
    Calculate the total weight of panels and channels.
    
    Parameters:
        panels (list): List of panel dimensions [(width, length, weight), ...].
        channels (list): List of channel dimensions [(x, length, weight), ...].
    Returns:
        tuple: Total weight of panels and channels.
    """
    panel_weights = sum(panel[2] for panel in panels)  # Sum panel weights
    channel_weights = sum(channel[2] for channel in channels)  # Sum channel weights
    return panel_weights, channel_weights

def visualize_filled_floor(floor, design_name="", floor_width=cfg.x_in, floor_length=cfg.y_in, add_channels=True, 
                           vertical=True, step_size=1, metrics=True):
    """
    Visualize the filled floor area with panels based on the backtracking algorithm's placement logic.
    Optionally, add evenly spaced channels (vertical or horizontal) within individual panels.

    Parameters:
        floor_width (float): Width of the floor area.
        floor_length (float): Length of the floor area.
        panels (list): List of panel dimensions [(width, length), ...].
        gauge_array (numpy.ndarray): 2D array of gauge values for the panels.
        cap (Capabilities): Panel capabilities including material and gauge.
        add_channels (bool): If True, channels are added within panels.
        vertical (bool): If True, channels are added vertically; otherwise, horizontally.
    """
    panels = floor['panels']
    channels = floor['channels']
    cap = floor['cap']

    material = cfg.material
    gauge = cap.gauge

    fig, ax = plt.subplots(figsize=(10, 6))

    # Draw the floor boundary
    ax.set_xlim(0, floor_width)
    ax.set_ylim(0, floor_length)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("Width (inches)")
    ax.set_ylabel("Length (inches)")
    
    current_x = 0
    current_y = 0

    for panel in panels:
        panel_width, panel_length, _ = panel
        
        # Check if the panel fits in the current row
        if current_x + panel_width > floor_width + 0.01:  # Allow a small tolerance for floating point errors
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
        
        # Move the x position for the next panel
        current_x += panel_width
        last_panel_length = panel_length

    if add_channels:
        channels = _obtain_channels(panels, gauge=gauge, vertical=vertical, step_size=step_size)
        for channel in channels:
            if vertical:
                x, length, _ = channel
                ax.axvline(x=x, ymin=0, ymax=length,
                            color='red', linestyle='-', linewidth=10, alpha=0.15)
            else:
                y, length, _ = channel
                ax.axhline(y=y, xmin=0, xmax=length,
                            color='red', linestyle='-', linewidth=10, alpha=0.15)

    # Add legend manually using 2D lines
    panel_legend = Line2D([0], [0], color='blue', alpha=0.5, lw=2, label='Panel')
    channel_legend = Line2D([0], [0], color='red', alpha=0.5, linestyle='--', lw=2, label='Channel')
    ax.legend(handles=[panel_legend, channel_legend], loc='lower right', fontsize=12)

    # Title and subtitle
    title = f"Design {design_name}"
    fig.suptitle(title, fontsize=18, fontweight='bold', y=0.95)

    if metrics:
        panel_weights, channel_weights = _get_panel_and_channel_weights(panels, channels)

        channel_gauge = gd.FLOOR_BEAMS.gauge
        channel_material = gd.FLOOR_BEAMS.material
        channel_type = gd.FLOOR_BEAMS.profile_type

        channel_info = (
            f"Channel: {channel_gauge} ga {channel_material} {channel_type}-Profile, "
            f"Mass: {channel_weights:.1f} lb"
        )
        panel_info = (
            f"Panel: {gauge} ga {material}, "
            f"Mass: {panel_weights:.1f} lb"
        )
        total_mass = channel_weights + panel_weights
        channel_ratio = int(round(100 * channel_weights / total_mass))
        panel_ratio = 100 - channel_ratio
        usage_info = (
            f"Total Mass: {total_mass:.1f} lb"
        )
        # Add colored ratio text with adjusted positions to avoid overlap
        text_y = 0.80
        fig.text(0.5, text_y + 0.08, channel_info, fontsize=14, ha='center', va='top', color='red')
        fig.text(0.5, text_y + 0.04, panel_info, fontsize=14, ha='center', va='top', color='blue')
        # Use separate fig.text for colored ratios
        fig.text(0.45, text_y, f"{usage_info}   Mass Ratio: ", fontsize=14, ha='center', va='top', color='black')
        fig.text(0.63, text_y, f"{channel_ratio}%", fontsize=14, ha='left', va='top', color='red')
        fig.text(0.68, text_y, " | ", fontsize=14, ha='left', va='top', color='black')
        fig.text(0.70, text_y, f"{panel_ratio}%", fontsize=14, ha='left', va='top', color='blue')

        plt.subplots_adjust(top=0.75)  # Adjust top margin to fit the text

    # Show the plot
    plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

"""
n_sols = 1
top_floors = []
for gauge in [10, 12, 14, 16, 18]:
    floors = fill_floor_with_panels(gauge, n_sols=20)
    top_floors.extend(floors)

print(f"Found {len(top_floors)} solutions. Showing top {n_sols} in terms of weight.")
top_floors = sorted(top_floors, 
                    key=lambda x: sum(panel[2] for panel in x['panels']) + sum(channel[2] for channel in x['channels']))[:n_sols] 

for i, floor in enumerate(top_floors, start=1):
    visualize_filled_floor(floor, add_channels=True, vertical=True, design_name=str(i))
"""