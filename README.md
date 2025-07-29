# AMDP_Thesis

Repository for 2025 AMDP Thesis by **Enrique Flores** and **Stanley Salim**.

## Overview

This repository contains analysis and tools for manufacturing process optimization and assembly analysis.

## Project Components

### mfg_regions
Analysis of manufacturing capabilities of Tube Laser, Automatic Panel Bender, and Manual Press Brake machines. Comparison in terms of dimensions, materials, and cost.

### find_joint_lengths
iLogic script to automatically detect all the joint lengths between components in an Autodesk Inventor assembly. This is performed using geometric proximity between parts.

### optimizer
Program to automatically generate an automation friendly, low-cost water distribution or water collection sub-module. main.py needs to be executed within the optimizer/ folder for relative paths to work. Library dependencies are as follows:
- numpy 2.2.6
- pandas 2.2.3
- openpyxl 3.1.5
- scipy 1.15.3
- matplotlib 3.10.0
- xlwings 0.32.1

## Authors

- **Enrique Flores**
- **Stanley Salim**

## Copyright

© 2025 Enrique Flores and Stanley Salim. All rights reserved. 