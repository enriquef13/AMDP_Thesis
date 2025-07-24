import general_data as gd
import numpy as np

class Profile:
    def __init__(self, material, gauge, profile_type):
        self.material = material
        self.gauge = gauge
        self.profile_type = profile_type
        self.profiles = {
            'C': {'h': 3.6875, 'b': 3, 'f': 0},
            'Rectangular': {'h': 4, 'b': 3.25, 'f': 0},
            'Hat': {'h': 4, 'b': 3.50, 'f': 1.25},
            'Double C': {'h': 4, 'b': 3.25, 'f': 0.75}
        }
        self.profile = self.profiles[profile_type]
        self.get_data()

    def get_data(self):
        """
        Calculate the Area Moment of Inertia (I), cross-sectional area (A), and section modulus (C) for the profile. 
        """
        t = next((k for k, v in gd.GAUGES[self.material].items() if v == self.gauge), None)
        b = self.profile['b']
        h = self.profile['h']
        f = self.profile['f']
        term1 = b * np.power(h, 3) / 12
        if self.profile_type == 'C':
            self.I = term1 - (b - t) * np.power((h - 2 * t), 3) / 12
            self.A = b * h - (b - t) * (h - 2 * t)
            self.c = h / 2
            self.unique_bends = 2
        elif self.profile_type == 'Rectangular':
            self.I = term1 - (b - 2 * t) * np.power((h - 2 * t), 3) / 12
            self.A = b * h - (b - 2 * t) * (h - 2 * t)
            self.c = h / 2
            self.unique_bends = 3
        elif self.profile_type == 'Hat':
            term1 = b * np.pow(h + 2 * f - 2 * t, 3) / 12
            term2 = (b - t) * np.pow(h - 2 * t, 3) / 12
            term3 = (b - t) * np.pow(f - t, 3) / 12 + (b - t) * (f - t) * np.pow(h/2 + (f-t)/2, 2)
            self.I = term1 - term2 - 2 * term3
            self.A = b * (h + 2 * f - 2 * t) - (b - t) * (h - 2 * t) - 2 * (b - t) * (f - t)
            self.c = h / 2 + (f - t)
            self.unique_bends = 4
        elif self.profile_type == 'Double C':
            term2 = (b - 2 * t) * np.power(h - 2 * t, 3) / 12
            term3 = t * np.power(h - 2 * f, 3) / 12
            self.I = term1 - term2 - term3
            self.A = b * h - (b - 2 * t) * (h - 2 * t) - t * (h - 2 * f)
            self.c = h / 2
            self.unique_bends = 4

        if self.profile_type in ['C', 'Hat', 'Double C']:
            self.perimeter = self.width = 2 * (f + b) + h
        elif self.profile_type == 'Rectangular':
            self.perimeter = self.width = 2 * (b + h)     
        self.corner_welds = 0