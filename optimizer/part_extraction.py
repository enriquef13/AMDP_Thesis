import general_data as gd
import config as cfg
from capabilities import Capabilities

def _get_assy_category(cap, gauge, material, length, width):
    weight = cap.density[f'{gauge}_{material[:3]}'] * length * width
    if weight < 10:
        return "Class 1"
    elif weight <= 50 and max(length, width) < 72:
        return "Class 2"
    elif weight <= 100:
        return "Class 3"
    else:
        return "Class 4"

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
    cap = details['cap']
    panel_height = details['panel_height']
    panel_width = details['panel_width']
    panel_gauge = details['wall_gauge'] 
    panel_material = details['panel_material']
    
    panel_bends = 4
    panel_class = _get_assy_category(cap, panel_gauge, panel_material, panel_height+6, panel_width+6)

    part_name = f"W_Panel_{wall_type}_{design_name}"
    panel_entry = _get_entry(design_name, part_name, panel_height+6, panel_width+6,
                             n_panels * 2, gd.CUT_MSP, gd.FORM_APB,
                             panel_material, panel_gauge, panel_bends, panel_class)
    part_entries.append(panel_entry)

    channel_data = details['channel_data']
    special_case = channel_data.profile_type == 'I' and gd.I_IS_DOUBLE_C
    channel_gauge = channel_data.gauge
    channel_material = channel_data.material
    channel_width = channel_data.width if not special_case else 9.6875 # Width for double C profile
    channel_bends = channel_data.unique_bends
    channel_cap = Capabilities(material=channel_material, gauge=channel_gauge)

    h_channel_length = _get_horizontal_channel_length(nodes)
    n_horizontal_channels = 2 if not special_case else 4
    v_channel_length = _get_vertical_channel_length(nodes)
    n_vertical_channels = len(nodes) if special_case else len(nodes) // 2
    d_channel_length, n_diagonal_channels = _get_diagonal_channel_length(nodes, members)
    n_diagonal_channels = n_diagonal_channels * 2 if special_case else n_diagonal_channels
    v_channel_class = _get_assy_category(channel_cap, channel_gauge, channel_material, v_channel_length, channel_width)
    h_channel_class = _get_assy_category(channel_cap, channel_gauge, channel_material, h_channel_length, channel_width)

    v_channel_name = f"W_Channel_V{wall_type}_{design_name}"
    v_channel_entry = _get_entry(design_name, v_channel_name, channel_width, v_channel_length,
                                 n_vertical_channels * 2, gd.CUT_TL, gd.FORM_RF,
                                 channel_material, channel_gauge, channel_bends, v_channel_class)
    part_entries.append(v_channel_entry)
    
    h_channel_name = f"W_Channel_H{wall_type}_{design_name}"
    h_channel_entry = _get_entry(design_name, h_channel_name, channel_width, h_channel_length,
                                 n_horizontal_channels * 2, gd.CUT_TL, gd.FORM_RF,
                                 channel_material, channel_gauge, 0, h_channel_class)
    part_entries.append(h_channel_entry)

    if n_diagonal_channels:
        d_channel_class = _get_assy_category(channel_cap, channel_gauge, channel_material, d_channel_length, channel_width)
        d_channel_name = f"W_Channel_D{wall_type}_{design_name}"
        d_channel_entry = _get_entry(design_name, d_channel_name, channel_width, d_channel_length,
                                     n_diagonal_channels * 2, gd.CUT_TL, gd.FORM_RF,
                                     channel_material, channel_gauge, 0, d_channel_class)
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
    b_panel_class = _get_assy_category(cap, panel_gauge, panel_material, b_panel_length+3, b_panel_width+9)

    panel_entry = _get_entry(design_name, f"F_Panel_B_{design_name}", b_panel_width+9, b_panel_length+3,
                             n_panels, gd.CUT_MSP, gd.FORM_APB,
                             panel_material, panel_gauge, panel_bends, b_panel_class)
    part_entries.append(panel_entry)
    
    if not all_same:
        t_panel_width = panels[-1][0]
        t_panel_length = panels[-1][1]
        t_panel_class = _get_assy_category(cap, panel_gauge, panel_material, t_panel_length+3, t_panel_width+9)
        panel_entry = _get_entry(design_name, f"F_Panel_T_{design_name}", t_panel_width+9, t_panel_length+3,
                                 n_panels, gd.CUT_MSP, gd.FORM_APB,
                                 panel_material, panel_gauge, panel_bends, t_panel_class)
        part_entries.append(panel_entry)

    if len(channels) > 0:
        n_channels = len(channels) * 2 if gd.I_IS_DOUBLE_C else len(channels)
        channel_length = channels[0][1]
        channel_gauge = gd.FLOOR_BEAMS.gauge
        channel_material = gd.FLOOR_BEAMS.material
        channel_width = gd.FLOOR_BEAMS.width if not gd.I_IS_DOUBLE_C else 9.6875  # Width for double C profile
        channel_bends = gd.FLOOR_BEAMS.unique_bends
        channel_cap = Capabilities(material=channel_material, gauge=channel_gauge)
        channel_class = _get_assy_category(channel_cap, channel_gauge, channel_material, channel_length, channel_width)

        channel_entry = _get_entry(design_name, f"F_Channel_{design_name}", channel_width, channel_length,
                                    n_channels, gd.CUT_TL, gd.FORM_RF,
                                    channel_material, channel_gauge, channel_bends, channel_class)
        part_entries.append(channel_entry)

    return part_entries