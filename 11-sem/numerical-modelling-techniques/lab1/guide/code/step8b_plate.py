def plate_exact(X, Y, gamma, a=0.5):
    """Точна швидкість: пластина x = 0, |y| ≤ a, потік (1, 0), циркуляція gamma."""
    zp = -1j * (X + 1j * Y)                      # поворот: пластина лягає на [-a, a]
    root = np.sqrt(zp - a) * np.sqrt(zp + a)     # вітка √(z²-a²) ~ z на нескінченності
    alpha = -np.pi / 2                           # у повернутій системі потік іде вниз
    dw = np.cos(alpha) - 1j * np.sin(alpha) * zp / root + gamma / (2j * np.pi * root)
    vbar = -1j * dw                              # назад у вихідну систему: u - iv
    return vbar.real, -vbar.imag


def plate_exact_psi(X, Y, gamma, a=0.5):
    """Точна функція течії ψ = Im w, де w — комплексний потенціал пластини."""
    zp = -1j * (X + 1j * Y)
    root = np.sqrt(zp - a) * np.sqrt(zp + a)
    alpha = -np.pi / 2
    w = np.cos(alpha) * zp - 1j * np.sin(alpha) * root
    w = w + gamma / (2j * np.pi) * np.log(zp + root)
    return w.imag


def plate(m):
    """Відрізок з m точок, колокації посередині, нормалі (-1, 0)."""
    qx0, qy0 = np.zeros(m), np.linspace(-0.5, 0.5, m)
    qxc, qyc = qx0[:-1], (qy0[:-1] + qy0[1:]) / 2
    return qx0, qy0, qxc, qyc, -np.ones(m - 1), np.zeros(m - 1)


xp = np.linspace(-1, 1, 201)
Xp, Yp = np.meshgrid(xp, xp)
mask = np.hypot(Xp, np.maximum(np.abs(Yp) - 0.5, 0)) > 0.15     # далі 0.15 від пластини
Ms = [10, 20, 40, 80, 160]
errors = {}
for g0 in (0.0, 1.0):
    errors[g0] = []
    for m in Ms:
        qx0, qy0, *colloc = plate(m)
        Gq = solve_gammas(qx0, qy0, *colloc, vinf, g0)
        uq, vq = velocity_field(Xp, Yp, qx0, qy0, Gq, vinf, 0.01)
        with np.errstate(divide="ignore", invalid="ignore"):
            ue, ve = plate_exact(Xp, Yp, g0)
        errors[g0].append(np.max(np.hypot(uq - ue, vq - ve)[mask]))
    print(f"Γ0 = {g0}: похибки", np.round(errors[g0], 3))

# --- Рисунок 1: збіжність ---
fig, ax = plt.subplots(figsize=(6, 4))
for g0, err in errors.items():
    ax.loglog(Ms, err, "o-", label=f"Γ0 = {g0:g}")
ax.loglog(Ms, 1.3 / np.array(Ms), "k--", lw=1, label="~ 1/M")
ax.set_xlabel("M")
ax.set_ylabel("max |V_МДО - V_точн|")
ax.set_title("Пластина: похибка спадає як 1/M")
ax.grid(alpha=0.3, which="both")
ax.legend()
plt.show()

# --- Рисунок 2: МДО проти точного розв'язку при M = 40, Γ0 = 1 ---
m, g0 = 40, 1.0
qx0, qy0, *colloc = plate(m)
Gq = solve_gammas(qx0, qy0, *colloc, vinf, g0)
uq, vq = velocity_field(Xp, Yp, qx0, qy0, Gq, vinf, 0.01)
psi_m = psi_direct(Xp, Yp, qx0, qy0, Gq, vinf, 0.01)
with np.errstate(divide="ignore", invalid="ignore"):
    ue, ve = plate_exact(Xp, Yp, g0)
    psi_e = plate_exact_psi(Xp, Yp, g0)
psi_m -= psi_m[100, 0] - psi_e[100, 0]           # ψ — до сталої: вирівнюємо в (-1, 0)

fig, ax = plt.subplots(1, 3, figsize=(17, 5))
levels = np.linspace(-1.1, 1.1, 23)
ax[0].contour(Xp, Yp, psi_m, levels=levels, colors="tab:blue", linewidths=1.5)
ax[0].contour(Xp, Yp, psi_e, levels=levels, colors="tab:red", linewidths=0.8,
              linestyles="--")
ax[0].set_title("ψ: МДО (суцільні) і точний (пунктир)")

err = np.hypot(uq - ue, vq - ve)
im = ax[1].imshow(np.log10(err + 1e-12), extent=(-1, 1, -1, 1), origin="lower",
                  cmap="magma", vmin=-4, vmax=0)
fig.colorbar(im, ax=ax[1], label="log10 |ΔV|")
ax[1].set_title("Де похибка: біля пластини й кінців")

for a in ax[:2]:
    a.plot([0, 0], [-0.5, 0.5], "k-", lw=3)
    a.set_aspect("equal")

yy = np.linspace(-1, 1, 401)
xl = np.full_like(yy, 0.3)                       # вертикаль x = 0.3 за пластиною
with np.errstate(divide="ignore", invalid="ignore"):
    ue_l, ve_l = plate_exact(xl, yy, g0)
ax[2].plot(yy, np.hypot(ue_l, ve_l), "k-", lw=2.5, label="точний")
for m_l in (5, 10, 40):
    qx0, qy0, *colloc = plate(m_l)
    Gl = solve_gammas(qx0, qy0, *colloc, vinf, g0)
    ul, vl = velocity_field(xl, yy, qx0, qy0, Gl, vinf, 0.01)
    ax[2].plot(yy, np.hypot(ul, vl), "--", label=f"МДО, M = {m_l}")
ax[2].set_xlabel("y")
ax[2].set_ylabel("|V|")
ax[2].set_title("|V| уздовж x = 0.3: зі зростанням M → точний")
ax[2].grid(alpha=0.3)
ax[2].legend()
plt.show()


# --- Рисунок 3: 4 графіки лаби для пластини ---
def plot_four(X, Y, x0, y0, G, v_inf, delta, title, mask=None):
    """4 графіки лаби (як у кроці 7) для будь-якого контуру; mask ховає частину."""
    u, v = velocity_field(X, Y, x0, y0, G, v_inf, delta)
    phi, _ = transformed(X, Y, x0, y0, G, v_inf, delta)
    psi = psi_direct(X, Y, x0, y0, G, v_inf, delta)
    if mask is not None:
        u, v, phi, psi = (np.where(mask, np.nan, F) for F in (u, v, phi, psi))
    speed = np.hypot(u, v)
    ext = (X.min(), X.max(), Y.min(), Y.max())
    s = max(1, X.shape[0] // 25)                 # ≈ 25 стрілок уздовж кожної осі

    fig, ax = plt.subplots(2, 2, figsize=(11, 10))
    ax[0, 0].imshow(speed, extent=ext, origin="lower", cmap="Blues",
                    vmax=np.nanpercentile(speed, 99))
    ax[0, 0].quiver(X[::s, ::s], Y[::s, ::s], (u / speed)[::s, ::s],
                    (v / speed)[::s, ::s], scale=35, width=0.003)
    ax[0, 0].set_title("1) векторне поле V на тлі |V|")
    panels = [(ax[0, 1], speed, "2) |V| = const", "Blues"),
              (ax[1, 0], phi, "3) φ = const", "RdBu_r"),
              (ax[1, 1], psi, "4) ψ = const", "RdBu_r")]
    for a, F, name, cmap in panels:
        levels = np.linspace(*np.nanpercentile(F, [1, 99]), 30)
        cs = a.contourf(X, Y, F, levels=levels, cmap=cmap, extend="both")
        a.contour(X, Y, F, levels=levels, colors="k", linewidths=0.4)
        fig.colorbar(cs, ax=a)
        a.set_title(name)
    for a in ax.flat:
        a.plot(x0, y0, "k-", lw=2)
        a.set_aspect("equal")
    fig.suptitle(title)
    plt.show()


qx0, qy0, *colloc = plate(80)
Gq = solve_gammas(qx0, qy0, *colloc, vinf, 1.0)
Xs, Ys = np.meshgrid(np.linspace(-1, 1, 300), np.linspace(-1, 1, 300))
plot_four(Xs, Ys, qx0, qy0, Gq, vinf, 0.01, "Пластина: M = 80, Γ0 = 1")
