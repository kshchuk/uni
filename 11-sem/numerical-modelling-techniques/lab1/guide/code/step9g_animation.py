from matplotlib.animation import FuncAnimation
from IPython.display import HTML

rng = np.random.default_rng(0)
P = np.column_stack([rng.uniform(-1, 1, 400), rng.uniform(-1, 1, 400)])   # частинки
dt = 0.01


def advect(P):
    """Крок методу середньої точки для dr/dt = V(r) [Л2, сл. 39–40]."""
    u1, v1 = velocity_field(P[:, 0], P[:, 1], x0, y0, G, V_INF, DELTA)
    Pm = P + 0.5 * dt * np.column_stack([u1, v1])
    u2, v2 = velocity_field(Pm[:, 0], Pm[:, 1], x0, y0, G, V_INF, DELTA)
    P = P + dt * np.column_stack([u2, v2])
    P[P[:, 0] > 1, 0] -= 2                      # вийшла праворуч — заходить зліва
    return P


fig, ax = plt.subplots(figsize=(5, 5))
ax.plot(x0, y0, "r-", lw=3)
dots, = ax.plot(P[:, 0], P[:, 1], ".", ms=3)
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect("equal")


def update(frame):
    global P
    P = advect(P)
    dots.set_data(P[:, 0], P[:, 1])
    return dots,


anim = FuncAnimation(fig, update, frames=150, interval=40, blit=True)
plt.close(fig)
HTML(anim.to_jshtml())
