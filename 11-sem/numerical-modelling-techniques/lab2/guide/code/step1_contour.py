t = np.linspace(np.pi / 2, 3 * np.pi / 2, M)    # параметр кожної особливості
x0 = XC + R * np.cos(t)                         # x0[j], y0[j] — точки ω0j
y0 = R * np.sin(t)
L = np.pi * R                                   # довжина контуру (півкола)
h = L / (M - 1)                                 # крок між вихорами
DELTA = L / (2 * M)                             # δ = L/(2M) [Сл. 15]

print(f"L = {L:.4f}, h = {h:.4f}, DELTA = {DELTA:.4f}")
