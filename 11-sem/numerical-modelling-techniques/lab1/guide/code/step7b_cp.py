Cp = 1 - speed**2 / np.sum(V_INF**2)             # коефіцієнт тиску [Л2, сл. 11]

fig, ax = plt.subplots(figsize=(6, 5))
levels = np.linspace(np.percentile(Cp, 1), 1, 30)
cs = ax.contourf(X, Y, Cp, levels=levels, cmap="RdBu_r", extend="min")
ax.plot(x0, y0, "k-", lw=2)
ax.set_aspect("equal")
fig.colorbar(cs, ax=ax)
ax.set_title("Cp = 1 - |V|² / V∞²")
plt.show()
