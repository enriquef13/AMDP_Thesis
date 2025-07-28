
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
from cost import update_and_read_excel, quit_excel
import config as cfg
import numpy as np
import pandas as pd # type: ignore
import xlwings as xw # type: ignore


quit_excel()

plot = True
n_top = 15
n_designs = 15
xframes = generate_top_n_frames(n_designs, xwall=True, plot=plot)
yframes = generate_top_n_frames(n_designs, xwall=False, plot=plot)
floors = generate_top_n_floors(n_designs, plot=plot)

xwall_part_entries = {}
xwall_joint_entries = {}
for i, xwall in enumerate(xframes):
    xwall_parts = get_wall_parts(xwall, f'XW{i+1}')
    xwall_joints = extract_wall_joints(xwall, xwall_parts)
    xwall_part_entries[f'XW{i+1}'] = xwall_parts
    xwall_joint_entries[f'XW{i+1}'] = xwall_joints

ywall_part_entries = {}
ywall_joint_entries = {}
for i, ywall in enumerate(yframes):
    ywall_parts = get_wall_parts(ywall, f'YW{i+1}')
    ywall_joints = extract_wall_joints(ywall, ywall_parts)
    ywall_part_entries[f'YW{i+1}'] = ywall_parts
    ywall_joint_entries[f'YW{i+1}'] = ywall_joints

floor_part_entries = {}
floor_joint_entries = {}
for i, floor in enumerate(floors):
    floor_parts = get_floor_parts(floor, f'F{i+1}')
    floor_joints = extract_floor_joints(floor, floor_parts)
    floor_part_entries[f'F{i+1}'] = floor_parts
    floor_joint_entries[f'F{i+1}'] = floor_joints

final_part_entries = {**xwall_part_entries, **ywall_part_entries, **floor_part_entries}
final_joint_entries = {**xwall_joint_entries, **ywall_joint_entries, **floor_joint_entries}

final_part_entry_list = []
for value in final_part_entries.values():
    for part in value:
        final_part_entry_list.append(part)

final_joint_entry_list = []
for value in final_joint_entries.values():
    for joint in value:
        final_joint_entry_list.append(joint)


filepath = 'cost_calculator.xlsx'
values = update_and_read_excel(filepath, final_part_entry_list, final_joint_entry_list, submodule_type=cfg.submodule_type)
for i, value in enumerate(values):
    print(f"Design {i+1}: {value[0]}, Cost: ${value[-1]}")
