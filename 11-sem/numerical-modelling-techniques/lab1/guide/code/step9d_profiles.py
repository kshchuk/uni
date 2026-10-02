yy = np.linspace(-1, 1, 401)
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, xline in zip(axes, (-0.5, 0.6)):
    for g0 in (-1.0, 0.0, 1.0):
        Gg = solve_gammas(x0, y0, xc, yc, nx, ny, V_INF, g0)
        ul, vl = velocity_field(np.full_like(yy, xline), yy, x0, y0, Gg, V_INF, DELTA)
        ax.plot(yy, np.hypot(ul, vl), label=f"Γ0 = {g0:g}")
    ax.axhline(1, color="gray", ls=":", label="|V∞| = 1")
    ax.set_title(f"|V| уздовж вертикалі x = {xline}")
    ax.set_xlabel("y")
    ax.grid(alpha=0.3)
axes[0].set_ylabel("|V|")
axes[0].legend()
plt.show()
