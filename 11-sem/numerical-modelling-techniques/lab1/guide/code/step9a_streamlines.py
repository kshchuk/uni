fig, ax = plt.subplots(figsize=(7, 6))
ax.imshow(speed, extent=(-1, 1, -1, 1), origin="lower", cmap="Blues",
          vmax=np.percentile(speed, 99))
ax.streamplot(xs, ys, u, v, density=1.6, color="k", linewidth=0.7, arrowsize=0.8)
ax.plot(x0, y0, "r-", lw=3)
ax.set_aspect("equal")
ax.set_title(f"Лінії течії (траєкторії частинок), Γ0 = {GAMMA0:g}")
plt.show()
