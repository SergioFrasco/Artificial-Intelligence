import numpy as np

pRainGivenRain = 0.7
pRainGivenNoRain = 0.3
pNoRainGivenRain = 0.3
pNoRainGivenNoRain = 0.7
pUmbrellaGivenRain = 0.9
pUmbrellaGivenNoRain = 0.2

def forward_algorithm(O):
    n = len(O)
    F = np.zeros((n + 3, 2))  # Increased size to include 2 future timesteps
    F[0, 0] = 0.5
    F[0, 1] = 0.5

    for t in range(1, n + 1):
        # Umbrella
        if O[t - 1] == 1:
            F[t, 0] = (F[t - 1, 0] * pRainGivenRain + F[t - 1, 1] * pNoRainGivenRain) * pUmbrellaGivenRain 
            F[t, 1] = (F[t - 1, 0] * (pRainGivenNoRain) + F[t - 1, 1] * (pNoRainGivenNoRain)) * pUmbrellaGivenNoRain
        # No Umbrella
        else:
            F[t, 0] = (F[t - 1, 1] * (1 - pRainGivenRain) + F[t - 1, 0] * (1 - pNoRainGivenRain)) * (1 - pUmbrellaGivenRain)
            F[t, 1] = (F[t - 1, 1] * (1 - pRainGivenNoRain) + F[t - 1, 0] * (1 - pNoRainGivenNoRain)) * (1 - pUmbrellaGivenNoRain)

        F = F / np.sum(F, axis=1, keepdims=True)


    for t in range(n + 1, n + 3):
        F[t, 0] = F[t - 1, 0] * pRainGivenRain + F[t - 1, 1] * pRainGivenNoRain
        F[t, 1] = F[t - 1, 0] * pNoRainGivenRain + F[t - 1, 1] * pNoRainGivenNoRain
        F = F / np.sum(F, axis=1, keepdims=True)

    return F[:, 0]

O = [int(x) for x in input().split()]
P = forward_algorithm(O)
for t, p in enumerate(P):
    print(f"Timestep {t}: {round(p, 3)}")