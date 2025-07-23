"""
Code to generate structural frames based on given dimensions and constraints.
Generates structurally-feasible configurations of nodes and members within specified limits.
"""

import random
import numpy as np
from structural_frames import calculate_wall_frame_structural
from profiles import Profile

def generate_frames(x, y, n_frames=5, min_nodes=4, max_nodes=12, display=False):
    """
    Generate all possible configurations of nodes and members.
    Returns a list of tuples, each containing the number of nodes and members.
    """

    corner_nodes = {0: [0, 0], 1: [x, 0], 2: [0, y], 3: [x, y]}
    channel_types = ['C', 'Rectangular', 'Hat', 'Double C']

    node_range = range(min_nodes, max_nodes + 1)
    frames = []

    while len(frames) < n_frames:
        # Randomly select the number of nodes and members for this frame
        num_nodes = random.choice(node_range)
        num_members = random.choice(_get_member_range(num_nodes))
        print(f"Generating frame with {num_nodes} nodes and {num_members} members.")
        num_nodes -= len(corner_nodes)  # Adjust for corner nodes

        # Start with corner nodes
        nodes = corner_nodes.copy()
        for i in range(num_nodes):
            done = False
            while not done:
                sel_edge = random.randint(0, 3)  # Select a random edge (0 to 3)
                if sel_edge == 0: node_pair = [random.randint(0, x), 0]
                elif sel_edge == 1: node_pair = [x, random.randint(0, y)]
                elif sel_edge == 2: node_pair = [random.randint(0, x), y]
                elif sel_edge == 3: node_pair = [0, random.randint(0, y)]

                if node_pair not in nodes.values():
                    nodes[i + len(corner_nodes)] = node_pair
                    done = True
        
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
        top_nodes = {idx: n for idx, n in sorted_nodes.items() if n[1] == y and n not in corner_nodes.values()}
        top_id_nodes = list(top_nodes.keys())
        bottom_nodes = {idx: n for idx, n in sorted_nodes.items() if n[1] == 0 and n not in corner_nodes.values()}
        bottom_id_nodes = list(bottom_nodes.keys())

        if display:
            print(f"Nodes: {nodes}")
            print("")
            print(f"Left Nodes: {left_nodes}")
            print(f"Right Nodes: {right_nodes}")
            print(f"Top Nodes: {top_nodes}")
            print(f"Bottom Nodes: {bottom_nodes}")

        left_members = [[left_id_nodes[i], left_id_nodes[i+1]] for i in range(len(left_id_nodes) - 1)]
        right_members = [[right_id_nodes[i], right_id_nodes[i+1]] for i in range(len(right_id_nodes) - 1)]
        member_pairs = left_members + right_members
        num_members -= len(member_pairs)
        print(f"Initial Member Pairs: {member_pairs}")
        print("")

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

        if len(remaining_nodes) > num_members or len(remaining_nodes) <= 0:
            print("Not enough members for the remaining nodes. Skipping this frame.")
            continue
        
        done = False
        n_joints_middle = int(np.ceil(len(remaining_nodes) / 2))
        while not done:
            for node in remaining_nodes.keys():
                sel_node = random.choice(list(nodes.keys()))
                if sel_node == node: 
                    continue
                pair = [sel_node, node]
                if not _check_members(pair, member_pairs):
                    member_pairs.append(pair)
                    num_members -= 1
                    n_joints_middle -= 1
                    if n_joints_middle <= 0:
                        done = True
                        break
        
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

frames = generate_frames(10, 5, n_frames=10, min_nodes=4, max_nodes=12, display=False)
c_channel = Profile('GLV-M5', 14, 'C')
for i, frame in enumerate(frames):
    try: 
        calculate_wall_frame_structural(frame[0], frame[1], c_channel, q=10000000, display=True)
    except Exception as e:
        print(f"Error processing frame {i + 1}: {e}")