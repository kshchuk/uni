"""Лаб. №2: нестаціонарна відривна течія — вільні вихори сліду [П, §7.2, §5.2, §6.5.1]."""
import time

import numpy as np

from . import fields
from .contour import Contour
from .kernels import induced
from .steady import influence_matrix


class Simulation:
    """Метод дискретних вихорів з відривом з точок `contour.separation`.

    Один крок (етапи I–IV [П, §6.5.1]): вихори в точках відриву стають вільними,
    γ^p_{n+1} = Γ_p(t_n) (гіпотеза Кутта–Жуковського [П, §5.2]); швидкості всіх вільних вихорів;
    τ_n = δ / max|V| (7.2.27); рух усіх, включно з новими (i = 1..n+1, формула (39) слайда 10);
    непроникнення [П, §7.2.4]; СЛАР (7.2.19)–(7.2.20) з умовою Кельвіна ΣΓ + Σγ = 0.

    x_max  — вихори далі цієї відстані вздовж потоку видаляються (циркуляція лишається в обліку);
    absorb — (центр, радіус): вихори всередині кола поглинаються контуром (для порожнин, як у «5»).
    """

    def __init__(self, contour: Contour, v_inf=(1.0, 0.0), x_max=8.0, absorb=None):
        self.contour = contour
        self.v_inf = np.asarray(v_inf, float)
        self.x_max = x_max
        self.absorb = absorb
        self.A_inv = np.linalg.inv(influence_matrix(contour))   # матриця не змінюється в часі
        self.fx = self.fy = self.fg = np.empty(0)
        self.shed_total = 0.0                                   # Σγ усіх відірваних (з видаленими)
        self.t = 0.0
        self.G = self.solve_gammas(self.fx, self.fy, self.fg, 0.0)
        self.history = []                                       # (t, Cx, Cy, N)
        self.frames = []                                        # (t, G, fx, fy, fg)
        self.n_steps = 0

    # ------------------------------------------------------------------ фізика
    def velocity(self, x, y, G=None, fx=None, fy=None, fg=None):
        """Швидкість (7.2.22): потік + приєднані вихори + вільні вихори (регуляризовано)."""
        c, d = self.contour, self.contour.delta
        G = self.G if G is None else G
        fx, fy, fg = (self.fx, self.fy, self.fg) if fx is None else (fx, fy, fg)
        ub, vb = induced(x, y, c.x0, c.y0, G, d)
        uf, vf = induced(x, y, fx, fy, fg, d)
        return self.v_inf[0] + ub + uf, self.v_inf[1] + vb + vf

    def solve_gammas(self, fx, fy, fg, shed_total):
        """Γ1..ΓM з (7.2.19)–(7.2.20): права частина — потік і слід, останній рядок — Кельвін."""
        c = self.contour
        uf, vf = induced(c.xc, c.yc, fx, fy, fg, c.delta)
        b = np.empty(c.M)
        b[:-1] = -(c.nx * (self.v_inf[0] + uf) + c.ny * (self.v_inf[1] + vf))
        b[-1] = -shed_total
        return self.A_inv @ b

    def impulse(self, G, fx, fy, fg):
        """Гідродинамічний імпульс (ділений на ρ): Σ Γ (y, −x) по всіх вихорах."""
        c = self.contour
        return np.array([G @ c.y0 + fg @ fy, -(G @ c.x0) - fg @ fx])

    def time_step(self, G, fx, fy, fg, shed_total):
        """Один крок t_n → t_{n+1}; повертає новий стан і τ_n. Стан об'єкта не змінює."""
        c = self.contour
        sep = c.separation
        px = np.append(fx, c.x0[sep])
        py = np.append(fy, c.y0[sep])
        pg = np.append(fg, G[sep])
        u, v = self.velocity(px, py, G, fx, fy, fg)
        dt = c.delta / np.max(np.hypot(u, v))
        px, py = c.keep_out(px, py, px + u * dt, py + v * dt)
        shed_total += G[sep].sum()
        G = self.solve_gammas(px, py, pg, shed_total)
        return G, px, py, pg, shed_total, dt

    # ------------------------------------------------------------------ цикл
    def step(self):
        """Зробити один крок, записати сили, видалити далекі / поглинути вихори."""
        P_old = self.impulse(self.G, self.fx, self.fy, self.fg)
        G, fx, fy, fg, shed, dt = self.time_step(self.G, self.fx, self.fy, self.fg,
                                                 self.shed_total)
        self.t += dt
        self.n_steps += 1
        P = self.impulse(G, fx, fy, fg)
        Cx, Cy = -2 * (P - P_old) / dt               # F = −ρ dP/dt, C = F / (ρ V∞² D / 2)
        self.history.append((self.t, Cx, Cy, len(fg)))
        far = fx * self.v_inf[0] + fy * self.v_inf[1] > self.x_max
        fx, fy, fg = fx[~far], fy[~far], fg[~far]
        if self.absorb is not None:
            (ax, ay), ar = self.absorb
            cav = np.hypot(fx - ax, fy - ay) < ar
            shed -= fg[cav].sum()                    # циркуляція переходить на контур
            fx, fy, fg = fx[~cav], fy[~cav], fg[~cav]
        self.G, self.fx, self.fy, self.fg, self.shed_total = G, fx, fy, fg, shed
        return dt

    def run(self, t_end, frame_dt=0.5, progress=True, every=500):
        """Крокувати до t_end; кадри кожні frame_dt; статус із часом кожні `every` кроків."""
        t0 = time.time()
        if not self.frames:
            self._frame()
        while self.t < t_end:
            dt = self.step()
            if self.t >= len(self.frames) * frame_dt:
                self._frame()
            if progress and self.n_steps % every == 0:
                print(f"[{time.time() - t0:6.0f} с] крок {self.n_steps}: t = {self.t:6.2f} / "
                      f"{t_end:g}, вихорів {len(self.fg)}, dt = {dt:.4f}", flush=True)
        if progress:
            print(f"готово за {time.time() - t0:.0f} с: {self.n_steps} кроків, t = {self.t:.2f}, "
                  f"вихорів у сліді {len(self.fg)}")
        return self

    def _frame(self):
        self.frames.append((self.t, self.G.copy(), self.fx.copy(), self.fy.copy(), self.fg.copy()))

    def frame_at(self, t):
        """Збережений кадр, найближчий до моменту t."""
        return min(self.frames, key=lambda f: abs(f[0] - t))

    # ------------------------------------------------------------------ поля й аналіз
    def kelvin_residual(self):
        """|ΣΓ + Σγ(у сліді) + Σγ(видалених/поглинених)| — має бути ~1e-15."""
        return abs(self.G.sum() + self.shed_total)

    def phi(self, X, Y):
        """Потенціал (7.2.38) — пряма формула, з розрізами від вихорів."""
        c = self.contour
        return fields.phi_direct(X, Y, np.r_[c.x0, self.fx], np.r_[c.y0, self.fy],
                                 np.r_[self.G, self.fg], self.v_inf)

    def psi(self, X, Y):
        """Функція течії (6.4.43) — однозначна, без розрізів."""
        c = self.contour
        return fields.psi(X, Y, np.r_[c.x0, self.fx], np.r_[c.y0, self.fy],
                          np.r_[self.G, self.fg], self.v_inf, c.delta)

    def forces(self):
        """Масиви t, Cx, Cy, N з історії."""
        h = np.array(self.history)
        return h[:, 0], h[:, 1], h[:, 2], h[:, 3]

    def summary(self, t_from=None, smooth=15):
        """Середній Cx і число Струхаля (пік спектра згладженого Cy) за t > t_from."""
        t, Cx, Cy, _ = self.forces()
        t_from = t[-1] / 2 if t_from is None else t_from
        k = np.ones(smooth) / smooth
        sx, sy = np.convolve(Cx, k, mode="same"), np.convolve(Cy, k, mode="same")
        late = t > t_from
        tu = np.linspace(t[late][0], t[late][-1], 4096)
        cy = np.interp(tu, t[late], sy[late])
        spec = np.abs(np.fft.rfft(cy - cy.mean()))
        freq = np.fft.rfftfreq(len(tu), d=tu[1] - tu[0])
        ok = (freq > 0.02) & (freq < 1.0)
        return {"Cx_mean": float(sx[late].mean()), "St": float(freq[ok][np.argmax(spec[ok])])}
