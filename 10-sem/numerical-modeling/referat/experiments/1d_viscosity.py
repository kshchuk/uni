# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Експеримент 1: схемна (чисельна) в'язкість у 1D рівнянні Бюргерса.
Розв'язуємо рівняння Бюргерса  u_t + (u^2/2)_x = nu * u_xx  (nu -- мала фізична
в'язкість, що регуляризує фронт) двома схемами та порівнюємо передачу крутого фронту:
  - Upwind (1-й порядок): велика штучна в'язкість -> сильно "розмазує" фронт.
  - MacCormack (2-й порядок, предиктор-коректор): мала схемна в'язкість ->
    фронт лишається різким (ціна -- незначний дисперсійний "виліт" біля розриву).
Модифіковане рівняння (за Роучем): u_t + a u_x = (nu + nu_num) u_xx,
nu_num = a*dx/2*(1-C), C = a*dt/dx -- число Куранта. Саме nu_num у схемі 1-го
порядку домінує і додатково згладжує розв'язок.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

L_DOM = 2.0 * np.pi
N_X = 200
T_FINAL = 3.0
CFL = 0.4
NU_PHYS = 0.002   # мала фізична в'язкість (регуляризація фронту)
FPS = 20
OUTPUT_DIR = Path(__file__).resolve().parent / "figures"


def get_writer(fps: int):
    # Перевірка наявності ffmpeg для запису .mp4 (інакше fallback на .gif)
    if shutil.which("ffmpeg"):
        try:
            return animation.FFMpegWriter(fps=fps, bitrate=1800), ".mp4"
        except (RuntimeError, FileNotFoundError):
            pass
    print("УВАГА: ffmpeg не знайдено. Зберігаємо .gif через PillowWriter.")
    return animation.PillowWriter(fps=fps), ".gif"


def initial_profile(x: np.ndarray) -> np.ndarray:
    # Гладкий початковий профіль; нелінійність робить фронт усе крутішим з часом
    return 0.5 + 0.5 * np.sin(x)


def burgers_flux(u: np.ndarray) -> np.ndarray:
    # Консервативний потік F(u) = u^2 / 2
    return 0.5 * u * u


def diffusion(u: np.ndarray, dx: float, nu: float) -> np.ndarray:
    # Фізична дифузія nu*u_xx (центральні різниці, періодичні ГУ)
    return nu * (np.roll(u, -1) - 2.0 * u + np.roll(u, 1)) / (dx * dx)


def step_upwind(u, dx, dt, nu):
    # Явна схема проти потоку 1-го порядку (для a=u>0 -- різниця назад).
    # Додає схемну в'язкість nu_num = a*dx/2*(1-C), що розмазує фронт.
    flux = burgers_flux(u)
    dflux = (flux - np.roll(flux, 1)) / dx
    return u - dt * dflux + dt * diffusion(u, dx, nu)


def step_maccormack(u, dx, dt, nu):
    # Схема MacCormack 2-го порядку: предиктор (різниці вперед) + коректор (назад).
    flux = burgers_flux(u)
    u_pred = u - (dt / dx) * (np.roll(flux, -1) - flux) + dt * diffusion(u, dx, nu)
    flux_pred = burgers_flux(u_pred)
    u_new = (
        0.5 * (u + u_pred)
        - 0.5 * (dt / dx) * (flux_pred - np.roll(flux_pred, 1))
        + 0.5 * dt * diffusion(u_pred, dx, nu)
    )
    return u_new


def stable_dt(u, dx, cfl, nu):
    # Крок за часом з урахуванням конвективного (CFL) та дифузійного обмежень
    umax = max(float(np.max(np.abs(u))), 1e-6)
    dt_conv = cfl * dx / umax
    dt_diff = 0.4 * dx * dx / nu if nu > 0 else dt_conv
    return min(dt_conv, dt_diff)


def solve_burgers(scheme, n_x, t_final, cfl, nu, store_every):
    x = np.linspace(0.0, L_DOM, n_x, endpoint=False)
    dx = x[1] - x[0]
    u = initial_profile(x)
    step_fn = step_upwind if scheme == "upwind" else step_maccormack
    t, times, history, step = 0.0, [0.0], [u.copy()], 0
    while t < t_final - 1e-12:
        dt = stable_dt(u, dx, cfl, nu)
        if t + dt > t_final:
            dt = t_final - t
        u = step_fn(u, dx, dt, nu)
        t += dt
        step += 1
        if step % store_every == 0:
            times.append(t)
            history.append(u.copy())
    if times[-1] < t_final - 1e-10:
        times.append(t)
        history.append(u.copy())
    return x, np.array(times), np.stack(history, axis=0)


def run_animation(x, times_up, hist_up, times_mc, hist_mc, output_path, fps):
    n_frames = min(len(times_up), len(times_mc))
    y_min = min(hist_up.min(), hist_mc.min()) - 0.1
    y_max = max(hist_up.max(), hist_mc.max()) + 0.1
    fig, ax = plt.subplots(figsize=(9, 5))
    line_up, = ax.plot(x, hist_up[0], "r-", lw=2, label="Upwind (1st order)")
    line_mc, = ax.plot(x, hist_mc[0], "b-", lw=2, label="MacCormack (2nd order)")
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("x")
    ax.set_ylabel("u")
    ax.set_title("Burgers equation: scheme (numerical) viscosity")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, va="top")

    def update(frame):
        line_up.set_ydata(hist_up[frame])
        line_mc.set_ydata(hist_mc[frame])
        time_text.set_text(f"t = {times_up[frame]:.3f}")
        return line_up, line_mc, time_text

    anim = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000 // fps, blit=True)
    writer, ext = get_writer(fps)
    out = output_path.with_suffix(ext)
    out.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out), writer=writer, dpi=100)
    plt.close(fig)
    print(f"Збережено: {out}")


def main():
    parser = argparse.ArgumentParser(description="1D Burgers: upwind vs MacCormack (scheme viscosity)")
    parser.add_argument("--nx", type=int, default=N_X)
    parser.add_argument("--t-final", type=float, default=T_FINAL)
    parser.add_argument("--cfl", type=float, default=CFL)
    parser.add_argument("--nu", type=float, default=NU_PHYS, help="фізична в'язкість")
    parser.add_argument("--fps", type=int, default=FPS)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "1d_burgers_schemes.mp4")
    args = parser.parse_args()
    store_every = max(1, int(args.nx * args.t_final / (args.fps * 30)))
    print("Computing upwind (1st order)...")
    x, t_up, h_up = solve_burgers("upwind", args.nx, args.t_final, args.cfl, args.nu, store_every)
    print("Computing MacCormack (2nd order)...")
    _, t_mc, h_mc = solve_burgers("maccormack", args.nx, args.t_final, args.cfl, args.nu, store_every)
    run_animation(x, t_up, h_up, t_mc, h_mc, args.output, args.fps)


if __name__ == "__main__":
    main()
