px0 = np.zeros(5)                                # відрізок від (0, -0.5) до (0, 0.5)
py0 = np.linspace(-0.5, 0.5, 5)
ddx, ddy = np.diff(px0), np.diff(py0)
ell = np.hypot(ddx, ddy)
pxc, pyc = (px0[:-1] + px0[1:]) / 2, (py0[:-1] + py0[1:]) / 2   # колокації (7.1.2)
pnx, pny = -ddy / ell, ddx / ell
vinf = np.array([1.0, 0.0])

for g0 in (0.0, 1.0):
    Gp = solve_gammas(px0, py0, pxc, pyc, pnx, pny, vinf, g0)
    xp, yp = np.array([-0.5]), np.array([0.3])
    up, vp = velocity_field(xp, yp, px0, py0, Gp, vinf, 0.01)
    php, psp = transformed(xp, yp, px0, py0, Gp, vinf, 0.01)
    print(f"Γ0 = {g0}: Γ = {np.round(Gp, 6)}")
    print(f"   (u, v) = ({up[0]:.4f}, {vp[0]:.4f}), φ = {php[0]:.4f}, ψ = {psp[0]:.4f}")
