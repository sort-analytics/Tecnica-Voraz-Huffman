"""Pruebas: python test_huffman.py"""
import os
import huffman_core as hc
import mst


def roundtrip(raw, name="t.txt"):
    text, enc = hc.decode_raw(raw)
    f = hc.compute_frequencies(text); r = hc.build_tree(f); c = hc.generate_codes(r)
    blob = hc.pack_file(raw, name, f, c, enc, text)
    out, ok = hc.decompress(hc.parse_file(blob))
    assert out == raw and ok, name
    return len(raw), len(blob)


# texto pequeño verificable a mano
f = hc.compute_frequencies("abracadabra")
assert f == {"a": 5, "b": 2, "r": 2, "c": 1, "d": 1}
codes = hc.generate_codes(hc.build_tree(f))
assert sum(f[s] * len(codes[s]) for s in f) == 23   # costo óptimo para abracadabra
print("abracadabra:", codes)

for raw in [b"", b"aaaa", b"x", "áéí ñ 你好 😀\r\n".encode(), bytes(range(256)), os.urandom(500)]:
    roundtrip(raw)
big = ("En un lugar de la Mancha de cuyo nombre no quiero acordarme\n" * 2000).encode()
print("repetitivo:", roundtrip(big))
t, w = mst.kruskal(mst.parse_edges("A B 4\nA C 3\nB C 1\nB D 2\nC D 4\nC E 5\nD E 6\nD F 3\nE F 2"))
assert w == mst.prim(mst.parse_edges("A B 4\nA C 3\nB C 1\nB D 2\nC D 4\nC E 5\nD E 6\nD F 3\nE F 2"))[1] == 11
print("TODAS LAS PRUEBAS OK")
