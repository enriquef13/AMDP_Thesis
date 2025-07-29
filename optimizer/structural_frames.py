import numpy as np # type: ignore
import pandas as pd # type: ignore
from scipy.linalg import solve # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
from matplotlib.lines import Line2D # type: ignore
import general_data as gd
import config as cfg
import os

def calculate_wall_frame_structural(nodes, members, channel, q, display=False, plot=False, title=None, metrics=None, store_plot=False):
    """
    Calculate the structural properties of a wall based on its nodes and members.
    
    Parameters:
        nodes: Dictionary of node coordinates in the format {idx1: [x1, y1], idx2: [x2, y2], ...}.
        members: List of member definitions in the format [[node1_idx, node2_idx], [node2_idx, node3_idx], ...].
        channel: Profile object representing the channel section.
        panel_material: Material of the wall panel.
        q: Uniform distributed load applied to the frame (lbf/in).
    """

    E = gd.MATERIALS[channel.material]["youngs_mod"]       # Young's modulus (psi)
    Fy = gd.MATERIALS[channel.material]["yield_strength"]  # Yield strength (psi)
    A = channel.A  # Cross-sectional area (in²)
    I = channel.I  # Area moment of inertia (in^4)
    c = channel.c  # Distance from neutral axis to extreme fiber (in)

    K = gd.EFFECTIVE_LENGTH_FACTOR                  # Effective length factor (pinned-pinned)
    load_factor = gd.LOAD_FACTOR                    # Load factor (LRFD)
    max_deflection_ratio = gd.DEFLECTION_LIMIT      # Deflection limit

    # Resistance factors for buckling, axial, shear, and bending
    buckling_resistance_factor = gd.RESISTANCE_FACTORS[channel.material]["buckling"]
    axial_resistance_factor = gd.RESISTANCE_FACTORS[channel.material]["axial"]
    shear_resistance_factor = gd.RESISTANCE_FACTORS[channel.material]["shear"]
    bending_resistance_factor = gd.RESISTANCE_FACTORS[channel.material]["bending"]

    # Filter out invalid members (non-existent in nodes dictionary)
    members = [m for m in members if m[0] in nodes and m[1] in nodes]
    top_edge_pairs = _get_top_edge_pairs(nodes)

    node_ids = list(nodes.keys())
    dof_per_node = 3
    total_dof = len(nodes) * dof_per_node

    K_global = np.zeros((total_dof, total_dof))
    F_global = np.zeros(total_dof)

    for (i, j) in members:
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        k_elem, _ = _frame_stiffness(xi, yi, xj, yj, E, A, I)
        dof_map = [3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2]
        for m in range(6):
            for n in range(6):
                K_global[dof_map[m], dof_map[n]] += k_elem[m, n]

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

    fixed_dofs = [3*node_id + dof for node_id, (_, y) in nodes.items() if y == 0 for dof in range(3)]
    free_dofs = [i for i in range(total_dof) if i not in fixed_dofs]
    K_ff = K_global[np.ix_(free_dofs, free_dofs)]
    F_f = F_global[free_dofs]
    u_f = solve(K_ff, F_f)
    u_global = np.zeros(total_dof)
    u_global[free_dofs] = u_f

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
        buckling_fail = axial < 0 and abs(axial) > buckling_resistance_factor * buckling_load
        axial_fail = abs(axial_stress) > axial_resistance_factor * Fy
        shear_fail = abs(shear_stress) > shear_resistance_factor * 0.6 * Fy
        bending_fail = abs(bending_stress) > bending_resistance_factor * Fy

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

    max_y = max(n[1] for n in nodes.values())
    for i, j in members:
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        if yi == yj == max_y:
            L = abs(xj - xi)
            M = q * L**2 / 8
            distributed_bending_stress = M * c / I
            if abs(distributed_bending_stress) > bending_resistance_factor * Fy:
                failed_members.add((i, j))
                if display:
                    print(f"Top edge member {i}-{j} fails due to distributed load bending moment.")

    deflection_limit_ratio = max_deflection_ratio
    node_deflections = {}
    deflected_members = []

    for i, j in members:
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        L = np.sqrt((xj - xi)**2 + (yj - yi)**2)
        limit = deflection_limit_ratio * L
        u_i, v_i = u_global[3*i], u_global[3*i+1]
        u_j, v_j = u_global[3*j], u_global[3*j+1]
        mag_i = np.sqrt(u_i**2 + v_i**2)
        mag_j = np.sqrt(u_j**2 + v_j**2)
        rel_disp = np.sqrt((u_j - u_i)**2 + (v_j - v_i)**2)
        max_deflection = max(mag_i, mag_j, rel_disp)

        node_deflections[i] = mag_i
        node_deflections[j] = mag_j

        if mag_i > limit or mag_j > limit or rel_disp > limit:
            deflected_members.append((i, j))

        if display:
            print(f"Member {i}-{j}: Max deflection = {max_deflection:.4f} in, Limit = {limit:.4f} in")

            if deflected_members:
                print(f"\nMembers exceeding L/{int(1/deflection_limit_ratio)}:")
                for i, j in deflected_members:
                    print(f"Member {i}-{j}")
            else:
                print("\nAll deflections within limits.")

            df_results = pd.DataFrame(internal_results)
            print(df_results.round(3))

    if store_plot or plot:
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plot members
        for i, j in members:
            x = [nodes[i][0], nodes[j][0]]
            y = [nodes[i][1], nodes[j][1]]
            color = 'red' if (i, j) in failed_members or (i, j) in deflected_members else 'black'
            ax.plot(x, y, color=color, lw=2)

        # Plot nodes and labels
        for idx, (x, y_val) in nodes.items():
            ax.plot(x, y_val, 'ro')
            ax.text(x + 0.2, y_val + 0.2, f'{idx}', fontsize=8)

        # Title and subtitle
        main_title = title or "2D Frame Structure"
        fig.suptitle(main_title, fontsize=18, y=0.96, fontweight='bold')

        if metrics:
            channel_info = (
                f"Channel: {channel.gauge} ga {channel.material} {channel.profile_type}-Profile, "
                f"Mass: {metrics['total_member_mass']:.1f} lb"
            )
            panel_info = (
                f"Panel: {metrics['wall_gauge']} ga {metrics.get('panel_material', 'N/A')}, "
                f"Mass: {metrics['total_panel_mass']:.1f} lb"
            )
            member_mass = metrics['total_member_mass']
            panel_mass = metrics['total_panel_mass']
            total_mass = member_mass + panel_mass
            member_ratio = int(round(100 * member_mass / total_mass))
            panel_ratio = 100 - member_ratio
            usage_info = (
                f"Total Mass: {total_mass:.1f} lb"
            )
            # Add colored ratio text with adjusted positions to avoid overlap
            fig.text(0.5, 0.91, channel_info, fontsize=14, ha='center', va='top', color='red')
            fig.text(0.5, 0.87, panel_info, fontsize=14, ha='center', va='top', color='blue')
            # Use separate fig.text for colored ratios
            fig.text(0.45, 0.83, f"{usage_info}   Mass Ratio: ", fontsize=14, ha='center', va='top', color='black')
            fig.text(0.66, 0.83, f"{member_ratio}%", fontsize=14, ha='left', va='top', color='red')
            fig.text(0.71, 0.83, " | ", fontsize=14, ha='left', va='top', color='black')
            fig.text(0.73, 0.83, f"{panel_ratio}%", fontsize=14, ha='left', va='top', color='blue')

        # Add panel rectangles and dotted boundaries
        if metrics:
            panel_width = metrics.get('panel_width', None)
            x_min = min(n[0] for n in nodes.values())
            x_max = max(n[0] for n in nodes.values())
            y_min = min(n[1] for n in nodes.values())
            y_max = max(n[1] for n in nodes.values())

            if panel_width:
                current_x = x_min
                panel_count = int(np.floor((x_max - x_min) / panel_width))
                
                for i in range(panel_count):

                    rect = patches.Rectangle(
                        (current_x, y_min), panel_width, y_max - y_min,
                        linewidth=5, linestyle='--', edgecolor='blue', facecolor='lightblue', alpha=0.25,
                    )
                    ax.add_patch(rect)

                    current_x += panel_width

        # Axes and grid adjustments
        y_vals = [n[1] for n in nodes.values()]
        y_min_data, y_max_data = min(y_vals), max(y_vals)
        y_pad = 0.1 * (y_max_data - y_min_data) if y_max_data > y_min_data else 5
        ax.set_ylim(y_min_data - y_pad, y_max_data + y_pad)

        if "XW" in title:
            ax.set_xlabel("Length (in)")
            ax.set_ylabel("Height (in)")
        elif "YW" in title:
            ax.set_xlabel("Width (in)")
            ax.set_ylabel("Height (in)")
        else:
            ax.set_xlabel("X (in)")
            ax.set_ylabel("Y (in)")
        ax.grid(True)
        ax.set_ylim(y_min_data - 20, y_max_data + 20)
        
        # Add legend
        legend_elements = [
            Line2D([0], [0], color='black', lw=2, label='Channels'),
            Line2D([0], [0], color='blue', lw=2, linestyle='--', alpha=0.5, label='Panels')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

        plt.subplots_adjust(top=0.75)  

        if plot: plt.show()
        if store_plot:
            path = cfg.store_path
            if not os.path.exists(path):
                os.makedirs(path)
            fig.savefig(f"{path}/{title}.png", bbox_inches='tight', dpi=300)
            plt.close(fig)


    # Return structural soundness
    return len(failed_members) == 0 and len(deflected_members) == 0


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

def distribute_load(x, y, q):
    perimeter = 2 * (x + y)
    return q / perimeter

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
#     4: [cfg.x_in//2, 20],
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

# q = distribute_load(cfg.x_in, cfg.y_in, cfg.top_load)
# if check_nodes(cfg.x_in, cfg.z_in, nodes_x):
#     calculate_wall_frame_structural(nodes_x, members_x, c_channel, q=q, display=True)