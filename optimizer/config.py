import general_data as gd

# Example of HXV3 basin (22 ft x 14 ft x 26 in)
submodule_type = 'Water Collection Welded'      # Type of submodule
material = gd.SST                               # Material type (gd.SST or gd.GLV)
x_in = 315                                      # Longer dimension in inches
y_in = 160                                      # Shorter dimension in inches
z_in = 30                                       # Basin height in inches
water_height_in = 21                            # Water height in inches
wind_zone = gd.WIND_NTC                         # Wind zone classification (gd.WIND_NTC, gd.WIND_TC, or gd.WIND_TCM)
top_load = 11540.0584                           # Uniform load on top edges (lbf)

# # Dimensions for GAC CWB
# x_in = 258
# y_in = 142
# z_in = 26