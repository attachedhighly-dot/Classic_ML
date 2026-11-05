import numpy as np
import matplotlib.pyplot as plt

# Parameters
N0 = 1000  # initial nuclei
thalf = 5730  # half-life in years (e.g., Carbon-14)
lam = np.log(2) / thalf

# Time grid
t = np.linspace(0, 20000, 200)

# Vectorized calculation
N_t = N0 * np.exp(-lam * t)

plt.plot(t, N_t, label="Exact Decay $N(t) = N_0 e^{-\lambda t}$")
plt.xlabel("Time (years)")
plt.ylabel("Undecayed Nuclei $N(t)$")
plt.legend()
plt.show()
