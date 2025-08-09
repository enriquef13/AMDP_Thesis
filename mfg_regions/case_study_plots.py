from scipy.stats import f # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np
from sklearn.linear_model import LinearRegression # type: ignore
from sklearn.metrics import r2_score # type: ignore

# Data
def plot_1():
    categories = ['Material Cost', 'Labor Cost', 'Assembly Cost', 'Total Cost']
    legacy_costs = [2244, 2325, 424, 4993]
    concept_costs = [2774, 1286, 908, 4967]

    # Bar positions
    x = np.arange(len(categories))
    bar_width = 0.32  # Reduce bar width for spacing
    spacing = 0.015   # Add spacing between bars

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot bars
    ax.bar(x - (bar_width / 2 + spacing), legacy_costs, bar_width, label='Legacy', color='#4f8cd6')
    ax.bar(x + (bar_width / 2 + spacing), concept_costs, bar_width, label='Concept', color='#66c2a5')

    # Add labels, title, and legend
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylabel('Cost ($)', fontsize=14)
    ax.set_title('MPB vs APB-TL: Cost Comparison', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12)

    # Show the plot
    plt.tight_layout()
    plt.show()

def plot_2():
    # Data
    iterations = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    material_cost = [7625, 8037, 9995, 9317, 9060, 9322, 9494, 10431, 10057]
    labor_cost = [3243, 3268, 3667, 3464, 2529, 2592, 3378, 4459, 3472]
    assembly_cost = [2636, 2853, 3453, 3244, 3062, 3035, 3314, 3773, 3968]

    # Function to calculate F-statistic
    def calculate_f_statistic(y, y_pred):
        ssr = np.sum((y_pred - np.mean(y))**2)  # Regression sum of squares
        sse = np.sum((y - y_pred)**2)           # Error sum of squares
        df_model = 1                            # Degrees of freedom for the model
        df_residual = len(y) - 2                # Degrees of freedom for residuals
        msr = ssr / df_model                    # Mean square regression
        mse = sse / df_residual                 # Mean square error
        f_statistic = msr / mse                 # F-statistic
        return f_statistic, df_model, df_residual
    
    # Function to calculate F-critical
    def calculate_f_critical(df_model, df_residual, confidence=0.95):
        return f.ppf(confidence, df_model, df_residual)
    
    # Create a 1x3 subplot layout
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Material Cost Plot
    ax = axes[0]
    ax.scatter(iterations, material_cost, color='blue', label='Material Cost')
    model = LinearRegression().fit(np.array(iterations).reshape(-1, 1), material_cost)
    trendline = model.predict(np.array(iterations).reshape(-1, 1))
    f_stat, df_model, df_residual = calculate_f_statistic(material_cost, trendline)
    f_critical = calculate_f_critical(df_model, df_residual)
    print(f"F-statistic for Material Cost: {f_stat:.2f}, F-critical: {f_critical:.2f}")
    ax.plot(iterations, trendline, color='blue', linestyle='--', label=f'Trendline (R²={r2_score(material_cost, trendline):.2f}), F={f_stat:.1f}>{f_critical:.1f}')
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Material Cost ($)', fontsize=12)
    ax.set_title('Material Cost', fontsize=14, fontweight='bold')
    ax.set_ylim(min(material_cost) * 0.9, max(material_cost) * 1.1)  # Adjust y-axis limit for better visibility
    ax.legend(fontsize=10, loc='upper left')

    # Labor Cost Plot
    ax = axes[1]
    ax.scatter(iterations, labor_cost, color='green', label='Labor Cost')
    model = LinearRegression().fit(np.array(iterations).reshape(-1, 1), labor_cost)
    trendline = model.predict(np.array(iterations).reshape(-1, 1))
    f_stat, df_model, df_residual = calculate_f_statistic(labor_cost, trendline)
    f_critical = calculate_f_critical(df_model, df_residual)
    print(f"F-statistic for Labor Cost: {f_stat:.2f}, F-critical: {f_critical:.2f}")
    ax.plot(iterations, trendline, color='green', linestyle='--', label=f'Trendline (R²={r2_score(labor_cost, trendline):.2f}), F={f_stat:.1f}<{f_critical:.1f}')
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Labor Cost ($)', fontsize=12)
    ax.set_title('Labor Cost', fontsize=14, fontweight='bold')
    ax.set_ylim(min(labor_cost) * 0.9, max(labor_cost) * 1.1)  # Adjust y-axis limit for better visibility
    ax.legend(fontsize=10, loc='upper left')

    # Assembly Cost Plot
    ax = axes[2]
    ax.scatter(iterations, assembly_cost, color='orange', label='Assembly Cost')
    model = LinearRegression().fit(np.array(iterations).reshape(-1, 1), assembly_cost)
    trendline = model.predict(np.array(iterations).reshape(-1, 1))
    f_stat, df_model, df_residual = calculate_f_statistic(assembly_cost, trendline)
    f_critical = calculate_f_critical(df_model, df_residual)
    print(f"F-statistic for Assembly Cost: {f_stat:.2f}, F-critical: {f_critical:.2f}")
    ax.plot(iterations, trendline, color='orange', linestyle='--', label=f'Trendline (R²={r2_score(assembly_cost, trendline):.2f}), F={f_stat:.1f}>{f_critical:.1f}')
    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Assembly Cost ($)', fontsize=12)
    ax.set_title('Assembly Cost', fontsize=14)
    ax.set_ylim(min(assembly_cost) * 0.9, max(assembly_cost) * 1.1)  # Adjust y-axis limit for better visibility
    ax.legend(fontsize=10, loc='upper right')

    # Adjust layout
    plt.tight_layout()
    plt.show()

def plot_stacked_bar_chart():
    # Data
    iterations = ['2%', '12%', '57%', '58%', '59%', '59%', '74%', '78%', '100%']
    material_cost = [7625, 8037, 9995, 9317, 9060, 9322, 9494, 10431, 10057]
    labor_cost = [3243, 3268, 3667, 3464, 2529, 2592, 3378, 4459, 3472]
    assembly_cost = [2636, 2853, 3453, 3244, 3062, 3035, 3314, 3773, 3968]

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Bar positions
    x = np.arange(len(iterations))
    bar_width = 0.6

    # Plot stacked bars
    ax.bar(x, material_cost, bar_width, label='Material Cost', color='#4f8cd6')
    ax.bar(x, labor_cost, bar_width, bottom=material_cost, label='Fabrication Cost', color='#e74c3c')
    ax.bar(x, assembly_cost, bar_width, bottom=np.array(material_cost) + np.array(labor_cost), label='Assembly Cost', color='#66c2a5')

    # Add labels, title, and legend
    ax.set_xticks(x)
    ax.set_xticklabels(iterations, fontsize=12)
    ax.set_ylabel('Cost ($)', fontsize=14)
    ax.set_title('Cost Across APB Compliance Iterations', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='lower right')

    # Show the plot
    plt.tight_layout()
    plt.show()

def plot_case_a():
    # Data
    products = ['Optimized', 'Legacy', 'Concept']
    material_cost = [6238, 7625, 9060]
    fabrication_cost = [2071, 2891, 2427]
    assembly_cost = [2652, 2636, 3062]

    # Bar positions
    y = np.arange(len(products))
    bar_height = 0.6

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot stacked bars
    ax.barh(y, material_cost, bar_height, label='Material Cost', color='#4f8cd6')
    ax.barh(y, fabrication_cost, bar_height, left=material_cost, label='Fabrication Cost', color='#e74c3c')
    ax.barh(y, assembly_cost, bar_height, left=np.array(material_cost) + np.array(fabrication_cost), label='Assembly Cost', color='#66c2a5')

    # Add labels, title, and legend
    ax.set_yticks(y)
    ax.set_yticklabels(products, fontsize=12, rotation=45, ha='right')
    ax.set_xlabel('Cost ($)', fontsize=14)
    ax.set_title('Case A: SST', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')

    # Show the plot
    plt.tight_layout()
    plt.show()

plot_case_a()

# plot_stacked_bar_chart()
# plot_1()
# plot_2()