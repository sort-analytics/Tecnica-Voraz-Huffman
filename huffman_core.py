"""Núcleo del algoritmo de Huffman (técnica voraz) + formato de archivo .huff

Flujo: texto -> frecuencias -> árbol (voraz, cola de prioridad) -> códigos
       -> bits empaquetados -> archivo .huff -> (leer) -> árbol -> texto.
"""
import hashlib
import heapq
import struct
from collections import Counter

MAGIC = b"HUFF"
VERSION = 1
HEADER_FMT = ">4sBBBQQ32sIQH"   # ver documentación en README
HEADER_SIZE = struct.calcsize(HEADER_FMT)
EXTENSION = ".huff"


class Node:
    __slots__ = ("freq", "symbol", "left", "right")

    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq, self.symbol, self.left, self.right = freq, symbol, left, right

    @property
    def is_leaf(self):
        return self.left is None and self.right is None


# ---------------------------------------------------------------- 1. frecuencias
def compute_frequencies(text):
    """Frecuencia de cada carácter."""
    return dict(Counter(text))


# ---------------------------------------------------------------- 2. árbol (voraz)
def build_tree(freqs, steps=None):
    """Construye el árbol de Huffman.

    Estrategia voraz: en cada paso se extraen los DOS nodos de menor frecuencia
    y se fusionan en uno nuevo cuya frecuencia es la suma. El desempate es
    determinista (orden de creación) para poder reconstruir el mismo árbol
    desde el archivo comprimido.
    `steps` (lista opcional) recibe una descripción de cada fusión.
    """
    if not freqs:
        return None
    heap, order = [], 0
    for sym in sorted(freqs):
        heap.append((freqs[sym], order, Node(freqs[sym], symbol=sym)))
        order += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        parent = Node(f1 + f2, left=a, right=b)
        if steps is not None:
            steps.append(f"Fusionar {_label(a)} ({f1}) + {_label(b)} ({f2}) -> nodo ({f1 + f2})")
        heapq.heappush(heap, (parent.freq, order, parent))
        order += 1
    return heap[0][2]


def _label(n):
    return repr(n.symbol) if n.is_leaf else "[interno]"


# ---------------------------------------------------------------- 3. códigos
def generate_codes(root):
    """Recorre el árbol: izquierda = '0', derecha = '1'."""
    if root is None:
        return {}
    if root.is_leaf:                 # un único símbolo distinto
        return {root.symbol: "0"}
    codes, stack = {}, [(root, "")]
    while stack:
        node, code = stack.pop()
        if node.is_leaf:
            codes[node.symbol] = code
        else:
            stack.append((node.right, code + "1"))
            stack.append((node.left, code + "0"))
    return codes


# ---------------------------------------------------------------- 4. codificar / decodificar
def encode_text(text, codes):
    """Devuelve (bytes empaquetados, número de bits válidos)."""
    bits = "".join([codes[c] for c in text])
    nbits = len(bits)
    if nbits == 0:
        return b"", 0
    bits += "0" * ((-nbits) % 8)
    return int(bits, 2).to_bytes(len(bits) // 8, "big"), nbits


def bytes_to_bits(data, nbits):
    if not data:
        return ""
    return bin(int.from_bytes(data, "big"))[2:].zfill(len(data) * 8)[:nbits]


def decode_bits(bits, root, nchars):
    """Recorre el árbol bit a bit hasta recuperar `nchars` símbolos."""
    if root is None or nchars == 0:
        return ""
    if root.is_leaf:
        return root.symbol * nchars

    def to_nested(n):                # estructura anidada rápida
        return n.symbol if n.is_leaf else [to_nested(n.left), to_nested(n.right)]

    nested = to_nested(root)
    out, node = [], nested
    for b in bits:
        node = node[b == "1"]
        if node.__class__ is str:
            out.append(node)
            node = nested
            if len(out) == nchars:
                break
    return "".join(out)


# ---------------------------------------------------------------- 5. formato .huff
def decode_raw(raw):
    """bytes -> (texto, código de codificación 0=utf-8, 1=latin-1)."""
    try:
        return raw.decode("utf-8"), 0
    except UnicodeDecodeError:
        return raw.decode("latin-1"), 1


def pack_file(raw, name, freqs, codes, enc, text):
    data, nbits = encode_text(text, codes)
    name_b = name.encode("utf-8")[:65535]
    header = struct.pack(HEADER_FMT, MAGIC, VERSION, enc, 0, len(raw), len(text),
                         hashlib.sha256(raw).digest(), len(freqs), nbits, len(name_b))
    table = b"".join(struct.pack(">II", ord(s), freqs[s]) for s in sorted(freqs))
    return header + name_b + table + data


def parse_file(blob):
    """Lee un .huff y devuelve un dict con metadatos, tabla y datos."""
    if len(blob) < HEADER_SIZE or blob[:4] != MAGIC:
        raise ValueError("No es un archivo .huff válido (firma incorrecta).")
    (_, ver, enc, flags, osize, nchars, sha, nuniq, nbits, nlen) = struct.unpack(
        HEADER_FMT, blob[:HEADER_SIZE])
    if ver != VERSION:
        raise ValueError(f"Versión de formato no soportada: {ver}")
    p = HEADER_SIZE
    name = blob[p:p + nlen].decode("utf-8", "replace"); p += nlen
    freqs = {}
    for _ in range(nuniq):
        cp, f = struct.unpack(">II", blob[p:p + 8]); p += 8
        freqs[chr(cp)] = f
    data = blob[p:]
    if len(data) != (nbits + 7) // 8:
        raise ValueError("Archivo corrupto: longitud de datos inconsistente.")
    root = build_tree(freqs)
    return dict(version=ver, encoding=enc, orig_size=osize, nchars=nchars, sha256=sha,
                n_unique=nuniq, nbits=nbits, name=name, freqs=freqs, data=data,
                root=root, codes=generate_codes(root), header_size=p,
                compressed_size=len(blob))


def decompress(info):
    """Devuelve (bytes originales, integridad_ok)."""
    bits = bytes_to_bits(info["data"], info["nbits"])
    text = decode_bits(bits, info["root"], info["nchars"])
    raw = text.encode("utf-8" if info["encoding"] == 0 else "latin-1")
    ok = hashlib.sha256(raw).digest() == info["sha256"] and len(raw) == info["orig_size"]
    return raw, ok


# ---------------------------------------------------------------- utilidades
def fmt_size(n):
    if n >= 1024 ** 2:
        return f"{n:,} bytes ({n / 1024 ** 2:.2f} MB)"
    return f"{n:,} bytes ({n / 1024:.2f} KB)"


def show_sym(c):
    return {"\n": "\\n", "\r": "\\r", "\t": "\\t", " ": "␣", "\ufeff": "BOM"}.get(c, c)


def metrics(orig, comp):
    saved = orig - comp
    return dict(saved=saved, pct=(saved / orig * 100) if orig else 0.0,
                ratio=(orig / comp) if comp else 0.0)
