import general_data as gd

submodule_type = 'Water Collection Welded'      # Type of submodule
material = gd.SST                               # Material type (gd.SST or gd.GLV)
x_in = 258                                      # Longer dimension in inches
y_in = 142                                      # Shorter dimension in inches
z_in = 26                                       # Basin height in inches
water_height_in = 21                            # Water height in inches
wind_zone = gd.WIND_NTC                         # Wind zone classification (gd.WIND_NTC, gd.WIND_TC, or gd.WIND_TCM)
top_load = 11540.0584                           # Uniform load on top edges (lbf)