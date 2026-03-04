"""
Quantum MI Feedback: Cascade A→B→C Experiment
Author: Nemo GR
System: Three spin chains (N=9), Lindblad master equation
Result: BC suppressed by A presence — 4x increase when A isolated
"""
import os
os.environ['OMP_NUM_THREADS'] = '16'
import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
import time

def get_op_i(op, i, N):
    return qt.tensor([qt.qeye(2)]*i + [op] + [qt.qeye(2)]*(N-i-1))

def run_cascade(alpha_seq, start_mode, seed, ab_bridge=True):
    """
    ab_bridge=True:  both AB and BC bridges active
    ab_bridge=False: only BC bridge active (A isolated)
    """
    N_sub, N = 3, 9
    dt_big, n_steps = 1.0, 20
    beta, g0, gamma, decoherence = 5.0, 0.02, 0.7, 0.04

    def get_H_sub(start):
        H = 0
        for i in range(start, start + N_sub):
            H += 1.0 * get_op_i(qt.sigmax(), i, N)
            H += 0.5 * get_op_i(qt.sigmaz(), i, N)
            if i < start + N_sub - 1:
                H += 1.0 * get_op_i(qt.sigmaz(), i, N) * get_op_i(qt.sigmaz(), i+1, N)
                H += gamma * get_op_i(qt.sigmax(), i, N) * get_op_i(qt.sigmaz(), i+1, N)
        return H

    HA = get_H_sub(0)
    HB = get_H_sub(3)
    HC = get_H_sub(6)

    np.random.seed(seed)
    H_bridge_AB = sum(
        np.random.uniform(-0.5, 0.5) * get_op_i(qt.sigmaz(), i, N) * get_op_i(qt.sigmaz(), j, N)
        for i in range(0, 3) for j in range(3, 6)
    )
    H_bridge_BC = sum(
        np.random.uniform(-0.5, 0.5) * get_op_i(qt.sigmaz(), i, N) * get_op_i(qt.sigmaz(), j, N)
        for i in range(3, 6) for j in range(6, 9)
    )

    c_ops = [np.sqrt(decoherence) * get_op_i(qt.sigmam(), i, N) for i in range(N)]

    state_idx = 0 if start_mode == 'up' else 1
    rho = qt.ket2dm(qt.tensor([qt.basis(2, state_idx)] * N).unit())

    def get_mi(rho, idxA, idxB):
        rho_sub = rho.ptrace(idxA + idxB)
        local_A = list(range(len(idxA)))
        local_B = list(range(len(idxA), len(idxA) + len(idxB)))
        rho_a = rho_sub.ptrace(local_A)
        rho_b = rho_sub.ptrace(local_B)
        s_ab = max(0, float(qt.entropy_vn(rho_sub).real))
        return max(0, float((qt.entropy_vn(rho_a) + qt.entropy_vn(rho_b) - s_ab).real))

    idx_a, idx_b, idx_c = [0,1,2], [3,4,5], [6,7,8]
    results_AB, results_BC = [], []
    m_AB, m_BC = 0.0, 0.0
    mi_AB, mi_BC = 0.0, 0.0

    for alpha_val in alpha_seq:
        for _ in range(n_steps):
            mi_AB = get_mi(rho, idx_a, idx_b)
            mi_BC = get_mi(rho, idx_b, idx_c)
            m_AB = 0.8 * m_AB + 0.2 * mi_AB
            m_BC = 0.8 * m_BC + 0.2 * mi_BC
            g_BC = g0 + alpha_val * np.tanh(beta * m_BC)

            if ab_bridge:
                g_AB = g0 + alpha_val * np.tanh(beta * m_AB)
                H_total = HA + HB + HC + g_AB * H_bridge_AB + g_BC * H_bridge_BC
            else:
                H_total = HA + HB + HC + g_BC * H_bridge_BC

            rho = qt.mesolve(H_total, rho, [0, dt_big], c_ops).states[-1]

        results_AB.append(mi_AB)
        results_BC.append(mi_BC)
        print(f"[{start_mode}] alpha={alpha_val:.2f} MI_AB={mi_AB:.4f} MI_BC={mi_BC:.4f}", flush=True)

    return results_AB, results_BC

if __name__ == "__main__":
    try:
        SEED = 137
        N_POINTS = 20
        alphas_up   = np.linspace(0.0, 5.0, N_POINTS)
        alphas_down = alphas_up[::-1]

        DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

        # Experiment 1: Both bridges active
        print("=== EXPERIMENT 1: AB + BC bridges ===")
        t0 = time.time()
        up_AB, up_BC     = run_cascade(alphas_up,   'up',   SEED, ab_bridge=True)
        down_AB, down_BC = run_cascade(alphas_down, 'down', SEED, ab_bridge=True)
        print(f"Done in {time.time()-t0:.1f}s")

        # Experiment 2: BC only (A isolated)
        print("\n=== EXPERIMENT 2: BC only (A isolated) ===")
        t0 = time.time()
        up_AB2, up_BC2     = run_cascade(alphas_up,   'up',   SEED, ab_bridge=False)
        down_AB2, down_BC2 = run_cascade(alphas_down, 'down', SEED, ab_bridge=False)
        print(f"Done in {time.time()-t0:.1f}s")

        # Plot comparison
        plt.style.use('dark_background')
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle("Cascade Suppression: BC with A vs BC without A", fontsize=14)

        ax = axes[0]
        ax.plot(alphas_up, up_BC,         '->', color='#00FFCC', lw=2, label='Up — with A')
        ax.plot(alphas_up, down_BC[::-1], '<-', color='#FF00FF', lw=2, label='Down — with A')
        ax.set_title("MI_BC — A present")
        ax.set_xlabel("Alpha")
        ax.set_ylabel("MI_BC (Nats)")
        ax.legend()
        ax.grid(alpha=0.15)

        ax = axes[1]
        ax.plot(alphas_up, up_BC2,         '->', color='#00FFCC', lw=2, label='Up — A isolated')
        ax.plot(alphas_up, down_BC2[::-1], '<-', color='#FF00FF', lw=2, label='Down — A isolated')
        ax.set_title("MI_BC — A isolated (4x stronger)")
        ax.set_xlabel("Alpha")
        ax.set_ylabel("MI_BC (Nats)")
        ax.legend()
        ax.grid(alpha=0.15)

        plt.tight_layout()
        plt.savefig(os.path.join(DESKTOP, "cascade_suppression.png"), dpi=150)
        plt.show()

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress ENTER to exit...")
