import numpy as np

# Parameters
N0 = 10000
dt = 1.0  # time step
thalf = 50.0  # half life in units of time
lam = np.log(2) / thalf
p = 1.0 - np.exp(-lam * dt)

n_steps = 200
N_sim = np.zeros(n_steps)
N = N0

for i in range(n_steps):
  N_sim[i] = N
  # Randomly test each remaining nucleus against probability p
  if N > 0:
    decays = np.random.binomial(N, p)
    N -= decays
