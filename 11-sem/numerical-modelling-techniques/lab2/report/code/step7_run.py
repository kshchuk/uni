fx, fy, fg = np.empty(0), np.empty(0), np.empty(0)   # слід: координати та γ
shed_total = 0.0
time_now = 0.0
history = []                                    # рядки (t, Cx, Cy, кількість вихорів)
frames = []                                     # кадри для рисунків і анімації
FRAME_DT = 0.5
P_old = impulse(G, fx, fy, fg)

while time_now < T_END:
    G, fx, fy, fg, shed_total, dt = time_step(G, fx, fy, fg, shed_total)
    time_now += dt
    P = impulse(G, fx, fy, fg)
    Cx, Cy = -2 * (P - P_old) / dt              # F = -ρ dP/dt, C = F / (ρ V∞² D / 2)
    history.append((time_now, Cx, Cy, len(fg)))
    far = fx > X_MAX                            # видаляємо вихори, що відлетіли
    P -= impulse(np.zeros(M), fx[far], fy[far], fg[far])
    fx, fy, fg = fx[~far], fy[~far], fg[~far]
    P_old = P
    if time_now >= len(frames) * FRAME_DT:
        frames.append((time_now, G.copy(), fx.copy(), fy.copy(), fg.copy()))
    if len(history) % 500 == 0:
        print(f"крок {len(history)}: t = {time_now:.1f}, вихорів {len(fg)}")

history = np.array(history)
print(f"готово: {len(history)} кроків, t = {time_now:.2f}, вихорів у сліді {len(fg)}")
