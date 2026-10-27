"""Huffman Compressor - GUI (Tkinter). Ejecutar: python app.py"""
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import gutenberg
import huffman_core as hc
import mst as mstlib


def make_canvas(parent):
    f = ttk.Frame(parent)
    c = tk.Canvas(f, bg="white")
    xs = ttk.Scrollbar(f, orient="horizontal", command=c.xview)
    ys = ttk.Scrollbar(f, orient="vertical", command=c.yview)
    c.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
    c.grid(row=0, column=0, sticky="nsew"); ys.grid(row=0, column=1, sticky="ns")
    xs.grid(row=1, column=0, sticky="ew")
    f.rowconfigure(0, weight=1); f.columnconfigure(0, weight=1)
    return f, c


def draw_tree(c, root):
    c.delete("all")
    if root is None:
        return
    leaves = [sum(1 for _ in _leaves(root))]
    if leaves[0] > 400:
        c.create_text(20, 20, anchor="nw", text=f"Árbol demasiado grande para dibujar ({leaves[0]} hojas).")
        return
    pos, idx = {}, [0]

    def lay(n, d):
        if n.is_leaf:
            x = idx[0] * 46 + 30; idx[0] += 1
        else:
            x = (lay(n.left, d + 1) + lay(n.right, d + 1)) / 2
        pos[id(n)] = (x, d * 70 + 40)
        return x
    lay(root, 0)
    stack = [root]
    while stack:                      # aristas
        n = stack.pop()
        if n.is_leaf:
            continue
        x, y = pos[id(n)]
        for child, bit in ((n.left, "0"), (n.right, "1")):
            cx, cy = pos[id(child)]
            c.create_line(x, y, cx, cy, fill="#888")
            c.create_text((x + cx) / 2 + (-7 if bit == "0" else 7), (y + cy) / 2,
                          text=bit, fill="#c0392b", font=("Arial", 9, "bold"))
            stack.append(child)
    stack = [root]
    while stack:                      # nodos
        n = stack.pop()
        x, y = pos[id(n)]
        if n.is_leaf:
            c.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#d5f5e3", outline="#27ae60")
            c.create_text(x, y - 4, text=hc.show_sym(n.symbol), font=("Consolas", 10, "bold"))
            c.create_text(x, y + 8, text=str(n.freq), font=("Arial", 7))
        else:
            c.create_oval(x - 14, y - 14, x + 14, y + 14, fill="#d6eaf8", outline="#2980b9")
            c.create_text(x, y, text=str(n.freq), font=("Arial", 7))
            stack += [n.left, n.right]
    c.configure(scrollregion=c.bbox("all") and tuple(v + d for v, d in zip(c.bbox("all"), (-20, -20, 20, 20))))


def _leaves(n):
    stack = [n]
    while stack:
        x = stack.pop()
        if x.is_leaf:
            yield x
        else:
            stack += [x.left, x.right]


def make_code_table(parent):
    cols = ("sym", "uni", "freq", "pct", "code", "len")
    t = ttk.Treeview(parent, columns=cols, show="headings", height=12)
    for c, h, w in zip(cols, ("Símbolo", "Unicode", "Frecuencia", "%", "Código Huffman", "Bits"),
                       (70, 80, 90, 70, 300, 50)):
        t.heading(c, text=h); t.column(c, width=w, anchor="w")
    return t


def fill_code_table(t, freqs, codes):
    t.delete(*t.get_children())
    total = sum(freqs.values()) or 1
    for s in sorted(freqs, key=lambda k: -freqs[k]):
        t.insert("", "end", values=(hc.show_sym(s), f"U+{ord(s):04X}", f"{freqs[s]:,}",
                                    f"{freqs[s] / total * 100:.2f}", codes.get(s, ""),
                                    len(codes.get(s, ""))))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Huffman Compressor - Análisis de Algoritmos 2026B")
        self.geometry("1100x720")
        self.raw = None; self.name = ""; self.text = ""; self.enc = 0
        self.freqs = self.root_node = self.codes = self.blob = None
        self.steps = []
        self.info = None; self.recovered = None
        nb = self.nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=6, pady=6)
        self._tab_input(); self._tab_analysis(); self._tab_tree(); self._tab_compress()
        self._tab_inspector(); self._tab_mst()
        self.status = tk.StringVar(value="1) Carga un .txt o busca un libro de Project Gutenberg.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x")

    # ------------------------------------------------------------ Pestaña 1: entrada
    def _tab_input(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="1. Entrada")
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=8)
        ttk.Button(top, text="Subir archivo .txt…", command=self.load_txt).pack(side="left")
        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Label(top, text="Gutenberg (título, autor, palabra):").pack(side="left")
        self.q = tk.StringVar(); e = ttk.Entry(top, textvariable=self.q, width=30)
        e.pack(side="left", padx=4); e.bind("<Return>", lambda _: self.search_book())
        ttk.Button(top, text="Buscar", command=self.search_book).pack(side="left")
        self.books = ttk.Treeview(f, columns=("id", "title", "author"), show="headings", height=8)
        for c, h, w in (("id", "ID", 60), ("title", "Título", 500), ("author", "Autor", 300)):
            self.books.heading(c, text=h); self.books.column(c, width=w)
        self.books.pack(fill="x", padx=8)
        ttk.Button(f, text="Descargar obra seleccionada", command=self.download_book).pack(pady=6)
        self.strip = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Quitar licencia/encabezado de Gutenberg", variable=self.strip).pack()
        self.preview = ScrolledText(f, height=12, wrap="word"); self.preview.pack(fill="both", expand=True, padx=8, pady=8)

    def set_input(self, raw, name):
        self.raw, self.name = raw, name
        self.text, self.enc = hc.decode_raw(raw)
        self.freqs = self.root_node = self.codes = self.blob = None
        self.preview.delete("1.0", "end"); self.preview.insert("1.0", self.text[:5000])
        self.status.set(f"Cargado '{name}': {hc.fmt_size(len(raw))}. Ve a '2. Análisis'.")
        self.nb.select(1)

    def load_txt(self):
        p = filedialog.askopenfilename(filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if p:
            with open(p, "rb") as fh:
                self.set_input(fh.read(), os.path.basename(p))

    def search_book(self):
        q = self.q.get().strip()
        if not q:
            return
        self.status.set("Buscando en Project Gutenberg…")

        def work():
            try:
                res = gutenberg.search(q)
                self.after(0, lambda: self._show_books(res))
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Error de red", str(ex)))
        threading.Thread(target=work, daemon=True).start()

    def _show_books(self, res):
        self.books.delete(*self.books.get_children()); self._urls = {}
        for b in res:
            iid = self.books.insert("", "end", values=(b["id"], b["title"], b["author"]))
            self._urls[iid] = b
        self.status.set(f"{len(res)} obras con texto disponible.")

    def download_book(self):
        sel = self.books.selection()
        if not sel:
            return
        b = self._urls[sel[0]]
        self.status.set(f"Descargando '{b['title']}'…")

        def work():
            try:
                raw = gutenberg.download(b["url"])
                if self.strip.get():
                    raw = gutenberg.strip_boilerplate(raw)
                self.after(0, lambda: self.set_input(raw, f"gutenberg_{b['id']}.txt"))
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Error de descarga", str(ex)))
        threading.Thread(target=work, daemon=True).start()

    # ------------------------------------------------------------ Pestaña 2: análisis
    def _tab_analysis(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="2. Análisis")
        bar = ttk.Frame(f); bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="ANALIZAR (frecuencias)", command=self.analyze).pack(side="left")
        ttk.Button(bar, text="CONSTRUIR HUFFMAN (árbol + códigos)", command=self.build).pack(side="left", padx=8)
        self.table = make_code_table(f); self.table.pack(fill="both", expand=True, padx=8)
        ttk.Label(f, text="Pasos voraces (fusión de los dos nodos menos frecuentes):").pack(anchor="w", padx=8)
        self.steps_box = ScrolledText(f, height=8); self.steps_box.pack(fill="x", padx=8, pady=6)

    def _need_input(self):
        if self.raw is None:
            messagebox.showinfo("Falta entrada", "Primero carga un .txt o descarga un libro.")
            return False
        return True

    def analyze(self):
        if not self._need_input():
            return
        self.freqs = hc.compute_frequencies(self.text)
        fill_code_table(self.table, self.freqs, {})
        self.status.set(f"{len(self.freqs)} símbolos distintos, {len(self.text):,} caracteres.")

    def build(self):
        if self.freqs is None:
            self.analyze()
        if self.freqs is None:
            return
        self.steps = []
        self.root_node = hc.build_tree(self.freqs, self.steps)
        self.codes = hc.generate_codes(self.root_node)
        fill_code_table(self.table, self.freqs, self.codes)
        self.steps_box.delete("1.0", "end")
        self.steps_box.insert("1.0", "\n".join(f"{i + 1}. {s}" for i, s in enumerate(self.steps)))
        draw_tree(self.tree_canvas, self.root_node)
        self.status.set("Árbol y códigos generados. Ve a '3. Árbol' o '4. Comprimir'.")

    # ------------------------------------------------------------ Pestaña 3: árbol
    def _tab_tree(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="3. Árbol")
        fr, self.tree_canvas = make_canvas(f); fr.pack(fill="both", expand=True)
        ttk.Label(f, text="Verde = hoja (símbolo/frecuencia) · Azul = nodo interno (suma) · rojo = bit de la rama").pack()

    # ------------------------------------------------------------ Pestaña 4: comprimir
    def _tab_compress(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="4. Comprimir")
        bar = ttk.Frame(f); bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="COMPRIMIR", command=self.compress).pack(side="left")
        ttk.Button(bar, text="Guardar .huff…", command=self.save_huff).pack(side="left", padx=8)
        ttk.Button(bar, text="Verificar integridad (descomprimir en memoria)", command=self.verify).pack(side="left")
        self.metrics_box = ScrolledText(f, font=("Consolas", 11)); self.metrics_box.pack(fill="both", expand=True, padx=8, pady=8)

    def compress(self):
        if not self._need_input():
            return
        if self.codes is None:
            self.build()
        self.status.set("Comprimiendo…")
        self.update_idletasks()
        self.blob = hc.pack_file(self.raw, self.name, self.freqs, self.codes, self.enc, self.text)
        o, c = len(self.raw), len(self.blob)
        m = hc.metrics(o, c)
        total_bits = sum(self.freqs[s] * len(self.codes[s]) for s in self.freqs)
        avg = total_bits / max(1, len(self.text))
        out = (f"Original:            {hc.fmt_size(o)}\n"
               f"Comprimido (.huff):  {hc.fmt_size(c)}\n"
               f"  - encabezado+tabla: {hc.fmt_size(c - (total_bits + 7) // 8)}\n"
               f"  - datos codificados: {hc.fmt_size((total_bits + 7) // 8)}\n"
               f"Ahorro:              {hc.fmt_size(m['saved'])}\n"
               f"Reducción:           {m['pct']:.2f} %\n"
               f"Razón de compresión: {m['ratio']:.3f} : 1\n"
               f"Símbolos distintos:  {len(self.freqs)}\n"
               f"Bits codificados:    {total_bits:,}\n"
               f"Longitud media:      {avg:.4f} bits/símbolo (vs 8 bits ASCII)\n")
        self.metrics_box.delete("1.0", "end"); self.metrics_box.insert("1.0", out)
        self.status.set("Comprimido. Guarda el .huff o verifica la integridad.")

    def save_huff(self):
        if self.blob is None:
            self.compress()
        if self.blob is None:
            return
        p = filedialog.asksaveasfilename(defaultextension=hc.EXTENSION, initialfile=os.path.splitext(self.name)[0] + hc.EXTENSION,
                                         filetypes=[("Huffman", "*" + hc.EXTENSION)])
        if p:
            with open(p, "wb") as fh:
                fh.write(self.blob)
            self.status.set(f"Guardado: {p}")

    def verify(self):
        if self.blob is None:
            self.compress()
        if self.blob is None:
            return
        raw, ok = hc.decompress(hc.parse_file(self.blob))
        same = raw == self.raw
        self.metrics_box.insert("end", f"\nIntegridad SHA-256: {'OK' if ok else 'FALLÓ'}\n"
                                       f"Comparación byte a byte: {'IDÉNTICO' if same else 'DIFERENTE'}\n")
        self.status.set("Integridad verificada." if ok and same else "¡Error de integridad!")

    # ------------------------------------------------------------ Pestaña 5: inspector
    def _tab_inspector(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="5. Inspector")
        bar = ttk.Frame(f); bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="Abrir .huff…", command=self.open_huff).pack(side="left")
        ttk.Button(bar, text="DESCOMPRIMIR", command=self.decompress_info).pack(side="left", padx=8)
        ttk.Button(bar, text="Descargar .txt…", command=self.save_txt).pack(side="left")
        sub = ttk.Notebook(f); sub.pack(fill="both", expand=True, padx=8, pady=4)
        self.i_meta = ScrolledText(sub, font=("Consolas", 10)); sub.add(self.i_meta, text="Metadatos")
        t = ttk.Frame(sub); sub.add(t, text="Frecuencias y códigos")
        self.i_table = make_code_table(t); self.i_table.pack(fill="both", expand=True)
        tf = ttk.Frame(sub); sub.add(tf, text="Árbol reconstruido")
        fr, self.i_canvas = make_canvas(tf); fr.pack(fill="both", expand=True)
        self.i_bits = ScrolledText(sub, font=("Consolas", 10)); sub.add(self.i_bits, text="Datos binarios")
        self.i_text = ScrolledText(sub, wrap="word"); sub.add(self.i_text, text="Texto recuperado")
        self.i_sub = sub

    def open_huff(self):
        p = filedialog.askopenfilename(filetypes=[("Huffman", "*" + hc.EXTENSION), ("Todos", "*.*")])
        if not p:
            return
        try:
            with open(p, "rb") as fh:
                blob = fh.read()
            info = hc.parse_file(blob)
        except Exception as ex:
            messagebox.showerror("Archivo inválido", str(ex)); return
        info["file"] = os.path.basename(p); self.info = info; self.recovered = None
        m = hc.metrics(info["orig_size"], info["compressed_size"])
        meta = (f"Archivo:             {info['file']}  (extensión {os.path.splitext(p)[1]})\n"
                f"Nombre original:     {info['name']}\n"
                f"Versión del formato: {info['version']}\n"
                f"Codificación texto:  {'UTF-8' if info['encoding'] == 0 else 'Latin-1'}\n"
                f"Tamaño original:     {hc.fmt_size(info['orig_size'])}\n"
                f"Tamaño comprimido:   {hc.fmt_size(info['compressed_size'])}\n"
                f"Ahorro:              {hc.fmt_size(m['saved'])}\n"
                f"Compresión:          {m['pct']:.2f} %  (razón {m['ratio']:.3f}:1)\n"
                f"Símbolos distintos:  {info['n_unique']}\n"
                f"Caracteres totales:  {info['nchars']:,}\n"
                f"Bits codificados:    {info['nbits']:,}  (último byte usa {info['nbits'] % 8 or 8} bits válidos)\n"
                f"Tamaño encabezado+tabla: {info['header_size']} bytes\n"
                f"SHA-256 original:    {info['sha256'].hex()}\n")
        self.i_meta.delete("1.0", "end"); self.i_meta.insert("1.0", meta)
        fill_code_table(self.i_table, info["freqs"], info["codes"])
        draw_tree(self.i_canvas, info["root"])
        bits = hc.bytes_to_bits(info["data"][:64], min(info["nbits"], 512))
        groups = " ".join(bits[i:i + 8] for i in range(0, len(bits), 8))
        self.i_bits.delete("1.0", "end")
        self.i_bits.insert("1.0", "Primeros bytes (binario):\n" + groups +
                           "\n\nPrimeros bytes (hex):\n" + info["data"][:64].hex(" ") +
                           f"\n\n... {len(info['data']):,} bytes de datos en total.")
        self.i_text.delete("1.0", "end")
        self.status.set("Archivo inspeccionado. Pulsa DESCOMPRIMIR para recuperar el texto.")

    def decompress_info(self):
        if not self.info:
            messagebox.showinfo("Inspector", "Abre primero un archivo .huff."); return
        self.status.set("Descomprimiendo…"); self.update_idletasks()
        raw, ok = hc.decompress(self.info)
        self.recovered = raw
        txt = raw.decode("utf-8" if self.info["encoding"] == 0 else "latin-1")
        self.i_text.delete("1.0", "end")
        self.i_text.insert("1.0", f"[Integridad SHA-256: {'OK' if ok else 'FALLÓ'}]\n\n" + txt[:100000] +
                           ("\n\n[… vista truncada; el .txt descargado es completo]" if len(txt) > 100000 else ""))
        self.i_sub.select(self.i_text)
        self.status.set("Descompresión " + ("correcta, integridad verificada." if ok else "CON ERRORES."))

    def save_txt(self):
        if self.recovered is None:
            self.decompress_info()
        if self.recovered is None:
            return
        p = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="recuperado.txt")
        if p:
            with open(p, "wb") as fh:
                fh.write(self.recovered)
            self.status.set(f"Guardado: {p}")

    # ------------------------------------------------------------ Pestaña 6: MST
    def _tab_mst(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="6. Expansión mínima")
        left = ttk.Frame(f); left.pack(side="left", fill="y", padx=8, pady=8)
        ttk.Label(left, text="Aristas (origen destino peso):").pack(anchor="w")
        self.edges_box = tk.Text(left, width=22, height=20)
        self.edges_box.insert("1.0", "A B 4\nA C 3\nB C 1\nB D 2\nC D 4\nC E 5\nD E 6\nD F 3\nE F 2\n")
        self.edges_box.pack()
        ttk.Button(left, text="Kruskal", command=lambda: self.run_mst("kruskal")).pack(fill="x", pady=2)
        ttk.Button(left, text="Prim", command=lambda: self.run_mst("prim")).pack(fill="x", pady=2)
        self.mst_out = tk.Text(left, width=22, height=8); self.mst_out.pack()
        self.mst_canvas = tk.Canvas(f, bg="white"); self.mst_canvas.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    def run_mst(self, algo):
        import math
        edges = mstlib.parse_edges(self.edges_box.get("1.0", "end"))
        if not edges:
            return
        tree, total = mstlib.kruskal(edges) if algo == "kruskal" else mstlib.prim(edges)
        self.mst_out.delete("1.0", "end")
        self.mst_out.insert("1.0", f"{algo.upper()}\n" + "\n".join(f"{u}-{v}  ({w:g})" for u, v, w in tree) +
                            f"\nPeso total: {total:g}")
        nodes = sorted({n for e in edges for n in e[:2]})
        c = self.mst_canvas; c.delete("all"); c.update_idletasks()
        cx, cy, r = c.winfo_width() / 2, c.winfo_height() / 2, min(c.winfo_width(), c.winfo_height()) / 2 - 40
        pos = {n: (cx + r * math.cos(2 * math.pi * i / len(nodes)), cy + r * math.sin(2 * math.pi * i / len(nodes)))
               for i, n in enumerate(nodes)}
        chosen = {frozenset((u, v)) for u, v, _ in tree}
        for u, v, w in edges:
            sel = frozenset((u, v)) in chosen
            (x1, y1), (x2, y2) = pos[u], pos[v]
            c.create_line(x1, y1, x2, y2, fill="#e74c3c" if sel else "#bbb", width=4 if sel else 1)
            c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"{w:g}", fill="#333", font=("Arial", 9, "bold"))
        for n, (x, y) in pos.items():
            c.create_oval(x - 14, y - 14, x + 14, y + 14, fill="#d6eaf8", outline="#2980b9")
            c.create_text(x, y, text=n, font=("Arial", 10, "bold"))


if __name__ == "__main__":
    App().mainloop()
