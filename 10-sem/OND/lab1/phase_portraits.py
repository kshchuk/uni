import numpy as np
import matplotlib.pyplot as plt


def normalize_vectors(u, v):
    mag = np.hypot(u, v)
    mag[mag == 0] = 1.0
    return u / mag, v / mag


def plot_system(
    f,
    xlim,
    ylim,
    density,
    seeds,
    title,
    output_name,
    stream_color="royalblue",
    separatrices=None,
    separatrix_labels=None,
):
    x = np.linspace(xlim[0], xlim[1], 29)
    y = np.linspace(ylim[0], ylim[1], 29)
    X, Y = np.meshgrid(x, y)
    U, V = f(X, Y)
    Un, Vn = normalize_vectors(U, V)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    ax.quiver(X, Y, Un, Vn, color="black", alpha=0.9, pivot="mid", scale=26)

    ax.streamplot(
        X,
        Y,
        U,
        V,
        color=stream_color,
        density=density,
        linewidth=2.2,
        arrowsize=1.2,
        start_points=np.array(seeds, dtype=float),
    )

    ax.axhline(0, color="black", linewidth=1.1)
    ax.axvline(0, color="black", linewidth=1.1)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.25)

    if separatrices:
        # Draw separatrices as invariant straight lines through the origin.
        # Each separatrix is given by a direction vector (vx, vy).
        x_line = np.linspace(xlim[0], xlim[1], 300)
        for i, (vx, vy) in enumerate(separatrices):
            if abs(vx) < 1e-12:
                ax.plot(
                    [0, 0],
                    [ylim[0], ylim[1]],
                    "--",
                    color="darkgreen",
                    linewidth=2.0,
                    label="Сепаратриси" if i == 0 else None,
                )
            else:
                k = vy / vx
                y_line = k * x_line
                mask = (y_line >= ylim[0]) & (y_line <= ylim[1])
                ax.plot(
                    x_line[mask],
                    y_line[mask],
                    "--",
                    color="darkgreen",
                    linewidth=2.0,
                    label="Сепаратриси" if i == 0 else None,
                )
        ax.legend(loc="upper right")
        if separatrix_labels:
            for text, x0, y0 in separatrix_labels:
                ax.text(
                    x0,
                    y0,
                    text,
                    color="darkgreen",
                    fontsize=11,
                    fontweight="bold",
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5),
                )

    fig.tight_layout()
    fig.savefig(output_name)
    plt.close(fig)


def system3(x, y):
    return -2 * x - 5 * y, 2 * x + 2 * y


def system6(x, y):
    return x, 2 * x - y


if __name__ == "__main__":
    seeds3 = [
        [2, 0],
        [4, 0],
        [-3, 1.5],
        [1.5, -2],
        [-2.5, -1],
        [0.8, 2.4],
    ]
    plot_system(
        system3,
        xlim=(-5, 5),
        ylim=(-5, 5),
        density=1.05,
        seeds=seeds3,
        title="Фазовий портрет: Завдання 3 (Центр)",
        output_name="portrait3_python.png",
        stream_color="blue",
        separatrices=None,
        separatrix_labels=None,
    )

    seeds6 = [
        [1, 0],
        [-1, 0],
        [0.5, 1],
        [-0.5, -1],
        [0, 2.5],
        [0, -2.5],
    ]
    plot_system(
        system6,
        xlim=(-3, 3),
        ylim=(-3, 3),
        density=1.0,
        seeds=seeds6,
        title="Фазовий портрет: Завдання 6 (Сідло)",
        output_name="portrait6_python.png",
        stream_color="red",
        separatrices=[(1, 1), (0, 1)],
        separatrix_labels=[("y=x", 1.55, 1.45), ("x=0", 0.08, 2.25)],
    )

    print("Saved: portrait3_python.png, portrait6_python.png")
