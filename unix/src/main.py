"""Minimal two-qubit Bell-state simulator that outputs JS results."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Dict, List, Sequence


State = List[complex]


def hadamard(state: State, qubit: int, n_qubits: int) -> State:
    new_state: State = [0j] * len(state)
    size = 1 << n_qubits
    step = 1 << qubit
    for i in range(size):
        partner = i ^ step
        if i < partner:
            a = state[i]
            b = state[partner]
            new_state[i] = (a + b) / math.sqrt(2)
            new_state[partner] = (a - b) / math.sqrt(2)
    # fill untouched amplitudes when i > partner
    for i in range(size):
        if new_state[i] == 0j:
            new_state[i] = state[i]
    return new_state


def cnot(state: State, control: int, target: int, n_qubits: int) -> State:
    new_state = state.copy()
    size = 1 << n_qubits
    for i in range(size):
        if (i >> control) & 1:
            flipped = i ^ (1 << target)
            new_state[flipped] = state[i]
            new_state[i] = state[flipped]
    return new_state


def measure_counts(state: State, shots: int) -> Dict[str, int]:
    basis_states = [format(i, f"0{int(math.log2(len(state)))}b") for i in range(len(state))]
    probs = [abs(ampl) ** 2 for ampl in state]
    counts: Dict[str, int] = {b: 0 for b in basis_states}
    for _ in range(shots):
        r = random.random()
        acc = 0.0
        for b, p in zip(basis_states, probs):
            acc += p
            if r <= acc:
                counts[b] += 1
                break
    return {b: c for b, c in counts.items() if c > 0}


def bell_circuit(shots: int = 1000) -> Dict[str, object]:
    n_qubits = 2
    state: State = [0j] * (1 << n_qubits)
    state[0] = 1 + 0j
    state = hadamard(state, qubit=0, n_qubits=n_qubits)
    state = cnot(state, control=0, target=1, n_qubits=n_qubits)
    counts = measure_counts(state, shots)
    return {
        "circuit": "bell_pair",
        "shots": shots,
        "counts": counts,
    }


def write_js_results(result: Dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    js = "export const measurementResults = " + json.dumps(result, indent=2) + ";\n"
    out_path.write_text(js, encoding="utf-8")


def main() -> None:
    result = bell_circuit(shots=512)
    out_file = Path("dist/results.js")
    write_js_results(result, out_file)
    print(f"Wrote JS results to {out_file}")


if __name__ == "__main__":
    main()
