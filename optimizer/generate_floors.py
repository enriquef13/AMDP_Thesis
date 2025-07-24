from capabilities import Capabilities
import config as cfg
import general_data as gd
import math
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore

def obtain_APB_limits(cap):
    x_min = cap.APB_min_width
    x_max = min(cap.APB_max_width, cap.max_sheet_width)
    y_min = cap.APB_min_length
    y_max = min(cap.APB_max_length, cap.max_sheet_length)

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

    # Ensure minimum dimensions
    return x_min, x_max - 5, y_min, y_max - 5

def obtain_MPB_limits(cap):
    x_min = 0
    x_max = cap.max_sheet_width
    y_min = 0
    y_max = cap.MPB_max_dim
    return x_min, x_max, y_min, y_max


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
    placed_panels = []
    panel_index = 0
    current_x = 0
    current_y = 0
    remaining_width = floor_width
    remaining_length = floor_length
    
    while panel_index < len(panels):
        panel_width, panel_length = panels[panel_index]
        panel_index += 1
        
        # Place the panel
        rect = patches.Rectangle((current_x, current_y), panel_width, panel_length,
                                  edgecolor='black', facecolor='lightblue', alpha=0.8)
        ax.add_patch(rect)
        
        # Add text label showing dimensions
        ax.text(current_x + panel_width/2, current_y + panel_length/2, 
                f"{panel_width}x{panel_length}", 
                horizontalalignment='center', verticalalignment='center')
        
        placed_panels.append((current_x, current_y, panel_width, panel_length))
        
        # Update remaining width
        remaining_width -= panel_width
        
        # Check if we need to move to the next row
        if remaining_width <= 0 and panel_index < len(panels):
            current_x = 0
            current_y += panel_length
            remaining_width = floor_width
            remaining_length -= panel_length
        else:
            current_x += panel_width
    
    # Show the plot
    plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

cap = Capabilities(gd.SST, 12)
x_min, x_max, y_min, y_max = obtain_APB_limits(cap)
print(f"APB Limits: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

floor_width = cfg.x_in
floor_length = cfg.y_in
panels = fill_floor_with_panels(floor_width, floor_length, x_min, x_max, y_min, y_max)

print(f"Number of panels: {len(panels)}")
print("Panel dimensions:")
for panel in panels:
    print(f"Width: {panel[0]}, Length: {panel[1]}")

# Visualize the filled floor
visualize_filled_floor(floor_width, floor_length, panels)