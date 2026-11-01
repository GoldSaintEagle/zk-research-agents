#!/usr/bin/env python3
"""polite_http.py -- one rate-limited, caching HTTP client for every script that queries
IACR ePrint (or its mirror), DBLP, Crossref, DataCite or the Wayback API.

Why one module: eprint.iacr.org bans IP addresses that fetch too fast, DBLP serves bot
challenges and Crossref drops connections under load.  Every script in this repo that
talks to these services goes through `PoliteClient`, so the limits below hold everywhere.
It lives next to eprint_search.py because install.sh copies whole skill folders (lib/ is
not installed into user projects); bib-verify imports it from ../../eprint-search/scripts.

Rules enforced (defaults are conservative; override with arguments or environment):

  min interval   >= 3 s between two requests to the same host      ZKRA_HTTP_MIN_INTERVAL
                 (the last request time per host is kept in a locked stamp file in the
                 cache directory, so consecutive or parallel runs are spaced too)
  retries        429 / 503 -> honour Retry-After (seconds or HTTP date), else exponential
                 backoff min_interval * 2^k; at most 3 retries         ZKRA_HTTP_MAX_RETRIES
                 a Retry-After longer than 300 s is not waited out: the request fails
  budget         at most 300 network requests per client (one script run); the next one
                 raises RequestBudgetExceeded and the caller stops   ZKRA_HTTP_MAX_REQUESTS
  cache          successful (200) answers are cached on disk for 7 days, keyed by URL;
                 a cache hit makes no request and uses no budget      ZKRA_HTTP_CACHE_TTL (s)
                 directory .cache/eprint/ under the working directory ZKRA_HTTP_CACHE_DIR
                 (git-ignored: .cache/ is in .gitignore)              ZKRA_HTTP_NO_CACHE=1
  connections    a dropped connection or timeout is retried once (after 2 * min interval)
  User-Agent     names the tool and the repository; never a browser string.

Redirects are never followed silently: a 3xx comes back as a Response with `.location`
unless follow_redirects=True (each hop is a rate-limited request).  ePrint answers a
banned client with a 302, and the caller must be able to see that.

    python3 polite_http.py --selftest      # offline: fake transport, fake clock
"""
from __future__ import annotations

import email.utils
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

try:
    import fcntl          # POSIX: lets parallel runs share the per-host spacing
except ImportError:       # pragma: no cover - Windows: spacing per process only
    fcntl = None

REPO_URL = "https://github.com/FranklinZty/zk-research-agents"
UA = f"zk-research-agents/0.2 (literature tools, rate-limited; +{REPO_URL})"

DEFAULT_MIN_INTERVAL = 3.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_REQUESTS = 300
DEFAULT_CACHE_TTL = 7 * 24 * 3600
DEFAULT_CACHE_DIR = os.path.join(".cache", "eprint")
MAX_RETRY_AFTER = 300.0
RETRY_STATUSES = (429, 503)


class RequestBudgetExceeded(RuntimeError):
    """The per-run request cap was reached; stop and tell the user."""


class HTTPStatusError(OSError):
    """A non-2xx, non-3xx answer (after retries).  `.status`, `.response`."""

    def __init__(self, response: "Response"):
        super().__init__(f"HTTP {response.status} for {response.url}")
        self.status = response.status
        self.response = response


@dataclass
class Response:
    url: str
    status: int
    headers: dict = field(default_factory=dict)   # lower-cased names
    body: bytes = b""
    from_cache: bool = False

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    @property
    def location(self) -> str | None:
        loc = self.headers.get("location")
        return urllib.parse.urljoin(self.url, loc) if loc else None

    def json(self):
        return json.loads(self.text)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def urllib_transport(url: str, headers: dict, timeout: float, method: str = "GET") -> Response:
    """The real network call: one request, no redirect following.  Connection errors raise
    URLError/TimeoutError/OSError; HTTP error statuses are returned, not raised."""
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            return Response(url, r.status, {k.lower(): v for k, v in r.headers.items()},
                            r.read() if method != "HEAD" else b"")
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read() if method != "HEAD" else b""
        except OSError:
            pass
        return Response(url, e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, body)


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def parse_retry_after(value: str | None, now: float) -> float | None:
    """Seconds to wait from a Retry-After header (delta-seconds or HTTP date), or None."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = email.utils.parsedate_to_datetime(value).timestamp()
    except (TypeError, ValueError, IndexError):
        return None
    return max(0.0, when - now)


class PoliteClient:
    def __init__(self, min_interval: float | None = None, max_retries: int | None = None,
                 max_requests: int | None = None, cache_dir: str | None = None,
                 cache_ttl: float | None = None, use_cache: bool | None = None,
                 timeout: float = 25.0, transport=None, clock=time.time, sleep=time.sleep,
                 log=None):
        self.min_interval = (min_interval if min_interval is not None
                             else _env_float("ZKRA_HTTP_MIN_INTERVAL", DEFAULT_MIN_INTERVAL))
        self.max_retries = int(max_retries if max_retries is not None
                               else _env_float("ZKRA_HTTP_MAX_RETRIES", DEFAULT_MAX_RETRIES))
        self.max_requests = int(max_requests if max_requests is not None
                                else _env_float("ZKRA_HTTP_MAX_REQUESTS", DEFAULT_MAX_REQUESTS))
        self.cache_dir = cache_dir or os.environ.get("ZKRA_HTTP_CACHE_DIR") or DEFAULT_CACHE_DIR
        self.cache_ttl = cache_ttl if cache_ttl is not None else _env_float("ZKRA_HTTP_CACHE_TTL",
                                                                            DEFAULT_CACHE_TTL)
        self.use_cache = (use_cache if use_cache is not None
                          else os.environ.get("ZKRA_HTTP_NO_CACHE", "") not in ("1", "true", "yes"))
        self.timeout = timeout
        self.transport = transport or urllib_transport
        self.clock, self.sleep = clock, sleep
        self.log = log or (lambda msg: print(msg, file=sys.stderr))
        self.requests = 0          # network requests made (cache hits excluded)
        self.cache_hits = 0
        self._last: dict[str, float] = {}

    # -- spacing ----------------------------------------------------------------
    def _stamp_path(self, host: str) -> str:
        return os.path.join(self.cache_dir, "_last", host.replace(":", "_"))

    def _last_request(self, host: str) -> float:
        last = self._last.get(host, 0.0)
        if self.use_cache:      # other processes (parallel verifiers) write the same stamp file
            try:
                with open(self._stamp_path(host), encoding="ascii") as fh:
                    last = max(last, float(fh.read().strip() or 0))
            except (OSError, ValueError):
                pass
        return last

    def throttle(self, url: str) -> None:
        """Wait until min_interval has passed since the last request to this host (in this
        process or, through a locked stamp file in the cache folder, in any other)."""
        host = urllib.parse.urlsplit(url).netloc.lower()
        lock = None
        if self.use_cache and fcntl is not None:
            try:
                os.makedirs(os.path.dirname(self._stamp_path(host)), exist_ok=True)
                lock = open(self._stamp_path(host) + ".lock", "a")
                fcntl.flock(lock, fcntl.LOCK_EX)
            except OSError:
                lock = None
        try:
            wait = self._last_request(host) + self.min_interval - self.clock()
            if wait > 0:
                self.sleep(wait)
            self._last[host] = self.clock()
            if self.use_cache:
                try:
                    os.makedirs(os.path.dirname(self._stamp_path(host)), exist_ok=True)
                    with open(self._stamp_path(host), "w", encoding="ascii") as fh:
                        fh.write(f"{self._last[host]:.3f}")
                except OSError:
                    pass
        finally:
            if lock is not None:
                fcntl.flock(lock, fcntl.LOCK_UN)
                lock.close()

    def _count(self, url: str) -> None:
        if self.requests >= self.max_requests:
            raise RequestBudgetExceeded(
                f"request budget of {self.max_requests} reached before {url}; stop here, re-run later "
                f"(finished lookups are cached) or raise the cap (--max-requests / ZKRA_HTTP_MAX_REQUESTS)")
        self.requests += 1

    # -- cache ------------------------------------------------------------------
    def _cache_path(self, url: str) -> str:
        host = urllib.parse.urlsplit(url).netloc.lower().replace(":", "_")
        return os.path.join(self.cache_dir, host, hashlib.sha256(url.encode()).hexdigest() + ".json")

    def _cache_get(self, url: str) -> Response | None:
        if not self.use_cache:
            return None
        try:
            with open(self._cache_path(url), encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            return None
        if d.get("url") != url or self.clock() - d.get("fetched", 0) > self.cache_ttl:
            return None
        self.cache_hits += 1
        return Response(url, d["status"], d.get("headers", {}), d["body"].encode("utf-8"), from_cache=True)

    def _cache_put(self, r: Response) -> None:
        if not self.use_cache or r.status != 200:
            return
        path = self._cache_path(r.url)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            keep = {k: v for k, v in r.headers.items() if k in ("content-type", "link", "cache-control")}
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"url": r.url, "status": r.status, "headers": keep, "fetched": self.clock(),
                           "body": r.text}, fh)
        except OSError:
            pass

    # -- requests ---------------------------------------------------------------
    def request(self, url: str, method: str = "GET", cache: bool = True) -> Response:
        """One logical request: cache, spacing, budget, 429/503 retries.  Returns any
        status except a retry status that never cleared (then HTTPStatusError)."""
        if method == "GET" and cache:
            hit = self._cache_get(url)
            if hit is not None:
                return hit
        headers = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.5"}
        attempt, conn_failures = 0, 0
        while True:
            self._count(url)
            self.throttle(url)
            try:
                r = self.transport(url, headers, self.timeout, method)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                # dropped TLS connections (seen with Crossref under load): one retry, then raise
                if conn_failures >= 1:
                    raise
                conn_failures += 1
                self.log(f"note: {urllib.parse.urlsplit(url).netloc}: {exc}; one retry in "
                         f"{2 * self.min_interval:.0f} s")
                self.sleep(2 * self.min_interval)
                continue
            if r.status not in RETRY_STATUSES:
                if method == "GET" and cache:
                    self._cache_put(r)
                return r
            if attempt >= self.max_retries:
                raise HTTPStatusError(r)
            wait = parse_retry_after(r.headers.get("retry-after"), self.clock())
            if wait is None:
                wait = self.min_interval * (2 ** attempt)
            if wait > MAX_RETRY_AFTER:
                self.log(f"note: {urllib.parse.urlsplit(url).netloc} asks to wait {wait:.0f} s; not waiting")
                raise HTTPStatusError(r)
            self.log(f"note: HTTP {r.status} from {urllib.parse.urlsplit(url).netloc}; "
                     f"retry {attempt + 1}/{self.max_retries} in {wait:.0f} s")
            self.sleep(wait)
            attempt += 1

    def get(self, url: str, follow_redirects: bool = False, cache: bool = True) -> Response:
        r = self.request(url, cache=cache)
        hops = 0
        while follow_redirects and 300 <= r.status < 400 and r.location and hops < 5:
            r, hops = self.request(r.location, cache=cache), hops + 1
        return r

    def get_text(self, url: str, follow_redirects: bool = True) -> str:
        """Body of a 2xx answer; HTTPStatusError otherwise (urllib-like behaviour)."""
        r = self.get(url, follow_redirects=follow_redirects)
        if not 200 <= r.status < 300:
            raise HTTPStatusError(r)
        return r.text


_DEFAULT: PoliteClient | None = None


def default_client() -> PoliteClient:
    """The process-wide client (one budget, one spacing table per run)."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = PoliteClient()
    return _DEFAULT


def set_default_client(client: PoliteClient) -> None:
    global _DEFAULT
    _DEFAULT = client


def add_cli_args(ap) -> None:
    """The shared rate-limit options, for argparse parsers of the calling scripts."""
    g = ap.add_argument_group("rate limits (shared with every ePrint/DBLP/Crossref script)")
    g.add_argument("--min-interval", type=float, default=None,
                   help=f"seconds between two requests to one host (default {DEFAULT_MIN_INTERVAL:g}, "
                        "env ZKRA_HTTP_MIN_INTERVAL)")
    g.add_argument("--max-requests", type=int, default=None,
                   help=f"network requests allowed in this run (default {DEFAULT_MAX_REQUESTS}, "
                        "env ZKRA_HTTP_MAX_REQUESTS)")
    g.add_argument("--cache-dir", default=None, help=f"answer cache (default {DEFAULT_CACHE_DIR})")
    g.add_argument("--no-cache", action="store_true", help="neither read nor write the cache")


def client_from_args(a) -> PoliteClient:
    c = PoliteClient(min_interval=a.min_interval, max_requests=a.max_requests, cache_dir=a.cache_dir,
                     use_cache=False if a.no_cache else None)
    set_default_client(c)
    return c


# ---------------------------------------------------------------- selftest ---

class FakeNet:
    """Scripted transport plus a fake clock; records (time, url) of every request."""

    def __init__(self, routes):
        self.routes = routes        # url (or prefix ending in '*') -> list of Responses / exceptions
        self.now = 1_000_000.0
        self.calls: list[tuple[float, str]] = []

    def clock(self):
        return self.now

    def sleep(self, s):
        self.now += s

    def __call__(self, url, headers, timeout, method="GET"):
        assert "Mozilla" not in headers["User-Agent"] and REPO_URL in headers["User-Agent"]
        self.calls.append((self.now, url))
        for key, seq in self.routes.items():
            if url == key or (key.endswith("*") and url.startswith(key[:-1])):
                item = seq.pop(0) if len(seq) > 1 else seq[0]
                if isinstance(item, BaseException):
                    raise item
                return Response(url, item.status, dict(item.headers), item.body)
        raise urllib.error.URLError(f"no fake route for {url}")


def selftest() -> int:
    import tempfile
    ok = Response("", 200, {"content-type": "text/plain"}, b"hello")
    with tempfile.TemporaryDirectory() as tmp:
        # 1. spacing per host: three requests to one host are >= 3 s apart; another host is not delayed
        net = FakeNet({"https://a.example/*": [ok], "https://b.example/*": [ok]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, cache_dir=tmp + "/c1",
                         min_interval=3.0, log=lambda m: None)
        for i in range(3):
            c.get(f"https://a.example/{i}")
        c.get("https://b.example/x")
        ta = [t for t, u in net.calls if "a.example" in u]
        assert all(t2 - t1 >= 3.0 for t1, t2 in zip(ta, ta[1:])), ta
        assert net.calls[-1][0] == ta[-1], "a different host must not wait"
        # 2. cache: same URL again -> no request, no budget
        n = len(net.calls)
        r = c.get("https://a.example/0")
        assert r.from_cache and r.text == "hello" and len(net.calls) == n and c.requests == 4
        # spacing survives a new client (stamp file in the cache dir)
        c2 = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, cache_dir=tmp + "/c1",
                          min_interval=3.0, log=lambda m: None)
        t0 = net.now
        c2.get("https://a.example/new")
        assert net.calls[-1][0] >= ta[-1] + 3.0 and net.now >= t0
        # expired cache entries are fetched again
        net.now += DEFAULT_CACHE_TTL + 1
        assert not c2.get("https://a.example/0").from_cache
        # 3. 429 with Retry-After: 7, then 503 without it (backoff 3 * 2^1), then 200
        logs = []
        net = FakeNet({"https://r.example/q": [Response("", 429, {"retry-after": "7"}),
                                               Response("", 503), ok]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False,
                         min_interval=3.0, log=logs.append)
        assert c.get("https://r.example/q").status == 200
        t = [x for x, _ in net.calls]
        assert t[1] - t[0] >= 7.0 and t[2] - t[1] >= 6.0, t
        assert len(logs) == 2 and "retry 1/3" in logs[0] and c.requests == 3
        # Retry-After as an HTTP date
        assert abs(parse_retry_after(email.utils.formatdate(net.now + 42, usegmt=True), net.now) - 42) < 1.5
        # max retries: a host that always answers 429 fails after 1 + 3 attempts
        net = FakeNet({"https://r.example/q": [Response("", 429)]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False,
                         min_interval=1.0, log=lambda m: None)
        try:
            c.get("https://r.example/q")
            raise AssertionError("expected HTTPStatusError")
        except HTTPStatusError as e:
            assert e.status == 429 and len(net.calls) == 4
        # a Retry-After beyond the cap is not waited out
        net = FakeNet({"https://r.example/q": [Response("", 429, {"retry-after": "3600"})]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False,
                         log=lambda m: None)
        t0 = net.now
        try:
            c.get("https://r.example/q")
            raise AssertionError("expected HTTPStatusError")
        except HTTPStatusError:
            assert net.now - t0 < 60 and len(net.calls) == 1
        # a dropped connection is retried once, a second failure is raised
        net = FakeNet({"https://t.example/q": [urllib.error.URLError("EOF"), ok]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False, log=lambda m: None)
        assert c.get("https://t.example/q").status == 200 and len(net.calls) == 2
        net = FakeNet({"https://t.example/q": [TimeoutError("timed out")]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False, log=lambda m: None)
        try:
            c.get("https://t.example/q")
            raise AssertionError("expected TimeoutError")
        except TimeoutError:
            assert len(net.calls) == 2
        # 4. budget: the 4th network request raises, cache hits are free
        net = FakeNet({"https://a.example/*": [ok]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, cache_dir=tmp + "/c4",
                         max_requests=3, log=lambda m: None)
        for i in range(3):
            c.get(f"https://a.example/{i}")
        c.get("https://a.example/1")
        try:
            c.get("https://a.example/9")
            raise AssertionError("expected RequestBudgetExceeded")
        except RequestBudgetExceeded as e:
            assert "budget of 3" in str(e) and len(net.calls) == 3
        # 5. redirects are visible, not followed by default
        net = FakeNet({"https://e.example/x": [Response("", 302, {"location": "https://n.example/blocked.txt"})],
                       "https://n.example/*": [ok]})
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False, log=lambda m: None)
        r = c.get("https://e.example/x")
        assert r.status == 302 and r.location == "https://n.example/blocked.txt" and len(net.calls) == 1
        assert c.get("https://e.example/x", follow_redirects=True).text == "hello"
    print("selftest: OK (spacing, cache, Retry-After, backoff, max retries, connection retry, budget, redirects)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    print(__doc__)
