# Baseline catalogue (public ZK libraries only)

This catalogue lists public baselines. It does **not** pin anything for your
project. Your project keeps its own `baselines/MANIFEST.md`, owned by
`baseline-engineer`, with one row per baseline you actually use. Each row gives the
exact commit SHA, the build command and flags, the machine, and the date. See
`skills/baseline-pin/SKILL.md`.

Fetch: `references/baselines/fetch.sh DEST NAME...` clones the repository and
records the resolved SHA in `DEST/PINNED.tsv`. `fetch.sh --selftest` checks the
catalogue against this file and against the crbench parser registry.

**Pinning.** The "tag seen" column shows the newest release tag that
`git ls-remote --tags` listed on 2026-11-01. It is a starting point, not a pin:
this catalogue deliberately records **no commit SHAs** (a SHA copied from a
catalogue is easy to get wrong and goes stale). Pin it yourself:

1. pick the release tag the competitor's paper or artifact used (else the newest one);
2. `fetch.sh` it and copy the **full 40-hex SHA** from `PINNED.tsv` into your project MANIFEST,
   next to the tag;
3. from then on re-fetch by SHA (`PIN_<name>=<sha>`), because tags can be moved.

`HEAD` means the project had no usable release tag on that date, so the SHA is the
only pin. Re-check with `git ls-remote --tags URL` before you rely on a tag.

**Parser** names are crbench parsers (`lib/bench/crbench/parsers.py`, `crbench parsers`);
per-library recipes are in `crbench adapters` (`lib/bench/crbench/adapters.py`).
`none yet` means crbench has no parser for that output: keep the raw log, use
`shell-time` / `gnu-time` for wall clock and memory, and add a parser (with a
synthetic-log test) before numbers go into EVIDENCE.md.

Items marked **needs verification** are commands or facts that could not be
confirmed from the project's own README on 2026-11-01. `baseline-engineer` confirms
them against the pinned commit and records the actual command in the project MANIFEST.

## Project MANIFEST row format (copy into your project)

```markdown
| name | url | tag | commit (full SHA) | build recipe (exact) | toolchain + flags + features | threads / GPU | bench command | parser | statement + size | field / curve / PCS | soundness (bits, regime, level definition) | timing scope | role / what it is the baseline FOR | fairness notes |
```

## Universal fairness checklist (apply to every comparison)

- [ ] **Same statement.** Prove the same computation end to end (e.g. SHA-256 on the same
      input length), not "the same number of constraints": constraint and row counts are
      not comparable across arithmetizations (R1CS, Plonkish, AIR, CCS, binary towers).
- [ ] **Same soundness.** Both arms at the same number of bits, under the same regime
      (proven vs conjectured proximity bounds) and the same level definition
      (worst-case or average-case); recompute the baseline's level with
      `skills/soundness-budget`. Print the library's actual parameters at runtime
      (field / extension degree, blowup, query count, grinding bits, curve): defaults
      change between releases and differ from the ones quoted in papers.
- [ ] **Same field / curve where it matters.** A 31-bit-field prover against a
      BN254 prover is a comparison of *systems*, not of a technique; say which one
      you are making.
- [ ] **Same timing scope.** Witness generation, preprocessing / setup, key generation,
      trace generation, proving, recursion / wrapping (e.g. STARK→SNARK) and
      verification each in its own column; never one arm with witness generation and
      the other without.
- [ ] **Every timed proof verified.** The bench run verifies every proof it times; a
      run whose proof does not verify is discarded, not averaged.
- [ ] **Same threads and hardware features.** One thread against one thread, and N
      against N (`RAYON_NUM_THREADS`, `GOMAXPROCS`, `taskset`). Same
      `RUSTFLAGS="-C target-cpu=native"` (AVX2 / AVX-512 / NEON / GFNI) and asm features
      on both arms or on neither. A GPU arm is compared with a GPU arm, or the CPU
      and GPU numbers are reported side by side with the hardware named.
- [ ] **Same toolchain discipline.** Release profile, LTO setting and nightly channel
      recorded (several libraries pin a nightly in `rust-toolchain.toml`).
- [ ] **Same machine and session.** Interleaved rounds (`crbench run`), not different
      days. Trust ratios from back-to-back pairs.
- [ ] **Report all four.** Prover time, verifier time, proof size and peak memory
      (`gnu-time`), even when the headline is prover time.
- [ ] **Strongest baseline, current release.** These libraries move fast: compare
      against the current release of the strongest system for the statement, dated.
- [ ] **Reproduce cited numbers.** Never mix your measurement with a printed number
      in one ratio; re-measure the baseline yourself.
- [ ] **Build freshness.** Clean tree at the pinned SHA, `crbench stale BIN SRC`
      before timing, separate build directory per configuration.

---

## Proof-system libraries and SNARK frameworks

| fetch name | url | tag seen | build | bench | parser | fairness notes |
|---|---|---|---|---|---|---|
| `arkworks-algebra` | https://github.com/arkworks-rs/algebra | `v0.6.0` | `cargo build --release` | `cargo bench` (criterion; list with `cargo bench -- --list`) | `criterion` | Fields, curves, MSM, FFT. The `asm` and `parallel` features change results: record them; `RAYON_NUM_THREADS` on both arms. Curve crates live in `arkworks-rs/curves`. |
| `arkworks-groth16` | https://github.com/arkworks-rs/groth16 | `v0.6.0` | `cargo build --release` | `cargo bench` (criterion) | `criterion` | Groth16 reference prover. Report the curve (BN254 / BLS12-381) and whether witness generation is in the timed region. |
| `halo2-pse` | https://github.com/privacy-scaling-explorations/halo2 | `v2023_04_20` | `cargo build --release` | `cargo bench` (criterion; bench names **needs verification**) | `criterion` | PSE fork with KZG. State k (rows = 2^k), the commitment scheme (KZG / IPA) and the fork. The newest tag is old: compare against the commit the competitor used. |
| `halo2-zcash` | https://github.com/zcash/halo2 | `halo2_proofs-0.4.0` | `cargo build --release` | `cargo bench` (criterion) | `criterion` | Original IPA-based halo2 (Pasta curves). Do not mix with the PSE fork's numbers: different PCS and curve. |
| `plonky2` | https://github.com/0xPolygonZero/plonky2 | `v1.1.0` | `cargo build --release` (README: needs a recent nightly) | `RUSTFLAGS=-Ctarget-cpu=native cargo run --release --example bench_recursion -- -vv` (README); `cargo bench` for components | `criterion` (components); recursion example: `generic` / `shell-time` | Goldilocks + FRI. Record the FRI config (rate, queries, proof-of-work bits) and whether the number is a recursive proof. |
| `plonky3` | https://github.com/Plonky3/Plonky3 | `v0.8.0` | `RUSTFLAGS="-Ctarget-cpu=native" cargo build --release` | README benchmarks: `cargo run --example prove_prime_field_31 --release --features parallel -- --field koala-bear ...`; components: `cargo bench` | `criterion` (components); examples: `generic` / `shell-time` | SIMD paths are enabled via `RUSTFLAGS`, not Cargo features (README). Record field (BabyBear / KoalaBear / Mersenne31 / Goldilocks), extension degree, FRI blowup, queries and `--security-bits`. |
| `gnark` | https://github.com/Consensys/gnark | `v0.16.4` | `go build ./...` | `go test -run=^$ -bench=<B> -benchtime=10x -count=5 ./...`; debug logs for constraint counts | `gobench`; logs: `gnark` (adapter `gnark-log`) | Report the constraint count next to the time, the backend (Groth16 / PLONK) and the curve. `GOMAXPROCS` on both arms. GPU (icicle) acceleration is a build tag: same on both arms. |
| `lambdaworks` | https://github.com/lambdaclass/lambdaworks | `v0.15.0` | `cargo build --release` | `cargo bench` (criterion; per-crate benches **needs verification**) | `criterion` | Fields, curves, STARK and PLONK provers in one library; record which prover and field. Has CUDA/Metal features: same on both arms. |
| `expander` | https://github.com/PolyhedraZK/Expander | `v1.2.0` | `cargo build --release` (MPI is used for multi-process runs: **needs verification**) | bench binary and its flags **needs verification** | `generic` / `shell-time` (format **needs verification**) | GKR-based prover. Record field (M31 / BN254 / GF(2) extension), the number of processes and whether SIMD packing is on. |
| `binius64` | https://github.com/binius-zk/binius64 | `HEAD` (no release tag seen) | `RUSTFLAGS="-C target-cpu=native" cargo build --release` | `RUSTFLAGS="-Ctarget-cpu=native" cargo run --release -p binius-examples -- sha512 prove --message-len 65536` (README) | `generic` / `shell-time` (example output format **needs verification**) | Current Binius line (binary tower fields). `RAYON_NUM_THREADS` / `taskset` per the README; GFNI / NEON availability changes results: record the CPU flags. |
| `binius` | https://github.com/IrreducibleOSS/binius | `HEAD` (no release tag seen) | `RUSTFLAGS="-C target-cpu=native" cargo build --release` | `cargo bench` (criterion, README) | `criterion` | Earlier Binius code base; whether it is still maintained or superseded by `binius64` **needs verification**. Pin the code base the competitor's paper used. |
| `stwo` | https://github.com/starkware-libs/stwo | `v2.3.0` | `cargo build --release --features "prover,parallel"` (README; nightly pinned in `rust-toolchain.toml`) | `cargo bench` (criterion; bench names **needs verification**) | `criterion` | Circle STARK over Mersenne31. Record `parallel` on/off, blowup, queries and PoW bits; compare at the same bits and regime. |
| `icicle` | https://github.com/ingonyama-zk/icicle | `v4.0.0` | C++: `cmake -S icicle -B build -DFIELD=<f> && cmake --build build -j` (README); Rust: `cargo build --release` | GPU benches per backend **needs verification** | `criterion` for the Rust wrappers (**needs verification**); C++ harness: `gbench` / `generic` | GPU (CUDA / Metal) MSM and NTT. Name the GPU, driver and backend version; compare against a GPU baseline, or report CPU and GPU side by side. Count host↔device transfers in the timed region or say they are excluded. |

## Circuit DSLs, compilers and their provers

| fetch name | url | tag seen | build | bench | parser | fairness notes |
|---|---|---|---|---|---|---|
| `circom` | https://github.com/iden3/circom | `v2.2.3` | `cargo build --release` | `circom <c>.circom --r1cs --wasm --sym -o build` | `circom` | Pin compiler version and `--O0/--O1/--O2`: it changes the linear-constraint count. Compiler and prover are separate tools: pin both. |
| `snarkjs` | https://github.com/iden3/snarkjs | `v0.7.6` | `npm install` (or `npm install -g snarkjs@<ver>`) | `time snarkjs groth16 prove ...`; `snarkjs r1cs info` for counts | `snarkjs` | Prints no timings: keep the shell `time` output. Node version matters; record it. |
| `rapidsnark` | https://github.com/iden3/rapidsnark | `v0.0.8` | `make host` (README; macOS: `make macos_arm64`) | `time ./prover <zkey> <wtns> proof.json public.json` | `rapidsnark` | Witness generation (wasm or C++) is a separate step: time it separately and state which one the comparison includes. |
| `noir` | https://github.com/noir-lang/noir | `v1.0.0` | `cargo build --release` (or the `noirup` installer at the same version) | `nargo info --package <p>` for opcode counts; proving with the backend (below) | `nargo-info` | ACIR opcodes are not backend gates: report the backend's gate count from the backend's own tool. Pin nargo and the backend together. |
| `barretenberg` | https://github.com/AztecProtocol/barretenberg | `v6.0.0` | per its README (C++/CMake) **needs verification**; this repository may be a mirror of `AztecProtocol/aztec-packages` (**needs verification**) | `time bb prove ...` (flags **needs verification**) | `shell-time` | Default proving backend for Noir. Record the `bb` version that matches the pinned nargo. |

## zkVMs

| fetch name | url | tag seen | build | bench | parser | fairness notes |
|---|---|---|---|---|---|---|
| `risc0` | https://github.com/risc0/risc0 | `v3.0.6` | toolchain via `rzup install` (README), then `cargo build --release` in the host crate | `RISC0_INFO=1 RUST_LOG=info cargo run --release -p <host>` | `risc0` | Report segments, rows / cycles and the prover backend (CPU / CUDA / Metal). Pin the `rzup` toolchain version. State the proof type (composite / succinct / Groth16). |
| `sp1` | https://github.com/succinctlabs/sp1 | `v6.10.0` | `sp1up` toolchain (SP1 book), `cargo prove build` in the program crate (**needs verification** for this release) | `RUST_LOG=info cargo run --release --bin <script>` | `sp1` | Cycles from the execution report; time execute and prove separately; state the proof type (core / compressed / Groth16 / PLONK) and CPU vs GPU prover. |
| `jolt` | https://github.com/a16z/jolt | `HEAD` (pre-release tags only, newest `v0.3.0-alpha`) | `cargo build --release -p jolt-prover` (README) | `cargo run --release -p jolt-prover --features profiling -- profile --name fibonacci --format chrome` (README; writes `benchmark-runs/<ts>/summary.json`) | none yet (keep `summary.json`; wall clock via `shell-time`) | Lookup / sum-check zkVM. Report the guest program, the trace length and the PCS. Read prover time and peak memory from `summary.json`; a `jolt` parser is a crbench follow-up. |

Compare zkVMs on the same guest program and input, with cycle counts from each VM's own
report (different ISAs and precompiles make "cycles" incomparable on their own), and
report whether a precompile was used for the hot function.

## Folding and IVC

| fetch name | url | tag seen | build | bench | parser | fairness notes |
|---|---|---|---|---|---|---|
| `nova` | https://github.com/microsoft/Nova | `HEAD` (no release tag seen) | `cargo build --release` | `cargo bench` (criterion; benches incl. `benches/sha256.rs`); `cargo run --release --example minroot` (README) | `criterion` | Report per-step folding time and the final compressed SNARK separately; name the curve cycle and the compressing SNARK. |
| `sonobe` | https://github.com/privacy-scaling-explorations/sonobe | `HEAD` (pre-release tags only, newest `v0.1.0-alpha.1`) | `cargo build --release` | examples / benches **needs verification** | `criterion` if benches use criterion, else `generic` (**needs verification**) | Several folding schemes (Nova, HyperNova, ProtoGalaxy) and deciders in one library: name the scheme, the curve cycle and the decider; time folding steps and the decider separately. |

## Solvers for circuit audits

Used by `skills/circuit-audit` (witness-uniqueness and under-constraint queries), not as
proving baselines.

| fetch name | url | tag seen | build | bench | parser | fairness notes |
|---|---|---|---|---|---|---|
| `cadical` | https://github.com/arminbiere/cadical | `rel-3.0.1` | `./configure && make` | `cadical <f>.cnf` | `sat` | Fix the seed; report the CNF hash and SAT/UNSAT, not only the time. |
| `kissat` | https://github.com/arminbiere/kissat | `rel-4.0.4` | `./configure && make` | `kissat <f>.cnf` | `sat` | Solver variance is large: compare over many instances or seeds, never one. |

## How a baseline enters a project

1. `baseline-engineer` fetches it with `fetch.sh` and copies the tag **and** the resolved
   full SHA into the project's `baselines/MANIFEST.md`.
2. It builds the baseline with the exact recipe and records toolchain, flags and features,
   aligned with `impl/BUILD.md` (prover-engineer).
3. It runs the library's own tests and checks that a proof for the target statement
   verifies.
4. It prints the actual runtime parameters (field, extension degree, blowup, queries,
   grinding, curve, k) and recomputes the soundness level with `skills/soundness-budget`;
   the competitor is signed off only at the same bits, regime and level definition as ours.
5. It runs `crbench run` with the baseline as its only arm, repeated at least 3 times,
   every proof verified, to get a reference median.
6. It hands the recipe to `experimenter`.
