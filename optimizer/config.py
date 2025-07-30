import general_data as gd

# Example of HXV3 basin (22 ft x 14 ft x 27 in)
submodule_type = gd.WATER_COLLECTION_TRIARMOR       # Type of submodule
material = gd.GLV                                 # Material type (gd.SST or gd.GLV)
x_in = 160                                        # Longer dimension in inches
y_in = 58                                        # Shorter dimension in inches
z_in = 27                                         # Basin height in inches (min 26 inches, max 50 inches)
water_height_in = 10                              # Water height in inches
top_load = 200                                  # Uniform load on top edges (lbf)
cost_calc_path = 'cost_calculator.xlsx' # Path to the Cost Calculator Excel file
store_path = 's3f_14x24_wd_glv_cons/'                # Path to store generated plots
n_top_final_designs = 15                          # Number of top designs to consider
n_configurations = 35                             # Number of design configurations used to generate the top designs

# # Dimensions for GAC CWB
# x_in = 235
# y_in = 135
# z_in = 26   
