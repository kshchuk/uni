fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, g0 in zip(axes, (-1.0, 0.0, 1.0)):
    Gg = solve_gammas(x0, y0, xc, yc, nx, ny, V_INF, g0)
    ug, vg = velocity_field(X, Y, x0, y0, Gg, V_INF, DELTA)
    ax.streamplot(xs, ys, ug, vg, density=1.3, color=np.hypot(ug, vg), cmap="viridis",
                  linewidth=0.8)
    ax.plot(x0, y0, "r-", lw=3)
    ax.set_aspect("equal")
    ax.set_title(f"Γ0 = {g0:g}")
fig.suptitle("Як циркуляція змінює обтікання (колір ліній — швидкість)")
plt.show()
