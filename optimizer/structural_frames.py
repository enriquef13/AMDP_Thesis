import numpy as np
import pandas as pd # type: ignore
from scipy.linalg import solve # type: ignore
import matplotlib.pyplot as plt # type: ignore
from profiles import Profile
import general_data as gd
import config as cfg

def calculate_wall_frame_structural(nodes, members, channel, q, display=False):
    """
    Calculate the structural properties of a wall based on its nodes and members.
    
    Parameters:
        nodes: Dictionary of node coordinates in the format {idx1: [x1, y1], idx2: [x2, y2], ...}.
        members: List of member definitions in the format [[node1_idx, node2_idx], [node2_idx, node3_idx], ...].
        channel: Profile object representing the channel section.
        q: Uniform distributed load applied to the frame (lbf/in).
    """
    E = gd.MATERIALS[channel.material]["youngs_mod"]       # Young's modulus (psi)
    Fy = gd.MATERIALS[channel.material]["yield_strength"]  # Yield strength (psi)
    A = channel.A  # Cross-sectional area (in²)
    I = channel.I  # Area moment of inertia (in^4)
    c = channel.c  # Distance from neutral axis to extreme fiber (in)

    K = 1.0                             # Effective length factor (pinned-pinned)
    load_factor = 1.5                   # Load factor (LRFD)
    resistance_factor = 0.9             # Resistance factor (LRFD)
    max_deflection_ratio = 1/360        # Deflection limit

    # Filter out invalid members (non-existent in nodes dictionary)
    members = [m for m in members if m[0] in nodes and m[1] in nodes]

    top_edge_pairs = _get_top_edge_pairs(nodes)

    # === Setup ===
    node_ids = list(nodes.keys())
    num_nodes = len(node_ids)
    dof_per_node = 3
    total_dof = num_nodes * dof_per_node

    K_global = np.zeros((total_dof, total_dof))
    F_global = np.zeros(total_dof)

    # === Assemble Global Stiffness Matrix ===
    for (i, j) in members:
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        k_elem, _ = _frame_stiffness(xi, yi, xj, yj, E, A, I)
        dof_map = [3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2]
        for m in range(6):
            for n in range(6):
                K_global[dof_map[m], dof_map[n]] += k_elem[m, n]

    # === Apply Uniform Load on Top Edge (factored) ===
    node_force = dict.fromkeys(nodes.keys(), 0.0)
    for i, j in top_edge_pairs:
        xi, _ = nodes[i]
        xj, _ = nodes[j]
        L = abs(xj - xi)
        load = load_factor * q * L
        node_force[i] += load / 2
        node_force[j] += load / 2
    
    for node_id, force in node_force.items():
        F_global[3*node_id + 1] -= force

    # === Apply Boundary Conditions ===
    fixed_dofs = []
    for node_id in nodes:
        if nodes[node_id][1] == 0:  # Only fix nodes on the bottom edge (y = 0)
            fixed_dofs += [3*node_id, 3*node_id+1, 3*node_id+2]

    free_dofs = [i for i in range(total_dof) if i not in fixed_dofs]
    K_ff = K_global[np.ix_(free_dofs, free_dofs)]
    F_f = F_global[free_dofs]

    # === Solve ===
    u_f = solve(K_ff, F_f)
    u_global = np.zeros(total_dof)
    u_global[free_dofs] = u_f

    # === Compute Reactions ===
    R_global = K_global @ u_global - F_global

    # === Internal Forces per Member ===
    internal_results = []
    failed_members = set()

    for i, j in members:
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        k_elem, L = _frame_stiffness(xi, yi, xj, yj, E, A, I)
        dof_map = [3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2]
        u_elem = u_global[dof_map]
        f_local = k_elem @ u_elem
        axial = f_local[3]
        shear = f_local[4]
        moment = f_local[5]

        axial_stress = axial / A
        shear_stress = shear / A
        bending_stress = moment * c / I

        buckling_load = (np.pi**2 * E * I) / (K * L)**2
        buckling_fail = axial < 0 and abs(axial) > resistance_factor * buckling_load

        axial_fail = abs(axial_stress) > resistance_factor * Fy
        shear_fail = abs(shear_stress) > resistance_factor * 0.6 * Fy
        bending_fail = abs(bending_stress) > resistance_factor * Fy

        failed = axial_fail or shear_fail or bending_fail or buckling_fail
        if failed:
            failed_members.add((i, j))

        internal_results.append({
            "Member": f"{i}-{j}",
            "Length (in)": L,
            "Axial Force (lbf)": axial,
            "Shear Force (lbf)": shear,
            "Bending Moment (lbf-in)": moment,
            "Axial Stress (psi)": axial_stress,
            "Shear Stress (psi)": shear_stress,
            "Bending Stress (psi)": bending_stress,
            "Fails?": failed
        })

    # === Deflection Check ===
    L_span = max(n[0] for n in nodes.values()) - min(n[0] for n in nodes.values())
    deflection_limit = max_deflection_ratio * L_span
    node_deflections = {}
    deflected_nodes = []

    for i, (x, y) in nodes.items():
        if 3*i+1 in free_dofs:
            v_disp = u_global[3*i+1]
            node_deflections[i] = v_disp
            if abs(v_disp) > deflection_limit:
                deflected_nodes.append(i)

    if deflected_nodes:
        print("\nNodes exceeding deflection limit (L/360):")
        for i in deflected_nodes:
            print(f"Node {i} - Vertical deflection: {node_deflections[i]*1000:.2f} in")
    else:
        print("\nAll vertical deflections are within the allowable limit.")

    # === Evaluate Beam Deflection ===
    if display:
        print("\nMaximum internal beam deflections:")
        for i, j in members:
            max_deflection, _, _ = _evaluate_beam_deflection(i, j, u_global, nodes)
            print(f"Member {i}-{j}: Max internal deflection = {max_deflection*1000:.2f} in")

        # Display internal forces
        df_results = pd.DataFrame(internal_results)
        print(df_results.round(3))

        # === Visualize the 2D Structure with Failure Highlight ===
        plt.figure(figsize=(8, 6))
        for i, j in members:
            x = [nodes[i][0], nodes[j][0]]
            y = [nodes[i][1], nodes[j][1]]
            color = 'red' if (i, j) in failed_members or (j, i) in failed_members else 'black'
            plt.plot(x, y, color=color, lw=2)

        for idx, (x, y) in nodes.items():
            plt.plot(x, y, 'ro')
            plt.text(x + 0.1, y + 0.1, f'{idx}', fontsize=9)

        plt.title("2D Frame Structure")
        plt.xlabel("X (in)")
        plt.ylabel("Y (in)")
        plt.grid(True)
        plt.axis("equal")
        plt.tight_layout()
        plt.show()

def _get_top_edge_pairs(nodes):
    # Step 1: Find max y
    max_y = max(y for _, y in nodes.values())
    
    # Step 2: Get top-edge node IDs
    top_edge_nodes = [node_id for node_id, (x, y) in nodes.items() if y == max_y]
    
    # Step 3: Sort by x-coordinate
    top_edge_nodes.sort(key=lambda i: nodes[i][0])
    
    # Step 4: Pair consecutive nodes
    top_edge_pairs = [(top_edge_nodes[i], top_edge_nodes[i+1]) for i in range(len(top_edge_nodes) - 1)]

    return top_edge_pairs

def _frame_stiffness(x1, y1, x2, y2, E, A, I):
    L = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    c = (x2 - x1) / L
    s = (y2 - y1) / L

    k_local = np.array([
        [ A*E/L,       0,          0,      -A*E/L,       0,          0],
        [ 0,      12*E*I/L**3,  6*E*I/L**2,  0, -12*E*I/L**3,  6*E*I/L**2],
        [ 0,      6*E*I/L**2,   4*E*I/L,    0, -6*E*I/L**2,   2*E*I/L],
        [-A*E/L,      0,          0,       A*E/L,       0,          0],
        [ 0,     -12*E*I/L**3, -6*E*I/L**2,  0,  12*E*I/L**3, -6*E*I/L**2],
        [ 0,      6*E*I/L**2,   2*E*I/L,    0, -6*E*I/L**2,   4*E*I/L]
    ])

    T = np.array([
        [ c,  s, 0,  0, 0, 0],
        [-s,  c, 0,  0, 0, 0],
        [ 0,  0, 1,  0, 0, 0],
        [ 0,  0, 0,  c, s, 0],
        [ 0,  0, 0, -s, c, 0],
        [ 0,  0, 0,  0, 0, 1]
    ])

    return T.T @ k_local @ T, L

def _evaluate_beam_deflection(i, j, u_global, nodes, num_points=20):
    dof_map = [3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2]
    u_elem = u_global[dof_map]
    v_i, theta_i = u_elem[1], u_elem[2]
    v_j, theta_j = u_elem[4], u_elem[5]

    xi, yi = nodes[i]
    xj, yj = nodes[j]
    L = np.sqrt((xj - xi)**2 + (yj - yi)**2)

    xs = np.linspace(0, L, num_points)
    deflections = []
    for x in xs:
        xi_norm = x / L
        N1 = 1 - 3*xi_norm**2 + 2*xi_norm**3
        N2 = x * (1 - 2*xi_norm + xi_norm**2)
        N3 = 3*xi_norm**2 - 2*xi_norm**3
        N4 = x * (xi_norm**2 - xi_norm)
        v = N1 * v_i + N2 * theta_i + N3 * v_j + N4 * theta_j
        deflections.append(v)

    max_deflection = max(deflections, key=abs)
    return max_deflection, xs, deflections

def distribute_load(x, y, q):
    perimeter = 2 * (x + y)
    q_x = x * q / perimeter
    q_y = y * q / perimeter
    return q_x, q_y

def check_nodes(x, z, nodes):
    check = True
    for node in nodes.values():
        if (node[0] == 0 or node[0] == x) and (0 <= node[1] <= z):
            pass
        elif (node[1] == 0 or node[1] == z) and (0 <= node[0] <= x):
            pass
        else:
            print(f"Node {node} out of bounds: {0 <= node[0] <= x} and {0 <= node[1] <= z}")
            check = False
    return check

# Example usage:

# Nodes (index: [x or y, z]) 
# corner_nodes = [0, cfg.z_in], [cfg.x_in, cfg.z_in]
# nodes_x = {
#     0: [0, 0],
#     1: [25, 0],
#     2: [53, 0],
#     3: corner_nodes[0],
#     4: [25, 20],
#     5: corner_nodes[1]
# }

# c_channel = Profile(material=gd.SST, gauge=8, profile_type="C")

# # Members 
# members_x = [
#     [0, 1], [1, 2],                 # bottom
#     [3, 4], [4, 5],                 # top
#     [0, 3], [1, 4], [2, 5],         # verticals
#     [0, 4], [1, 3], [1, 5], [2, 4]  # diagonals
# ]

# q_x, q_y = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)
# if check_nodes(cfg.x_in, cfg.z_in, nodes_x):
#     calculate_wall_frame_structural(nodes_x, members_x, c_channel, q=q_x, display=True)