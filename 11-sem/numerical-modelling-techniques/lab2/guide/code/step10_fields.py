def theta(x, y, xs, ys):
    """Круговий арктангенс (7.1.14): arg(z - ω) / 2π у межах [0, 1)."""
    return np.mod(np.arctan2(y - ys, x - xs), 2 * np.pi) / (2 * np.pi)


def phi_field(X, Y, G, fx, fy, fg):
    """Потенціал (7.2.38): потік + приєднані вихори + вільні вихори."""
    phi = X * V_INF[0] + Y * V_INF[1]
    for xs, ys, g in zip(np.r_[x0, fx], np.r_[y0, fy], np.r_[G, fg]):
        phi += g * theta(X, Y, xs, ys)
    return phi


def psi_field(X, Y, G, fx, fy, fg):
    """Функція течії (6.4.43): потік мінус Σ γ/(2π) ln R по всіх вихорах (R ≥ δ)."""
    psi = Y * V_INF[0] - X * V_INF[1]
    for xs, ys, g in zip(np.r_[x0, fx], np.r_[y0, fy], np.r_[G, fg]):
        R = np.maximum(np.hypot(X - xs, Y - ys), DELTA)
        psi -= g / (2 * np.pi) * np.log(R)
    return psi


(xa, xb), (ya, yb) = flow_box(1.0, 4.0, 1.5)   # область уздовж потоку за перешкодою
ny_ = int(300 * (yb - ya) / (xb - xa))          # стільки ж точок на одиницю довжини
X, Y = np.meshgrid(np.linspace(xa, xb, 300), np.linspace(ya, yb, ny_))
u, v = velocity(X.ravel(), Y.ravel(), G, fx, fy, fg)
u, v = u.reshape(X.shape), v.reshape(X.shape)
speed = np.hypot(u, v)
phi = phi_field(X, Y, G, fx, fy, fg)
psi = psi_field(X, Y, G, fx, fy, fg)
print(f"сітка {X.shape[1]}×{X.shape[0]}, max|V| = {speed.max():.2f}")
