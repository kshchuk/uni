def circle(m, gap):
    """Коло радіуса R з розривом gap (рад) праворуч: точки, колокації, нормалі."""
    tt = np.linspace(gap / 2, 2 * np.pi - gap / 2, m)
    ttc = 0.5 * (tt[:-1] + tt[1:])
    return (R * np.cos(tt), R * np.sin(tt),
            R * np.cos(ttc), R * np.sin(ttc), -np.cos(ttc), -np.sin(ttc))


def cylinder_exact(X, Y, gamma):
    """Точний розв'язок для циліндра (слайд 11): u, v і функція течії ψ."""
    z = X + 1j * Y
    vbar = 1 - R**2 / z**2 + gamma / (2j * np.pi * z)
    psi = (z + R**2 / z).imag - gamma / (2 * np.pi) * np.log(np.abs(z))
    return vbar.real, -vbar.imag, psi


gap = np.radians(4)                    # малий розрив: контур лишається розімкненим
cx0, cy0, *ccol = circle(80, gap)
xg = np.linspace(-1.2, 1.2, 201)
Xc, Yc = np.meshgrid(xg, xg)
outside = np.hypot(Xc, Yc) >= 0.7
with np.errstate(divide="ignore", invalid="ignore"):
    for g0 in (0.0, 2.0):
        Gc = solve_gammas(cx0, cy0, *ccol, vinf, g0)
        uq, vq = velocity_field(Xc, Yc, cx0, cy0, Gc, vinf, 0.01)
        ue, ve, _ = cylinder_exact(Xc, Yc, g0)
        err = np.max(np.hypot(uq - ue, vq - ve)[outside])
        print(f"Γ0 = {g0}: max похибка поза r = 0.7: {err:.1e}")

# --- Рисунок 1: лінії течії МДО поверх точних ---
inside = np.hypot(Xc, Yc) < R
fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))
for a, g0 in zip(ax, (0.0, 2.0)):
    Gc = solve_gammas(cx0, cy0, *ccol, vinf, g0)
    psi_m = psi_direct(Xc, Yc, cx0, cy0, Gc, vinf, 0.01)
    with np.errstate(divide="ignore", invalid="ignore"):
        _, _, psi_e = cylinder_exact(Xc, Yc, g0)
    psi_m -= psi_m[100, 0] - psi_e[100, 0]       # вирівнюємо сталу в точці (-1.2, 0)
    levels = np.linspace(-1.1, 1.1, 23)
    a.contour(Xc, Yc, np.where(inside, np.nan, psi_m), levels=levels, colors="tab:blue",
              linewidths=1.5)
    a.contour(Xc, Yc, np.where(inside, np.nan, psi_e), levels=levels, colors="tab:red",
              linewidths=0.8, linestyles="--")
    a.plot(cx0, cy0, "k-", lw=2)
    a.set_aspect("equal")
    a.set_title(f"Γ0 = {g0:g}: МДО (суцільні) і точний (пунктир)")
plt.show()

# --- Рисунок 2: карта похибки, швидкість навколо кола, вплив розриву ---
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
g0 = 2.0
Gc = solve_gammas(cx0, cy0, *ccol, vinf, g0)
uq, vq = velocity_field(Xc, Yc, cx0, cy0, Gc, vinf, 0.01)
with np.errstate(divide="ignore", invalid="ignore"):
    ue, ve, _ = cylinder_exact(Xc, Yc, g0)
err = np.where(inside, np.nan, np.hypot(uq - ue, vq - ve))
im = ax[0].imshow(np.log10(err + 1e-12), extent=(-1.2, 1.2, -1.2, 1.2), origin="lower",
                  cmap="magma", vmin=-7, vmax=-1)
fig.colorbar(im, ax=ax[0], label="log10 |ΔV|")
ax[0].plot(cx0, cy0, "w-", lw=1.5)
ax[0].set_aspect("equal")
ax[0].set_title("log-похибка, Γ0 = 2")

theta_c = np.linspace(0, 2 * np.pi, 361)
rr = 1.1 * R                                     # коло трохи більше за циліндр
xr, yr = rr * np.cos(theta_c), rr * np.sin(theta_c)
for g0, color in ((0.0, "tab:blue"), (2.0, "tab:red")):
    Gc = solve_gammas(cx0, cy0, *ccol, vinf, g0)
    ur, vr = velocity_field(xr, yr, cx0, cy0, Gc, vinf, 0.01)
    ue, ve, _ = cylinder_exact(xr, yr, g0)
    ax[1].plot(np.degrees(theta_c), np.hypot(ue, ve), "-", color=color, lw=2.5,
               label=f"точний, Γ0 = {g0:g}")
    ax[1].plot(np.degrees(theta_c), np.hypot(ur, vr), "k:", lw=1.2)
ax[1].plot([], [], "k:", label="МДО")
ax[1].set_xlabel("кут θ, градуси (0 — праворуч, 180 — ліворуч)")
ax[1].set_ylabel(f"|V| на колі r = {rr:.2f}")
ax[1].set_title("Мінімуми |V| — точки зупинки")
ax[1].grid(alpha=0.3)
ax[1].legend()

gaps = [30, 20, 10, 4, 2]
for g0, color in ((0.0, "tab:blue"), (2.0, "tab:red")):
    errs = []
    for gdeg in gaps:
        gx0, gy0, *gcol = circle(80, np.radians(gdeg))
        Gg = solve_gammas(gx0, gy0, *gcol, vinf, g0)
        ug, vg = velocity_field(Xc, Yc, gx0, gy0, Gg, vinf, 0.01)
        with np.errstate(divide="ignore", invalid="ignore"):
            ue, ve, _ = cylinder_exact(Xc, Yc, g0)
        errs.append(np.max(np.hypot(ug - ue, vg - ve)[outside]))
    ax[2].semilogy(gaps, errs, "o-", color=color, label=f"Γ0 = {g0:g}")
ax[2].invert_xaxis()
ax[2].set_xlabel("розрив у колі, градуси")
ax[2].set_ylabel("max |ΔV| поза r = 0.7")
ax[2].set_title("Похибка падає, доки розрив > кроку (≈4.5°)")
ax[2].grid(alpha=0.3, which="both")
ax[2].legend()
plt.show()

# --- Рисунок 3: 4 графіки лаби для кола (функція plot_four — з тесту на пластині) ---
Xs, Ys = np.meshgrid(np.linspace(-1.2, 1.2, 300), np.linspace(-1.2, 1.2, 300))
Gc = solve_gammas(cx0, cy0, *ccol, vinf, 2.0)
plot_four(Xs, Ys, cx0, cy0, Gc, vinf, 0.01, "Коло з розривом 4°: M = 80, Γ0 = 2",
          mask=np.hypot(Xs, Ys) < R)             # всередині кола не показуємо
