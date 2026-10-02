phi_d = phi_direct(X, Y, x0, y0, G, V_INF)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, F, title in [(axes[0], phi_d, "пряма формула (7.1.13'): віяло розрізів"),
                     (axes[1], phi, "перетворена (7.1.22'): один розріз")]:
    levels = np.linspace(*np.percentile(F, [1, 99]), 30)
    ax.contourf(X, Y, F, levels=levels, cmap="RdBu_r", extend="both")
    ax.contour(X, Y, F, levels=levels, colors="k", linewidths=0.4)
    ax.plot(x0, y0, "k-", lw=2)
    ax.set_aspect("equal")
    ax.set_title(title)
plt.show()
