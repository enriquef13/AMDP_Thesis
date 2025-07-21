import general_data as gd
import config as cfg
from cost import update_and_read_excel
from structural_panels import calculate_floor_gauge, calculate_wall_gauge 
from profiles import Profile

filepath = 'cost_calculator.xlsx'
set_id = 'Set 1'
submodule_type = cfg.submodule_type

panel_parts = [{"name": "Floor 1", "type": "floor", "stream": "APB", "qty": 2, "width_in": 53, "length_in": 33, "water_height_in": 10, "wind_zone": "TC", "material": "SST-M3"},
               {"name": "Wall 1", "type": "wall", "stream": "APB", "qty": 2, "width_in": 138, "height_in": 27, "water_height_in": 10, "wind_zone": "TC", "material": "SST-M3"}]

channel_parts = [{"name": "Channel 1", "qty": 4, "width_in": 2, "length_in": 10, "material": "SST-M3", "gauge": 8}]

part_entries = []

# for part in panel_parts:
#     cut = gd.CUT_MSP if part["stream"] == "APB" else gd.CUT_MSL
#     form = gd.FORM_APB if part["stream"] == "APB" else gd.FORM_MPB
#     perimeter = 2 * (part["width_in"] + part["length_in"]) if part["type"] == "floor" else 2 * (part["width_in"] + part["height_in"])
#     length = part["length_in"] if part["type"] == "floor" else part["height_in"]
#     width = part["width_in"]
#     g = [width, length, part["water_height_in"], part["wind_zone"], part["material"]]
#     gauge = calculate_floor_gauge(g[0], g[1], g[2], g[4]) if part["type"] == "floor" else calculate_wall_gauge(g[0], g[1], g[2], g[3], g[4])

#     part_entry = [set_id, part["name"], 
#                   part["qty"], 
#                   cut, 
#                   form, 
#                   part["material"], 
#                   gauge, 
#                   0, 
#                   perimeter, 
#                   4, 
#                   4, 
#                   width, 
#                   length, 
#                   'Class 1']

#     part_entries.append(part_entry)

# for part in channel_parts:
#     cut = gd.CUT_TL
#     form = gd.FORM_RF
#     perimeter = 2 * (part["width_in"] + part["length_in"])
#     length = part["length_in"]
#     width = part["width_in"]

#     channel_entry = [set_id, part["name"], 
#                      part["qty"], 
#                      cut, 
#                      form, 
#                      part["material"], 
#                      part["gauge"], 
#                      0, 
#                      perimeter, 
#                      4, 
#                      0,  
#                      length,
#                      width, 
#                      'Class 1']

#     part_entries.append(channel_entry)

# cost = update_and_read_excel(filepath, part_entries, submodule_type=submodule_type)