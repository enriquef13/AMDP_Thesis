
from generate_walls import generate_top_n_frames
from generate_floors import generate_top_n_floors
from cost import update_and_read_excel, quit_excel
from helpers import entries_to_list, get_part_and_joint_entries, get_design_summary_df, get_top_n_designs, get_top_part_and_joint_entries
import config as cfg

quit_excel()

n_top = cfg.n_top_final_designs
n_configs = cfg.n_configurations
# xframes = generate_top_n_frames(n_configs, xwall=True)
# yframes = generate_top_n_frames(n_configs, xwall=False)
floors = generate_top_n_floors(n_configs)

raise ValueError("No frames generated. Check the configuration and input parameters.")

xwall_part_entries, xwall_joint_entries = get_part_and_joint_entries(xframes, design_name='XW')
ywall_part_entries, ywall_joint_entries = get_part_and_joint_entries(yframes, design_name='YW')
floor_part_entries, floor_joint_entries = get_part_and_joint_entries(floors, design_name='F')

final_part_entries = {**xwall_part_entries, **ywall_part_entries, **floor_part_entries}
final_joint_entries = {**xwall_joint_entries, **ywall_joint_entries, **floor_joint_entries}

final_part_entry_list = entries_to_list(final_part_entries)
final_joint_entry_list = entries_to_list(final_joint_entries)

print(f"Writing {len(final_part_entry_list)} part entries and {len(final_joint_entry_list)} joint entries to Excel (this may take a while)...")
values = update_and_read_excel(cfg.cost_calc_path, final_part_entry_list, final_joint_entry_list, submodule_type=cfg.submodule_type)
for i, value in enumerate(values):
    print(f"Sub-design {i+1}: {value[0]}, Cost: ${value[-1]}")

design_summary_df = get_design_summary_df(values)
top_n_designs = get_top_n_designs(design_summary_df, n=n_top)
top_part_entries, top_joint_entries = get_top_part_and_joint_entries(top_n_designs, final_part_entries, final_joint_entries)

print(f"Final {n_top} designs. Writing {len(top_part_entries)} part entries and {len(top_joint_entries)} joint entries to Excel (this may take another while)...")
final_values = update_and_read_excel(cfg.cost_calc_path, top_part_entries, top_joint_entries, submodule_type=cfg.submodule_type)
final_values = sorted(final_values, key=lambda x: x[-1])  # Sort by cost
for i, value in enumerate(final_values):
    print(f"Design {i+1}: {value[0]}, Cost: ${value[-1]}")