from joint_detection import extract_floor_wall_joints, extract_wall_joints, extract_floor_joints
from part_extraction import get_floor_parts, get_wall_parts
import pandas as pd # type: ignore
import re
from collections import defaultdict

def entries_to_list(entries):
    """
    Convert a dictionary of entries to a list of lists.
    """
    entry_list = []
    for value in entries.values():
        for entry in value:
            entry_list.append(entry)
    return entry_list

def get_part_and_joint_entries(designs, design_name='XW'):
    """
    Convert part and joint entries to a list of lists.
    """
    part_entries = {}
    joint_entries = {}

    wall = design_name in ['XW', 'YW']
    for i, design in enumerate(designs):
        if wall:
            design_parts = get_wall_parts(design, f'{design_name}{i+1}')
            design_joints = extract_wall_joints(design, design_parts)
        else:
            design_parts = get_floor_parts(design, f'{design_name}{i+1}')
            design_joints = extract_floor_joints(design, design_parts)

        part_entries[f'{design_name}{i+1}'] = design_parts
        joint_entries[f'{design_name}{i+1}'] = design_joints

    return part_entries, joint_entries

def get_design_summary_df(values):
    """
    Extract names and costs from entries.
    """
    df = pd.DataFrame(values)
    design_summary = df.iloc[:, [0, -1]]
    design_summary.columns = ['Design_Name', 'Cost']
    design_summary = design_summary.sort_values(by='Cost').reset_index(drop=True)
    for row in design_summary.itertuples():
        design_name = row[1]
        if 'XW' in design_name:
            design_summary.at[row.Index, 'Type'] = 'X-Wall'
        elif 'YW' in design_name:
            design_summary.at[row.Index, 'Type'] = 'Y-Wall'
        elif 'F' in design_name:
            design_summary.at[row.Index, 'Type'] = 'Floor'

    return design_summary

def get_top_n_designs(design_summary_df, n=15):
    """
    Get the top n designs based on cost.
    """
    top_designs = {}
    floor_df = design_summary_df[design_summary_df['Type'] == "Floor"]
    xwall_df = design_summary_df[design_summary_df['Type'] == "X-Wall"]
    ywall_df = design_summary_df[design_summary_df['Type'] == "Y-Wall"]

    for i, floor in floor_df.iterrows():
        for j, xwall in xwall_df.iterrows():
            for k, ywall in ywall_df.iterrows():
                design_name = f"{floor['Design_Name']}_{xwall['Design_Name']}_{ywall['Design_Name']}"
                cost = floor['Cost'] + xwall['Cost'] + ywall['Cost']
                top_designs[design_name] = cost

    top_designs = sorted(top_designs.items(), key=lambda item: item[1])[:n]

    return dict(top_designs)

def get_top_part_and_joint_entries(top_designs, part_entries, joint_entries):
    """
    Get part and joint entries for the top designs.
    """
    updated_part_entries = []
    updated_joint_entries = []

    # Convert top_designs to a set of design_names for quick lookup
    top_design_names = top_designs.keys()

    # Helper to update entries
    def update_parts(entries):
        entries = entries_to_list(entries) if isinstance(entries, dict) else entries
        updated = []
        for entry in entries:
            for design_name in top_design_names:
                if entry[0] in design_name.split('_'):
                    new_entry = entry.copy()
                    new_entry[0] = design_name
                    # Replace after last "_" in entry[1] with design_name
                    prefix = new_entry[1][:new_entry[1].rfind("_")+1] 
                    new_entry[1] = prefix + design_name
                    updated.append(new_entry)
        return updated
    
    def replace_part_name_with_design(part_name, design_name):
        # Match patterns like XWn1, YWn1, or Fn1
        match = re.search(r'(XW\d+|YW\d+|F\d+)(:.*)?', part_name)
        if match:
            base, suffix = match.groups()
            suffix = suffix if suffix else ""  # Keep :n2 if it exists
            # Replace only the base (e.g., XWn1, YWn1, Fn1) with the design name
            return part_name.replace(base + suffix, design_name + suffix)
        return part_name  # Return unchanged if no match is found
    
    def extract_part_base(part_name):
        # Use regex to find the substring between the last "_" and the ":"
        match = re.search(r'_(F\d+|XW\d+|YW\d+):', part_name)
        if match:
            return match.group(1)  # Return the captured group (e.g., F1, XW2, YW1)
        return None  # Return None if no match is found
    
    def update_joints(entries):
        entries = entries_to_list(entries) if isinstance(entries, dict) else entries
        updated = []
        for entry in entries:
            for design_name in top_design_names:
                partA = entry[0]
                partB = entry[1]
                if extract_part_base(partA) in design_name.split('_') and extract_part_base(partB) in design_name.split('_'):
                    new_entry = entry.copy()
                    new_entry[0] = replace_part_name_with_design(partA, design_name)
                    new_entry[1] = replace_part_name_with_design(partB, design_name)
                    updated.append(new_entry)
        return updated

    updated_part_entries = update_parts(part_entries)
    updated_joint_entries = update_joints(joint_entries)

    # Group updated_part_entries by part_set (the first entry in each row)
    part_set_groups = defaultdict(list)
    for entry in updated_part_entries:
        part_set = entry[0]
        part_set_groups[part_set].append(entry)

    # Now, for each part_set, call your function with the entire slice (list of entries for that part_set)
    def process_part_set(part_set_entries):
        floor_entries = [entry for entry in part_set_entries if entry[1].startswith("F")]
        wall_entries = [entry for entry in part_set_entries if entry[1].startswith("W")]
        floor_wall_joints = extract_floor_wall_joints(floor_entries, wall_entries, wall_entries)
        updated_joint_entries.extend(floor_wall_joints)

    for part_set, entries in part_set_groups.items():
        process_part_set(entries)


    return updated_part_entries, updated_joint_entries
    