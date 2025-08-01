import matplotlib.pyplot as plt # type: ignore
import numpy as np
from scipy.stats import f # type: ignore
import scipy.stats as stats # type: ignore

GLV = [4.71,
       7.60,
       5.51,
       4.60,
       5.77,
       6.57,
       5.22,
       11.53,
       6.27,
       5.09]

SST = [11.96,
       20.83,
       13.87,
       11.74,
       15.04,
       17.27,
       12.50,
       30.29,
       16.47,
       13.37]

WEIGHT = [4.22,
          6.72,
          5.08,
          5.36,
          6.99,
          8.07,
          5.99,
          11.47,
          5.99,
          4.62]

def scatter_costs():
    """
    Scatter the costs for GLV, SST.
    """
    plt.figure(figsize=(6, 4))
    # GLV trend line
    glv_fit = np.polyfit(WEIGHT, GLV, 1)
    glv_trend = np.poly1d(glv_fit)
    glv_r2 = np.corrcoef(WEIGHT, GLV)[0, 1] ** 2
    plt.plot(WEIGHT, glv_trend(WEIGHT), color='blue', linestyle='--', label=f'GLV Line Fit (R²={glv_r2:.2f})', linewidth=1)
    # SST trend line
    sst_fit = np.polyfit(WEIGHT, SST, 1)
    sst_trend = np.poly1d(sst_fit)
    sst_r2 = np.corrcoef(WEIGHT, SST)[0, 1] ** 2
    plt.plot(WEIGHT, sst_trend(WEIGHT), color='green', linestyle='--', label=f'SST Line Fit (R²={sst_r2:.2f})', linewidth=1)
    
    plt.scatter(WEIGHT, GLV, label='GLV Cost Data', color='blue')
    plt.scatter(WEIGHT, SST, label='SST Cost Data', color='green')
    plt.title('Rollformed Material Costs', fontsize=16, fontweight='bold', color='black')
    plt.xlabel('Weight (lbs/ft)')
    plt.ylabel('Cost ($/ft)')
    plt.yticks([])
    plt.xticks([])
    plt.legend()
    # plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Perform F-test for GLV
    glv_ssr = np.sum((glv_trend(WEIGHT) - np.mean(GLV))**2)  # Regression sum of squares
    glv_sse = np.sum((GLV - glv_trend(WEIGHT))**2)  # Error sum of squares
    glv_df_reg = 1  # Degrees of freedom for regression
    glv_df_err = len(WEIGHT) - 2  # Degrees of freedom for error
    glv_f_stat = (glv_ssr / glv_df_reg) / (glv_sse / glv_df_err)
    glv_f_crit = f.ppf(0.95, glv_df_reg, glv_df_err)  # 95% confidence level

    # Perform F-test for SST
    sst_ssr = np.sum((sst_trend(WEIGHT) - np.mean(SST))**2)  # Regression sum of squares
    sst_sse = np.sum((SST - sst_trend(WEIGHT))**2)  # Error sum of squares
    sst_df_reg = 1  # Degrees of freedom for regression
    sst_df_err = len(WEIGHT) - 2  # Degrees of freedom for error
    sst_f_stat = (sst_ssr / sst_df_reg) / (sst_sse / sst_df_err)
    sst_f_crit = f.ppf(0.95, sst_df_reg, sst_df_err)  # 95% confidence level

    # Display F-test results
    print(f"GLV F-statistic: {glv_f_stat:.2f}, F-critical: {glv_f_crit:.2f}")
    print(f"SST F-statistic: {sst_f_stat:.2f}, F-critical: {sst_f_crit:.2f}")

    # Calculate residuals
    glv_residuals = GLV - glv_trend(WEIGHT)
    sst_residuals = SST - sst_trend(WEIGHT)

    # Normalize residuals
    glv_residuals_normalized = glv_residuals / np.max(np.abs(glv_residuals))
    sst_residuals_normalized = sst_residuals / np.max(np.abs(sst_residuals))

    # Plot Q-Q plot for normalized GLV residuals
    plt.figure(figsize=(6, 4))
    stats.probplot(glv_residuals_normalized, dist="norm", plot=plt)
    plt.title("Q-Q Plot for Normalized GLV Residuals.\nRollforming Cost Model.", fontsize=16, fontweight='bold', color='black')
    plt.yticks([-1, -0.5, 0, 0.5, 1])  # Set y-ticks
    plt.tight_layout()
    plt.show()

    # Plot Q-Q plot for normalized SST residuals
    plt.figure(figsize=(6, 4))
    stats.probplot(sst_residuals_normalized, dist="norm", plot=plt)
    plt.title("Q-Q Plot for Normalized SST Residuals.\nRollforming Cost Model.", fontsize=16, fontweight='bold', color='black')
    plt.yticks([-1, -0.5, 0, 0.5, 1])  # Set y-ticks
    plt.tight_layout()
    plt.show()

scatter_costs()