import general_data as gd

# Example of HXV3 basin (22 ft x 14 ft x 27 in)
submodule_type = gd.WATER_COLLECTION_TRIARMOR       # Type of submodule
material = gd.GLV                                 # Material type (gd.SST or gd.GLV)
x_in = 250                                        # Longer dimension in inches (min 26, max 145)
y_in = 135                                        # Shorter dimension in inches (min 26, max 145)
z_in = 27                                         # Basin height in inches (min 26 inches, max 50 inches)
water_height_in = 15                              # Water height in inches
top_load = 20000                                  # Uniform load on top edges (lbf)
cost_calc_path = 'cost_calc/cost_calculator.xlsx' # Path to the Cost Calculator Excel file
store_path = 'plots/'                             # Path to store generated plots
n_top_final_designs = 15                          # Number of top designs to consider (max 100)
n_configurations = 30                             # Number of design configurations used to generate the top designs (max 30)

# OPTIONAL: Define APB - TL ratio
use_ratio = False                                 # Require a ratio of panel bender to tube laser in generated designs
APB_ratio = 0.8                                   # Ratio that will go into the panel bender vs tube laser
ratio_variance = 0.2                              # Allowed variation (+/-) in the ratio of panel bender to tube laser