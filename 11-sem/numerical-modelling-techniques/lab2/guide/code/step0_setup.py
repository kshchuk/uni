import numpy as np
import matplotlib.pyplot as plt

M = 24                                          # кількість вихорів на контурі
ALPHA = 0.0                                     # кут набігаючого потоку, рад
V_INF = np.array([np.cos(ALPHA), np.sin(ALPHA)])   # |V∞| = 1
R = 0.5                                         # радіус півкола: розмір перешкоди 1
XC = R / 2                                      # центр кола: перешкода по центру
T_END = 80.0                                    # тривалість моделювання
X_MAX = 8.0                                     # далі цієї межі вихори видаляємо
