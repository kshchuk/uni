import numpy as np
import matplotlib.pyplot as plt

M = 80                                          # кількість дискретних особливостей
GAMMA0 = 1.0                                    # циркуляція: запустіть для -1, 0, 1
ALPHA = 0.0                                     # кут набігаючого потоку, рад
V_INF = np.array([np.cos(ALPHA), np.sin(ALPHA)])   # |V∞| = 1
R = 0.5                                         # радіус півкола: діаметр = 1
XC = R / 2                                      # центр кола: перешкода по центру
