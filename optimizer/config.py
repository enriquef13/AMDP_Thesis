import general_data as gd

submodule_type = 'Water Collection Welded'      # Type of submodule
material = gd.SST                               # Material type (gd.SST or gd.GLV)
x_in = 53                                       # Longer dimension in inches
y_in = 33                                       # Shorter dimension in inches
z_in = 20                                       # Basin height in inches
water_height_in = 10                            # Water height in inches
wind_zone = gd.WIND_NTC                         # Wind zone classification (gd.WIND_NTC, gd.WIND_TC, or gd.WIND_TCM)
top_load = 50e10                                   # Uniform load on top edges (lbf)