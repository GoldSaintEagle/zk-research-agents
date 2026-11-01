import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import cryptomath  # noqa: E402


DOCTEST_MODULES = ("cryptomath.algebra.finite_field", "cryptomath.zk.mle", "cryptomath.zk.r1cs")


class TestPackage(unittest.TestCase):
    def test_lazy_imports(self):
        self.assertIn("algebra", cryptomath.SUBPACKAGES)
        av = cryptomath.available()
        for name in cryptomath.SUBPACKAGES:
            self.assertTrue(av[name], name)
        self.assertTrue(hasattr(cryptomath.algebra, "cyclotomic_poly"))
        with self.assertRaises(AttributeError):
            cryptomath.does_not_exist  # noqa: B018

    def test_toy_markers(self):
        d = os.path.join(ROOT, "cryptomath", "zk")
        for fn in os.listdir(d):
            if fn.endswith(".py"):
                with open(os.path.join(d, fn)) as fh:
                    first = fh.readline()
                self.assertIn("TOY: not secure", first, fn)

    def test_zk_lazy_and_light(self):
        """r1cs / plonkish / mle / sumcheck / merkle and costmodel's counters work without sympy and numpy
        (skill scripts run with a bare Python): import them with both blocked."""
        import subprocess
        code = ("import sys; sys.modules['sympy'] = None; sys.modules['numpy'] = None; sys.path.insert(0, %r); "
                "from cryptomath.zk import r1cs, plonkish, mle, sumcheck, merkle; "
                "from cryptomath.costmodel import Counter, zkops; "
                "import random; assert sumcheck.run([[1, 2, 3, 4]], 97, random.Random(0))['accepted']" % ROOT)
        subprocess.run([sys.executable, "-c", code], check=True)

    def test_no_forbidden_strings(self):
        # patterns are assembled from pieces so this file does not match itself
        pieces = [("order", "-?4"), ("order", " four"), ("symmetry", "-graded"), ("#5", "28"),
                  ("#6", "99"), ("19" + "2", r"\.168\."), ("/home/", "luck"), ("ac", "pk"),
                  ("soseri", "halsona")]
        pat = re.compile("|".join(a + b for a, b in pieces),
                       re.IGNORECASE)
        for sub in cryptomath.SUBPACKAGES:
            d = os.path.join(ROOT, "cryptomath", sub)
            for fn in os.listdir(d):
                if fn.endswith(".py"):
                    with open(os.path.join(d, fn)) as fh:
                        self.assertIsNone(pat.search(fh.read()), fn)

    def test_doctests(self):
        import doctest
        import importlib

        import numpy as np
        for name in DOCTEST_MODULES:
            res = doctest.testmod(importlib.import_module(name), extraglobs={"np": np})
            self.assertEqual(res.failed, 0, name)


if __name__ == "__main__":
    unittest.main()
