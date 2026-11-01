"""Adapter recipes: how to benchmark each public baseline with crbench.

These are *recipes*, not vendored code.  Each entry tells you which parser to use
and a typical command template (run from the baseline's build directory, see
``references/baselines/MANIFEST.md`` for fetch/pin/build).  ``{target}`` and
``{threads}`` are placeholders you fill in.

Fairness reminders printed by ``crbench adapters NAME`` come from the manifest's
fairness checklist: same parameters, same thread count, same compiler and flags,
same machine, interleaved rounds, every timed proof verified. Recipes for arkworks, gnark and circom match
the MANIFEST rows; the others are the commands experimenter needs for the remaining parsers.
"""
from __future__ import annotations

ADAPTERS: dict[str, dict] = {
    # MANIFEST entries: arkworks, gnark, circom (compiler) + snarkjs / rapidsnark (provers)
    "arkworks": {"parser": "criterion", "cmd": "cargo bench --bench {target} -- --noplot",
                 "notes": "Record the curve / field and the asm and parallel features; RAYON_NUM_THREADS={threads} on both arms."},
    "gnark": {"parser": "gobench", "cmd": "go test -run=^$ -bench={target} -benchtime=10x -count=5 ./...",
              "notes": "GOMAXPROCS={threads}. Report the constraint count next to the time and name the backend (Groth16 / PLONK) and curve."},
    "gnark-log": {"parser": "gnark", "cmd": "go run ./cmd/{target}",
                  "notes": "Debug-level gnark logs give nbConstraints and 'prover done ... took=' (ms); set the logger level to debug."},
    "circom": {"parser": "circom", "cmd": "circom {target}.circom --r1cs --wasm --sym -o build",
               "notes": "Pin the compiler version and the optimisation flag (--O0/--O1/--O2): it changes the linear-constraint count."},
    "snarkjs": {"parser": "snarkjs", "cmd": "time snarkjs groth16 prove build/{target}.zkey build/{target}.wtns proof.json public.json",
                "notes": "snarkjs prints no timings: keep the shell time output in the log. 'snarkjs r1cs info build/{target}.r1cs' gives the counts. Node version matters."},
    "rapidsnark": {"parser": "rapidsnark", "cmd": "time ./prover build/{target}.zkey build/{target}.wtns proof.json public.json",
                   "notes": "Witness generation (wasm or C++) is a separate step: time it separately and say which one the paper reports."},
    "halo2": {"parser": "criterion", "cmd": "cargo bench --bench {target} -- --noplot",
              "notes": "State k (rows = 2^k), the commitment scheme (KZG / IPA) and the halo2 fork; RAYON_NUM_THREADS={threads}."},
    "plonky3": {"parser": "criterion", "cmd": "cargo bench --bench {target} -- --noplot",
                "notes": "Record the field (BabyBear / Goldilocks / Mersenne31), extension degree, FRI blowup and query count."},
    "nargo": {"parser": "nargo-info", "cmd": "nargo info --package {target}",
              "notes": "ACIR opcodes are not backend gates: record the backend gate count separately with the backend's own tool."},
    "risc0": {"parser": "risc0", "cmd": "RISC0_INFO=1 RUST_LOG=info cargo run --release -p {target}",
              "notes": "Report segments, rows / cycles and the prover (CPU / CUDA / Metal); pin the toolchain (rzup) version."},
    "sp1": {"parser": "sp1", "cmd": "RUST_LOG=info cargo run --release --bin {target}",
            "notes": "Cycles from the execution report; time execute and prove separately and state the proof type (core / compressed / Groth16)."},
    "sat": {"parser": "sat", "cmd": "cadical {target}.cnf",
            "notes": "For solver-based circuit audits: fix the random seed; report solver version and the CNF hash."},
    "gnu-time": {"parser": "gnu-time", "cmd": "/usr/bin/time -v {target}", "notes": "Peak memory (max RSS)."},
}


def describe(name: str) -> str:
    a = ADAPTERS[name]
    return f"{name}: parser={a['parser']}\n  cmd:   {a['cmd']}\n  notes: {a['notes']}"


if __name__ == "__main__":
    for n in ADAPTERS:
        assert ADAPTERS[n]["parser"]
        print(describe(n))
