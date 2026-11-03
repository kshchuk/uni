def theta(x, y, xs, ys):
    """Круговий арктангенс (7.1.14): arg(z - ω) / 2π у межах [0, 1)."""
    return np.mod(np.arctan2(y - ys, x - xs), 2 * np.pi) / (2 * np.pi)


def wrap(a):
    """Приводить різницю кутів (у частках 2π) до (-1/2, 1/2]: прибирає стрибки."""
    return a - np.round(a)


def phi_field(X, Y, G, fx, fy, fg):
    """Потенціал (7.2.38): потік + приєднані вихори + вільні вихори."""
    phi = X * V_INF[0] + Y * V_INF[1]
    for xs, ys, g in zip(np.r_[x0, fx], np.r_[y0, fy], np.r_[G, fg]):
        phi += g * theta(X, Y, xs, ys)
    return phi


def dphi_dt(X, Y, G0, fx0, fy0, G1, fx1, fy1, fg1, dt):
    """∂φ/∂t між кроками n і n+1 (без розрізів, див. гайд)."""
    ox = np.r_[fx0, x0[0], x0[-1]]              # де кожен вільний вихор був на кроці n
    oy = np.r_[fy0, y0[0], y0[-1]]              # (новонароджені — на кінцях контуру)
    d = np.zeros_like(X)
    for i in range(len(fg1)):
        d += fg1[i] * wrap(theta(X, Y, fx1[i], fy1[i]) - theta(X, Y, ox[i], oy[i]))
    dB = G1 - G0
    dB[[0, -1]] = G1[[0, -1]]                   # кінцеві Γ на кроці n стали вільними
    S = np.cumsum(dB)                           # S_M = 0 за теоремою Кельвіна
    for j in range(M - 1):
        d += S[j] * wrap(theta(X, Y, x0[j], y0[j]) - theta(X, Y, x0[j + 1], y0[j + 1]))
    return d / dt


X, Y = np.meshgrid(np.linspace(-1, 4, 300), np.linspace(-1.5, 1.5, 180))
xs_, ys_ = X.ravel(), Y.ravel()
u, v = velocity(xs_, ys_, G, fx, fy, fg)
u, v = u.reshape(X.shape), v.reshape(X.shape)
speed = np.hypot(u, v)
phi = phi_field(X, Y, G, fx, fy, fg)
# ще один крок, щоб оцінити ∂φ/∂t
G1, fx1, fy1, fg1, _, dt1 = time_step(G, fx, fy, fg, shed_total)
Cp = 1 - speed**2 - 2 * dphi_dt(X, Y, G, fx, fy, G1, fx1, fy1, fg1, dt1)   # (7.2.39)
print(f"Cp перед перешкодою (x = -0.3, y = 0): {Cp[90, 42]:.2f}")
