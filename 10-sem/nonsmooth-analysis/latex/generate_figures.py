#!/usr/bin/env python3
"""Generate illustrations for Негладка_оптимізація.tex."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

OUTPUT_DIR = Path(__file__).resolve().parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

for style in ("ggplot", "seaborn-v0_8-whitegrid", "default"):
    try:
        plt.style.use(style)
        break
    except OSError:
        continue

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
    }
)


def save_figure(fig, name: str) -> Path:
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_subgradient_3d() -> Path:
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    x = np.linspace(-2, 2, 50)
    y = np.linspace(-2, 2, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sqrt(X**2 + Y**2)

    ax.plot_surface(X, Y, Z, cmap="coolwarm", alpha=0.6, edgecolor="none")
    ax.scatter([0], [0], [0], color="red", s=100, label="Точка зламу (0,0)")

    Z_plane1 = 0.5 * X + 0.5 * Y
    Z_plane2 = -0.5 * X + 0.5 * Y
    ax.plot_surface(X, Y, Z_plane1, color="green", alpha=0.3)
    ax.plot_surface(X, Y, Z_plane2, color="orange", alpha=0.3)

    ax.set_title("Субдиференціал: опорні гіперплощини у точці зламу")
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_zlabel("$f(x,y)$")
    ax.set_zlim(-1, 3)
    ax.legend(loc="upper left")
    return save_figure(fig, "subgradient_3d.png")


def plot_eps_subgradient() -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.linspace(0, 2.5, 100)
    f_x = x**2
    eps = 0.5
    f_x_eps = f_x - eps

    ax.plot(x, f_x, "b-", linewidth=2, label="$f(x) = x^2$")
    ax.plot(x, f_x_eps, "b--", linewidth=1.5, label="$f(x) - \\epsilon$")

    x0, y0 = 1, 1
    ax.plot(x0, y0, "ro", markersize=8, label="Точка $x_0$")

    ax.plot(x, 2 * (x - x0) + y0, "g-", label="Точний субградієнт $v=2$")
    ax.plot(x, 1 * (x - x0) + y0, "m-", linewidth=2, label="$\\epsilon$-субградієнт $v=1$")

    ax.fill_between(x, f_x_eps, f_x, color="blue", alpha=0.1)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_ylim(-0.5, 5)
    ax.set_title("Геометричний зміст $\\epsilon$-субградієнта")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    return save_figure(fig, "eps_subgradient.png")


def plot_clarke_descent() -> Path:
    fig, ax = plt.subplots(figsize=(7, 7))

    polygon_points = np.array([[1, 1], [1, 3], [3, 2], [2, 1]])
    poly = Polygon(
        polygon_points,
        closed=True,
        color="skyblue",
        alpha=0.5,
        edgecolor="blue",
        linewidth=2,
    )
    ax.add_patch(poly)

    origin = np.array([0.0, 0.0])
    z_k = np.array([1.0, 1.0])
    g_k = -z_k / np.linalg.norm(z_k)

    ax.plot(origin[0], origin[1], "ko", markersize=8, label="Нуль (0,0)")
    ax.plot(z_k[0], z_k[1], "ro", markersize=8, label="Проекція $z_k$")

    ax.annotate("", xy=z_k, xytext=origin, arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.annotate("", xy=g_k, xytext=origin, arrowprops=dict(arrowstyle="->", color="green", lw=3))

    ax.text(1.5, 2.0, "$\\partial_C f(x_k)$", fontsize=14)
    ax.text(g_k[0] - 0.25, g_k[1] - 0.25, "$g_k$", fontsize=14, color="green")

    ax.set_xlim(-1.5, 4)
    ax.set_ylim(-1.5, 4)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_aspect("equal")
    ax.set_title("Напрямок найкрутішого спуску (проекція на $\\partial_C f$)")
    ax.legend()
    return save_figure(fig, "clarke_descent.png")


def main() -> None:
    paths = [
        plot_subgradient_3d(),
        plot_eps_subgradient(),
        plot_clarke_descent(),
    ]
    for path in paths:
        print(f"Збережено: {path}")


if __name__ == "__main__":
    main()
