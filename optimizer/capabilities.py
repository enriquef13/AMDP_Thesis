import math

class Capabilities:
    def __init__(self, material, gauge):
        self.material = material if len(material) == 3 else material[:3]
        self.gauge = gauge
        self._extract_data()

    def _extract_data(self):
        gauges = {
            "SST-M3": {18: 0.047, 16: 0.059, 14: 0.075, 12: 0.101, 10: 0.128, 8: 0.158},
            "GLV-M5": {18: 0.042, 16: 0.053, 14: 0.066, 12: 0.096, 10: 0.129, 8: 0.157}
        }

        self.gauge_material = f"{self.gauge}_{self.material}"

        mat = "SST-M3" if self.material == 'SST' else "GLV-M5"
        self.thickness = gauges[mat][self.gauge]

        self.max_flange_width = {
            '18_GLV': 149.6,
            '16_GLV': 149.6,
            '14_GLV': 149.6,
            '12_GLV': 149.6,
            '10_GLV': 118.11,
            '8_GLV':  0,
            '18_SST': 149.6,
            '16_SST': 149.6,
            '14_SST': 118.11,
            '12_SST': 108.26,
            '10_SST': 82.67,
            '8_SST':  0
        }

        # Density values taken from cost calculator
        self.density = {
            '18_GLV': 0.013346144,
            '16_GLV': 0.01646971,
            '14_GLV': 0.020161197,
            '12_GLV': 0.028396052,
            '10_GLV': 0.03805071,
            '8_GLV':  0.045149723,
            '18_SST': 0.016825925, 
            '16_SST': 0.013634801,
            '14_SST': 0.021467559,
            '12_SST': 0.029880521,
            '10_SST': 0.038583586,
            '8_SST':  0.046706446
        }

        self.max_sheet_length = 180
        self.max_sheet_width = 60

        self.APB_max_flange_length = 8
        self.APB_min_flange_length = self.thickness* 5
        self.APB_min_throat_length = 15.75
        self.APB_max_flat_diagonal = 157.48
        self.APB_max_mass = 286.6
        self.APB_min_width = self.APB_min_length = self.APB_min_throat_length + 2 * (self.APB_max_flange_length * 5/8)
        self.APB_max_width = self.APB_max_length = self.max_flange_width[self.gauge_material]

        self.MPB_max_dim = 168

        self.TL_max_length = 334.65
        self.TL_max_diagonal_width = 7.87
        self.TL_max_mass_per_length = 7.348
        self.TL_max_width = 13 # Min constraint (conservative - assuming two 3" flanges)
        # self.TL_max_width = round(4*((self.TL_max_diagonal_width**2 / 2) ** 0.5), 2) # Max constraint (based on diagonal width with 4 flanges)

    def obtain_APB_limits(self):
        x_min = self.APB_min_width
        x_max = min(self.APB_max_width, self.max_sheet_width - 10)
        y_min = self.APB_min_length
        y_max = min(self.APB_max_length, self.max_sheet_length - 10)

        # Apply diagonal constraint
        max_diagonal = self.APB_max_flat_diagonal
        if x_max**2 + y_max**2 > max_diagonal**2:
            x_max = min(x_max, math.sqrt(max_diagonal**2 - y_min**2))
            y_max = min(y_max, math.sqrt(max_diagonal**2 - x_min**2))

        # Apply mass constraint
        max_mass = self.APB_max_mass / self.density[self.gauge_material]
        if x_max * y_max > max_mass:
            x_max = min(x_max, max_mass / y_min)
            y_max = min(y_max, max_mass / x_min)

        if self.gauge == 16 or self.gauge_material == "14_GLV" or self.gauge_material == "12_GLV":
            return x_min, x_max, y_min, y_max - 5  # Ensure minimum dimensions

        # Ensure minimum dimensions
        return x_min, x_max, y_min, y_max

    def obtain_MPB_limits(self):
        x_min = 0
        x_max = self.max_sheet_width
        y_min = 0
        y_max = self.MPB_max_dim
        return x_min, x_max, y_min, y_max