
import general_data as gd

def _extract_wall_joints(frame, part_entries):

    nodes, members, details = frame
    joint_entries = []
    panel_name = part_entries[0][1]
    v_channel_name = part_entries[1][1]
    h_channel_name = part_entries[2][1]
    try:
        d_channel_name = part_entries[3][1] if "Channel_D" in part_entries[3][1] else None
    except Exception as e:
        d_channel_name = None

    v_channel_length = part_entries[1][-3]
    try:
        d_channel_length = part_entries[3][-3] if d_channel_name else 0
    except Exception as e:
        d_channel_length = 0
    panel_length = part_entries[0][-3]

    # Panel-to-Panel Joints
    n_panels = part_entries[0][2] // 2
    for i in range(n_panels - 1):
        panel1 = f"{panel_name}:{i + 1}"
        panel2 = f"{panel_name}:{i + 2}"
        joint_length = details['panel_height']
        joint_entries.append([panel1, panel2, joint_length])

        panel3 = f"{panel_name}:{i + n_panels + 1}"
        panel4 = f"{panel_name}:{i + n_panels + 2}"
        joint_length = details['panel_height']
        joint_entries.append([panel3, panel4, joint_length])


    # Channel-to-Channel and Panel-to-Channel Joints
    member_dictionary = {v_channel_name: [], d_channel_name: [] if d_channel_name else None}
    for member in members:
        x1, y1 = nodes[member[0]]
        x2, y2 = nodes[member[1]]
        if x1 == x2:
            member_dictionary[v_channel_name].append(member)
        elif y1 != y2 and x1 != x2 and d_channel_name is not None:
            member_dictionary[d_channel_name].append(member)

    special_case = details['channel_data'].profile_type == 'I' and gd.I_IS_DOUBLE_C

    for i, member in enumerate(member_dictionary[v_channel_name]):
        joint_entries.append([f"{v_channel_name}:{i + 1}", f"{h_channel_name}:{1}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
        joint_entries.append([f"{v_channel_name}:{i + 1}", f"{h_channel_name}:{2}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
        joint_entries.append([f"{v_channel_name}:{i + 1}", f"{panel_name}:{1}", v_channel_length])

        joint_entries.append([f"{v_channel_name}:{i + len(member_dictionary[v_channel_name]) + 1}", f"{h_channel_name}:{3}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
        joint_entries.append([f"{v_channel_name}:{i + len(member_dictionary[v_channel_name]) + 1}", f"{h_channel_name}:{4}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
        joint_entries.append([f"{v_channel_name}:{i + len(member_dictionary[v_channel_name]) + 1}", f"{panel_name}:{1}", v_channel_length])

        if special_case:
            joint_entries.append([f"{v_channel_name}:{i + 1}", f"{v_channel_name}:{i + 2}", v_channel_length])
            joint_entries.append([f"{v_channel_name}:{i + len(member_dictionary[v_channel_name]) + 1}", f"{v_channel_name}:{i + len(member_dictionary[v_channel_name]) + 2}", v_channel_length])

    if d_channel_name is not None:        
        for i, member in enumerate(member_dictionary[d_channel_name]):
            joint_entries.append([f"{d_channel_name}:{i + 1}", f"{h_channel_name}:{1}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
            joint_entries.append([f"{d_channel_name}:{i + 1}", f"{h_channel_name}:{2}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
            joint_entries.append([f"{d_channel_name}:{i + 1}", f"{panel_name}:{1}", d_channel_length])

            joint_entries.append([f"{d_channel_name}:{i + len(member_dictionary[d_channel_name]) + 1}", f"{h_channel_name}:{3}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
            joint_entries.append([f"{d_channel_name}:{i + len(member_dictionary[d_channel_name]) + 1}", f"{h_channel_name}:{4}", max(details['channel_data'].profile['h'], details['channel_data'].profile['b'])])
            joint_entries.append([f"{d_channel_name}:{i + len(member_dictionary[d_channel_name]) + 1}", f"{panel_name}:{1}", d_channel_length])

            if special_case:
                joint_entries.append([f"{d_channel_name}:{i + 1}", f"{d_channel_name}:{i + 2}", d_channel_length])
                joint_entries.append([f"{d_channel_name}:{i + len(member_dictionary[d_channel_name]) + 1}", f"{d_channel_name}:{i + len(member_dictionary[d_channel_name]) + 2}", d_channel_length])

    for i in range(n_panels*2):
        joint_entries.append([f"{h_channel_name}:{1}", f"{panel_name}:{i + 1}", panel_length])
        joint_entries.append([f"{h_channel_name}:{2}", f"{panel_name}:{i + 1}", panel_length])

    if special_case:
        for i in range(4):
            joint_entries.append([f"{h_channel_name}:{i + 1}", f"{h_channel_name}:{i + 2}", nodes[max(nodes, key=lambda x: nodes[x][0])][0]])
    return joint_entries

def _extract_floor_joints(floor, part_entries):

    joint_entries = []
    channels, panels, cap = floor['channels'], floor['panels'], floor['cap']

    channel_length = channels[0][1]
    n_channels = part_entries[-1][2]
    print(n_channels)
    channel_name = part_entries[-1][1]
    channel_type = gd.FLOOR_BEAMS.profile_type
 
    all_same = all(panels[0] == panel for panel in panels)
    n_panels = len(panels) if all_same else len(panels) // 2
    b_panel_length = part_entries[0][-3] 
    b_panel_name = part_entries[0][1]
    if not all_same:
        t_panel_length = part_entries[1][-3] 
        t_panel_width = part_entries[1][-2]
        t_panel_name = part_entries[1][1]

    # Panel-to-Panel Joints
    for i in range(n_panels - 1):
        panel1 = f"{b_panel_name}:{i + 1}"
        panel2 = f"{b_panel_name}:{i + 2}"
        joint_length = b_panel_length
        joint_entries.append([panel1, panel2, joint_length])

        if not all_same:
            panel3 = f"{t_panel_name}:{i + 1}"
            panel4 = f"{t_panel_name}:{i + 2}"
            joint_length = t_panel_length
            joint_entries.append([panel3, panel4, joint_length])

    if not all_same:
        for i in range(n_panels):
            panel1 = f"{t_panel_name}:{i + 1}"
            panel2 = f"{b_panel_name}:{i + 1}"
            joint_length = t_panel_width
            joint_entries.append([panel1, panel2, joint_length])

    # Channel-to-Channel Joints
    if gd.I_IS_DOUBLE_C:
        for i in range(n_channels // 2):
            joint_entries.append([f"{channel_name}:{i + 1}", f"{channel_name}:{i + 2}", channel_length])

    # Panel-to-Channel Joints
    for i in range(n_channels // 2):
        joint_entries.append([f"{channel_name}:{i + 1}", f"{b_panel_name}:{1}", channel_length])

    return joint_entries

def _extract_floor_wall_joints(frames, panels, channels):
    return

def extract_joints():
    wall_joints = _extract_wall_joints()
    floor_joints = _extract_floor_joints()
    floor_wall_joints = _extract_floor_wall_joints()


    return 

import part_extraction as p 

# print(p.floor_entries)
joint1 = _extract_wall_joints(p.x_frame, p.x_entries)
# joint2 = _extract_wall_joints(p.y_frame, p.y_entries)
# joint = _extract_floor_joints(p.floor, p.floor_entries)
for j in joint1:
    print(j)

# for j in joint2:
#     print(j)
