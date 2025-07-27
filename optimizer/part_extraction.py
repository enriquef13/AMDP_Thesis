def _get_wall_parts(frame, design_name, x_wall=True):
    """
    Extract wall parts from the frames.

    Args:
        frame: A tuple containing nodes, members, and details of the wall frame.
        design_name: XW#_YW#_F#
    """
    nodes, members, details = frame

    n_panels = details['n_panels']
    panel_length = details['panel_length']
    panel_width = details['panel_width']
    panel_gauge = details['wall_gauge'] 
    panel_material = details['panel_material']
    panel_bends = 4

    channel_data = details['channel_data']
    channel_type = channel_data.profile_type
    channel_gauge = channel_data.gauge
    channel_material = channel_data.material
    channel_width = channel_data.width
    channel_bends = channel_data.unique_bends

    h_channel_length = _get_horizontal_channel_length(nodes)
    n_horizontal_channels = 2
    v_channel_length = _get_vertical_channel_length(nodes)
    n_vertical_channels = len(nodes) // 2
    d_channel_length, n_diagonal_channels = _get_diagonal_channel_length(nodes)

    part_entries = []

    panel_type = 'X' if x_wall else 'Y'
    panel_entry = [f"W_Panel_{panel_type}_{design_name}"]

            



def _get_horizontal_channel_length(nodes):
    """
    Extract horizontal channels from the panels.
    """
    x_min = nodes[0][0]
    x_max = nodes[1][0]
    return x_max - x_min

def _get_vertical_channel_length(nodes):
    """
    Extract vertical channels from the panels.
    """
    y_min = nodes[0][1]
    y_max = nodes[2][1]
    return y_max - y_min

def _get_diagonal_channel_length(nodes, members):
    """
    Extract diagonal channels from the panels.
    """
    n_diagonal_channels = 0

    # Create a set of member pairs for quick lookup
    # member_set = set(tuple(sorted(member)) for member in members)

    # Loop through all members to find diagonal connections
    for member in members:
        idx1, idx2 = member
        x1, y1 = nodes[idx1]
        x2, y2 = nodes[idx2]

        # Check if the current member is diagonal
        if abs(x1 - x2) > 0 and abs(y1 - y2) > 0:  # Both x and y must differ for a diagonal
            d_channel_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # Calculate diagonal length
            n_diagonal_channels += 1
    try:
        return d_channel_length, n_diagonal_channels
    except Exception as e:
        return 0, 0

def _get_floor_parts():
    """
    Extract floor parts from the panels and channels.
    """
    return

def get_design_parts():
    """
    Extract all design parts including wall and floor parts.
    """
    wall_parts = _get_wall_parts()
    floor_parts = _get_floor_parts()

    design_parts = {
        'wall_parts': wall_parts,
        'floor_parts': floor_parts
    }

    return design_parts

from generate_walls import generate_frames
from structural_frames import calculate_wall_frame_structural
import config as cfg
from profiles import Profile

channel_type = Profile(cfg.material, 10, "C")
frame = generate_frames(cfg.x_in, cfg.z_in, channel_type, cfg.material, n_frames=1, min_nodes=12, max_nodes=12, diagonal_plan="A")   
d_channel_length, n_diagonal_channels = _get_diagonal_channel_length(frame[0][0], frame[0][1])

calculate_wall_frame_structural(
            frame[0][0],
            frame[0][1],
            channel_type,
            q=1000,
            display=True,
            plot=True,
            title=f"Design TEST",
            metrics=frame[0][2]
        )