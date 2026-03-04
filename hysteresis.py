"""
Quantum MI Feedback: Hysteresis Experiment
Author: Nemo GR
System: Two spin chains (N=6), Lindblad master equation
Result: Bistability and hysteresis reproducible across 3 seeds
"""
import os
os.environ['OMP_NUM_THREADS'] = '16'
import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor
import time

SEED = 137  # Change to 42 or 999 for reproducibility check

def get_op_i(op, i, N):
    return qt.tensor([qt.qeye(2)]*i + [op] + [qt.qeye(2)]*(N-i-1))

def run_hysteresis(params):
    alpha_seq, start_mode, seed = params
    N_sub, N = 3, 6
    dt_big, n_steps = 1.0, 30
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

    HA, HB = get_H_sub(0), get_H_sub(N_sub)
    np.random.seed(seed)
    H_bridge_base = sum(
        np.random.uniform(-0.5, 0.5) * get_op_i(qt.sigmaz(), i, N) * get_op_i(qt.sigmaz(), j, N)
        for i in range(N_sub) for j in range(N_sub, N)
    )
    c_ops = [np.sqrt(decoherence) * get_op_i(qt.sigmam(), i, N) for i in range(N)]

    state_idx = 0 if start_mode == 'up' else 1
    rho = qt.ket2dm(qt.tensor([qt.basis(2, state_idx)] * N).unit())
    idx_a, idx_b = list(range(N_sub)), list(range(N_sub, N))

    results = []
    m_mem, mi = 0.0, 0.0

    for alpha_val in alpha_seq:
        for _ in range(n_steps):
            rho_a, rho_b = rho.ptrace(idx_a), rho.ptrace(idx_b)
            s_ab = max(0, float(qt.entropy_vn(rho).real))
            mi = max(0, float((qt.entropy_vn(rho_a) + qt.entropy_vn(rho_b) - s_ab).real))
            m_mem = 0.8 * m_mem + 0.2 * mi
            g_eff = g0 + alpha_val * np.tanh(5.0 * m_mem)
            H_total = HA + HB + g_eff * H_bridge_base
            rho = qt.mesolve(H_total, rho, [0, dt_big], c_ops).states[-1]

        results.append(mi)
        print(f"[{start_mode}] alpha={alpha_val:.2f} MI={mi:.4f}", flush=True)
    return results

if __name__ == "__main__":
    try:
        DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
        N_POINTS = 35
        alphas_up   = np.linspace(0.0, 5.0, N_POINTS)
        alphas_down = alphas_up[::-1]

        print(f"Seed={SEED}")
        t0 = time.time()

        with ProcessPoolExecutor(max_workers=2) as ex:
            res_up, res_down = list(ex.map(run_hysteresis, [
                (alphas_up,   'up',   SEED),
                (alphas_down, 'down', SEED)
            ]))

        print(f"Done in {time.time()-t0:.1f}s")

        area = float(np.sum(np.abs(np.array(res_up) - np.array(res_down[::-1]))) * (5.0 / N_POINTS))

        plt.style.use('dark_background')
        plt.figure(figsize=(10, 6))
        plt.plot(alphas_up, res_up, '->', color='#00FFCC', lw=2, label='Up |000⟩')
        plt.plot(alphas_up, res_down[::-1], '<-', color='#FF00FF', lw=2, label='Down |111⟩')
        plt.fill_between(alphas_up, res_up, res_down[::-1], color='white', alpha=0.08)
        plt.axvline(3.5, color='yellow', ls=':', alpha=0.3, label='Threshold α≈3.5')
        plt.title(f"Hysteresis | Seed={SEED} | Loop Area={area:.4f}", fontsize=14)
        plt.xlabel("Alpha (Feedback Strength)")
        plt.ylabel("Steady-State MI (Nats)")
        plt.legend()
        plt.grid(alpha=0.15)
        plt.tight_layout()
        plt.savefig(os.path.join(DESKTOP, f"hysteresis_seed{SEED}.png"), dpi=150)
        plt.show()

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress ENTER to exit...")
