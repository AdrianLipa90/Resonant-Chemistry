# PhaseNav QGT spectroscopy bridge v0.1 — CANDIDATE_ONLY

Status: `CANDIDATE_ONLY / PHYSICAL_BINDING_OPEN / CANON_WRITE_AUTHORITY_FALSE / EPISTEMIC_CHYBA`.

For a parameter-dependent Hamiltonian `H(lambda)|n>=E_n|n>`, non-degenerate perturbation theory gives

`<m|d_mu n> = <m|d_mu H|n>/(E_n-E_m)` for `m != n`.

The corresponding quantum geometric tensor is reconstructed from transition data as

`Q^(n)_{mu,nu} = sum_{m!=n} <n|d_mu H|m><m|d_nu H|n>/(E_n-E_m)^2`.

The implementation in `reschem/qgt_spectroscopy_bridge_v01.py` provides:

- reconstruction of QGT from energies and derivative-operator matrix elements;
- transition-operator promotion defect `Delta_mu = mu_new P - P mu_old`;
- transition-amplitude comparison across an isometric promotion;
- direct comparison `Delta_Q = Q_predicted - Q_spectroscopic` with Frobenius and max-absolute residuals.

This interface is intended for future validation against atomic/molecular and electrophotonic observables. It does not claim that measured spectra already validate a Cayley–Dickson carrier, TIR, PhaseNav, or an SM–GR bridge.
