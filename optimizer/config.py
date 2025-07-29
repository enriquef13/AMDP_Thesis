import general_data as gd

# Example of HXV3 basin (22 ft x 14 ft x 27 in)
submodule_type = gd.WATER_COLLECTION_WELDED     # Type of submodule
material = gd.SST                               # Material type (gd.SST or gd.GLV)
x_in = 310                                      # Longer dimension in inches
y_in = 160                                      # Shorter dimension in inches
z_in = 27                                       # Basin height in inches (min 26 inches, max 50 inches)
water_height_in = 15                            # Water height in inches
wind_zone = gd.WIND_NTC                         # Wind zone classification (gd.WIND_NTC, gd.WIND_TC, or gd.WIND_TCM)
top_load = 40000                                # Uniform load on top edges (lbf)
cost_calc_path = 'cost_calculator.xlsx'         # Path to the Cost Calculator Excel file
store_path = 'temp_plots/'                      # Path to store generated plots
n_top_final_designs = 15                        # Number of top designs to consider
n_configurations = 20                           # Number of design configurations used to generate the top designs


# Dead load = 1.4
# Tensile = 0.9
# Bending = 

# # Dimensions for GAC CWB
# x_in = 235
# y_in = 135
# z_in = 26   