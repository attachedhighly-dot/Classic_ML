Becquerels

import numpy as np
import matplotlib as mlt

# 1. Physical Constants
AVOGADRO = 6.02214076e23  # atoms per mole

# 2. Input Parameters (Example: Carbon-14)
mass_grams = 0.001       # 1 milligram of C-14
molar_mass = 14.003      # grams per mole
half_life_years = 5730.0 # half-life in years

# 3. Convert Half-Life to Seconds (SI Units)
seconds_in_year = 365.25 * 24 * 3600
half_life_seconds = half_life_years * seconds_in_year

# 4. Calculate Decay Constant (lambda in 1/s)
lam = np.log(2) / half_life_seconds

# 5. Calculate Initial Number of Nuclei (N0)
N0 = (mass_grams / molar_mass) * AVOGADRO

# 6. Calculate Initial Activity (A0) in Becquerels
A0 = lam * N0
print(f"Initial Activity (A0): {A0:.4e} Bq")
print(f"Initial Activity in MBq: {A0 / 1e6:.2f} MBq\n")

# 7. Calculate Activity Over a Time Grid using NumPy
# Let's look at a timeline from 0 to 20,000 years (sampled at 5 timepoints)
years_grid = np.array([0, 2500, 5730, 11460, 20000])
seconds_grid = years_grid * seconds_in_year

# Vectorized formula: A(t) = A0 * e^(-lambda * t)
activity_grid = A0 * np.exp(-lam * seconds_grid)

# Display the results
print(f"{'Time (Years)':<15}{'Activity (Bq)':<20}{'Activity (MBq)':<15}")
for yr, bq in zip(years_grid, activity_grid):
    print(f"{yr:<15,}{bq:<20.2f}{bq/1e6:<15.4f}")
