"""PINN for Burgers — TensorFlow + PhiFlow (physicalloss-code tutorial structure)."""
from __future__ import annotations

import os
import time
from typing import Tuple

import numpy as np
import tensorflow as tf

tf.compat.v1.disable_eager_execution()
tf.compat.v1.disable_v2_behavior()

# PhiFlow TF backend (tutorial: from phi.tf.flow import *)
from phi.tf.flow import *  # noqa: F403

from burgers_fdm import (
    BETA,
    GAMMA,
    L_DOM,
    T_FINAL,
    build_grid,
    u_exact,
)

N_SAMPLE_POINTS_BND = 100
N_SAMPLE_POINTS_INNER = 1000
PH_FACTOR = 1.0
ITERS_DEFAULT = 10000
LR = 0.02


def _dense_layer(y, units, activation, name, reuse):
    """tf.compat.v1.layers.dense replacement (Keras 3 removed v1 layers)."""
    with tf.compat.v1.variable_scope(name, reuse=reuse):
        in_dim = int(y.shape[-1])
        w = tf.compat.v1.get_variable("kernel", shape=[in_dim, units], dtype=tf.float32)
        b = tf.compat.v1.get_variable("bias", shape=[units], dtype=tf.float32)
        y = tf.matmul(y, w) + b
        if activation is not None:
            y = activation(y)
    return y


def network(x, t):
    """Dense NN as in PBDL physicalloss-code: 8×20 tanh + linear out."""
    y = math.stack([x, t], axis=-1)
    for i in range(8):
        y = _dense_layer(y, 20, tf.nn.tanh, "layer%d" % i, reuse=tf.compat.v1.AUTO_REUSE)
    return _dense_layer(y, 1, None, "layer_out", reuse=tf.compat.v1.AUTO_REUSE)


def f_residual(u, x, t, beta=BETA, gamma=GAMMA):
    """Physics loss R = u_t + beta*u*u_x - gamma*u_xx (lr2 coefficients)."""
    u_t = gradients(u, t)
    u_x = gradients(u, x)
    u_xx = gradients(u_x, x)
    return u_t + beta * u * u_x - gamma * u_xx


def sample_ic(N: int, l: float = L_DOM) -> Tuple:
    """Initial condition u(x,0)=f(x)."""
    x_np = np.random.uniform(0.0, l, N).astype(np.float32)
    t_np = np.zeros(N, dtype=np.float32)
    u_np = u_exact(x_np, 0.0).astype(np.float32)
    return tf.convert_to_tensor(x_np), tf.convert_to_tensor(t_np), tf.convert_to_tensor(u_np)


def sample_bc(N: int, l: float = L_DOM, T: float = T_FINAL) -> Tuple:
    """Dirichlet on x=0 and x=l from u*."""
    N2 = N // 2
    t_np = np.random.uniform(0.0, T, N).astype(np.float32)
    x_np = np.zeros(N, dtype=np.float32)
    x_np[:N2] = 0.0
    x_np[N2:] = l
    u_np = np.empty(N, dtype=np.float32)
    for j in range(N2):
        u_np[j] = u_exact(np.array([0.0]), float(t_np[j]))[0]
    for j in range(N2, N):
        u_np[j] = u_exact(np.array([l]), float(t_np[j]))[0]
    return tf.convert_to_tensor(x_np), tf.convert_to_tensor(t_np), tf.convert_to_tensor(u_np)


def build_loss_graph(l: float = L_DOM, T: float = T_FINAL):
    """loss_u + ph_factor * loss_ph as in tutorial."""
    math.choose_backend(1)
    x_ic, t_ic, u_ic = sample_ic(N_SAMPLE_POINTS_BND // 2)
    x_bc, t_bc, u_bc = sample_bc(N_SAMPLE_POINTS_BND)
    x_b = math.concat([x_ic, x_bc], axis=0)
    t_b = math.concat([t_ic, t_bc], axis=0)
    u_b = math.concat([u_ic, u_bc], axis=0)

    loss_u = math.l2_loss(network(x_b, t_b)[:, 0] - u_b)

    x_ph_np = np.random.uniform(0.0, l, N_SAMPLE_POINTS_INNER).astype(np.float32)
    t_ph_np = np.random.uniform(0.0, T, N_SAMPLE_POINTS_INNER).astype(np.float32)
    x_ph = tf.convert_to_tensor(x_ph_np)
    t_ph = tf.convert_to_tensor(t_ph_np)
    loss_ph = math.l2_loss(f_residual(network(x_ph, t_ph)[:, 0], x_ph, t_ph))

    loss = loss_u + PH_FACTOR * loss_ph
    optim = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=LR).minimize(loss)
    return loss, optim, loss_u, loss_ph


def build_inference_grid(nx: int = 101, nt: int = 151, l: float = L_DOM, T: float = T_FINAL):
    grids_xt = np.meshgrid(np.linspace(0.0, l, nx), np.linspace(0.0, T, nt), indexing="ij")
    grid_x, grid_t = [tf.convert_to_tensor(t.astype(np.float32)) for t in grids_xt]
    grid_u = math.expand_dims(network(grid_x, grid_t))
    return grid_x, grid_t, grid_u


def train_pinn(iters: int = ITERS_DEFAULT, log_every: int = 1000) -> Tuple[float, list]:
    """Train PINN; returns elapsed seconds and loss history."""
    tf.compat.v1.reset_default_graph()
    loss, optim, _, _ = build_loss_graph()
    hist = []
    session = Session(None)
    session.initialize_variables()
    t0 = time.perf_counter()
    try:
        for step in range(iters + 1):
            _, lv = session.run([optim, loss])
            if step < 3 or step % log_every == 0:
                hist.append((step, float(lv)))
            if step % 500 == 0 and step > 0:
                print(f"  PINN step {step}, loss={lv:.6f}")
        _, _, grid_u = build_inference_grid()
        u_grid = session.run(grid_u)
    finally:
        pass
    elapsed = time.perf_counter() - t0
    return elapsed, hist, u_grid


def run_pinn_quick(iters: int = 2000) -> np.ndarray:
    """Short train for figure script."""
    elapsed, hist, u_grid = train_pinn(iters=iters, log_every=500)
    print(f"PINN done: {iters} iters, {elapsed:.1f}s, final loss={hist[-1][1]:.6f}")
    return np.asarray(u_grid)[0, :, :, 0]
