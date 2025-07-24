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

    if cap.gauge == 16 or cap.gauge_material == "14_GLV" or cap.gauge_material == "12_GLV":
        return x_min, x_max - 5, y_min, y_max - 5  # Ensure minimum dimensions

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
    Fills a rectangular area with panels, minimizing the number of panels used.
    This is a recursive tiling algorithm optimized for this problem.
    """
    
    # The grid represents the floor. 0 = empty, 1 = filled.
    grid = [[0 for _ in range(floor_width)] for _ in range(floor_length)]
    
    # Memoization cache to store results for subproblems
    memo = {}

    def solve(current_panels_count):
        # --- 1. Find the first empty cell (top-left most) ---
        first_empty = None
        for r in range(floor_length):
            for c in range(floor_width):
                if grid[r][c] == 0:
                    first_empty = (r, c)
                    break
            if first_empty:
                break
        
        # If no empty cell, we have a complete solution
        if not first_empty:
            return current_panels_count
        
        r, c = first_empty

        # --- Memoization Check ---
        # Create a tuple key representing the remaining shape (simplified)
        subproblem_key = (floor_length - r, floor_width - c)
        if subproblem_key in memo and memo[subproblem_key] <= current_panels_count:
             return float('inf') # Prune this path

        min_found = float('inf')

        # --- 2. Determine max possible width/height for a new panel ---
        max_h = 0
        while r + max_h < floor_length and grid[r + max_h][c] == 0:
            max_h += 1
        
        max_w = 0
        while c + max_w < floor_width and grid[r][c + max_w] == 0:
            max_w += 1

        # --- 3. Iterate through possible panel sizes (largest first) ---
        # Prioritize placing panels that fill the entire available width or height
        # This is a heuristic to reduce creating complex empty shapes.
        
        # Try filling the width
        for w in range(min(max_w, x_max), int(x_min) - 1, -1):
            for h in range(min(max_h, y_max), int(y_min) - 1, -1):
                if is_valid_placement(r, c, h, w):
                    place_panel(r, c, h, w, 1) # Place
                    result = solve(current_panels_count + 1)
                    min_found = min(min_found, result)
                    place_panel(r, c, h, w, 0) # Backtrack

        # Try filling the height (with rotated panels)
        for h in range(min(max_h, x_max), int(x_min) - 1, -1):
            for w in range(min(max_w, y_max), int(y_min) - 1, -1):
                if is_valid_placement(r, c, h, w):
                    place_panel(r, c, h, w, 1) # Place
                    result = solve(current_panels_count + 1)
                    min_found = min(min_found, result)
                    place_panel(r, c, h, w, 0) # Backtrack
        
        memo[subproblem_key] = min_found
        return min_found

    def is_valid_placement(r, c, h, w):
        # Check if the rectangle is empty
        for i in range(r, r + h):
            for j in range(c, c + w):
                if grid[i][j] == 1:
                    return False
        return True

    def place_panel(r, c, h, w, val):
        # Place or remove a panel from the grid
        for i in range(r, r + h):
            for j in range(c, c + w):
                grid[i][j] = val

    # This is a simplified version. For a true optimal solution, you'd need to
    # reconstruct the path. This implementation finds the minimum number of panels.
    # Reconstructing the panel list requires modifying `solve` to return the panel layout.
    # For now, let's focus on a working, optimized core logic.
    
    # The following is a placeholder for the greedy approach which is more likely to finish
    # and can be used until the recursive solver is fully implemented to return the panel list.
    print("Warning: Using a more stable greedy approach for now.")
    return greedy_fill_floor(floor_width, floor_length, x_min, x_max, y_min, y_max)


def greedy_fill_floor(floor_width, floor_length, x_min, x_max, y_min, y_max):
    """
    A robust greedy approach that fills the floor row by row.
    """
    panels = []
    current_y = 0
    while current_y < floor_length:
        current_x = 0
        # Determine the height of the current row, constrained by y_max
        row_height = min(y_max, floor_length - current_y)
        if row_height < y_min: break # Cannot fit any more rows

        while current_x < floor_width:
            remaining_width = floor_width - current_x
            
            # Find the best panel (w, h) to place at (current_x, current_y)
            best_panel = None
            best_area = -1

            # Option 1: Normal orientation
            w = min(x_max, remaining_width)
            h = row_height
            if w >= x_min:
                best_panel = (w, h)
                best_area = w * h

            # Option 2: Rotated orientation
            w_rot = min(y_max, remaining_width)
            h_rot = row_height
            # Check if rotated panel is valid and better
            if w_rot >= y_min and h_rot >= x_min and h_rot <= x_max:
                if w_rot * h_rot > best_area:
                    best_panel = (w_rot, h_rot)

            if best_panel:
                panels.append(best_panel)
                current_x += best_panel[0]
            else:
                break # Cannot fit any more panels in this row
        
        current_y += row_height
    return panels

def greedy_fill_floor(floor_width, floor_length, x_min, x_max, y_min, y_max):
    """
    Simple greedy approach to fill floor with valid panels when backtracking fails.
    Allows for panel rotation.
    """
    panels = []
    current_y = 0
    
    while current_y < floor_length:
        current_x = 0
        
        while current_x < floor_width:
            remaining_width = floor_width - current_x
            remaining_length = floor_length - current_y
            
            # Try different panel options and choose the best one
            best_panel = None
            best_area = 0
            
            # Normal orientation
            for w in range(int(min(x_max, remaining_width)), int(x_min) - 1, -1):
                for l in range(int(min(y_max, remaining_length)), int(y_min) - 1, -1):
                    if x_min <= w <= x_max and y_min <= l <= y_max:
                        area = w * l
                        if area > best_area:
                            best_area = area
                            best_panel = (w, l)
            
            # Rotated orientation
            for l in range(int(min(x_max, remaining_length)), int(x_min) - 1, -1):
                for w in range(int(min(y_max, remaining_width)), int(y_min) - 1, -1):
                    if y_min <= w <= y_max and x_min <= l <= x_max:
                        area = w * l
                        if area > best_area:
                            best_area = area
                            best_panel = (w, l)
            
            # If we found a panel that fits, add it
            if best_panel:
                panels.append(best_panel)
                current_x += best_panel[0]
            else:
                # No panel fits, move to next row
                break
                
        # Move to next row
        if current_x > 0:  # If we placed at least one panel in this row
            row_height = max(panel[1] for panel in panels if panels.index(panel) >= len(panels) - (current_x // min(x_min, y_min)))
            current_y += row_height
        else:
            # If we couldn't place any panel, we're done
            break
    
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

# cap = Capabilities(gd.SST, 12)
# x_min, x_max, y_min, y_max = obtain_APB_limits(cap)
# print(f"APB Limits: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")

# floor_width = cfg.x_in
# floor_length = cfg.y_in
# panels = fill_floor_with_panels(floor_width, floor_length, x_min, x_max, y_min, y_max)

# print(f"Number of panels: {len(panels)}")
# print("Panel dimensions:")
# for panel in panels:
#     print(f"Width: {panel[0]}, Length: {panel[1]}")

# # Visualize the filled floor
# visualize_filled_floor(floor_width, floor_length, panels)