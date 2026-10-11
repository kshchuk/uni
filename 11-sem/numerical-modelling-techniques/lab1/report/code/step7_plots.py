fig, ax = plt.subplots(2, 2, figsize=(11, 10))

s = 16                                           # стрілка в кожній 16-й точці сітки
ax[0, 0].imshow(speed, extent=(-1, 1, -1, 1), origin="lower", cmap="Blues",
                vmax=np.percentile(speed, 99))
ax[0, 0].quiver(X[::s, ::s], Y[::s, ::s], (u / speed)[::s, ::s], (v / speed)[::s, ::s],
                scale=35, width=0.003)
ax[0, 0].set_title("1) векторне поле V на тлі |V|")

panels = [(ax[0, 1], speed, "2) |V| = const", "Blues"),
          (ax[1, 0], phi, "3) φ = const", "RdBu_r"),
          (ax[1, 1], psi, "4) ψ = const", "RdBu_r")]
for a, F, title, cmap in panels:
    levels = np.linspace(*np.percentile(F, [1, 99]), 30)
    cs = a.contourf(X, Y, F, levels=levels, cmap=cmap, extend="both")
    a.contour(X, Y, F, levels=levels, colors="k", linewidths=0.4)
    fig.colorbar(cs, ax=a)
    a.set_title(title)

for a in ax.flat:
    a.plot(x0, y0, "k-", lw=2)
    a.set_aspect("equal")
fig.suptitle(f"M = {M}, Γ0 = {GAMMA0:g}, α = {ALPHA:g}")
fig.savefig(f"lab1_G{GAMMA0:+g}.png", dpi=150)
plt.show()
