# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Експеримент 2: течія в каверні з рухомою кришкою (lid-driven cavity).
2D нестисливі рівняння Нав'є-Стокса, метод дробових кроків (Chorin projection)
на рознесеній сітці MAC (Marker-and-Cell). Рівняння Пуассона для тиску
розв'язується прямим спектральним методом (дискретне косинус-перетворення, DCT),
що відповідає умовам Неймана й ефективно працює на GPU (MPS).
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

OUTPUT_DIR = Path(__file__).resolve().parent / "figures"


def get_device() -> torch.device:
    # Ініціалізація обчислювального пристрою: GPU Apple Silicon (MPS) або CPU
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(f"Device: {device} (Apple Silicon GPU)")
    else:
        device = torch.device("cpu")
        print("WARNING: MPS unavailable, using CPU")
    return device


def get_writer(fps: int):
    # Перевірка наявності ffmpeg для запису .mp4 (інакше fallback на .gif)
    if shutil.which("ffmpeg"):
        try:
            return animation.FFMpegWriter(fps=fps, bitrate=2500), ".mp4"
        except (RuntimeError, FileNotFoundError):
            pass
    print("УВАГА: ffmpeg не знайдено. Зберігаємо .gif через PillowWriter.")
    return animation.PillowWriter(fps=fps), ".gif"


class LidDrivenCavity:
    """
    Розв'язувач 2D НС методом проекції на рознесеній сітці MAC.
    Розкладка змінних (i -> x, j -> y):
      u : (n+1, n)  -- горизонтальна швидкість на вертикальних гранях
      v : (n, n+1)  -- вертикальна швидкість на горизонтальних гранях
      p : (n, n)    -- тиск у центрах комірок
    Кришка (верхня стінка, y=1) рухається зі швидкістю lid_speed.
    """

    def __init__(self, n, re, lid_speed, device):
        self.n = n
        self.re = re
        self.lid_speed = lid_speed
        self.device = device
        self.nu = lid_speed * 1.0 / re  # кінематична в'язкість (L=1, U=lid_speed)

        self.u = torch.zeros(n + 1, n, device=device)
        self.v = torch.zeros(n, n + 1, device=device)
        self.p = torch.zeros(n, n, device=device)

        self.h = 1.0 / n
        # Крок за часом з урахуванням конвективного (CFL) та в'язкого обмежень
        dt_conv = 0.25 * self.h / max(lid_speed, 1e-6)
        dt_visc = 0.25 * self.h * self.h / max(self.nu, 1e-12)
        self.dt = min(dt_conv, dt_visc)

        self._build_poisson_operator()

    def _build_poisson_operator(self):
        # Ортонормована матриця DCT-II та власні значення лапласіана (умови Неймана).
        # Це дозволяє розв'язати рівняння Пуассона тиску за одне перетворення.
        n, h = self.n, self.h
        k = torch.arange(n, device=self.device, dtype=torch.float32).reshape(n, 1)
        i = torch.arange(n, device=self.device, dtype=torch.float32).reshape(1, n)
        C = torch.cos(np.pi * (2 * i + 1) * k / (2 * n))
        scale = torch.full((n, 1), float(np.sqrt(2.0 / n)), device=self.device)
        scale[0, 0] = float(np.sqrt(1.0 / n))
        self.C = C * scale  # (n, n)
        self.Ct = self.C.t().contiguous()
        kk = torch.arange(n, device=self.device, dtype=torch.float32)
        lam = (2.0 * torch.cos(np.pi * kk / n) - 2.0) / (h * h)
        LAM = lam.reshape(n, 1) + lam.reshape(1, n)
        LAM[0, 0] = 1.0  # уникнення ділення на 0 для нульової моди
        self.inv_LAM = 1.0 / LAM
        self.inv_LAM[0, 0] = 0.0  # фіксуємо калібрування тиску (нульове середнє)

    # ------------------------------------------------------------------
    # Ghost-комірки для дотичних граничних умов (no-slip / рухома кришка)
    # ------------------------------------------------------------------
    def _u_ghost_y(self, u):
        # Доповнюємо u фіктивними рядами по y: низ (стінка, u=0) і верх (кришка, u=U)
        n = self.n
        ug = torch.empty(n + 1, n + 2, device=self.device, dtype=u.dtype)
        ug[:, 1:-1] = u
        ug[:, 0] = -u[:, 0]                           # нижня стінка: дотична швидкість 0
        ug[:, -1] = 2.0 * self.lid_speed - u[:, -1]   # верхня кришка: дотична швидкість U
        return ug

    def _v_ghost_x(self, v):
        # Доповнюємо v фіктивними стовпцями по x: ліва і права стінки (v=0)
        n = self.n
        vg = torch.empty(n + 2, n + 1, device=self.device, dtype=v.dtype)
        vg[1:-1, :] = v
        vg[0, :] = -v[0, :]    # ліва стінка: дотична швидкість 0
        vg[-1, :] = -v[-1, :]  # права стінка: дотична швидкість 0
        return vg

    # ------------------------------------------------------------------
    # Конвекція та дифузія (центральні різниці) для внутрішніх вузлів
    # ------------------------------------------------------------------
    def _rhs_u(self, u, v):
        n, h = self.n, self.h
        ug = self._u_ghost_y(u)
        un = u[1:n, :]
        dudx = (u[2:n + 1, :] - u[0:n - 1, :]) / (2 * h)
        dudy = (ug[1:n, 2:] - ug[1:n, 0:-2]) / (2 * h)
        # v інтерполюємо у вузли u (середнє з 4 сусідів)
        v_avg = 0.25 * (
            v[0:n - 1, 0:n] + v[1:n, 0:n] + v[0:n - 1, 1:n + 1] + v[1:n, 1:n + 1]
        )
        conv = un * dudx + v_avg * dudy
        # В'язкий член nu*Laplacian(u)
        lap = (
            (u[2:n + 1, :] - 2 * u[1:n, :] + u[0:n - 1, :]) / (h * h)
            + (ug[1:n, 2:] - 2 * ug[1:n, 1:-1] + ug[1:n, 0:-2]) / (h * h)
        )
        rhs = torch.zeros_like(u)
        rhs[1:n, :] = -conv + self.nu * lap
        return rhs

    def _rhs_v(self, u, v):
        n, h = self.n, self.h
        vg = self._v_ghost_x(v)
        vn = v[:, 1:n]
        dvdy = (v[:, 2:n + 1] - v[:, 0:n - 1]) / (2 * h)
        dvdx = (vg[2:, 1:n] - vg[0:-2, 1:n]) / (2 * h)
        # u інтерполюємо у вузли v
        u_avg = 0.25 * (
            u[0:n, 0:n - 1] + u[1:n + 1, 0:n - 1] + u[0:n, 1:n] + u[1:n + 1, 1:n]
        )
        conv = u_avg * dvdx + vn * dvdy
        lap = (
            (vg[2:, 1:n] - 2 * vg[1:-1, 1:n] + vg[0:-2, 1:n]) / (h * h)
            + (v[:, 2:n + 1] - 2 * v[:, 1:n] + v[:, 0:n - 1]) / (h * h)
        )
        rhs = torch.zeros_like(v)
        rhs[:, 1:n] = -conv + self.nu * lap
        return rhs

    # ------------------------------------------------------------------
    def divergence(self, u, v):
        # div у центрах комірок: (du/dx + dv/dy)
        return (u[1:, :] - u[:-1, :]) / self.h + (v[:, 1:] - v[:, :-1]) / self.h

    def solve_pressure(self, rhs):
        # Крок проекції тиску: lap(p) = rhs (умови Неймана) через прямий DCT-розв'язок.
        rhs_hat = self.C @ rhs @ self.Ct
        p_hat = rhs_hat * self.inv_LAM
        return self.Ct @ p_hat @ self.C

    # ------------------------------------------------------------------
    # Один крок інтегрування за схемою проекції Chorin
    # ------------------------------------------------------------------
    def step(self):
        n, h, dt = self.n, self.h, self.dt
        # Крок 1: проміжна швидкість u* (конвекція + в'язкість, явно)
        u_star = self.u + dt * self._rhs_u(self.u, self.v)
        v_star = self.v + dt * self._rhs_v(self.u, self.v)
        # Нормальні швидкості на стінках = 0
        u_star[0, :] = 0.0
        u_star[n, :] = 0.0
        v_star[:, 0] = 0.0
        v_star[:, n] = 0.0

        # Крок 2: рівняння Пуассона для тиску lap(p) = div(u*)/dt
        rhs = self.divergence(u_star, v_star) / dt
        self.p = self.solve_pressure(rhs)

        # Крок 3: корекція швидкості -> бездивергентне поле
        self.u = u_star.clone()
        self.v = v_star.clone()
        self.u[1:n, :] = u_star[1:n, :] - dt * (self.p[1:n, :] - self.p[0:n - 1, :]) / h
        self.v[:, 1:n] = v_star[:, 1:n] - dt * (self.p[:, 1:n] - self.p[:, 0:n - 1]) / h

    # ------------------------------------------------------------------
    def vorticity(self):
        # Завихреність omega = dv/dx - du/dy у внутрішніх вузлах сітки
        h, n = self.h, self.n
        dv_dx = (self.v[1:n, 1:n] - self.v[0:n - 1, 1:n]) / h
        du_dy = (self.u[1:n, 1:n] - self.u[1:n, 0:n - 1]) / h
        return dv_dx - du_dy

    def max_divergence(self):
        return float(self.divergence(self.u, self.v).abs().max().item())

    def run(self, n_steps, store_every):
        hist, times = [], []
        for step in range(n_steps + 1):
            if step % store_every == 0:
                hist.append(self.vorticity().detach().cpu().numpy())
                times.append(step * self.dt)
            if step < n_steps:
                self.step()
        return np.array(times), hist


def run_animation(history, times, re, output_path, fps):
    # Симетричні межі кольорів за робастним перцентилем (хвости вихорів не "вибілюють" картинку)
    vmax = float(np.percentile(np.abs(history[-1]), 99.0))
    vmax = max(vmax, 1e-6)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(history[0].T, origin="lower", extent=[0, 1, 0, 1],
                   cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="equal")
    plt.colorbar(im, ax=ax, label="omega (vorticity)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    title = ax.set_title(f"Lid-driven cavity Re={re:.0f}, t=0")

    def update(f):
        im.set_array(history[f].T)
        title.set_text(f"Lid-driven cavity Re={re:.0f}, t={times[f]:.2f}")
        return [im, title]

    anim = animation.FuncAnimation(fig, update, frames=len(history),
                                   interval=1000 // fps, blit=True)
    writer, ext = get_writer(fps)
    out = output_path.with_suffix(ext)
    out.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out), writer=writer, dpi=120)
    plt.close(fig)
    print(f"Збережено: {out}")


def main():
    p = argparse.ArgumentParser(description="2D lid-driven cavity (MAC projection, PyTorch MPS)")
    p.add_argument("--n", type=int, default=128, help="вузлів на сторону")
    p.add_argument("--re", type=float, default=1000.0, help="число Рейнольдса")
    p.add_argument("--t-final", type=float, default=30.0, help="час інтегрування (до стаціонару)")
    p.add_argument("--fps", type=int, default=20)
    p.add_argument("--output", type=Path, default=OUTPUT_DIR / "2d_cavity_vorticity.mp4")
    args = p.parse_args()

    device = get_device()
    solver = LidDrivenCavity(args.n, args.re, 1.0, device)
    n_steps = int(args.t_final / solver.dt)
    store_every = max(1, n_steps // (args.fps * 20))
    print(f"Re={args.re}, grid {args.n}x{args.n}, dt={solver.dt:.2e}, steps={n_steps}")
    times, hist = solver.run(n_steps, store_every)
    print(f"Фінальна max|div(u)| = {solver.max_divergence():.2e}")
    run_animation(hist, times, args.re, args.output, args.fps)


if __name__ == "__main__":
    main()
