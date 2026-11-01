"""cryptomath.symmetric -- arithmetization-oriented primitive costs and GF(2^n) arithmetic.

Only what ZK circuits need is kept: the cost of AO hashes / ciphers inside a circuit and
binary-field arithmetic (binary-tower and GF(2^n)-based proof systems).

Modules
-------
gf2n      GF(2^n) arithmetic, power maps x^d, Gold / Kasami exponent checks
afcost    cost formulas for MiMC, HADES/Poseidon, Rasta, LowMC, Trivium-like, AES
          (S-box count, multiplications = R1CS constraints for x^alpha, depth)

Quick start::

    from cryptomath.symmetric import hades_cost, GF2n
    hades_cost(3, 8, 57).mults        # 243 multiplications for Poseidon t=3, x^5
    GF2n(8).mul(0x57, 0x83)           # 0xC1
"""
from .gf2n import (GF2n, DEFAULT_MODULI, is_irreducible_gf2, power_map, inverse_map,
                   cyclotomic_class, is_gold_exponent, is_kasami_exponent, gold_is_apn,
                   kasami_is_apn, is_permutation_exponent)
from .afcost import (CipherCost, power_mult_cost, mimc_rounds, mimc_cost, hades_cost, rasta_cost,
                     lowmc_cost, trivium_like_cost, aes128_boolean_cost, compare as compare_costs)

__all__ = [n for n in dir() if not n.startswith("_")]
