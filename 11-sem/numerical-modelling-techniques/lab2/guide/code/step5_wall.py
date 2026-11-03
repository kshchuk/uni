def keep_out(x_old, y_old, x_new, y_new):
    """Непроникнення для рухомих вихорів (§7.2.4): не пускаємо їх крізь дугу.

    Вихор, що перетнув дугу або підійшов до неї ближче за DELTA, повертаємо
    на свій бік контуру на відстань не меншу за DELTA (відбиття по радіусу).
    """
    r_old = np.hypot(x_old - XC, y_old)
    r_new = np.hypot(x_new - XC, y_new)
    side = np.where(r_old >= R, 1.0, -1.0)      # +1 — зовні кола, -1 — у «чаші»
    gap = r_new - R                             # відстань до кола зі знаком
    on_arc = x_new - XC <= 0                    # дуга займає ліву половину кола
    bad = on_arc & ((np.sign(gap) != side) | (np.abs(gap) < DELTA))
    r_fix = R + side * np.maximum(np.abs(gap), DELTA)
    k = np.where(bad, r_fix / np.maximum(r_new, 1e-12), 1.0)
    return XC + (x_new - XC) * k, y_new * k
