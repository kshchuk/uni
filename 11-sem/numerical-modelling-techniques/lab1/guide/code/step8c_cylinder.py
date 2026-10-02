gap = np.radians(4)                    # малий розрив: контур лишається розімкненим
tt = np.linspace(gap / 2, 2 * np.pi - gap / 2, 80)
cx0, cy0 = R * np.cos(tt), R * np.sin(tt)        # коло з центром у (0, 0)
ttc = 0.5 * (tt[:-1] + tt[1:])
cxc, cyc = R * np.cos(ttc), R * np.sin(ttc)
cnx, cny = -np.cos(ttc), -np.sin(ttc)

Xc, Yc = np.meshgrid(np.linspace(-1.2, 1.2, 201), np.linspace(-1.2, 1.2, 201))
outside = np.hypot(Xc, Yc) >= 0.7
z = Xc + 1j * Yc
for g0 in (0.0, 2.0):
    Gc = solve_gammas(cx0, cy0, cxc, cyc, cnx, cny, vinf, g0)
    uq, vq = velocity_field(Xc, Yc, cx0, cy0, Gc, vinf, 0.01)
    with np.errstate(divide="ignore", invalid="ignore"):
        vbar = 1 - R**2 / z**2 + g0 / (2j * np.pi * z)   # слайд 11: циліндр
    err = np.max(np.hypot(uq - vbar.real, vq + vbar.imag)[outside])
    print(f"Γ0 = {g0}: max похибка поза r = 0.7: {err:.1e}")
