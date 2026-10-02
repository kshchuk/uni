def plate_exact(X, Y, gamma, a=0.5):
    """Точна швидкість: пластина x = 0, |y| ≤ a, потік (1, 0), циркуляція gamma."""
    zp = -1j * (X + 1j * Y)                      # поворот: пластина лягає на [-a, a]
    root = np.sqrt(zp - a) * np.sqrt(zp + a)     # вітка √(z²-a²) ~ z на нескінченності
    alpha = -np.pi / 2                           # у повернутій системі потік іде вниз
    dw = np.cos(alpha) - 1j * np.sin(alpha) * zp / root + gamma / (2j * np.pi * root)
    vbar = -1j * dw                              # назад у вихідну систему: u - iv
    return vbar.real, -vbar.imag


Xp, Yp = np.meshgrid(np.linspace(-1, 1, 201), np.linspace(-1, 1, 201))
mask = np.hypot(Xp, np.maximum(np.abs(Yp) - 0.5, 0)) > 0.15     # далі 0.15 від пластини
for g0 in (0.0, 1.0):
    errors = []
    for m in (10, 20, 40, 80, 160):
        qx0, qy0 = np.zeros(m), np.linspace(-0.5, 0.5, m)
        qxc, qyc = qx0[:-1], (qy0[:-1] + qy0[1:]) / 2
        qnx, qny = -np.ones(m - 1), np.zeros(m - 1)
        Gq = solve_gammas(qx0, qy0, qxc, qyc, qnx, qny, vinf, g0)
        uq, vq = velocity_field(Xp, Yp, qx0, qy0, Gq, vinf, 0.01)
        with np.errstate(divide="ignore", invalid="ignore"):
            ue, ve = plate_exact(Xp, Yp, g0)
        errors.append(np.max(np.hypot(uq - ue, vq - ve)[mask]))
    print(f"Γ0 = {g0}: похибки", np.round(errors, 3))
