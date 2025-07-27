"""
Code to generate structural frames based on given dimensions and constraints.
Generates structurally-feasible configurations of nodes and members within specified limits.
"""
import numpy as np # type: ignore
from structural_frames import calculate_wall_frame_structural, distribute_load
from capabilities import Capabilities
from profiles import Profile
import config as cfg
import general_data as gd
from structural_panels import calculate_wall_gauge
import itertools
import pandas as pd # type: ignore


def generate_frame(x, z, channel_type, panel_material, num_nodes=12, display=False, diagonal_plan="A"):
    """
    Generate a configuration of nodes and members.
    """
    if x == cfg.x_in: wall_type = 'X'
    else: wall_type = 'Y'
    corner_nodes = {0: [0, 0], 1: [x, 0], 2: [0, z], 3: [x, z]}

    num_remaining_nodes = num_nodes - len(corner_nodes)
    nodes = corner_nodes.copy()

    # Ensure symmetry
    if num_remaining_nodes > 0:
        if num_remaining_nodes % 2 == 0:
            num_remaining_nodes -= 1
        num_top_bot_nodes = num_remaining_nodes // 2
        start_len = len(nodes)
        for i in range(num_top_bot_nodes):
            pos_x = x / (num_top_bot_nodes + 1) * (i + 1)
            nodes[start_len + i] = [pos_x, 0]
            nodes[start_len + i + num_top_bot_nodes] = [pos_x, z]
        num_remaining_nodes -= num_top_bot_nodes * 2

    # Sort nodes and classify by edge
    sorted_nodes = dict(sorted(nodes.items(), key=lambda item: (item[1][1], item[1][0])))
    left_id_nodes = [idx for idx, n in sorted_nodes.items() if n[0] == 0]
    right_id_nodes = [idx for idx, n in sorted_nodes.items() if n[0] == x]
    top_id_nodes = [idx for idx, n in sorted_nodes.items() if n[1] == z]
    bottom_id_nodes = [idx for idx, n in sorted_nodes.items() if n[1] == 0]

    # Vertical and horizontal members
    vertical_pairs = [[bottom_id_nodes[i], top_id_nodes[i]] for i in range(len(bottom_id_nodes))]
    horizontal_pairs = []
    for i in range(len(bottom_id_nodes) - 1):
        horizontal_pairs.append([bottom_id_nodes[i], bottom_id_nodes[i + 1]])
    for i in range(len(top_id_nodes) - 1):
        horizontal_pairs.append([top_id_nodes[i], top_id_nodes[i + 1]])
    member_pairs = vertical_pairs + horizontal_pairs

    # Diagonals based on plan
    diagonal_pairs = _add_diagonals(nodes, bottom_id_nodes, top_id_nodes, member_pairs, plan=diagonal_plan)
    member_pairs += diagonal_pairs

    # Check if a top node is exactly at x midpoint
    x_mid = (max(n[0] for n in nodes.values()) + min(n[0] for n in nodes.values())) / 2.0
    has_center_top_node = any(abs(nodes[idx][0] - x_mid) < 1e-6 for idx in top_id_nodes)
    if has_center_top_node:
        # Fall back to Plan B
        diagonal_plan = "B"

    # Panel and material calculations
    # 1. Distance between vertical members = panel length
    x_positions = sorted([nodes[idx][0] for idx in bottom_id_nodes])
    width_between_nodes = x_positions[1] - x_positions[0]
    panel_height = z

    # Adjust panel length based on diagonal plan
    if diagonal_plan == "A":
        panel_width = width_between_nodes  
    elif diagonal_plan == "B":
        panel_width = width_between_nodes / 2
    elif diagonal_plan == "C":
        panel_width = width_between_nodes / 3
    elif diagonal_plan == "D":
        panel_width = width_between_nodes
    else:
        raise ValueError(f"Unknown diagonal plan '{diagonal_plan}'")

    _, wall_gauge = calculate_wall_gauge(panel_width, panel_height, cfg.water_height_in, wind_zone=cfg.wind_zone, material=panel_material)
    if wall_gauge < 10 or wall_gauge is None:
        raise ValueError("Calculated wall gauge is too thick.")
    cap = Capabilities(cfg.material, wall_gauge)
    min_height, max_height, min_width, max_width = cap.obtain_APB_limits()
    n_panels = int(np.ceil(x / max_width))
    panel_width = x / n_panels
    if (panel_width > max_width or panel_width < min_width or 
       panel_height < min_height or panel_height > max_height):
        raise ValueError("Panel dimensions outside of APB limits")

    # Material usage
    material = channel_type.material
    member_gauge = channel_type.gauge
    member_profile = channel_type.profile_type
    cap = Capabilities(material, member_gauge)
    member_width = channel_type.width
    member_density = cap.density[cap.gauge_material]

    total_member_mass = 0.0
    for pair in member_pairs:
        n1, n2 = nodes[pair[0]], nodes[pair[1]]
        length = np.linalg.norm(np.array(n1) - np.array(n2))
        mass = length * member_width * member_density
        total_member_mass += mass

    total_panel_area = n_panels * panel_width * panel_height
    cap = Capabilities(material, wall_gauge)
    panel_density = cap.density[cap.gauge_material]
    total_panel_mass = total_panel_area * panel_density

    total_mass = total_member_mass + total_panel_mass
    weight = 5
    weighted_total_mass = weight * total_member_mass + total_panel_mass

    frame = [
        nodes.copy(),
        member_pairs.copy(),
        {
            "n_panels": n_panels,
            "panel_height": panel_height,
            "panel_width": panel_width,
            "wall_gauge": wall_gauge,
            "total_member_mass": total_member_mass,
            "total_panel_mass": total_panel_mass,
            "total_mass": total_mass,
            "weighted_total_mass": weighted_total_mass,
            "panel_material": panel_material,
            "channel_data": channel_type,
            "wall_type": wall_type 
        }
    ]

    if display:
        print(f"Generated frame with {len(nodes)} nodes and {len(member_pairs)} members.")
        print(f"  Nodes: {frame[0]}")
        print(f"  Members: {frame[1]}")
        print(f"  Panels: {frame[2]}")
        print(f"  Total mass: {frame[2]['total_mass']:.2f}")

    return frame

def _add_diagonals(nodes, bottom_ids, top_ids, existing_members, plan="A"):
    diagonals = []
    used_pairs = set(tuple(sorted(pair)) for pair in existing_members)

    if plan == "A":
        return []

    elif plan == "B":
        n = len(top_ids)
        x_center = (max(n[0] for n in nodes.values()) + min(n[0] for n in nodes.values())) / 2.0

        for i, top_id in enumerate(top_ids):
            top_x = nodes[top_id][0]

            if abs(top_x - x_center) < 1e-6 and n % 2 == 1:
                # Center node (odd count): add both diagonals
                if i > 0:
                    d_left = (top_id, bottom_ids[i - 1])
                    if tuple(sorted(d_left)) not in used_pairs:
                        diagonals.append(list(d_left))
                if i < n - 1:
                    d_right = (top_id, bottom_ids[i + 1])
                    if tuple(sorted(d_right)) not in used_pairs:
                        diagonals.append(list(d_right))

            elif top_x < x_center and i < len(bottom_ids) - 1:
                # Left of center: diagonal to right-bottom
                diag = (top_id, bottom_ids[i + 1])
                if tuple(sorted(diag)) not in used_pairs:
                    diagonals.append(list(diag))

            elif top_x > x_center and i > 0:
                # Right of center: diagonal to left-bottom
                diag = (top_id, bottom_ids[i - 1])
                if tuple(sorted(diag)) not in used_pairs:
                    diagonals.append(list(diag))

        return diagonals

    elif plan == "C":
        for i in range(len(bottom_ids) - 1):
            b1, b2 = bottom_ids[i], bottom_ids[i + 1]
            t1, t2 = top_ids[i], top_ids[i + 1]
            d1 = (b1, t2)
            d2 = (b2, t1)
            if tuple(sorted(d1)) not in used_pairs:
                diagonals.append(list(d1))
            if tuple(sorted(d2)) not in used_pairs:
                diagonals.append(list(d2))

        return diagonals
    
    elif plan == "D":
        # Check if a top node is exactly at x midpoint
        x_mid = (max(n[0] for n in nodes.values()) + min(n[0] for n in nodes.values())) / 2.0
        has_center_top_node = any(abs(nodes[idx][0] - x_mid) < 1e-6 for idx in top_ids)

        if has_center_top_node:
            # Fall back to Plan B
            return _add_diagonals(nodes, bottom_ids, top_ids, existing_members, plan="B")
        else:
            # Like Plan C, but only every other panel
            diagonals = []
            for i in range(0, len(bottom_ids) - 1, 2):  # Every other panel
                b1, b2 = bottom_ids[i], bottom_ids[i + 1]
                t1, t2 = top_ids[i], top_ids[i + 1]
                d1 = (b1, t2)
                d2 = (b2, t1)
                if tuple(sorted(d1)) not in used_pairs:
                    diagonals.append(list(d1))
                if tuple(sorted(d2)) not in used_pairs:
                    diagonals.append(list(d2))
            return diagonals

    else:
        raise ValueError(f"Unknown diagonal plan '{plan}'")

"""

channel_materials = [gd.GLV, gd.SST]
panel_materials = [cfg.material]
node_options = [4, 6, 8, 10, 12, 14, 16]
gauge_options = [8, 10, 12, 14, 16, 18]
profile_options = ['C', 'Rectangular', 'Hat', 'Double C', 'I']
diagonal_plans = ['A', 'B', 'C', 'D']

results = []

total_combos = len(channel_materials) * len(panel_materials) * len(node_options) * len(gauge_options) * len(profile_options) * len(diagonal_plans)
print(f"Evaluating {total_combos} combinations...\n")

combo_id = 1

for ch_mat, pnl_mat, n_nodes, gauge, profile_type, diag_plan in itertools.product(channel_materials, panel_materials, node_options, gauge_options, profile_options, diagonal_plans):
    try:
        print(f"[{combo_id}/{total_combos}] Channel={ch_mat}, Panel={pnl_mat}, Nodes={n_nodes}, Gauge={gauge}, Profile={profile_type}, Plan={diag_plan}")
        
        # Set cfg material for panel first
        cfg.material = pnl_mat
        
        # Define channel separately
        channel_type = Profile(ch_mat, gauge, profile_type)

        frame = generate_frame(
            cfg.x_in, cfg.z_in,
            channel_type=channel_type,
            panel_material=pnl_mat,
            num_nodes=n_nodes,
            display=False,
            diagonal_plan=diag_plan
        )
        
        nodes, members = frame[0], frame[1]
        q = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)

        is_structural = calculate_wall_frame_structural(
            nodes,
            members,
            channel_type,
            q=q,
            display=False,
            plot=False
        )

        if not is_structural:
            print("  ❌ Frame failed structural check.")
            continue

        metrics = frame[2]
        results.append({
            "Channel Material": ch_mat,
            "Panel Material": pnl_mat,
            "Nodes": n_nodes,
            "Gauge": gauge,
            "Profile": profile_type,
            "Diagonal Plan": diag_plan,
            "Total Mass": metrics["total_mass"],
            "Total Member Mass": metrics["total_member_mass"],
            "Total Panel Mass": metrics["total_panel_mass"],
            "Wall Gauge": metrics["wall_gauge"],
            "Frame Data": frame,
            "Channel Type": channel_type
        })

    except Exception as e:
        print(f"  ⚠️ Skipped due to error: {e}")

    combo_id += 1

# Sort and display top designs
df_results = pd.DataFrame(results)
df_sorted = df_results.sort_values(by="Total Mass").reset_index(drop=True)

print(f"\n✅ {len(df_sorted)} structurally sound designs found out of {total_combos} combinations.")

n = 1
print(f"\n=== Top {n} Structurally Sound Designs ===")
top_n = df_sorted.head(n)

for i, row in top_n.iterrows():
    print(f"\n🔹 Design {i+1}")
    
    frame_data = row['Frame Data']
    channel_type = row['Channel Type']
    nodes, members = frame_data[0], frame_data[1]
    metrics = frame_data[2]
    q = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)

    try:
        calculate_wall_frame_structural(
            nodes,
            members,
            channel_type,
            q=q,
            display=True,
            plot=True,
            title=f"Design {i+1}",
            metrics=metrics
        )
    except Exception as e:
        print(f"  ❌ Error plotting design: {e}")

"""