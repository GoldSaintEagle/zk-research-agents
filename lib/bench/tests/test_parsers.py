import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crbench import parsers  # noqa: E402
from crbench.parsers import Record, parse_text, register_parser, values  # noqa: E402

# All logs below are SYNTHETIC, written to mimic each tool's output format.


class TestParsers(unittest.TestCase):
    def test_generic(self):
        txt = "keygen time: 12.5 ms\nEncrypt elapsed = 3 us\nbootstrap took 1.5 s\nRESULT name=toy t=2.5ms mults=26 status=CORRECT\n"
        recs = parse_text(txt, "generic")
        t = values(recs, "time")
        self.assertAlmostEqual(t[0], 0.0125)
        self.assertAlmostEqual(t[1], 3e-6)
        self.assertAlmostEqual(t[2], 1.5)
        self.assertAlmostEqual(values(recs, "t", "toy")[0], 0.0025)
        self.assertEqual(values(recs, "mults", "toy"), [26.0])
        self.assertTrue(any(r.metric == "status" and r.value == "CORRECT" for r in recs))

    def test_criterion(self):
        txt = "pbs/toy_param_2bit\n                        time:   [11.200 ms 11.350 ms 11.500 ms]\n"
        recs = parse_text(txt, "auto")
        mid = [r for r in recs if r.metric == "time"][0]
        self.assertAlmostEqual(mid.value, 0.01135)
        self.assertEqual(mid.label, "pbs/toy_param_2bit")
        self.assertAlmostEqual(values(recs, "time_lo")[0], 0.0112)

    def test_gobench(self):
        txt = "goos: linux\nBenchmarkToyMul/logN=10-8   \t    1000\t   1234567 ns/op\t  4096 B/op\t  12 allocs/op\nPASS\n"
        recs = parse_text(txt, "auto")
        self.assertAlmostEqual(values(recs, "time")[0], 1.234567e-3)
        self.assertEqual(recs[0].label, "BenchmarkToyMul/logN=10")
        self.assertEqual(values(recs, "alloc"), [4096.0])

    def test_gbench(self):
        txt = ("-----------------------------------------------------------\n"
               "Benchmark                 Time             CPU   Iterations\n"
               "-----------------------------------------------------------\n"
               "BM_ToyEvalMult         1.50 ms         1.49 ms          466\n")
        recs = parse_text(txt, "auto")
        self.assertAlmostEqual(values(recs, "time")[0], 1.5e-3)
        self.assertAlmostEqual(values(recs, "cpu_time")[0], 1.49e-3)

    def test_helib(self):
        txt = "  recrypt: 40.5 / 3 = 13.5   [recryption.cpp]\n  multiplyBy: 2.4 / 12 = 0.2   [Ctxt.cpp]\n"
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "time", "recrypt"), [13.5])
        self.assertEqual(values(recs, "count", "multiplyBy"), [12.0])

    def test_openfhe(self):
        txt = "Bootstrapping time: 812.4 ms\nEvalMult time [ms]: 4.2\n"
        recs = parse_text(txt, "openfhe")
        self.assertAlmostEqual(values(recs, "time")[0], 0.8124)
        self.assertAlmostEqual(values(recs, "time")[1], 0.0042)

    def test_lattice_estimator(self):
        txt = ("usvp                 :: rop: ≈2^131.2, red: ≈2^131.2, δ: 1.004000, β: 385, d: 1900, tag: usvp\n"
               "bdd                  :: rop: ≈2^129.8, red: ≈2^129.0, svp: ≈2^128.1, β: 377, η: 400, d: 1880, tag: bdd\n"
               "dual_hybrid          :: rop: ≈2^135.0, red: ≈2^134.9, guess: ≈2^127.3, β: 395, p: 3, zeta: 0, tag: dual_hybrid\n")
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "rop_bits", "bdd"), [129.8])
        self.assertEqual(values(recs, "beta", "usvp"), [385.0])
        sec = [r for r in recs if r.metric == "security_bits"][0]
        self.assertEqual(sec.value, 129.8)
        self.assertEqual(sec.label, "min:bdd")

    def test_sat(self):
        txt = "c some banner\ns UNSATISFIABLE\nc total process time since initialization:         2.41    seconds\n"
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "time"), [2.41])
        self.assertTrue(any(r.value == "UNSATISFIABLE" for r in recs))

    def test_mpspdz(self):
        txt = "Time = 0.512 seconds \nData sent = 1.5 MB in ~42 rounds (party 0)\nGlobal data sent = 3 MB (all parties)\n"
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "time"), [0.512])
        self.assertEqual(values(recs, "comm"), [1.5e6])
        self.assertEqual(values(recs, "rounds"), [42.0])
        self.assertEqual(values(recs, "comm_global"), [3e6])

    def test_gnu_time(self):
        txt = "\tElapsed (wall clock) time (h:mm:ss or m:ss): 1:02.50\n\tMaximum resident set size (kbytes): 2048\n"
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "time"), [62.5])
        self.assertEqual(values(recs, "max_rss"), [2048 * 1024.0])

    def test_register_custom(self):
        @register_parser("toytool", "custom", sniff=r"^TOYTOOL")
        def _p(text):
            return [Record("time", float(text.split()[-1]), "s", "toy", 1)]

        self.assertIn("toytool", parsers.REGISTRY)
        self.assertEqual(values(parse_text("TOYTOOL v1 0.25", "auto")), [0.25])
        parsers.REGISTRY.pop("toytool")

    def test_regex_parser_builder(self):
        parsers.regex_parser("toyrx", r"^lat=(?P<value>\d+(?:\.\d+)?)(?P<unit>ms)", description="x")
        self.assertEqual(values(parse_text("lat=3ms\n", "toyrx")), [0.003])
        parsers.REGISTRY.pop("toyrx")

    def test_adapters_reference_real_parsers(self):
        from crbench.adapters import ADAPTERS
        for name, a in ADAPTERS.items():
            self.assertIn(a["parser"], parsers.REGISTRY, name)

    def test_unknown(self):
        with self.assertRaises(KeyError):
            parse_text("x", "nope")
        with self.assertRaises(ValueError):
            parsers.to_seconds(1, "fortnights")


class TestZKParsers(unittest.TestCase):
    """ZK tool outputs. Every log is SYNTHETIC (made-up numbers) in the format named in the comment."""

    def test_shell_time(self):
        # bash `time` builtin and zsh `time` (format: bash/zsh manuals)
        txt = "real\t1m2.500s\nuser\t0m58.100s\nsys\t0m1.200s\n"
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "time", "real"), [62.5])
        self.assertEqual(values(recs, "time", "sys"), [1.2])
        z = parse_text("./prover a b  1.10s user 0.10s system 99% cpu 1.334 total\n", "shell-time")
        self.assertEqual(values(z, "time", "real"), [1.334])
        self.assertEqual(values(z, "time", "user"), [1.1])

    def test_snarkjs(self):
        # format: snarkjs README, `snarkjs r1cs info` example; verify line "snarkJS: OK!" needs verification
        txt = ("[INFO]  snarkJS: Curve: bn-128\n[INFO]  snarkJS: # of Wires: 1003\n"
               "[INFO]  snarkJS: # of Constraints: 1000\n[INFO]  snarkJS: # of Private Inputs: 2\n"
               "[INFO]  snarkJS: # of Public Inputs: 0\n[INFO]  snarkJS: # of Outputs: 1\n"
               "[INFO]  snarkJS: OK!\nreal\t0m0.812s\nuser\t0m0.900s\nsys\t0m0.050s\n")
        self.assertEqual(parsers.detect(txt), ["snarkjs"])         # shell-time is subsumed
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "constraints"), [1000.0])
        self.assertEqual(values(recs, "wires"), [1003.0])
        self.assertEqual(values(recs, "public_inputs"), [0.0])
        self.assertEqual(values(recs, "time", "real"), [0.812])
        self.assertEqual([r.value for r in recs if r.metric == "verify_status"], ["OK"])
        bad = parse_text("[ERROR] snarkJS: Invalid proof\n", "snarkjs")
        self.assertEqual([r.value for r in bad if r.metric == "verify_status"], ["INVALID"])

    def test_rapidsnark(self):
        # rapidsnark prints no timing by default (needs verification): shell time around the prover
        txt = "$ time ./prover circuit.zkey witness.wtns proof.json public.json\nreal\t0m0.214s\nuser\t0m1.500s\nsys\t0m0.020s\n"
        recs = parse_text(txt, "rapidsnark")
        self.assertEqual(values(recs, "time", "real"), [0.214])
        recs = parse_text("prove time: 214 ms\n", "rapidsnark")
        self.assertAlmostEqual(values(recs, "time")[0], 0.214)

    def test_circom(self):
        # format: circom 2.x compile summary as seen in public build logs -- needs verification
        txt = ("template instances: 3\nnon-linear constraints: 2\nlinear constraints: 1\npublic inputs: 1\n"
               "private inputs: 2\npublic outputs: 1\nwires: 6\nlabels: 9\nWritten successfully: ./toy.r1cs\n"
               "Everything went okay\n")
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "non_linear_constraints"), [2.0])
        self.assertEqual(values(recs, "linear_constraints"), [1.0])
        self.assertEqual(values(recs, "constraints"), [3.0])
        self.assertEqual(values(recs, "wires"), [6.0])

    def test_gnark(self):
        # format: gnark logger/logger.go (zerolog ConsoleWriter, 15:04:05) + groth16 prove.go ("prover done", took
        # in ms, zerolog default); the compile line with nbConstraints mirrors the frontend logger (needs verification)
        txt = ("10:21:09 INF compiling circuit\n"
               "10:21:09 INF parsed circuit inputs nbPublic=1 nbSecret=2\n"
               "10:21:09 INF building constraint builder nbConstraints=4096\n"
               "10:21:10 DBG prover done backend=groth16 curve=bn254 nbConstraints=4096 took=123.45\n"
               "10:21:10 DBG verifier done backend=groth16 curve=bn254 took=1.5\n")
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "constraints", "building constraint builder"), [4096.0])
        self.assertAlmostEqual(values(recs, "time", "prover")[0], 0.12345)
        self.assertAlmostEqual(values(recs, "time", "verifier")[0], 0.0015)
        # benchmarks stay with the gobench parser
        b = parse_text("BenchmarkProve/groth16-8   \t  10\t 98765432 ns/op\n", "gobench")
        self.assertAlmostEqual(values(b, "time")[0], 0.098765432)

    def test_halo2_criterion(self):
        # halo2 / plonky3 benches use criterion (format: criterion user guide, command-line output); the existing
        # parser handles long names on their own line, change / outlier lines and progress lines in between
        txt = ("Benchmarking prove/k=12: Warming up for 3.0000 s\n"
               "Benchmarking prove/k=12: Analyzing\n"
               "prove/k=12              time:   [1.2345 s 1.2500 s 1.2700 s]\n"
               "                        change: [-1.0% +0.5% +2.0%] (p = 0.60 > 0.05)\n"
               "                        No change in performance detected.\n"
               "Found 1 outliers among 10 measurements (10.00%)\n"
               "verify/plonk_with_lookups_k=16\n"
               "                        time:   [3.1000 ms 3.2000 ms 3.3000 ms]\n")
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "time", "prove/k=12"), [1.25])
        self.assertAlmostEqual(values(recs, "time", "verify/plonk_with_lookups_k=16")[0], 3.2e-3)
        self.assertEqual(len(values(recs, "time")), 2)

    def test_nargo_info(self):
        # format: noir tooling/noirc_artifacts_info (header Package | Function | ACIR Opcodes | Brillig Opcodes)
        txt = ("+---------+----------+--------------+-----------------+\n"
               "| Package | Function | ACIR Opcodes | Brillig Opcodes |\n"
               "+---------+----------+--------------+-----------------+\n"
               "| toy     | main     | 1,024        | 0               |\n"
               "| toy     | helper   | 0            | 37              |\n"
               "+---------+----------+--------------+-----------------+\n")
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "acir_opcodes", "toy/main"), [1024.0])
        self.assertEqual(values(recs, "brillig_opcodes", "toy/helper"), [37.0])
        # older layout with a backend circuit size column (needs verification for the exact version)
        old = ("| Package | Expression Width | ACIR Opcodes | Backend Circuit Size |\n"
               "| toy     | Bounded { width: 4 } | 12 | 2048 |\n")
        self.assertEqual(values(parse_text(old, "nargo-info"), "circuit_size", "toy"), [2048.0])
        js = ('{"programs": [{"package_name": "toy", "functions": [{"name": "main", "opcodes": 12}], '
              '"unconstrained_functions": [{"name": "u", "opcodes": 5}]}]}')
        recs = parse_text(js, "auto")
        self.assertEqual(values(recs, "acir_opcodes", "toy/main"), [12.0])
        self.assertEqual(values(recs, "brillig_opcodes", "toy/u"), [5.0])

    def test_risc0(self):
        # format: risc0 host/prove_info.rs Display for SessionStats, through tracing::info! (RISC0_INFO=1);
        # "total cycles" / "user cycles" lines of older releases need verification
        txt = ("2026-01-01T00:00:00Z  INFO risc0_zkvm::host::server::session: execution time: 12.345ms\n"
               "2026-01-01T00:00:00Z  INFO risc0_zkvm::host::server::session: number of segments: 2\n"
               "2026-01-01T00:00:00Z  INFO risc0_zkvm::host::server::session: 2097152 total rows (31337 padding)\n"
               "INFO risc0_zkvm::host::server::exec::executor: total cycles: 2097152\n"
               "INFO risc0_zkvm::host::server::exec::executor: user cycles: 1500000\n")
        recs = parse_text(txt, "auto")
        self.assertAlmostEqual(values(recs, "time", "execute")[0], 0.012345)
        self.assertEqual(values(recs, "segments"), [2.0])
        self.assertEqual(values(recs, "rows"), [2097152.0])
        self.assertEqual(values(recs, "padding_rows"), [31337.0])
        self.assertEqual(values(recs, "cycles", "user"), [1500000.0])

    def test_sp1(self):
        # format: sp1 examples/fibonacci/script/src/main.rs println! strings; "Number of cycles:" needs verification;
        # the proving-time line is printed by the user's own script
        txt = ("executed program with 9172 cycles\nproving time: 12.5 s\ngenerated proof\n"
               "successfully generated and verified proof for the program!\n")
        recs = parse_text(txt, "auto")
        self.assertEqual(values(recs, "cycles"), [9172.0])
        self.assertEqual(values(recs, "time"), [12.5])
        self.assertEqual([r.value for r in recs if r.metric == "verify_status"], ["OK"])
        self.assertEqual(values(parse_text("Number of cycles: 42\n", "sp1"), "cycles"), [42.0])


if __name__ == "__main__":
    unittest.main()
