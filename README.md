# Quantum MI Feedback: Bistability, Hysteresis & Cascade Suppression

**Author:** Nemo GR  
**Method:** Numerical simulation (Python/QuTiP, Lindblad master equation)  
**Status:** Amateur research, open for collaboration and critique

---

## What This Is

An open quantum spin system where bridge coupling strength is controlled 
in real time by mutual information (MI) via nonlinear feedback:
```
g_eff = g0 + α · tanh(β · m)
```

where `m` is exponential memory of MI between subsystems.  
Decoherence modeled via Lindblad operators.

---

## System

- Two spin chains (A and B), 3 qubits each (N=6 total)
- Random ZZ coupling bridge between chains
- Adaptive bridge: stronger when subsystems share more information
- Environment: amplitude damping on all qubits

---

## Results

### 1. Activation Threshold (α ≈ 3.5)
Below α ≈ 3.5, MI ≈ 0 regardless of initial state.  
Above threshold: sharp discontinuous jump in MI.  
Consistent with first-order dissipative phase transition.

### 2. Bistability (α ∈ [1.4, 3.5])
Same parameters → two different stable MI states depending on history.  
System remembers where it came from.

### 3. Hysteresis (3 independent seeds)
Sweeping α up then down produces non-overlapping MI curves.  
Loop area: 0.30–0.39 nats across seeds 137, 42, 999.  
Effect is structural, not seed-specific.

### 4. Asymmetric Relaxation
After a decoherence strike, the high-MI state (memory state) requires  
stronger feedback to recover than the cold-start state.  
Recovery threshold: α ≈ 2.3 (memory) vs α ≈ 1.8 (cold).

### 5. Cascade Suppression (A→B→C chain)
Three chains A, B, C with two adaptive bridges (AB and BC).  
**Unexpected finding:** MI_BC with A present ≈ 0.10 nats.  
MI_BC without A (isolated) ≈ 0.42 nats — **4x increase**.  
Subsystem A acts as a competing information sink,  
suppressing BC correlations through nonlinear feedback competition.  
Related to ancilla-induced disentangling but via active adaptive coupling.

---

## Key Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| N_sub | 3 | Qubits per chain |
| β | 5.0 | Feedback steepness |
| g0 | 0.02 | Base coupling |
| γ | 0.7 | Z2 symmetry breaking |
| decoherence | 0.04 | Amplitude damping rate |
| dt | 1.0 | Time step (mesolve) |
| steps/point | 30 | Thermalization steps |

---

## Requirements
```bash
pip install qutip numpy matplotlib
```

---

## Files

| File | Description |
|------|-------------|
| `hysteresis.py` | Main hysteresis scan (3 seeds) |
| `cascade_ABC.py` | Three-chain cascade experiment |
| `relaxation.py` | Relaxation after decoherence strike |

---

## Open Questions

1. Is the bistability here a genuine dissipative phase transition or a crossover?
2. Does the cascade suppression mechanism differ qualitatively from passive ancilla-induced disentangling?
3. Does the effect survive at N_sub = 4?

---

## Contact

Open to feedback from physicists.  
If you know related literature — please open an Issue.

github: spfilthes-ship-it
