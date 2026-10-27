"""Búsqueda y descarga de libros de Project Gutenberg (API gratuita Gutendex)."""
import json
import re
import urllib.parse
import urllib.request

UA = {"User-Agent": "HuffmanCompressor/1.0 (educational)"}


def search(query):
    url = "https://gutendex.com/books/?search=" + urllib.parse.quote(query)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        data = json.load(r)
    results = []
    for b in data.get("results", []):
        fmts = b.get("formats", {})
        txt = next((u for k, u in fmts.items() if k.startswith("text/plain") and "utf-8" in k), None) \
            or next((u for k, u in fmts.items() if k.startswith("text/plain")), None)
        if txt:
            authors = ", ".join(a["name"] for a in b.get("authors", [])) or "Anónimo"
            results.append(dict(id=b["id"], title=b["title"], author=authors, url=txt))
    return results


def download(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def strip_boilerplate(raw):
    """Quita la licencia de Gutenberg al inicio y al final (opcional)."""
    t = raw.decode("utf-8", "replace")
    m = re.search(r"\*\*\* ?START OF.*?\*\*\*", t)
    e = re.search(r"\*\*\* ?END OF", t)
    if m and e and e.start() > m.end():
        t = t[m.end():e.start()].strip("\r\n") + "\n"
    return t.encode("utf-8")
