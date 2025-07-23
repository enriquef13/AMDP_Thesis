"""
Code to generate structural frames based on given dimensions and constraints.
Generates structurally-feasible configurations of nodes and members within specified limits.
"""

import random
import numpy as np
from structural_frames import calculate_wall_frame_structural, distribute_load
from capabilities import Capabilities
from profiles import Profile
import config as cfg
import general_data as gd

def generate_frames(x, y, n_frames=5, min_nodes=4, max_nodes=12, display=False):
    """
    Generate all possible configurations of nodes and members.
    Returns a list of tuples, each containing the number of nodes and members.
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
                        
                        box_counter += 1  # Increment the box counter

                        # Add diagonal members only for every 3rd box
                        if box_counter % 1 == 0:
                            member_pairs.append([bottom_left, top_right])  # Diagonal 1
                            member_pairs.append([bottom_right, top_left])  # Diagonal 2

        frames.append([nodes.copy(), member_pairs.copy()])

    if display:
        for i, frame in enumerate(frames):
            print(f"Frame {i + 1}:")
            print(f"  Nodes: {frame[0]}")
            print(f"  Members: {frame[1]}")

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

# display = True
# n_nodes = 12
# frames = generate_frames(cfg.x_in, cfg.z_in, n_frames=1, min_nodes=n_nodes, max_nodes=n_nodes, display=False)
# c_channel = Profile('SST-M3', 8, 'Rectangular')
# for i, frame in enumerate(frames):
#     try:
#         q_x, q_y = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)
#         calculate_wall_frame_structural(frame[0], frame[1], c_channel, q=q_x/1000, display=display)
#     except Exception as e:
#         print(f"Error processing frame {i + 1}: {e}")