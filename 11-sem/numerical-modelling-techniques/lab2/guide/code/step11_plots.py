fig, ax = plt.subplots(2, 2, figsize=(13, 8.5))
ext = (X.min(), X.max(), Y.min(), Y.max())
s = 8                                           # стрілка в кожній 8-й точці сітки
ax[0, 0].imshow(speed, extent=ext, origin="lower", cmap="Blues", vmax=2.5)
ax[0, 0].quiver(X[::s, ::s], Y[::s, ::s], (u / speed)[::s, ::s], (v / speed)[::s, ::s],
                scale=45, width=0.002)
ax[0, 0].set_title("1) векторне поле V на тлі |V|")

panels = [(ax[0, 1], speed, "2) |V| = const", "Blues", (0, 2.5)),
          (ax[1, 0], phi, "3) φ = const", "RdBu_r", np.percentile(phi, [2, 98])),
          (ax[1, 1], Cp, "4) Cp = const", "RdBu_r", (-3, 1))]
for a, F, title, cmap, (lo, hi) in panels:
    levels = np.linspace(lo, hi, 26)
    cs = a.contourf(X, Y, F, levels=levels, cmap=cmap, extend="both")
    fig.colorbar(cs, ax=a)
    a.set_title(title)

for a in ax.flat:
    a.plot(x0, y0, "k-", lw=2)
    a.plot(fx, fy, ".", color="0.3", ms=1)
    a.set_xlim(X.min(), X.max())
    a.set_ylim(Y.min(), Y.max())
    a.set_aspect("equal")
fig.suptitle(f"t = {time_now:.1f}, M = {M}")
plt.show()
