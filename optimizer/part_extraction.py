import general_data as gd
import config as cfg

def get_wall_parts(frame, design_name):
    """
    Extract wall parts from the frames.

    Args:
        frame: A tuple containing nodes, members, and details of the wall frame.
        design_name: XW#_YW#_F#
    """
    part_entries = []

    nodes, members, details = frame

    wall_type = details['wall_type']
    n_panels = details['n_panels']
    panel_height = details['panel_height']
    panel_width = details['panel_width']
    panel_gauge = details['wall_gauge'] 
    panel_material = details['panel_material']
    panel_bends = 4

    part_name = f"W_Panel_{wall_type}_{design_name}"
    panel_entry = _get_entry(design_name, part_name, panel_height, panel_width, 
                             n_panels * 2, gd.CUT_MSP, gd.FORM_APB, 
                             panel_material, panel_gauge, panel_bends, "Class 2")
    part_entries.append(panel_entry)

    channel_data = details['channel_data']
    special_case = channel_data.profile_type == 'I' and gd.I_IS_DOUBLE_C
    channel_gauge = channel_data.gauge
    channel_material = channel_data.material
    channel_width = channel_data.width if not special_case else Profile(channel_material, channel_gauge, "C").width
    channel_bends = channel_data.unique_bends

    h_channel_length = _get_horizontal_channel_length(nodes)
    n_horizontal_channels = 2 if not special_case else 4
    v_channel_length = _get_vertical_channel_length(nodes)
    n_vertical_channels = len(nodes) // 2 if not special_case else len(nodes)
    d_channel_length, n_diagonal_channels = _get_diagonal_channel_length(nodes, members)
    n_diagonal_channels = n_diagonal_channels if not special_case else n_diagonal_channels * 2

    v_channel_name = f"W_Channel_V{wall_type}_{design_name}"
    v_channel_entry = _get_entry(design_name, v_channel_name, channel_width, v_channel_length,
                                 n_vertical_channels * 2, gd.CUT_TL, gd.FORM_RF, 
                                 channel_material, channel_gauge, channel_bends, "Class 2")
    part_entries.append(v_channel_entry)
    
    h_channel_name = f"W_Channel_H{wall_type}_{design_name}"
    h_channel_entry = _get_entry(design_name, h_channel_name, channel_width, h_channel_length,
                                 n_horizontal_channels * 2, gd.CUT_TL, gd.FORM_RF,
                                 channel_material, channel_gauge, 0, "Class 2")
    part_entries.append(h_channel_entry)

    if n_diagonal_channels:
        d_channel_name = f"W_Channel_D{wall_type}_{design_name}"
        d_channel_entry = _get_entry(design_name, d_channel_name, channel_width, d_channel_length,
                                     n_diagonal_channels * 2, gd.CUT_TL, gd.FORM_RF,
                                     channel_material, channel_gauge, 0, "Class 2")
        part_entries.append(d_channel_entry)

    return part_entries

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
    
def _get_entry(design_name, part_name, width, length, qty, cut_method, form_method, material, gauge, bends, class_type):
    cut_distance = 2 * (width + length)
    entry = [design_name, part_name, qty, cut_method, form_method, material, gauge, 0,
             cut_distance, bends, 4, length, width, class_type]
    return entry

def get_floor_parts(floor, design_name):
    """
    Extract floor parts from the panels and channels.
    """
    part_entries = []
    panels = floor['panels']
    channels = floor['channels']
    cap = floor['cap']

    all_same = all(panels[0] == panel for panel in panels)
    n_panels = len(panels) if all_same else len(panels) // 2
    b_panel_width = panels[0][0]
    b_panel_length = panels[0][1]
    panel_gauge = cap.gauge 
    panel_material = cfg.material
    panel_bends = 4

    panel_entry = _get_entry(design_name, f"F_Panel_1_{design_name}", b_panel_width, b_panel_length,
                             n_panels, gd.CUT_MSP, gd.FORM_APB,
                             panel_material, panel_gauge, panel_bends, "Class 2")
    part_entries.append(panel_entry)
    
    if not all_same:
        t_panel_width = panels[-1][0]
        t_panel_length = panels[-1][1]
        panel_entry = _get_entry(design_name, f"F_Panel_2_{design_name}", t_panel_width, t_panel_length,
                                 n_panels, gd.CUT_MSP, gd.FORM_APB,
                                 panel_material, panel_gauge, panel_bends, "Class 2")
        part_entries.append(panel_entry)

    n_channels = len(channels) * 2 if gd.I_IS_DOUBLE_C else len(channels)
    channel_length = channels[0][1]
    channel_gauge = gd.FLOOR_BEAMS.gauge
    channel_material = gd.FLOOR_BEAMS.material
    channel_width = gd.FLOOR_BEAMS.width if not gd.I_IS_DOUBLE_C else Profile(gd.FLOOR_BEAMS.material, gd.FLOOR_BEAMS.gauge, "C").width
    channel_bends = gd.FLOOR_BEAMS.unique_bends

    channel_entry = _get_entry(design_name, f"F_Channel_{design_name}", channel_width, channel_length,
                                n_channels, gd.CUT_TL, gd.FORM_RF,
                                channel_material, channel_gauge, channel_bends, "Class 2")
    part_entries.append(channel_entry)

    return part_entries

from generate_walls import generate_frame
from structural_frames import calculate_wall_frame_structural
from generate_floors import fill_floor_with_panels, visualize_filled_floor
from profiles import Profile

design_name = "XW1_YW1_F1"
channel_type = Profile(cfg.material, 10, "C")
x_frame = generate_frame(cfg.x_in, cfg.z_in, channel_type, cfg.material, num_nodes=12, diagonal_plan="C")
y_frame = generate_frame(cfg.y_in, cfg.z_in, channel_type, cfg.material, num_nodes=12, diagonal_plan="A")
floor = fill_floor_with_panels(10, n_sols=1, display=False)

x_entries = get_wall_parts(x_frame, design_name)
y_entries = get_wall_parts(y_frame, design_name)
calculate_wall_frame_structural(x_frame[0], x_frame[1], channel_type, 10, title=design_name, plot=True, metrics=x_frame[2])
calculate_wall_frame_structural(y_frame[0], y_frame[1], channel_type, 10, title=design_name, plot=True, metrics=y_frame[2])
visualize_filled_floor(floor, design_name)
floor_entries = get_floor_parts(floor, design_name)


part_entries = x_entries + y_entries + floor_entries
for entry in part_entries:
    print(entry)