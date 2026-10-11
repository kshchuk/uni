t = np.linspace(np.pi / 2, 3 * np.pi / 2, M)    # параметр кожної особливості
x0 = XC + R * np.cos(t)                         # x0[j], y0[j] — точки ω0j
y0 = R * np.sin(t)
h = R * np.pi / (M - 1)                         # крок уздовж дуги

size = np.hypot(x0[0] - x0[-1], y0[0] - y0[-1])
print(f"розмір = {size:.4f}, h = {h:.4f}")
