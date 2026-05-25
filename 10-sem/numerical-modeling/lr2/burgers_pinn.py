"""PINN for Burgers — TensorFlow + PhiFlow (forward + inverse gamma estimation).

Forward mode: fixed diffusion coefficient gamma=1; network learns u(x,t) from
IC/BC + physics residual on collocation points.

Inverse mode (killer feature): gamma is a trainable scalar (gamma_est) initialized
away from the true value; sparse interior observations from u*(x,t) plus physics
drive joint recovery of the field and the parameter.
"""
from __future__ import annotations

import time
from typing import List, Tuple

import numpy as np
import tensorflow as tf

# PhiFlow expects TF1 graph mode (matches PBDL tutorial stack).
tf.compat.v1.disable_eager_execution()
tf.compat.v1.disable_v2_behavior()

from phi.tf.flow import *  # noqa: F403 — Session, math, gradients

from burgers_fdm import (
    BETA,
    GAMMA,
    L_DOM,
    T_FINAL,
    build_grid,
    u_exact,
)

# --- Hyperparameters (aligned with physicalloss-code tutorial where noted) ---

N_SAMPLE_POINTS_BND = 100   # IC + Dirichlet BC collocation samples per step
N_SAMPLE_POINTS_INNER = 1000  # physics residual collocation points
N_SAMPLE_POINTS_OBS = 250   # sparse interior measurements (inverse PINN only)

PH_FACTOR = 1.0             # weight of physics loss in forward mode
ITERS_DEFAULT = 10000
ITERS_INVERSE_DEFAULT = 10000

GAMMA_INIT_DEFAULT = 0.5    # deliberate wrong start for inverse identification
PH_FACTOR_INVERSE = 10.0    # stronger physics weight for gamma identification
LR = 0.02                   # network learning rate (tutorial default)
GAMMA_LR = 0.08             # learning rate for trainable gamma_est


def _dense_layer(y, units, activation, name, reuse):
    """Manual dense layer — tf.compat.v1.layers.dense was removed in Keras 3."""
    with tf.compat.v1.variable_scope(name, reuse=reuse):
        in_dim = int(y.shape[-1])
        w = tf.compat.v1.get_variable("kernel", shape=[in_dim, units], dtype=tf.float32)
        b = tf.compat.v1.get_variable("bias", shape=[units], dtype=tf.float32)
        y = tf.matmul(y, w) + b
        if activation is not None:
            y = activation(y)
    return y


def network(x, t):
    """MLP u_theta(x,t): 8 hidden layers x 20 tanh units + linear output.

    Architecture mirrors physicsbaseddeeplearning.org/physicalloss-code.html.
    Inputs are stacked as [x, t]; output is scalar u.
    """
    y = math.stack([x, t], axis=-1)
    for i in range(8):
        y = _dense_layer(y, 20, tf.nn.tanh, "layer%d" % i, reuse=tf.compat.v1.AUTO_REUSE)
    return _dense_layer(y, 1, None, "layer_out", reuse=tf.compat.v1.AUTO_REUSE)


def _as_gamma_tensor(gamma):
    """Allow f_residual to accept either a Python float or a trainable Variable."""
    if isinstance(gamma, (tf.Tensor, tf.Variable)):
        return gamma
    return tf.constant(float(gamma), dtype=tf.float32)


def f_residual(u, x, t, beta=BETA, gamma=GAMMA):
    """Strong-form Burgers residual R = u_t + beta*u*u_x - gamma*u_xx.

    PhiFlow ``gradients`` builds the computational graph for automatic
    differentiation w.r.t. collocation coordinates x and t.
    In inverse mode, ``gamma`` is the trainable ``gamma_est`` variable.
    """
    gamma = _as_gamma_tensor(gamma)
    u_t = gradients(u, t)
    u_x = gradients(u, x)
    u_xx = gradients(u_x, x)
    return u_t + beta * u * u_x - gamma * u_xx


def sample_ic(N: int, l: float = L_DOM) -> Tuple:
    """Random x in (0,l) at t=0 with labels u = f(x) from the assignment profile."""
    x_np = np.random.uniform(0.0, l, N).astype(np.float32)
    t_np = np.zeros(N, dtype=np.float32)
    u_np = u_exact(x_np, 0.0).astype(np.float32)
    return tf.convert_to_tensor(x_np), tf.convert_to_tensor(t_np), tf.convert_to_tensor(u_np)


def sample_bc(N: int, l: float = L_DOM, T: float = T_FINAL) -> Tuple:
    """Dirichlet BC on x=0 and x=l: half the batch on each boundary, u = u*(x,t)."""
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


def sample_observations(N: int, l: float = L_DOM, T: float = T_FINAL) -> Tuple:
    """Sparse synthetic measurements u*(x,t) in the domain interior.

    Used only in inverse PINN to mimic experimental data at random (x,t) points.
    """
    x_np = np.random.uniform(0.0, l, N).astype(np.float32)
    t_np = np.random.uniform(0.0, T, N).astype(np.float32)
    u_np = u_exact(x_np, t_np).astype(np.float32)
    return tf.convert_to_tensor(x_np), tf.convert_to_tensor(t_np), tf.convert_to_tensor(u_np)


def _collocation_points(l: float, T: float, n: int):
    """Uniform random physics collocation points in the space-time rectangle."""
    x_ph_np = np.random.uniform(0.0, l, n).astype(np.float32)
    t_ph_np = np.random.uniform(0.0, T, n).astype(np.float32)
    return tf.convert_to_tensor(x_ph_np), tf.convert_to_tensor(t_ph_np)


def build_forward_loss_graph(l: float = L_DOM, T: float = T_FINAL):
    """Build TF graph for forward PINN: fixed gamma=1.

    Total loss = MSE on IC/BC data + PH_FACTOR * MSE(physics residual).
    Fresh random collocation samples are drawn each training step (Monte Carlo).
    """
    math.choose_backend(1)
    gamma = tf.constant(GAMMA, dtype=tf.float32)

    # Boundary/data term: initial profile + time-dependent Dirichlet values.
    x_ic, t_ic, u_ic = sample_ic(N_SAMPLE_POINTS_BND // 2)
    x_bc, t_bc, u_bc = sample_bc(N_SAMPLE_POINTS_BND)
    x_b = math.concat([x_ic, x_bc], axis=0)
    t_b = math.concat([t_ic, t_bc], axis=0)
    u_b = math.concat([u_ic, u_bc], axis=0)

    loss_u = math.l2_loss(network(x_b, t_b)[:, 0] - u_b)

    # Physics term: penalize violation of Burgers PDE at interior collocation pts.
    x_ph, t_ph = _collocation_points(l, T, N_SAMPLE_POINTS_INNER)
    loss_ph = math.l2_loss(f_residual(network(x_ph, t_ph)[:, 0], x_ph, t_ph, gamma=gamma))

    loss = loss_u + PH_FACTOR * loss_ph
    optim = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=LR).minimize(loss)
    return loss, optim, loss_u, loss_ph, None


def build_inverse_loss_graph(
    l: float = L_DOM,
    T: float = T_FINAL,
    gamma_init: float = GAMMA_INIT_DEFAULT,
    ph_factor: float = PH_FACTOR_INVERSE,
):
    """Build TF graph for inverse PINN: joint estimation of u and gamma.

    Extra data term ``loss_obs`` ties the network to sparse interior measurements.
    ``gamma_est`` enters the physics residual; two optimizers update network weights
    and gamma on separate learning rates to reduce gradient-scale mismatch.
    """
    math.choose_backend(1)
    with tf.compat.v1.variable_scope("inverse_pinn"):
        # Scalar trainable diffusion coefficient — the quantity we want to recover.
        gamma_est = tf.compat.v1.get_variable(
            "gamma_est",
            shape=(),
            initializer=tf.constant_initializer(float(gamma_init)),
            trainable=True,
            dtype=tf.float32,
        )

        x_ic, t_ic, u_ic = sample_ic(N_SAMPLE_POINTS_BND // 2)
        x_bc, t_bc, u_bc = sample_bc(N_SAMPLE_POINTS_BND)
        x_obs, t_obs, u_obs = sample_observations(N_SAMPLE_POINTS_OBS)

        loss_ic = math.l2_loss(network(x_ic, t_ic)[:, 0] - u_ic)
        loss_bc = math.l2_loss(network(x_bc, t_bc)[:, 0] - u_bc)
        loss_obs = math.l2_loss(network(x_obs, t_obs)[:, 0] - u_obs)
        loss_u = loss_ic + loss_bc + loss_obs

        x_ph, t_ph = _collocation_points(l, T, N_SAMPLE_POINTS_INNER)
        loss_ph = math.l2_loss(
            f_residual(network(x_ph, t_ph)[:, 0], x_ph, t_ph, gamma=gamma_est)
        )

        loss = loss_u + ph_factor * loss_ph

        # Split optimization: network weights vs. scalar gamma_est.
        net_vars = [
            v for v in tf.compat.v1.trainable_variables() if "gamma_est" not in v.name
        ]
        optim_net = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=LR).minimize(
            loss, var_list=net_vars
        )
        optim_gamma = tf.compat.v1.train.GradientDescentOptimizer(
            learning_rate=GAMMA_LR
        ).minimize(loss, var_list=[gamma_est])
        optim = tf.group(optim_net, optim_gamma)

    return loss, optim, loss_u, loss_ph, gamma_est


# Backward-compatible alias used by older scripts.
build_loss_graph = build_forward_loss_graph


def build_inference_grid(nx: int = 101, nt: int = 151, l: float = L_DOM, T: float = T_FINAL):
    """Fixed (x,t) grid for evaluating the trained network after optimization.

    Must be attached to the graph *before* session.initialize_variables() so that
    layer weights are created in the same graph as the loss.
    """
    grids_xt = np.meshgrid(np.linspace(0.0, l, nx), np.linspace(0.0, T, nt), indexing="ij")
    grid_x, grid_t = [tf.convert_to_tensor(t.astype(np.float32)) for t in grids_xt]
    grid_u = math.expand_dims(network(grid_x, grid_t))
    return grid_x, grid_t, grid_u


def train_pinn(iters: int = ITERS_DEFAULT, log_every: int = 1000) -> Tuple[float, list, np.ndarray]:
    """Run forward PINN training loop.

    Returns
    -------
    elapsed : wall-clock seconds
    hist : list of (step, total_loss)
    u_grid : (nx, nt) field from the inference grid at final weights
    """
    tf.compat.v1.reset_default_graph()
    loss, optim, _, _, _ = build_forward_loss_graph()
    # Inference grid must exist before variable init (see build_inference_grid docstring).
    _, _, grid_u = build_inference_grid()
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
                print(f"  forward PINN step {step}, loss={lv:.6f}")
        u_grid = session.run(grid_u)
    finally:
        pass
    elapsed = time.perf_counter() - t0
    return elapsed, hist, np.asarray(u_grid)[0, :, :, 0]


def train_inverse_pinn(
    gamma_init: float = GAMMA_INIT_DEFAULT,
    iters: int = ITERS_INVERSE_DEFAULT,
    log_every: int = 1000,
) -> Tuple[float, List[Tuple[int, float, float]], np.ndarray, float]:
    """Run inverse PINN: recover gamma_est together with the solution field.

    Returns
    -------
    elapsed : wall-clock seconds
    hist : list of (step, total_loss, gamma_est) — use for gamma convergence plots
    u_grid : (nx, nt) predicted field
    final_gamma : last value of the trainable diffusion coefficient
    """
    tf.compat.v1.reset_default_graph()
    loss, optim, _, _, gamma_est = build_inverse_loss_graph(gamma_init=gamma_init)
    _, _, grid_u = build_inference_grid()
    hist: List[Tuple[int, float, float]] = []
    session = Session(None)
    session.initialize_variables()
    t0 = time.perf_counter()
    try:
        for step in range(iters + 1):
            _, lv, gv = session.run([optim, loss, gamma_est])
            if step < 3 or step % log_every == 0:
                hist.append((step, float(lv), float(gv)))
            if step % 500 == 0 and step > 0:
                print(f"  inverse PINN step {step}, loss={lv:.6f}, gamma={gv:.4f}")
        u_grid = session.run(grid_u)
        final_gamma = float(session.run(gamma_est))
    finally:
        pass
    elapsed = time.perf_counter() - t0
    return elapsed, hist, np.asarray(u_grid)[0, :, :, 0], final_gamma


def run_pinn_quick(iters: int = 2000) -> np.ndarray:
    """Short forward training run for figure generation scripts."""
    elapsed, hist, u_grid = train_pinn(iters=iters, log_every=500)
    print(f"Forward PINN done: {iters} iters, {elapsed:.1f}s, final loss={hist[-1][1]:.6f}")
    return u_grid


def run_inverse_pinn_quick(iters: int = 2000, gamma_init: float = GAMMA_INIT_DEFAULT):
    """Short inverse training run — smoke test for gamma identification."""
    elapsed, hist, u_grid, gamma = train_inverse_pinn(
        gamma_init=gamma_init, iters=iters, log_every=500
    )
    print(
        f"Inverse PINN done: {iters} iters, {elapsed:.1f}s, "
        f"gamma={gamma:.4f} (init={gamma_init}), loss={hist[-1][1]:.6f}"
    )
    return u_grid, gamma, hist
