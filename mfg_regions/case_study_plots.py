import matplotlib.pyplot as plt # type: ignore
import numpy as np

def hxv3_sst():
    # Data
    products = ['Optimized', 'Concept', 'Legacy']
    material_cost = [5776, 9060, 7625]
    fabrication_cost = [1956, 2427, 2891]
    assembly_cost = [2570, 3062, 2636]

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

def hxv3_glv():
    # Data
    products = ['Optimized', 'Concept', 'Legacy']
    material_cost = [3152, 3323, 3110]
    fabrication_cost = [2048, 2381, 2863]
    assembly_cost = [699, 424, 659]

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
    ax.set_title('Case A: GLV', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')

    # Show the plot
    plt.tight_layout()
    plt.show()

def s3e_sst():
    # Data
    products = ['Optimized', 'Concept', 'Legacy']
    material_cost = [3896, 5005, 4397]
    fabrication_cost = [1390, 1299, 2343]
    assembly_cost = [1748, 1733, 1898]

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
    ax.set_title('Case B: SST', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')

    # Show the plot
    plt.tight_layout()
    plt.show()

def s3e_glv():
    # Data
    products = ['Optimized', 'Concept', 'Legacy']
    material_cost = [2279, 2774, 2244]
    fabrication_cost = [1384, 1286, 2325]
    assembly_cost = [425, 908, 424]

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
    ax.set_title('Case B: GLV', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')

    # Show the plot
    plt.tight_layout()
    plt.show()

def s15_sst():
    # Data
    products = ['Optimized', 'Legacy']
    material_cost = [1310, 2002]
    fabrication_cost = [734, 1006]
    assembly_cost = [708, 1039]

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
    ax.set_title('Case C: SST', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')

    # Show the plot
    plt.tight_layout()
    plt.show()

def s15_glv():
    # Data
    products = ['Optimized', 'Legacy']
    material_cost = [792, 730]
    fabrication_cost = [712, 1007]
    assembly_cost = [181, 135]

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
    ax.set_title('Case C: GLV', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='upper left')

    # Show the plot
    plt.tight_layout()
    plt.show()

hxv3_sst()
hxv3_glv()
s3e_sst()
s3e_glv()
s15_sst()
s15_glv()
