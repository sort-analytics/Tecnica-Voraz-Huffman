"""
Pruebas adicionales para Huffman Web Compressor.
Colocar este archivo en Code_huffman/ junto a huffman_core.py.

Ejecutar:
    python test_archivos.py
"""
import hashlib
import unittest
from pathlib import Path

import huffman_core as hc


class HuffmanFileTests(unittest.TestCase):
    def make_huff(self, raw: bytes, name="prueba.txt"):
        text, encoding = hc.decode_raw(raw)
        freqs = hc.compute_frequencies(text)
        root = hc.build_tree(freqs)
        codes = hc.generate_codes(root)
        return hc.pack_file(raw, name, freqs, codes, encoding, text)

    def roundtrip(self, raw: bytes):
        blob = self.make_huff(raw)
        info = hc.parse_file(blob)
        recovered, integrity_ok = hc.decompress(info)
        self.assertEqual(recovered, raw)
        self.assertTrue(integrity_ok)
        self.assertEqual(hashlib.sha256(recovered).digest(),
                         hashlib.sha256(raw).digest())
        return blob

    def test_texto_ascii(self):
        self.roundtrip(b"abracadabra")

    def test_texto_utf8_con_tildes_y_emoji(self):
        self.roundtrip("¡Hola, señor! 😀\nSegunda línea.\n".encode("utf-8"))

    def test_texto_repetitivo(self):
        self.roundtrip(("Huffman " * 10000).encode("utf-8"))

    def test_bytes_latin1(self):
        # Los bytes 0..255 fuerzan a probar la ruta Latin-1 si decode_raw la selecciona.
        raw = bytes(range(256))
        self.roundtrip(raw)

    def test_archivo_vacio(self):
        # El núcleo Python debe soportar vacío aunque la interfaz web podría no permitirlo.
        self.roundtrip(b"")

    def test_un_solo_simbolo(self):
        self.roundtrip(("x" * 1000).encode("utf-8"))

    def test_archivo_truncado_se_rechaza(self):
        blob = self.make_huff(b"Este archivo se va a truncar.")
        with self.assertRaises(Exception):
            hc.parse_file(blob[:-1])

    def test_firma_invalida_se_rechaza(self):
        blob = bytearray(self.make_huff(b"contenido"))
        blob[0:4] = b"XXXX"
        with self.assertRaises(Exception):
            hc.parse_file(bytes(blob))

    def test_version_invalida_se_rechaza(self):
        blob = bytearray(self.make_huff(b"contenido"))
        blob[4] = 255
        with self.assertRaises(Exception):
            hc.parse_file(bytes(blob))

    def test_archivo_generado_por_javascript(self):
        """
        Guarda como huff_generado_web.huff un archivo descargado desde la web.
        Si existe, esta prueba lo abre con el parser Python y verifica su contenido.
        """
        path = Path(__file__).with_name("huff_generado_web.huff")
        if not path.exists():
            self.skipTest("Copia aquí un .huff descargado desde la aplicación web.")
        blob = path.read_bytes()
        info = hc.parse_file(blob)
        recovered, integrity_ok = hc.decompress(info)
        self.assertTrue(integrity_ok)
        self.assertEqual(len(recovered), info["orig_size"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
