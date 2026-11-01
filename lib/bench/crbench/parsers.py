"""Regex-based, pluggable log-parser registry.

A *parser* turns raw tool output into a list of :class:`Record` objects with
normalised units (time -> seconds, memory/traffic -> bytes, security -> bits).

Shipped parsers (names used by ``crbench parse --parser NAME``):

``generic``           "time: 1.23 s", "Elapsed = 12 ms", "took 3.4sec", "RESULT name=... time=..."
``criterion``         Rust criterion (arkworks, halo2, plonky3, Binius, ...): ``time:   [1.1 ms 1.2 ms 1.3 ms]``
``gobench``           Go ``testing`` benchmarks (gnark): ``BenchmarkX-8  100  12345 ns/op``
``gbench``            Google Benchmark console (C++ provers, ICICLE benches): ``BM_X  123 ns  120 ns  1000``
``shell-time``        bash ``time`` (real/user/sys) and zsh ``time`` (``... 1.33 total``)
``snarkjs``           ``snarkjs r1cs info`` counts, ``snarkjs ... verify`` status, + shell ``time``
``rapidsnark``        rapidsnark prover / verifier timed with shell ``time`` (+ "time: X ms" lines)
``circom``            ``circom --r1cs`` summary: (non-)linear constraints, wires, inputs, labels
``gnark``             gnark zerolog lines: ``nbConstraints=N``, ``prover done ... took=X`` (ms)
``nargo-info``        ``nargo info`` table (ACIR / Brillig opcodes, circuit size) or ``--json``
``risc0``             RISC Zero session stats: execution time, segments, rows / cycles
``sp1``               SP1 scripts: ``executed program with N cycles``, ``Number of cycles: N``
``sat``               CaDiCaL / CryptoMiniSat / kissat: solve time + SAT/UNSAT status
``gnu-time``          ``/usr/bin/time -v``: wall clock and max RSS

Kept from the upstream toolkit (no ZK adapter uses them; their tests still run):
``helib``, ``openfhe``, ``lattice-estimator``, ``mpspdz``.

Format sources for the ZK parsers are listed next to each one; formats marked
"needs verification" were reconstructed from public logs, not from the tool's
documentation or source, and should be re-checked against a real run.

Register your own with :func:`register_parser` (see ``tests/test_parsers.py``).
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Callable, Iterable

TIME_UNITS = {
    "ns": 1e-9, "nanoseconds": 1e-9,
    "us": 1e-6, "µs": 1e-6, "μs": 1e-6, "microseconds": 1e-6,
    "ms": 1e-3, "milliseconds": 1e-3, "msec": 1e-3,
    "s": 1.0, "sec": 1.0, "secs": 1.0, "second": 1.0, "seconds": 1.0,
    "min": 60.0, "mins": 60.0, "minutes": 60.0,
    "h": 3600.0, "hours": 3600.0,
}
SIZE_UNITS = {
    "b": 1, "byte": 1, "bytes": 1,
    "kb": 1e3, "mb": 1e6, "gb": 1e9,
    "kib": 1024, "mib": 1024 ** 2, "gib": 1024 ** 3,
}
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
TU = r"(?:ns|us|µs|μs|ms|msec|milliseconds|microseconds|nanoseconds|seconds|second|secs|sec|s|minutes|mins|min|hours|h)"


def to_seconds(value: float, unit: str) -> float:
    u = unit.strip()
    factor = TIME_UNITS.get(u, TIME_UNITS.get(u.lower()))
    if factor is None:
        raise ValueError(f"unknown time unit {unit!r}")
    return float(value) * factor


def to_bytes(value: float, unit: str) -> float:
    u = unit.strip().lower()
    if u not in SIZE_UNITS:
        raise ValueError(f"unknown size unit {unit!r}")
    return float(value) * SIZE_UNITS[u]


@dataclass
class Record:
    metric: str            # e.g. "time", "rop_bits", "max_rss", "sat_status"
    value: float | str
    unit: str              # normalised unit: "s", "B", "bits", "" ...
    label: str = ""        # benchmark / attack / timer name if the log provides one
    line: int = 0          # 1-based line number in the source text
    raw: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


ParserFn = Callable[[str], list[Record]]


@dataclass
class Parser:
    name: str
    fn: ParserFn
    description: str = ""
    sniff: re.Pattern | None = None  # used by auto-detection


REGISTRY: dict[str, Parser] = {}


def register_parser(name: str, description: str = "", sniff: str | None = None):
    """Decorator: ``@register_parser("mytool", sniff=r"MyTool v\\d")``."""

    def deco(fn: ParserFn) -> ParserFn:
        REGISTRY[name] = Parser(name, fn, description, re.compile(sniff, re.M) if sniff else None)
        return fn

    return deco


def regex_parser(name: str, pattern: str, metric: str = "time", kind: str = "time",
                 description: str = "", sniff: str | None = None, flags=re.M | re.I) -> ParserFn:
    """Build and register a one-regex parser.

    ``pattern`` must have named groups ``value`` and ``unit`` (``unit`` optional ->
    seconds for time), and optionally ``label``.
    """
    rx = re.compile(pattern, flags)

    def fn(text: str) -> list[Record]:
        out = []
        for m in rx.finditer(text):
            gd = m.groupdict()
            v = float(gd["value"])
            unit = gd.get("unit") or ("s" if kind == "time" else "")
            if kind == "time":
                v, unit = to_seconds(v, unit), "s"
            elif kind == "size":
                v, unit = to_bytes(v, unit), "B"
            out.append(Record(metric, v, unit, (gd.get("label") or "").strip(),
                              text.count("\n", 0, m.start()) + 1, m.group(0).strip()))
        return out

    register_parser(name, description, sniff)(fn)
    return fn


def _lineno(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


# ---------------------------------------------------------------- generic
_GENERIC = re.compile(
    rf"^(?P<label>[^\n:=]*?)\b(?:time|elapsed|took|duration|runtime|latency)\b\s*(?:\([^)]*\))?\s*[:=]?\s*(?P<value>{NUM})\s*(?P<unit>{TU})\b",
    re.I | re.M,
)
_RESULT_KV = re.compile(r"^RESULT\b(?P<body>.*)$", re.M)


@register_parser("generic", "time: X s / elapsed = X ms / took X sec; RESULT k=v lines")
def parse_generic(text: str) -> list[Record]:
    out = []
    for m in _GENERIC.finditer(text):
        out.append(Record("time", to_seconds(float(m["value"]), m["unit"]), "s",
                          m["label"].strip(" \t-:>"), _lineno(text, m.start()), m.group(0).strip()))
    for m in _RESULT_KV.finditer(text):
        kv = dict(re.findall(r"(\w+)=(\S+)", m["body"]))
        label = kv.pop("name", kv.pop("label", ""))
        for k, v in kv.items():
            tm = re.fullmatch(rf"({NUM})({TU})?", v)
            if not tm:
                if k in ("status", "check", "verdict"):
                    out.append(Record(k, v, "", label, _lineno(text, m.start()), m.group(0)))
                continue
            val, unit = float(tm.group(1)), tm.group(2)
            if unit:
                out.append(Record(k, to_seconds(val, unit), "s", label, _lineno(text, m.start()), m.group(0)))
            else:
                out.append(Record(k, val, "", label, _lineno(text, m.start()), m.group(0)))
    return out


# ---------------------------------------------------------------- criterion (Rust)
_CRIT = re.compile(
    rf"^(?P<label>\S[^\n]*?)?\s*\n?\s*time:\s+\[(?P<lo>{NUM})\s*(?P<ulo>\S+)\s+(?P<mid>{NUM})\s*(?P<umid>\S+)\s+(?P<hi>{NUM})\s*(?P<uhi>[^\]\s]+)\s*\]",
    re.M,
)


@register_parser("criterion", "Rust criterion: time: [lo mid hi]; reports mid (point estimate) plus lo/hi",
                 sniff=r"time:\s+\[")
def parse_criterion(text: str) -> list[Record]:
    out = []
    for m in _CRIT.finditer(text):
        label = (m["label"] or "").strip()
        ln = _lineno(text, m.start("lo"))
        out.append(Record("time", to_seconds(float(m["mid"]), m["umid"]), "s", label, ln, m.group(0).strip()))
        out.append(Record("time_lo", to_seconds(float(m["lo"]), m["ulo"]), "s", label, ln))
        out.append(Record("time_hi", to_seconds(float(m["hi"]), m["uhi"]), "s", label, ln))
    return out


# ---------------------------------------------------------------- go test -bench (gnark)
_GOB = re.compile(rf"^(?P<label>Benchmark\S+?)(?:-\d+)?\s+(?P<iters>\d+)\s+(?P<value>{NUM})\s+ns/op(?P<rest>.*)$", re.M)


@register_parser("gobench", "go test -bench: BenchmarkX-8  N  T ns/op [B/op allocs/op]", sniff=r"^Benchmark\S+\s+\d+\s+\S+\s+ns/op")
def parse_gobench(text: str) -> list[Record]:
    out = []
    for m in _GOB.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("time", float(m["value"]) * 1e-9, "s", m["label"], ln, m.group(0).strip()))
        bm = re.search(rf"({NUM})\s+B/op", m["rest"])
        if bm:
            out.append(Record("alloc", float(bm.group(1)), "B", m["label"], ln))
    return out


# ---------------------------------------------------------------- google benchmark
_GB = re.compile(rf"^(?P<label>BM_\S+|\S+/\S+)\s+(?P<wall>{NUM})\s+(?P<uw>ns|us|ms|s)\s+(?P<cpu>{NUM})\s+(?P<uc>ns|us|ms|s)\s+(?P<iters>\d+)", re.M)


@register_parser("gbench", "Google Benchmark console: name  Time unit  CPU unit  Iterations", sniff=r"^-{20,}\s*\n?Benchmark\s+Time\s+CPU")
def parse_gbench(text: str) -> list[Record]:
    out = []
    for m in _GB.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("time", to_seconds(float(m["wall"]), m["uw"]), "s", m["label"], ln, m.group(0).strip()))
        out.append(Record("cpu_time", to_seconds(float(m["cpu"]), m["uc"]), "s", m["label"], ln))
    return out


# ---------------------------------------------------------------- HElib timers
_HELIB = re.compile(rf"^\s*(?P<label>[A-Za-z_][\w:<>~]*)\s*:\s*(?P<total>{NUM})\s*/\s*(?P<count>\d+)\s*=\s*(?P<avg>{NUM})", re.M)


@register_parser("helib", "HElib printAllTimers: name: total / count = avg  (seconds)", sniff=r":\s*\S+\s*/\s*\d+\s*=\s*\S+\s+\[")
def parse_helib(text: str) -> list[Record]:
    out = []
    for m in _HELIB.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("time_total", float(m["total"]), "s", m["label"], ln, m.group(0).strip()))
        out.append(Record("time", float(m["avg"]), "s", m["label"], ln))
        out.append(Record("count", float(m["count"]), "", m["label"], ln))
    return out


# ---------------------------------------------------------------- OpenFHE example style
_OFHE = re.compile(rf"^(?P<label>[^\n:]*?)\s*(?:time|took)\s*(?:\[\s*(?P<bunit>[a-zµμ]+)\s*\])?\s*[:=]?\s*(?P<value>{NUM})\s*(?P<unit>{TU})?\b", re.M | re.I)


@register_parser("openfhe", "OpenFHE examples: '<Label> time: 12.3 ms', 'Bootstrapping time [ms]: 123'")
def parse_openfhe(text: str) -> list[Record]:
    out = []
    for m in _OFHE.finditer(text):
        unit = m["unit"] or m["bunit"]
        if not unit:
            continue
        out.append(Record("time", to_seconds(float(m["value"]), unit), "s", m["label"].strip(" -:"), _lineno(text, m.start()), m.group(0).strip()))
    return out


# ---------------------------------------------------------------- lattice-estimator
_LE = re.compile(rf"^\s*(?P<label>[\w\-]+)\s*::\s*rop:\s*[≈~]?\s*2\^(?P<value>{NUM})(?P<rest>[^\n]*)$", re.M)
_BETA = re.compile(r"(?:β|beta):\s*(\d+)")


@register_parser("lattice-estimator", "LWE.estimate output lines 'attack :: rop: ≈2^X, ... β: B'; value = log2(rop) bits", sniff=r"::\s*rop:")
def parse_lattice_estimator(text: str) -> list[Record]:
    out = []
    for m in _LE.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("rop_bits", float(m["value"]), "bits", m["label"], ln, m.group(0).strip()))
        b = _BETA.search(m["rest"])
        if b:
            out.append(Record("beta", float(b.group(1)), "", m["label"], ln))
    if out:
        best = min((r for r in out if r.metric == "rop_bits"), key=lambda r: r.value)
        out.append(Record("security_bits", best.value, "bits", f"min:{best.label}", best.line))
    return out


# ---------------------------------------------------------------- shell time (bash / zsh)
# bash: "real\t0m1.234s" / "user ..." / "sys ..."; zsh: "cmd  1.10s user 0.10s system 99% cpu 1.334 total"
_BASH_T = re.compile(r"^(?P<label>real|user|sys)\s+(?:(?P<m>\d+)m)?(?P<s>[\d.]+)s\s*$", re.M)
_ZSH_T = re.compile(rf"(?P<user>{NUM})s user\s+(?P<sys>{NUM})s system\s+\S+ cpu\s+(?:(?P<m>\d+):)?(?P<total>{NUM}) total", re.M)


@register_parser("shell-time", "bash 'real 0m1.234s' / zsh '... 1.334 total' (label real/user/sys)",
                 sniff=r"^real\s+\d+m[\d.]+s\s*$|\d s user .* total$")
def parse_shell_time(text: str) -> list[Record]:
    out = []
    for m in _BASH_T.finditer(text):
        out.append(Record("time", 60 * float(m["m"] or 0) + float(m["s"]), "s", m["label"],
                          _lineno(text, m.start()), m.group(0).strip()))
    for m in _ZSH_T.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("time", 60 * float(m["m"] or 0) + float(m["total"]), "s", "real", ln, m.group(0).strip()))
        out.append(Record("time", float(m["user"]), "s", "user", ln))
        out.append(Record("time", float(m["sys"]), "s", "sys", ln))
    return out


# ---------------------------------------------------------------- snarkjs
# Source: snarkjs README (r1cs info example: "[INFO]  snarkJS: # of Constraints: 1000"). The verify line
# "snarkJS: OK!" / "snarkJS: Invalid proof" -- needs verification (the README only says "OK" is printed).
# snarkjs prints no timings itself: time it with the shell and keep the time output in the same log.
_SNARK_INFO = re.compile(r"snarkJS:\s*# of (?P<what>Wires|Constraints|Private Inputs|Public Inputs|Outputs|Labels):\s*(?P<value>\d+)", re.M)
_SNARK_OK = re.compile(r"snarkJS:\s*(?P<st>OK!?|Invalid proof)", re.M)


@register_parser("snarkjs", "snarkjs r1cs info counts (constraints, wires, ...), verify OK / Invalid proof, shell time",
                 sniff=r"snarkJS:")
def parse_snarkjs(text: str) -> list[Record]:
    out = []
    for m in _SNARK_INFO.finditer(text):
        metric = m["what"].lower().replace(" ", "_")
        out.append(Record(metric, float(m["value"]), "", "r1cs", _lineno(text, m.start()), m.group(0).strip()))
    for m in _SNARK_OK.finditer(text):
        out.append(Record("verify_status", "OK" if m["st"].startswith("OK") else "INVALID", "", "verify",
                          _lineno(text, m.start()), m.group(0).strip()))
    return out + parse_shell_time(text)


# ---------------------------------------------------------------- rapidsnark
# rapidsnark's prover / verifier binaries print no timing by default (needs verification for builds with
# their optional logging): time them with the shell; "time: X ms"-style lines are picked up as well.
@register_parser("rapidsnark", "rapidsnark prover/verifier: shell time (+ generic 'time: X ms' lines)")
def parse_rapidsnark(text: str) -> list[Record]:
    out = parse_shell_time(text)
    out += [r for r in parse_generic(text) if r.metric == "time"]
    return out


# ---------------------------------------------------------------- circom
# Format: circom 2.x compile summary ("template instances: N", "non-linear constraints: N", "linear constraints: N",
# "public inputs: N", "private inputs: N", "public outputs: N", "wires: N", "labels: N", "Everything went okay").
# needs verification: reconstructed from public build logs and tutorials; the official docs show no sample output.
_CIRCOM = re.compile(r"^\s*(?P<what>template instances|non-linear constraints|linear constraints|public inputs|"
                     r"private inputs|public outputs|private outputs|wires|labels):\s*(?P<value>\d+)\s*$", re.M | re.I)


@register_parser("circom", "circom --r1cs summary: non-linear / linear constraints (+ total), wires, inputs, labels",
                 sniff=r"^\s*non-linear constraints:\s*\d+")
def parse_circom(text: str) -> list[Record]:
    out, total = [], {}
    for m in _CIRCOM.finditer(text):
        metric = m["what"].lower().replace("-", "_").replace(" ", "_")
        out.append(Record(metric, float(m["value"]), "", "circom", _lineno(text, m.start()), m.group(0).strip()))
        if metric in ("non_linear_constraints", "linear_constraints"):
            total[metric] = float(m["value"])
    if total:
        out.append(Record("constraints", sum(total.values()), "", "circom"))
    return out


# ---------------------------------------------------------------- gnark
# Source: gnark logger/logger.go (zerolog ConsoleWriter, time format 15:04:05) and backend/groth16/*/prove.go
# (log.Debug().Dur("took", ...).Msg("prover done"), logger carrying nbConstraints). zerolog's default duration
# unit is milliseconds (float). Example: "10:21:09 DBG prover done backend=groth16 curve=bn254 nbConstraints=3 took=1.23".
_GNARK = re.compile(r"^(?:\S+\s+)?(?:DBG|INF|WRN)\s+(?P<msg>[^=\n]*?)\s+(?P<kv>\w+=\S+(?:\s+\w+=\S+)*)\s*$", re.M)


@register_parser("gnark", "gnark zerolog lines: nbConstraints=N; '<phase> done ... took=X' (ms)",
                 sniff=r"nbConstraints=\d+")
def parse_gnark(text: str) -> list[Record]:
    out = []
    for m in _GNARK.finditer(text):
        kv = dict(re.findall(r"(\w+)=(\S+)", m["kv"]))
        ln, msg = _lineno(text, m.start()), m["msg"].strip()
        label = msg.replace(" done", "") if msg.endswith(" done") else msg
        if "nbConstraints" in kv:
            out.append(Record("constraints", float(kv["nbConstraints"]), "", label, ln, m.group(0).strip()))
        if "took" in kv and re.fullmatch(NUM, kv["took"]):
            out.append(Record("time", float(kv["took"]) * 1e-3, "s", label, ln, m.group(0).strip()))
    return out


# ---------------------------------------------------------------- nargo info
# Source: noir tooling/noirc_artifacts_info (table header "Package | Function | ACIR Opcodes | Brillig Opcodes";
# --json: {"programs": [{"package_name", "functions": [{"name", "opcodes"}], "unconstrained_functions": [...]}]}).
# Older nargo versions add "Expression Width" / "Backend Circuit Size" columns: the table is read by header.
_NARGO_COLS = {"acir opcodes": "acir_opcodes", "brillig opcodes": "brillig_opcodes",
               "backend circuit size": "circuit_size", "circuit size": "circuit_size"}


@register_parser("nargo-info", "nargo info table (ACIR / Brillig opcodes, backend circuit size) or --json report",
                 sniff=r"ACIR Opcodes|\"programs\"\s*:")
def parse_nargo_info(text: str) -> list[Record]:
    out: list[Record] = []
    stripped = text.strip()
    if stripped.startswith("{"):
        import json
        try:
            rep = json.loads(stripped)
        except ValueError:
            rep = None
        if isinstance(rep, dict):
            for prog in rep.get("programs", []):
                pkg = prog.get("package_name", "")
                for kind, metric in (("functions", "acir_opcodes"), ("unconstrained_functions", "brillig_opcodes")):
                    for fn in prog.get(kind, []):
                        out.append(Record(metric, float(fn.get("opcodes", 0)), "", f"{pkg}/{fn.get('name', '')}"))
            return out
    header = None
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any(c.lower() in _NARGO_COLS for c in cells):
            header = [c.lower() for c in cells]
            continue
        if header is None or len(cells) != len(header):
            continue
        label = "/".join(cells[k] for k, h in enumerate(header) if h in ("package", "function"))
        for k, h in enumerate(header):
            if h in _NARGO_COLS and re.fullmatch(r"\d+", cells[k].replace(",", "")):
                out.append(Record(_NARGO_COLS[h], float(cells[k].replace(",", "")), "", label, i, line.strip()))
    return out


# ---------------------------------------------------------------- RISC Zero
# Source: risc0 risc0/zkvm/src/host/prove_info.rs, Display for SessionStats ("execution time: {:?}",
# "number of segments: {}", "{} total rows ({} padding)"), logged line by line through tracing::info! when
# RISC0_INFO is set. Older releases printed "total cycles: N" / "user cycles: N" (needs verification).
_R0_EXEC = re.compile(rf"execution time:\s*(?P<value>{NUM})\s*(?P<unit>{TU})", re.M)
_R0_SEG = re.compile(r"number of segments:\s*(?P<value>\d+)", re.M)
_R0_ROWS = re.compile(r"(?P<rows>\d+) total rows \((?P<pad>\d+) padding\)", re.M)
_R0_CYC = re.compile(r"(?P<kind>total|user) cycles:\s*(?P<value>\d+)", re.M)


@register_parser("risc0", "RISC Zero session stats: execution time, segments, total rows (padding), total/user cycles",
                 sniff=r"number of segments:\s*\d+")
def parse_risc0(text: str) -> list[Record]:
    out = []
    for m in _R0_EXEC.finditer(text):
        out.append(Record("time", to_seconds(float(m["value"]), m["unit"]), "s", "execute", _lineno(text, m.start()), m.group(0)))
    for m in _R0_SEG.finditer(text):
        out.append(Record("segments", float(m["value"]), "", "session", _lineno(text, m.start()), m.group(0)))
    for m in _R0_ROWS.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("rows", float(m["rows"]), "", "session", ln, m.group(0)))
        out.append(Record("padding_rows", float(m["pad"]), "", "session", ln))
    for m in _R0_CYC.finditer(text):
        out.append(Record("cycles", float(m["value"]), "", m["kind"], _lineno(text, m.start()), m.group(0)))
    return out


# ---------------------------------------------------------------- SP1
# Source: sp1 examples/fibonacci/script/src/main.rs ("executed program with {} cycles", "generated proof",
# "successfully generated and verified proof for the program!"). "Number of cycles: N" appears in other
# example scripts (needs verification). Proving time is whatever the script prints: generic time lines are kept.
_SP1_CYC = re.compile(r"executed program with (?P<a>\d+) cycles|Number of cycles:\s*(?P<b>\d+)", re.M | re.I)
_SP1_OK = re.compile(r"successfully generated and verified proof", re.I)


@register_parser("sp1", "SP1 scripts: 'executed program with N cycles' / 'Number of cycles: N', verify status, time lines",
                 sniff=r"executed program with \d+ cycles|Number of cycles:")
def parse_sp1(text: str) -> list[Record]:
    out = []
    for m in _SP1_CYC.finditer(text):
        out.append(Record("cycles", float(m["a"] or m["b"]), "", "execute", _lineno(text, m.start()), m.group(0)))
    for m in _SP1_OK.finditer(text):
        out.append(Record("verify_status", "OK", "", "verify", _lineno(text, m.start()), m.group(0)))
    out += [r for r in parse_generic(text) if r.metric == "time"]
    return out


# ---------------------------------------------------------------- SAT solvers
_SAT_T = re.compile(
    rf"^c\s+(?:total process time since initialization|Total time(?: \(this thread\))?|process-time|total real time since initialization)\s*:?\s*(?P<value>{NUM})\s*(?P<unit>seconds|s)?",
    re.M | re.I,
)
_SAT_S = re.compile(r"^s\s+(SATISFIABLE|UNSATISFIABLE|UNKNOWN)\s*$", re.M)


@register_parser("sat", "CaDiCaL/CryptoMiniSat/kissat 'c total process time ...' + 's SATISFIABLE'", sniff=r"^s\s+(?:UN)?SATISFIABLE")
def parse_sat(text: str) -> list[Record]:
    out = [Record("time", float(m["value"]), "s", "solver", _lineno(text, m.start()), m.group(0).strip()) for m in _SAT_T.finditer(text)]
    for m in _SAT_S.finditer(text):
        out.append(Record("sat_status", m.group(1), "", "solver", _lineno(text, m.start()), m.group(0).strip()))
    return out


# ---------------------------------------------------------------- MP-SPDZ
_MPS_T = re.compile(rf"^Time\s*=\s*(?P<value>{NUM})\s*seconds", re.M)
_MPS_D = re.compile(rf"^Data sent\s*=\s*(?P<value>{NUM})\s*(?P<unit>[KMG]?B)(?:\s*in\s*~?(?P<rounds>\d+)\s*rounds)?", re.M)
_MPS_G = re.compile(rf"^Global data sent\s*=\s*(?P<value>{NUM})\s*(?P<unit>[KMG]?B)", re.M)


@register_parser("mpspdz", "MP-SPDZ: Time = X seconds; Data sent = X MB in ~R rounds; Global data sent", sniff=r"^Data sent\s*=")
def parse_mpspdz(text: str) -> list[Record]:
    out = []
    for m in _MPS_T.finditer(text):
        out.append(Record("time", float(m["value"]), "s", "party", _lineno(text, m.start()), m.group(0).strip()))
    for m in _MPS_D.finditer(text):
        ln = _lineno(text, m.start())
        out.append(Record("comm", to_bytes(float(m["value"]), m["unit"]), "B", "party", ln, m.group(0).strip()))
        if m["rounds"]:
            out.append(Record("rounds", float(m["rounds"]), "", "party", ln))
    for m in _MPS_G.finditer(text):
        out.append(Record("comm_global", to_bytes(float(m["value"]), m["unit"]), "B", "all", _lineno(text, m.start()), m.group(0).strip()))
    return out


# ---------------------------------------------------------------- GNU time -v
_GT_W = re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(?P<value>[\d:.]+)")
_GT_M = re.compile(r"Maximum resident set size \(kbytes\):\s*(?P<value>\d+)")


@register_parser("gnu-time", "/usr/bin/time -v wall clock + max RSS", sniff=r"Maximum resident set size")
def parse_gnu_time(text: str) -> list[Record]:
    out = []
    for m in _GT_W.finditer(text):
        parts = [float(p) for p in m["value"].split(":")]
        secs = 0.0
        for p in parts:
            secs = secs * 60 + p
        out.append(Record("time", secs, "s", "wall", _lineno(text, m.start()), m.group(0).strip()))
    for m in _GT_M.finditer(text):
        out.append(Record("max_rss", float(m["value"]) * 1024, "B", "process", _lineno(text, m.start()), m.group(0).strip()))
    return out


# ---------------------------------------------------------------- dispatch
# a parser that already returns another parser's records (avoid duplicates in auto mode)
SUBSUMES = {"snarkjs": {"shell-time"}}


def detect(text: str) -> list[str]:
    """Return names of parsers whose sniff pattern matches ``text`` (most specific first)."""
    hits = [p.name for p in REGISTRY.values() if p.sniff is not None and p.sniff.search(text)]
    covered = set().union(*(SUBSUMES.get(h, set()) for h in hits)) if hits else set()
    hits = [h for h in hits if h not in covered]
    return hits or ["generic"]


def parse_text(text: str, parser: str | Iterable[str] = "auto") -> list[Record]:
    names = detect(text) if parser == "auto" else ([parser] if isinstance(parser, str) else list(parser))
    out: list[Record] = []
    for n in names:
        if n not in REGISTRY:
            raise KeyError(f"unknown parser {n!r}; known: {sorted(REGISTRY)}")
        out.extend(REGISTRY[n].fn(text))
    return out


def parse_file(path: str, parser: str = "auto") -> list[Record]:
    with open(path, encoding="utf-8", errors="replace") as f:
        return parse_text(f.read(), parser)


def values(records: Iterable[Record], metric: str = "time", label: str | None = None) -> list[float]:
    return [float(r.value) for r in records if r.metric == metric and (label is None or r.label == label)]


if __name__ == "__main__":
    demo = "[INFO]  snarkJS: # of Constraints: 1000\nreal\t0m1.234s\n"   # synthetic
    for r in parse_text(demo, ["snarkjs"]):
        print(r)
