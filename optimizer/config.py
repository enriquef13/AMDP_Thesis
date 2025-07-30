import general_data as gd

# Example of HXV3 basin (22 ft x 14 ft x 27 in)
submodule_type = gd.WATER_COLLECTION_WELDED       # Type of submodule
material = gd.SST                                 # Material type (gd.SST or gd.GLV)
x_in = 250                                        # Longer dimension in inches
y_in = 135                                        # Shorter dimension in inches
z_in = 27                                         # Basin height in inches (min 26 inches, max 50 inches)
water_height_in = 15                              # Water height in inches
top_load = 20000                                  # Uniform load on top edges (lbf)
cost_calc_path = 'cost_calculator.xlsx' # Path to the Cost Calculator Excel file
store_path = 's3_sst_aggr/'                       # Path to store generated plots
n_top_final_designs = 15                          # Number of top designs to consider
n_configurations = 30                             # Number of design configurations used to generate the top designs