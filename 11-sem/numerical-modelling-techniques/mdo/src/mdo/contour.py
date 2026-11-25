"""Контур перешкоди L_d: точки дискретних особливостей, колокації, нормалі, точки відриву.

Посилання: [П] — навчальний посібник ТЧМ, §7.1.2, §7.2.2 (дискретизація), §7.2.4 (непроникнення
для рухомих точок), с. 133 (δ = L/(2M)).
"""
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Contour:
    """Розімкнений контур з M дискретними вихорами і M − 1 колокаціями.

    x0, y0      — точки дискретних особливостей ω0j (обхід — від першої до останньої;
                  область течії ліворуч від напрямку обходу);
    xc, yc      — точки колокації, nx, ny — одиничні нормалі в них;
    separation  — індекси точок відриву (кінці й кутові точки) для лаб. №2;
    delta       — параметр регуляризації δ;
    L           — довжина контуру;
    kind, arc   — «arc» для дуги кола (тоді arc = (cx, cy, R, t0, t1)) або «polyline».
    """
    x0: np.ndarray
    y0: np.ndarray
    xc: np.ndarray
    yc: np.ndarray
    nx: np.ndarray
    ny: np.ndarray
    L: float
    delta: float
    separation: np.ndarray
    kind: str = "polyline"
    arc: tuple = field(default=None, repr=False)

    # ------------------------------------------------------------------ властивості
    @property
    def M(self):
        return len(self.x0)

    @property
    def ell(self):
        """Довжини хорд між сусідніми вихорами."""
        return np.hypot(np.diff(self.x0), np.diff(self.y0))

    @property
    def h(self):
        """Середній крок між вихорами вздовж контуру."""
        return self.L / (self.M - 1)

    @property
    def size(self):
        """Розмір перешкоди — найбільша відстань між її точками."""
        d = np.hypot(self.x0[:, None] - self.x0[None, :], self.y0[:, None] - self.y0[None, :])
        return d.max()

    # ------------------------------------------------------------------ конструктори
    @classmethod
    def arc_of_circle(cls, center, R, t0, t1, M, delta=None):
        """Дуга кола ω(t) = c + R e^{it}, t від t0 до t1 (t0 < t1 — проти год. стрілки).

        Колокації — на самій дузі посередині між вихорами, нормалі — точні, до центру кола
        (як у лаб. №1 і №2 для півкола). δ за замовчуванням L/(2M) [П, с. 133].
        """
        cx, cy = center
        t = np.linspace(t0, t1, M)
        tc = 0.5 * (t[:-1] + t[1:])
        L = R * abs(t1 - t0)
        return cls(x0=cx + R * np.cos(t), y0=cy + R * np.sin(t),
                   xc=cx + R * np.cos(tc), yc=cy + R * np.sin(tc),
                   nx=-np.cos(tc), ny=-np.sin(tc), L=L,
                   delta=L / (2 * M) if delta is None else delta,
                   separation=np.array([0, M - 1]), kind="arc", arc=(cx, cy, R, t0, t1))

    @classmethod
    def semicircle(cls, M, R=0.5, delta=None):
        """Варіант «С»: півколо розміру 2R = 1, відкрите праворуч, центроване в нулі."""
        return cls.arc_of_circle((R / 2, 0.0), R, np.pi / 2, 3 * np.pi / 2, M, delta)

    @classmethod
    def from_points(cls, x0, y0, separation=None, delta=None):
        """Контур з готових точок; колокації — середини хорд, нормалі до хорд [П, §7.1.2].

        separation — індекси точок відриву (за замовчуванням — кінці); δ за замовчуванням
        min(L/(2M), 0.95·ℓ_min/2), щоб колокації не потрапляли в коло регуляризації.
        """
        x0 = np.asarray(x0, float)
        y0 = np.asarray(y0, float)
        dx, dy = np.diff(x0), np.diff(y0)
        ell = np.hypot(dx, dy)
        if np.any(ell == 0):
            raise ValueError("у контурі є точки, що збігаються")
        M = len(x0)
        L = ell.sum()
        if delta is None:
            delta = min(L / (2 * M), 0.95 * ell.min() / 2)
        sep = np.array([0, M - 1]) if separation is None else np.asarray(separation, int)
        return cls(x0=x0, y0=y0, xc=(x0[:-1] + x0[1:]) / 2, yc=(y0[:-1] + y0[1:]) / 2,
                   nx=-dy / ell, ny=dx / ell, L=L, delta=delta, separation=sep)

    @classmethod
    def polyline(cls, vertices, M, separation="corners", delta=None):
        """Ламана через вершини, M вузлів: кожна вершина — вузол, кроки ≈ рівні.

        separation="corners" — відрив з кінців і всіх внутрішніх вершин (кутових точок);
        "ends" — лише з кінців; або явний список індексів вузлів.
        """
        V = np.asarray(vertices, float)
        seg = np.hypot(*np.diff(V, axis=0).T)
        n = np.maximum(1, np.round((M - 1) * seg / seg.sum()).astype(int))
        n[np.argmax(n)] += (M - 1) - n.sum()             # точно M − 1 відрізків
        pts, nodes = [V[:1]], [0]
        for k in range(len(seg)):
            s = np.linspace(0, 1, n[k] + 1)[1:, None]
            pts.append(V[k] + s * (V[k + 1] - V[k]))
            nodes.append(nodes[-1] + n[k])
        P = np.vstack(pts)
        if isinstance(separation, str):
            sep = nodes if separation == "corners" else [0, len(P) - 1]
        else:
            sep = separation
        return cls.from_points(P[:, 0], P[:, 1], separation=sep, delta=delta)

    @classmethod
    def segment(cls, a, b, M, delta=None):
        """Відрізок (пластина) від a до b з M вихорами."""
        return cls.polyline([a, b], M, separation="ends", delta=delta)

    def normalized(self):
        """Копія контуру розміру 1 з центром описаного прямокутника в нулі."""
        s = self.size
        c = np.array([(self.x0.max() + self.x0.min()) / 2, (self.y0.max() + self.y0.min()) / 2])
        new = Contour(x0=(self.x0 - c[0]) / s, y0=(self.y0 - c[1]) / s,
                      xc=(self.xc - c[0]) / s, yc=(self.yc - c[1]) / s, nx=self.nx, ny=self.ny,
                      L=self.L / s, delta=self.delta / s, separation=self.separation,
                      kind=self.kind)
        if self.kind == "arc":
            cx, cy, R, t0, t1 = self.arc
            new.arc = ((cx - c[0]) / s, (cy - c[1]) / s, R / s, t0, t1)
        return new

    # ------------------------------------------------------------------ непроникнення
    def keep_out(self, x_old, y_old, x_new, y_new):
        """Непроникнення для рухомих вихорів [П, §7.2.4].

        Вихор, що за крок перетнув контур або підійшов до нього ближче за δ, повертається на свій
        бік на відстань не меншу за δ (дзеркальне відбиття, варіант D на рис. 7.2.16).
        """
        if self.kind == "arc":
            return self._keep_out_arc(x_old, y_old, x_new, y_new)
        return self._keep_out_polyline(x_old, y_old, x_new, y_new)

    def _keep_out_arc(self, x_old, y_old, x_new, y_new):
        """Для дуги: бік — за відстанню до центру, відбиття вздовж радіуса."""
        cx, cy, R, t0, t1 = self.arc
        r_old = np.hypot(x_old - cx, y_old - cy)
        r_new = np.hypot(x_new - cx, y_new - cy)
        side = np.where(r_old >= R, 1.0, -1.0)
        gap = r_new - R
        ang = np.arctan2(y_new - cy, x_new - cx)
        on_arc = np.mod(ang - t0, 2 * np.pi) <= (t1 - t0)       # навпроти дуги
        bad = on_arc & ((np.sign(gap) != side) | (np.abs(gap) < self.delta))
        r_fix = R + side * np.maximum(np.abs(gap), self.delta)
        k = np.where(bad, r_fix / np.maximum(r_new, 1e-12), 1.0)
        return cx + (x_new - cx) * k, cy + (y_new - cy) * k

    def _keep_out_polyline(self, x_old, y_old, x_new, y_new):
        """Для ламаної: бік — за знаком векторного добутку з кожним відрізком."""
        ell = self.ell
        SA = np.column_stack([self.x0[:-1], self.y0[:-1]])
        SD = np.column_stack([np.diff(self.x0), np.diff(self.y0)]) / ell[:, None]
        SN = np.column_stack([self.nx, self.ny])
        po = np.column_stack([x_old, y_old])[:, None, :] - SA[None]
        pn = np.column_stack([x_new, y_new])[:, None, :] - SA[None]
        d_old = np.einsum("nsk,sk->ns", po, SN)                 # відстань зі знаком
        d_new = np.einsum("nsk,sk->ns", pn, SN)
        u_old = np.einsum("nsk,sk->ns", po, SD) / ell
        u_new = np.einsum("nsk,sk->ns", pn, SD) / ell
        inside = (u_new > 0) & (u_new < 1)
        denom = np.where(d_old != d_new, d_old - d_new, 1.0)
        u_cross = u_old + (u_new - u_old) * d_old / denom
        crossed = (np.sign(d_old) * np.sign(d_new) < 0) & (u_cross > 0) & (u_cross < 1)
        bad = crossed | (inside & (np.abs(d_new) < self.delta))
        hit = bad.any(axis=1)
        x_new, y_new = np.array(x_new, float), np.array(y_new, float)
        if not hit.any():
            return x_new, y_new
        dist = np.where(bad, np.abs(d_new), np.inf)
        k = np.nonzero(hit)[0]
        s = np.argmin(dist, axis=1)[hit]
        side = np.sign(d_old[k, s])
        side[side == 0] = np.sign(d_new[k, s][side == 0])
        side[side == 0] = 1.0
        shift = side * np.maximum(np.abs(d_new[k, s]), self.delta) - d_new[k, s]
        x_new[k] += shift * SN[s, 0]
        y_new[k] += shift * SN[s, 1]
        return x_new, y_new
