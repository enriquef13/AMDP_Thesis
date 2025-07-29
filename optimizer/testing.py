import pandas as pd # type: ignore
from generate_walls import generate_top_n_frames
from generate_floors import generate_top_n_floors
from helpers import entries_to_list, get_part_and_joint_entries, get_design_summary_df, get_top_n_designs, get_top_part_and_joint_entries

plot = True
n_top = 15
n_designs = 1
xframes = generate_top_n_frames(n_designs, xwall=True, plot=plot)
yframes = generate_top_n_frames(n_designs, xwall=False, plot=plot)
floors = generate_top_n_floors(n_designs, plot=plot)

xwall_part_entries, xwall_joint_entries = get_part_and_joint_entries(xframes, design_name='XW')
ywall_part_entries, ywall_joint_entries = get_part_and_joint_entries(yframes, design_name='YW')
floor_part_entries, floor_joint_entries = get_part_and_joint_entries(floors, design_name='F')

final_part_entries = {**xwall_part_entries, **ywall_part_entries, **floor_part_entries}
final_joint_entries = {**xwall_joint_entries, **ywall_joint_entries, **floor_joint_entries}

final_part_entry_list = entries_to_list(final_part_entries)
final_joint_entry_list = entries_to_list(final_joint_entries)

values = [["F1", "Water Collection Welded", "NA", 2880.10, 1214.49, 0.00, 0.00, 46.57, 126.74, 173.31, 1659.69, 100],
          ["XW1", "Water Collection Welded", "NA", 867.93, 1082.65, 0.00, 0.00, 56.52, 153.79, 210.31, 90.40, 100],
          ["YW1", "Water Collection Welded", "NA", 450.60, 657.76, 0.00, 0.00, 30.35, 82.59, 112.94, 45.20, 100]]

design_summary_df = get_design_summary_df(values)
# print(design_summary_df)

top_n_designs = get_top_n_designs(design_summary_df, n=5)
# print(top_n_designs)

top_part_entries, top_joint_entries = get_top_part_and_joint_entries(top_n_designs, final_part_entries, final_joint_entries)
for entry in top_joint_entries:
    print(entry)