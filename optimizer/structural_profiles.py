import numpy as np
import pandas as pd # type: ignore
from scipy.linalg import solve # type: ignore

def calculate_frame_structural(q):
    K = 1.0                             # Effective length factor (pinned-pinned)
    load_factor = 1.5                   # Load factor (LRFD)
    resistance_factor = 0.9             # Resistance factor (LRFD)
    max_deflection_ratio = 1/360        # Deflection limit
