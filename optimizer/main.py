
# Generate top 15 designs for each case (xwall, ywall, floor)
# Mix and match
# Extract parts from each design
# Extract joints from each design
# Input into cost calculator
# Evaluate and rank

from generate_walls import generate_top_n_frames
from generate_floors import generate_top_n_floors
from part_extraction import get_floor_parts, get_wall_parts
from joint_detection import extract_floor_wall_joints, extract_wall_joints, extract_floor_joints
from cost import update_and_read_excel
import config as cfg

plot = False
xframes = generate_top_n_frames(1, xwall=True, plot=plot)
yframes = generate_top_n_frames(1, xwall=False, plot=plot)
floors = generate_top_n_floors(1, plot=plot)

final_designs = []
for i, xwall in enumerate(xframes):
    for j, ywall in enumerate(yframes):
        for k, floor in enumerate(floors):
            design = {
                'xwall': xwall,
                'id_xwall': i + 1,
                'ywall': ywall,
                'id_ywall': j + 1,
                'floor': floor,
                'id_floor': k + 1
            }
            final_designs.append(design)

for i, design in enumerate(final_designs):
    xwall = design['xwall']
    id_xwall = design['id_xwall']
    ywall = design['ywall']
    id_ywall = design['id_ywall']
    floor = design['floor']
    id_floor = design['id_floor']

    design_name = f"XW{id_xwall}_YW{id_ywall}_F{id_floor}"

    xwall_parts = get_wall_parts(xwall, design_name)
    ywall_parts = get_wall_parts(ywall, design_name)
    floor_parts = get_floor_parts(floor, design_name)

    joints_x = extract_wall_joints(xwall, xwall_parts)
    joints_y = extract_wall_joints(ywall, ywall_parts)
    joints_f = extract_floor_joints(floor, floor_parts)

    joints_fw = extract_floor_wall_joints(floor_parts, xwall_parts, ywall_parts)

    design_part_entries = xwall_parts + ywall_parts + floor_parts
    design_joint_entries = joints_x + joints_y + joints_f + joints_fw

    filepath = "cost_calculator.xlsx"
    values = update_and_read_excel(filepath, design_part_entries, design_joint_entries, submodule_type=cfg.submodule_type)
    print(values)