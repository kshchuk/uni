N = 400                                          # «екран» N x N пікселів
xs = np.linspace(-1, 1, N)
ys = np.linspace(-1, 1, N)
X, Y = np.meshgrid(xs, ys)                       # X[i, j] = xs[j], Y[i, j] = ys[i]
