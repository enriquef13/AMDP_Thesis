import general_data as gd

material = gd.SST                            # Material type (gd.SST or gd.GLV)
submodule_type = 'Water Collection Welded'   # Type of submodule
x_in = 53                                    # Longer dimension in inches
y_in = 33                                    # Shorter dimension in inches
z_in = 10                                    # Basin height in inches
water_height_in = 10                         # Water height in inches
wind_zone = gd.WIND_NTC                      # Wind zone classification (gd.WIND_NTC, gd.WIND_TC, or gd.WIND_TCM)
q = 1000e5                                   # Uniform distributed load on top edge (lbf/in)