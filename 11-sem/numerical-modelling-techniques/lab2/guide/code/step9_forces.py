tt, Cx, Cy = history[:, 0], history[:, 1], history[:, 2]
k = 15                                          # згладжування ковзним середнім
smooth = lambda a: np.convolve(a, np.ones(k) / k, mode="same")

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(tt, smooth(Cx), color="tab:red", label="Cx (опір)")
ax.plot(tt, smooth(Cy), color="tab:blue", label="Cy (бокова сила)")
ax.set_xlabel("t")
ax.set_ylim(-4, 5)
ax.grid(alpha=0.3)
ax.legend()
plt.show()

late = tt > T_END / 2                           # усталений періодичний режим
spec = np.abs(np.fft.rfft(Cy[late] - Cy[late].mean()))
freq = np.fft.rfftfreq(late.sum(), d=np.mean(np.diff(tt[late])))
f_main = freq[np.argmax(spec[1:]) + 1]
print(f"середній Cx = {Cx[late].mean():.2f}, Струхаль St = f·D/V∞ = {f_main:.3f}")
