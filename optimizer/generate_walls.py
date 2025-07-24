"""
Code to generate structural frames based on given dimensions and constraints.
Generates structurally-feasible configurations of nodes and members within specified limits.
"""

import random
import numpy as np # type: ignore
from structural_frames import calculate_wall_frame_structural, distribute_load
from capabilities import Capabilities
from profiles import Profile
import config as cfg
import general_data as gd
from structural_panels import calculate_wall_gauge


def generate_frames(x, y, channel_type, n_frames=5, min_nodes=4, max_nodes=12, display=False):
    """
    Generate all possible configurations of nodes and members.
    Returns a list of tuples, each containing the number of nodes and members,
    as well as panel information, wall gauge, and material usage.
    The channel_type parameter should be a Profile instance representing the channel type.
    """

    corner_nodes = {0: [0, 0], 1: [x, 0], 2: [0, y], 3: [x, y]}

    node_range = range(min_nodes, max_nodes + 1)
    frames = []

    while len(frames) < n_frames:
        # Randomly select the number of nodes for this frame
        num_nodes = random.choice(node_range)
        num_remaining_nodes = num_nodes - len(corner_nodes)  # Adjust for corner nodes

        # Start by adding corner nodes
        nodes = corner_nodes.copy()

        # Add evenly spaced nodes along the top and bottom edges
        if num_remaining_nodes > 0: 
            if num_remaining_nodes % 2 == 0: num_remaining_nodes -= 1  # Ensure odd number of nodes for symmetry
            num_top_bot_nodes = num_remaining_nodes // 2
            start_len = len(nodes)
            for i in range(num_top_bot_nodes):
                pos_x = x / (num_top_bot_nodes + 1) * (i + 1)
                nodes[start_len + i] = [pos_x, 0]
                nodes[start_len + i + num_top_bot_nodes] = [pos_x, y]
            num_remaining_nodes -= num_top_bot_nodes * 2

        num_members = random.choice(_get_member_range(len(nodes)))
        print(f"Generating frame with {len(nodes)} nodes and {num_members} members.")

        # Sort nodes: top to bottom (ascending y), then left to right (ascending x)
        sorted_nodes = dict(
            sorted(
                nodes.items(),
                key=lambda item: (item[1][1], item[1][0])
            )
        )

        left_nodes = {idx: n for idx, n in sorted_nodes.items() if n[0] == 0}
        left_id_nodes = list(left_nodes.keys())
        right_nodes = {idx: n for idx, n in sorted_nodes.items() if n[0] == x}
        right_id_nodes = list(right_nodes.keys())
        top_nodes = {idx: n for idx, n in sorted_nodes.items() if n[1] == y}
        top_id_nodes = list(top_nodes.keys())
        bottom_nodes = {idx: n for idx, n in sorted_nodes.items() if n[1] == 0}
        bottom_id_nodes = list(bottom_nodes.keys())

        member_pairs = []
        vertical_pairs = [[bottom_id_nodes[i], top_id_nodes[i]] for i in range(len(bottom_id_nodes))]
        horizontal_pairs = []

        # Connect all consecutive nodes along the bottom edge
        for i in range(len(bottom_id_nodes) - 1):
            horizontal_pairs.append([bottom_id_nodes[i], bottom_id_nodes[i + 1]])

        # Connect all consecutive nodes along the top edge
        for i in range(len(top_id_nodes) - 1):
            horizontal_pairs.append([top_id_nodes[i], top_id_nodes[i + 1]])

        member_pairs = vertical_pairs + horizontal_pairs

        # Add diagonal members in all the consecutive node pairs
        # Identify all possible boxes (4 nodes forming a rectangle)
        # Add diagonal members in every 3rd box (4 nodes forming a rectangle)
        box_counter = 0  # Initialize a counter for boxes
        box_separation = 1  # Add diagonal members only for every 3rd box

        for i, bottom_left in enumerate(bottom_id_nodes[:-1]):
            for j, top_left in enumerate(top_id_nodes[:-1]):
                if i < len(bottom_id_nodes) - 1 and j < len(top_id_nodes) - 1:
                    bottom_right = bottom_id_nodes[i + 1]
                    top_right = top_id_nodes[j + 1]

                    # Ensure these nodes form a valid rectangle
                    if (nodes[bottom_left][0] == nodes[top_left][0] and
                        nodes[bottom_right][0] == nodes[top_right][0] and
                        nodes[bottom_left][1] == nodes[bottom_right][1] and
                        nodes[top_left][1] == nodes[top_right][1]):

                        # Add diagonal members only for every 3rd box
                        if box_counter % box_separation == 0:
                            member_pairs.append([bottom_left, top_right])  # Diagonal 1
                            member_pairs.append([bottom_right, top_left])  # Diagonal 2
                        
                        box_counter += 1  # Increment the box counter

                        

        # --- PANEL EXTRACTION AND WALL GAUGE CALCULATION ---
        # 1. Distance between vertical members = panel length
        # Find all unique x positions of bottom nodes (verticals)
        x_positions = sorted([nodes[idx][0] for idx in bottom_id_nodes])
        if len(x_positions) > 1:
            panel_length = x_positions[1] - x_positions[0]
        else:
            panel_length = x  # fallback

        # 2. Max y as panel width
        panel_width = max([n[1] for n in nodes.values()])

        # 3. Number of panels = max x / panel_length
        if panel_length > 0:
            n_panels = int(np.ceil(x / panel_length))
        else:
            n_panels = 1

        # 4. Calculate wall gauge
        wall_gauge = calculate_wall_gauge(panel_width, panel_length, cfg.water_height_in, wind_zone=cfg.wind_zone, material=cfg.material, display=True)
        if wall_gauge < 10 or wall_gauge is None:
            raise ValueError("Calculated wall gauge is too thick.")

        cap = Capabilities(cfg.material, wall_gauge)
        _, x_max, _, y_max = cap.obtain_APB_limits()
        max_length = max(x_max, y_max)
        n_panels = int(np.ceil(x / max_length))
        panel_length = x / n_panels

        # --- MATERIAL USAGE CALCULATION ---
        # 1. Member mass
        # Use the provided channel_type profile if given, else default
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

        # 2. Panel mass
        total_panel_area = n_panels * panel_length * panel_width
        cap = Capabilities(material, wall_gauge)
        panel_density = cap.density[cap.gauge_material]
        total_panel_mass = total_panel_area * panel_density

        # 3. Total mass
        total_mass = total_member_mass + total_panel_mass
        weight = 5
        weighted_total_mass = weight * total_member_mass + total_panel_mass

        frames.append([
            nodes.copy(),
            member_pairs.copy(),
            {
                "n_panels": n_panels,
                "panel_length": panel_length,
                "panel_width": panel_width,
                "wall_gauge": wall_gauge,
                "total_member_mass": total_member_mass,
                "total_panel_mass": total_panel_mass,
                "total_mass": total_mass,
                "weighted_total_mass": weighted_total_mass
            }
        ])

    if display:
        for i, frame in enumerate(frames):
            print(f"Frame {i + 1}:")
            print(f"  Nodes: {frame[0]}")
            print(f"  Members: {frame[1]}")
            print(f"  Panels: {frame[2]}")
            print(f"  Material Usage:")
            print(f"    Member mass: {frame[2]['total_member_mass']:.2f}")
            print(f"    Panel mass: {frame[2]['total_panel_mass']:.2f}")
            print(f"    Total mass: {frame[2]['total_mass']:.2f}")
            print(f"    Weighted total mass: {frame[2]['weighted_total_mass']:.2f}")

    return frames

def _get_member_range(n_nodes):
    """
    Calculate the range of possible members based on the number of nodes.
    """
    min_members = int(np.ceil(n_nodes / 2))
    min_nodes = 4
    max_members = 6
    counter = 0
    add = 3    
    for _ in range(min_nodes + 1, n_nodes + 1):
        max_members += add
        add += 1
        counter += 1
        if counter == 4:
            counter = 0
            add -= 1
    return range(min_members, max_members//2 + 3)

display = True
n_nodes = 14
channel_type = Profile(cfg.material, 16, 'C')
frames = generate_frames(cfg.x_in, cfg.z_in, channel_type=channel_type, n_frames=1, min_nodes=n_nodes, max_nodes=n_nodes, display=display)
for i, frame in enumerate(frames):
    try:
        q = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)
        calculate_wall_frame_structural(frame[0], frame[1], channel_type, q=q, display=display, plot=True)
    except Exception as e:
        print(f"Error processing frame {i + 1}: {e}")