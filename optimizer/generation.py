"""
Code to generate structural frames based on given dimensions and constraints.
Generates structurally-feasible configurations of nodes and members within specified limits.
"""

import random
import numpy as np
from structural_frames import calculate_wall_frame_structural, distribute_load
from profiles import Profile
import config as cfg

def generate_frames(x, y, n_frames=5, min_nodes=4, max_nodes=12, display=False):
    """
    Generate all possible configurations of nodes and members.
    Returns a list of tuples, each containing the number of nodes and members.
    """

    corner_nodes = {0: [0, 0], 1: [x, 0], 2: [0, y], 3: [x, y]}

    node_range = range(min_nodes, max_nodes + 1)
    frames = []

    while len(frames) < n_frames:
        # Randomly select the number of nodes and members for this frame
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

        if display:
            print(f"Nodes: {nodes}")
            print("")
            print(f"Left Nodes: {left_nodes}")
            print(f"Right Nodes: {right_nodes}")
            print(f"Top Nodes: {top_nodes}")
            print(f"Bottom Nodes: {bottom_nodes}")

        vertical_pairs = [[bottom_id_nodes[i], top_id_nodes[i]] for i in range(len(bottom_id_nodes))]
        num_members -= len(vertical_pairs)
        print(f"Initial Vertical Pairs: {vertical_pairs}")
        print("")

        member_pairs = vertical_pairs.copy()
        if num_members < 0:
            print("Not enough members for the given nodes. Skipping this frame.")
            continue

        # Get all node indices used in member_pairs
        used_nodes = set()
        for pair in member_pairs:
            used_nodes.update(pair)

        # Find remaining nodes not in member_pairs
        all_node_indices = set(sorted_nodes.keys())
        remaining_node_indices = all_node_indices - used_nodes
        remaining_nodes = {idx: sorted_nodes[idx] for idx in remaining_node_indices}
        
        done = False
        while not done:
            for node in nodes.keys():
                sel_node = random.choice(list(nodes.keys()))
                if sel_node == node:
                    continue
                pair = [sel_node, node]
                if not _check_overlap_members(pair, nodes) and not _check_members(pair, member_pairs):
                    member_pairs.append(pair)
                    num_members -= 1
                    if num_members <= 0:
                        done = True
                        break

        frames.append([nodes.copy(), member_pairs.copy()])

    if display:
        for i, frame in enumerate(frames):
            print(f"Frame {i + 1}:")
            print(f"  Nodes: {frame[0]}")
            print(f"  Members: {frame[1]}")

    return frames

def _check_members(pair, members):
    for member in members:
        if set(pair) == set(member):
            return True
    return False

def _check_overlap_members(pair, nodes):
    """
    Returns True if the member defined by 'pair' passes over (overlaps) more than one node.
    """
    idx1, idx2 = pair
    x1, y1 = nodes[idx1]
    x2, y2 = nodes[idx2]
    overlap_count = 0
    for idx, (x, y) in nodes.items():
        if idx == idx1 or idx == idx2:
            continue
        # Check if the node is collinear with the pair
        if (x2 - x1) * (y - y1) == (y2 - y1) * (x - x1):
            # Check if the node is strictly between the two nodes
            if min(x1, x2) < x < max(x1, x2) or min(y1, y2) < y < max(y1, y2):
                overlap_count += 1
                if overlap_count > 0:
                    return True
    return False

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
frames = generate_frames(cfg.x_in, cfg.z_in, n_frames=10, min_nodes=20, max_nodes=40, display=display)
c_channel = Profile('SST-M3', 8, 'Rectangular')
for i, frame in enumerate(frames):
    try:
        q_x, q_y = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)
        calculate_wall_frame_structural(frame[0], frame[1], c_channel, q=q_x, display=display)
    except Exception as e:
        print(f"Error processing frame {i + 1}: {e}")