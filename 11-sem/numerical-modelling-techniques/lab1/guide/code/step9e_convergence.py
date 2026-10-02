probes = np.array([[-0.5, 0.0], [0.6, 0.3], [0.0, -0.7]])   # точки спостереження
Ms = [10, 20, 40, 80, 160, 320]
values = []
for m in Ms:
    tm = np.linspace(np.pi / 2, 3 * np.pi / 2, m)
    xm0, ym0 = XC + R * np.cos(tm), R * np.sin(tm)
    tmc = 0.5 * (tm[:-1] + tm[1:])
    Gm = solve_gammas(xm0, ym0, XC + R * np.cos(tmc), R * np.sin(tmc),
                      -np.cos(tmc), -np.sin(tmc), V_INF, GAMMA0)
    delta_m = R * np.pi / (m - 1) / 2            # δ = h/2 для цього M
    up, vp = velocity_field(probes[:, 0], probes[:, 1], xm0, ym0, Gm, V_INF, delta_m)
    values.append(np.hypot(up, vp))
values = np.array(values)

fig, ax = plt.subplots(figsize=(7, 4))
for i, (px, py) in enumerate(probes):
    ax.semilogx(Ms, values[:, i], "o-", label=f"точка ({px}, {py})")
ax.set_xlabel("M")
ax.set_ylabel("|V| у точці")
ax.set_title("Збіжність за M: значення виходять на сталу")
ax.grid(alpha=0.3, which="both")
ax.legend()
plt.show()
print(np.round(values, 4))
