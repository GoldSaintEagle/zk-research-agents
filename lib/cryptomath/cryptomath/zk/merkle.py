# TOY: not secure -- truncatable SHA-256, no domain separation beyond leaf/node tags; for counting and demos.
"""Merkle commitments: commit, open, pruned multi-open, verify, collision extraction.

Binary tree over 2^depth leaves. Leaf hash H(0x00 || data), inner node
H(0x01 || left || right), where H is SHA-256 truncated to ``hash_bytes``
bytes ([CY24 §Definition, section:merkle-commitment-definition]).

* Single opening of leaf i: the sibling of every node on the path from i to the
  root (its *copath*), ``depth`` hashes.
* Multi-opening of a set I with path pruning: send only the copath nodes that
  are not themselves on a path of I, |copath(I) minus path(I)| hashes, between
  depth - log2|I| and |I| (depth - log2|I|)
  ([CY24 §Path pruning, lemma:path-pruning-is-copaths-minus-paths, lemma:path-pruning-lower-and-upper]);
  :func:`cryptomath.costmodel.zkops.merkle_pruned_nodes` counts the same set.
* Binding: two valid openings of different data at the same index contain a
  hash collision ([CY24 §Merkle commitment scheme, lemma:mt-binding]).
  :func:`extract_collision` is that reduction; with ``hash_bytes`` = 1 or 2 a
  birthday search finds collisions, so binding visibly fails (tests/test_zk.py).
* Hiding is *not* provided by the plain tree (CY24 salts the leaves and drops the salts
  when no privacy is needed, [CY24 §Definition, remark:mt-no-privacy]). ``hiding=True`` salts each leaf
  with :func:`cryptomath.protocols.commitments.hash_commit` (random 32-byte
  opening per leaf); the salt travels with the opened leaf.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = ["MerkleTree", "leaf_hash", "node_hash", "verify", "verify_many", "proof_size",
           "extract_collision", "find_leaf_collision"]


def _h(data: bytes, hash_bytes: int) -> bytes:
    return hashlib.sha256(data).digest()[:hash_bytes]


def leaf_hash(data: bytes, hash_bytes: int = 32) -> bytes:
    return _h(b"\x00" + data, hash_bytes)


def node_hash(left: bytes, right: bytes, hash_bytes: int = 32) -> bytes:
    return _h(b"\x01" + left + right, hash_bytes)


class MerkleTree:
    """``layers[0]`` = leaf hashes, ``layers[depth]`` = [root]."""

    def __init__(self, leaves: Sequence[bytes], hash_bytes: int = 32, hiding: bool = False):
        n = len(leaves)
        if n < 1 or n & (n - 1):
            raise ValueError("number of leaves must be a power of two")
        self.hash_bytes, self.depth = hash_bytes, n.bit_length() - 1
        self.data = list(leaves)
        self.salts: Optional[List[bytes]] = None
        if hiding:
            from ..protocols.commitments import hash_commit   # lazy: protocols imports sympy via ec
            commits = [hash_commit(d) for d in leaves]
            self.salts = [r for _, r in commits]
            level = [leaf_hash(c, hash_bytes) for c, _ in commits]
        else:
            level = [leaf_hash(d, hash_bytes) for d in leaves]
        self.layers = [level]
        while len(level) > 1:
            level = [node_hash(level[i], level[i + 1], hash_bytes) for i in range(0, len(level), 2)]
            self.layers.append(level)

    @property
    def root(self) -> bytes:
        return self.layers[-1][0]

    def open(self, i: int) -> List[bytes]:
        """Copath of leaf i, bottom-up."""
        path = []
        for lvl in range(self.depth):
            path.append(self.layers[lvl][i ^ 1])
            i >>= 1
        return path

    def open_many(self, indices) -> Dict[Tuple[int, int], bytes]:
        """Pruned multi-opening: {(level, index): hash} for copath(I) minus path(I)."""
        level_set, out = set(indices), {}
        for lvl in range(self.depth):
            for j in sorted({i ^ 1 for i in level_set} - level_set):
                out[(lvl, j)] = self.layers[lvl][j]
            level_set = {i >> 1 for i in level_set}
        return out

    def leaf_digest_input(self, i: int) -> bytes:
        """What the verifier hashes for leaf i (the salted commitment when hiding)."""
        if self.salts is None:
            return self.data[i]
        from ..protocols.commitments import hash_commit
        return hash_commit(self.data[i], self.salts[i])[0]


def verify(root: bytes, index: int, data: bytes, path: Sequence[bytes], hash_bytes: int = 32,
           salt: Optional[bytes] = None) -> bool:
    if salt is not None:
        from ..protocols.commitments import hash_commit
        data = hash_commit(data, salt)[0]
    cur = leaf_hash(data, hash_bytes)
    for sib in path:
        cur = node_hash(cur, sib, hash_bytes) if index % 2 == 0 else node_hash(sib, cur, hash_bytes)
        index >>= 1
    return cur == root


def verify_many(root: bytes, depth: int, leaves: Dict[int, bytes], proof: Dict[Tuple[int, int], bytes],
                hash_bytes: int = 32) -> bool:
    """Recompute the root from the opened leaves and a pruned proof; every proof node must be used."""
    known = {i: leaf_hash(d, hash_bytes) for i, d in leaves.items()}
    used = 0
    for lvl in range(depth):
        nxt = {}
        for i in sorted(known):
            j = i ^ 1
            if j in known:
                sib = known[j]
            elif (lvl, j) in proof:
                sib, used = proof[(lvl, j)], used + 1
            else:
                return False
            nxt[i >> 1] = node_hash(known[i], sib, hash_bytes) if i % 2 == 0 else node_hash(sib, known[i], hash_bytes)
        known = nxt
    return used == len(proof) and known.get(0) == root


def proof_size(depth: int, indices, hash_bytes: int = 32, pruned: bool = True) -> int:
    """Bytes of hash values in a (pruned or unpruned) opening of the leaf set ``indices``."""
    from ..costmodel.zkops import merkle_opening_nodes, merkle_pruned_nodes
    idx = set(indices)
    nodes = merkle_pruned_nodes(depth, idx) if pruned else merkle_opening_nodes(depth, len(idx))
    return nodes * hash_bytes


def extract_collision(index: int, data_a: bytes, path_a: Sequence[bytes], data_b: bytes,
                      path_b: Sequence[bytes], hash_bytes: int = 32) -> Optional[Tuple[bytes, bytes]]:
    """Given two openings of different data at the same index that verify against the same root, return
    two distinct preimages with the same hash (the reduction behind binding); None if there is none."""
    a, b = b"\x00" + data_a, b"\x00" + data_b
    i = index
    for lvl in range(len(path_a) + 1):
        ha, hb = _h(a, hash_bytes), _h(b, hash_bytes)
        if ha == hb and a != b:
            return a, b
        if lvl == len(path_a):
            break
        a = b"\x01" + (ha + path_a[lvl] if i % 2 == 0 else path_a[lvl] + ha)
        b = b"\x01" + (hb + path_b[lvl] if i % 2 == 0 else path_b[lvl] + hb)
        i >>= 1
    return None


def find_leaf_collision(hash_bytes: int, prefix: bytes = b"leaf-", limit: int = 1 << 20) -> Tuple[bytes, bytes]:
    """Birthday search for two leaf data with equal truncated leaf hashes (feasible for 1-3 bytes)."""
    seen: Dict[bytes, bytes] = {}
    for k in range(limit):
        d = prefix + k.to_bytes(4, "big")
        h = leaf_hash(d, hash_bytes)
        if h in seen:
            return seen[h], d
        seen[h] = d
    raise RuntimeError("no collision found")


if __name__ == "__main__":
    leaves = [b"v%d" % i for i in range(16)]
    T = MerkleTree(leaves)
    assert all(verify(T.root, i, leaves[i], T.open(i)) for i in range(16))
    I = {1, 2, 3, 9}
    pf = T.open_many(I)
    assert verify_many(T.root, 4, {i: leaves[i] for i in I}, pf)
    assert len(pf) * 32 == proof_size(4, I)
    print("merkle: OK")
