(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const encoder = new TextEncoder();
  const state = { text: '', raw: null, encoding: 0, sourceName: 'texto.txt', frequencies: null, root: null, codes: null, blob: null, inspected: null, recovered: null };
  const utf8 = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
  const MAX_FILE = 20 * 1024 * 1024;
  const FMT = { magic: 'HUFF', version: 1, headerSize: 4 + 1 + 1 + 1 + 8 + 8 + 32 + 4 + 8 + 2 };

  function setAlert(message = '') { $('app-alert').textContent = message; }
  function cleanName(name) { return (name || 'texto.txt').split(/[\\/]/).pop().replace(/[^\p{L}\p{N}._ -]/gu, '_').slice(0, 180) || 'texto.txt'; }
  function bytesToText(bytes) {
    try { return { text: utf8.decode(bytes), encoding: 0 }; }
    catch { let text = ''; for (let i = 0; i < bytes.length; i += 8192) text += String.fromCharCode(...bytes.subarray(i, i + 8192)); return { text, encoding: 1 }; }
  }
  function textToBytes(text, encoding) {
    if (encoding === 0) return encoder.encode(text);
    const out = new Uint8Array(text.length);
    for (let i = 0; i < text.length; i++) { const cp = text.codePointAt(i); if (cp > 255) throw new Error('El texto contiene símbolos fuera de Latin-1. Vuelve a cargarlo como UTF-8.'); out[i] = cp; if (cp > 0xffff) i++; }
    return out;
  }
  function formatBytes(n) {
    if (n >= 1024 ** 2) return `${(n / 1024 ** 2).toFixed(2)} MB`;
    if (n >= 1024) return `${(n / 1024).toFixed(2)} KB`;
    return `${n} bytes`;
  }
  function symbolLabel(s) { return ({ '\n': '\\n', '\r': '\\r', '\t': '\\t', ' ': '␣', '\ufeff': 'BOM' })[s] || s; }
  function codePointHex(s) { return 'U+' + s.codePointAt(0).toString(16).toUpperCase().padStart(4, '0'); }
  function computeFrequencies(text) { const f = new Map(); for (const ch of text) f.set(ch, (f.get(ch) || 0) + 1); return f; }
  function buildTree(freqs, steps = []) {
    let serial = 0; const heap = [];
    const cmp = (a, b) => a.freq - b.freq || a.order - b.order;
    function push(item) { let i = heap.push(item) - 1; while (i > 0) { const p = (i - 1) >> 1; if (cmp(heap[p], item) <= 0) break; heap[i] = heap[p]; i = p; } heap[i] = item; }
    function pop() { const top = heap[0], last = heap.pop(); if (heap.length) { let i = 0; while (true) { const l = i * 2 + 1, r = l + 1; if (l >= heap.length) break; const c = r < heap.length && cmp(heap[r], heap[l]) < 0 ? r : l; if (cmp(heap[c], last) >= 0) break; heap[i] = heap[c]; i = c; } heap[i] = last; } return top; }
    for (const [symbol, freq] of [...freqs].sort((a, b) => a[0].codePointAt(0) - b[0].codePointAt(0))) push({ freq, order: serial++, symbol, left: null, right: null });
    while (heap.length > 1) {
      const left = pop(), right = pop();
      const node = { freq: left.freq + right.freq, order: serial++, symbol: null, left, right };
      steps.push({ left, right, parent: node }); push(node);
    }
    return heap.length ? pop() : null;
  }
  function generateCodes(root) {
    const codes = new Map(); if (!root) return codes;
    if (!root.left && !root.right) { codes.set(root.symbol, '0'); return codes; }
    const stack = [[root, '']]; while (stack.length) { const [n, code] = stack.pop(); if (!n.left && !n.right) codes.set(n.symbol, code); else { stack.push([n.right, code + '1'], [n.left, code + '0']); } }
    return codes;
  }
  function getBits(text, codes) {
    let total = 0;
    for (const ch of text) { const code = codes.get(ch); if (code === undefined) throw new Error('No se encontró código para un símbolo.'); total += code.length; }
    const bytes = new Uint8Array(Math.ceil(total / 8)); let bitIndex = 0;
    for (const ch of text) for (const bit of codes.get(ch)) { if (bit === '1') bytes[bitIndex >> 3] |= (1 << (7 - (bitIndex & 7))); bitIndex++; }
    return { bytes, nbits: total };
  }
  async function digest(bytes) { return new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)); }
  function concat(parts) { const size = parts.reduce((a, p) => a + p.length, 0); const out = new Uint8Array(size); let pos = 0; for (const p of parts) { out.set(p, pos); pos += p.length; } return out; }
  async function packFile(raw, name, freqs, text, codes, encoding) {
    const coded = getBits(text, codes), nameBytes = encoder.encode(cleanName(name));
    if (nameBytes.length > 65535) throw new Error('El nombre del archivo es demasiado largo.');
    const symbols = [...freqs.keys()].sort((a, b) => a.codePointAt(0) - b.codePointAt(0));
    const header = new Uint8Array(FMT.headerSize), view = new DataView(header.buffer); header.set(encoder.encode('HUFF'), 0);
    view.setUint8(4, 1); view.setUint8(5, encoding); view.setUint8(6, 0); view.setBigUint64(7, BigInt(raw.length)); view.setBigUint64(15, BigInt([...text].length)); header.set(await digest(raw), 23);
    view.setUint32(55, symbols.length); view.setBigUint64(59, BigInt(coded.nbits)); view.setUint16(67, nameBytes.length);
    const table = new Uint8Array(symbols.length * 8), tv = new DataView(table.buffer); symbols.forEach((s, i) => { tv.setUint32(i * 8, s.codePointAt(0)); tv.setUint32(i * 8 + 4, freqs.get(s)); });
    return { blob: new Blob([header, nameBytes, table, coded.bytes], { type: 'application/octet-stream' }), nbits: coded.nbits, codedBytes: coded.bytes.length };
  }
  function readVar(bytes, offset, width) { const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength); return width === 8 ? v.getBigUint64(offset) : width === 4 ? v.getUint32(offset) : width === 2 ? v.getUint16(offset) : v.getUint8(offset); }
  function parseFile(bytes, filename) {
    if (bytes.length < FMT.headerSize || new TextDecoder().decode(bytes.subarray(0, 4)) !== 'HUFF') throw new Error('Firma incorrecta: no parece un archivo Huffman válido.');
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength), version = view.getUint8(4), encoding = view.getUint8(5), flags = view.getUint8(6);
    if (version !== 1) throw new Error(`Versión de formato no soportada: ${version}.`);
    if (encoding > 1 || flags !== 0) throw new Error('El archivo usa opciones de formato no compatibles.');
    const origSizeBig = readVar(bytes, 7, 8), ncharsBig = readVar(bytes, 15, 8), nbitsBig = readVar(bytes, 59, 8);
    if (origSizeBig > BigInt(Number.MAX_SAFE_INTEGER) || ncharsBig > BigInt(Number.MAX_SAFE_INTEGER) || nbitsBig > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error('El archivo supera el tamaño admitido por este navegador.');
    const origSize = Number(origSizeBig), nchars = Number(ncharsBig), nbits = Number(nbitsBig), nUnique = readVar(bytes, 55, 4), nameLen = readVar(bytes, 67, 2);
    let pos = FMT.headerSize; if (pos + nameLen + nUnique * 8 > bytes.length) throw new Error('Cabecera o tabla incompleta.');
    const name = new TextDecoder().decode(bytes.subarray(pos, pos + nameLen)); pos += nameLen;
    const freqs = new Map(); let totalFreq = 0;
    for (let i = 0; i < nUnique; i++) { const cp = readVar(bytes, pos, 4), freq = readVar(bytes, pos + 4, 4); pos += 8; if (!freq || cp > 0x10ffff || (cp >= 0xd800 && cp <= 0xdfff) || freqs.has(String.fromCodePoint(cp))) throw new Error('La tabla de frecuencias contiene una entrada inválida.'); freqs.set(String.fromCodePoint(cp), freq); totalFreq += freq; }
    if (totalFreq !== nchars) throw new Error('Las frecuencias no coinciden con la cantidad original de símbolos.');
    const data = bytes.subarray(pos), expected = Math.ceil(nbits / 8); if (data.length !== expected) throw new Error('Archivo corrupto: longitud de datos inconsistente.');
    if ((nchars === 0) !== (nUnique === 0) || (nchars > 0 && nUnique === 0)) throw new Error('Metadatos de texto vacío inconsistentes.');
    const root = buildTree(freqs), codes = generateCodes(root);
    return { version, encoding, origSize, nchars, nbits, nUnique, name, fileName: filename, freqs, data: data.slice(), root, codes, headerSize: pos, compressedSize: bytes.length, sha: bytes.slice(23, 55) };
  }
  function decode(info) {
    const out = []; let node = info.root, count = 0, current = '';
    if (!info.nchars) return '';
    if (node && !node.left && !node.right) return node.symbol.repeat(info.nchars);
    for (let i = 0; i < info.nbits; i++) {
      const bit = (info.data[i >> 3] >> (7 - (i & 7))) & 1; node = bit ? node.right : node.left;
      if (!node) throw new Error('El flujo binario no coincide con el árbol de Huffman.');
      if (!node.left && !node.right) { out.push(node.symbol); current = ''; if (++count > info.nchars) throw new Error('El flujo contiene más símbolos de los declarados.'); node = info.root; }
    }
    if (count !== info.nchars || node !== info.root) throw new Error('El flujo binario terminó antes de completar el texto declarado.');
    return out.join('');
  }
  function treeSVG(root) {
    if (!root) return '<div class="empty-tree">El texto no contiene símbolos.</div>';
    const leafCount = (n) => !n.left && !n.right ? 1 : leafCount(n.left) + leafCount(n.right);
    const leaves = leafCount(root); if (leaves > 180) return `<div class="empty-tree">Árbol con ${leaves} hojas. La tabla completa de códigos está disponible abajo.</div>`;
    const positions = new Map(); let index = 0, maxDepth = 0;
    function layout(n, depth) { maxDepth = Math.max(maxDepth, depth); let x; if (!n.left && !n.right) x = index++ * 62 + 34; else x = (layout(n.left, depth + 1) + layout(n.right, depth + 1)) / 2; positions.set(n, [x, depth * 72 + 35]); return x; }
    layout(root, 0); const width = Math.max(68, leaves * 62 + 12), height = Math.max(90, (maxDepth + 1) * 72 + 20), edges = [], nodes = [];
    function draw(n) { const [x, y] = positions.get(n); if (n.left) { const [cx, cy] = positions.get(n.left); edges.push(`<line x1="${x}" y1="${y}" x2="${cx}" y2="${cy}"/><text x="${(x + cx) / 2 - 7}" y="${(y + cy) / 2}" class="bit">0</text>`); draw(n.left); } if (n.right) { const [cx, cy] = positions.get(n.right); edges.push(`<line x1="${x}" y1="${y}" x2="${cx}" y2="${cy}"/><text x="${(x + cx) / 2 + 7}" y="${(y + cy) / 2}" class="bit">1</text>`); draw(n.right); }
      const leaf = !n.left && !n.right, label = leaf ? symbolLabel(n.symbol).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').slice(0, 8) : n.freq;
      nodes.push(`<g><circle cx="${x}" cy="${y}" r="${leaf ? 18 : 15}" class="${leaf ? 'leaf' : 'inner'}"/><text x="${x}" y="${y + 4}" class="node-label">${label}</text>${leaf ? `<text x="${x}" y="${y + 31}" class="freq-label">${n.freq}</text>` : ''}</g>`);
    }
    draw(root); return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Árbol binario de Huffman"><g class="edges">${edges.join('')}</g>${nodes.join('')}<style>.edges line{stroke:#aeb9b0;stroke-width:1.5}.bit{fill:#b9513b;font:600 10px 'DM Mono',monospace}.leaf{fill:#e6f5d8;stroke:#7fae51;stroke-width:1.5}.inner{fill:#e1eef5;stroke:#7eaac3;stroke-width:1.5}.node-label{text-anchor:middle;fill:#304137;font:600 9px 'DM Mono',monospace}.freq-label{text-anchor:middle;fill:#64736a;font:9px 'DM Sans',sans-serif}</style></svg>`;
  }
  function renderTable(freqs, codes, target) {
    const total = [...freqs.values()].reduce((a, b) => a + b, 0) || 1;
    const sorted = [...freqs].sort((a, b) => b[1] - a[1] || a[0].codePointAt(0) - b[0].codePointAt(0)), shown = sorted.slice(0, 5000);
    target.innerHTML = shown.map(([s, f]) => `<tr><td>${escapeHTML(symbolLabel(s))}</td><td>${codePointHex(s)}</td><td>${f.toLocaleString('es-MX')}</td><td>${(100 * f / total).toFixed(2)} %</td><td class="code-cell">${codes.get(s) || ''}</td><td>${(codes.get(s) || '').length}</td></tr>`).join('') + (sorted.length > shown.length ? `<tr><td colspan="6">Se muestran 5,000 de ${sorted.length.toLocaleString('es-MX')} símbolos; se conservaron todos en el archivo.</td></tr>` : '');
  }
  function escapeHTML(s) { return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]); }
  function metric(label, value, sub, highlight = false) { return `<div class="metric${highlight ? ' highlight' : ''}"><div class="metric-label">${label}</div><div class="metric-value">${value}</div><div class="metric-sub">${sub}</div></div>`; }
  function setSource(text, name, raw = null, encoding = 0) {
    state.text = text; state.raw = raw; state.encoding = encoding; state.sourceName = cleanName(name); state.blob = null; state.root = null; state.codes = null; state.frequencies = null;
    $('source-text').value = text; $('selected-file').textContent = name; $('source-meta').textContent = `${[...text].length.toLocaleString('es-MX')} caracteres · ${formatBytes(raw?.length ?? encoder.encode(text).length)}`;
    $('analyze-button').disabled = !text.length; $('build-button').disabled = !text.length; $('analysis-results').hidden = true; $('current-recovery').hidden = true; $('download-huff').disabled = true;
    $('encoding-status').textContent = encoding ? 'Archivo Latin-1 · recuperación byte a byte' : 'Archivo UTF-8 · recuperación byte a byte'; setAlert('');
  }
  function readTextArea() { const text = $('source-text').value; if (!text.length) { setAlert('Escribe texto o carga un archivo para continuar.'); return false; } if (text !== state.text) { state.text = text; state.raw = null; state.encoding = 0; state.sourceName = 'texto.txt'; state.frequencies = null; state.root = null; state.codes = null; $('selected-file').textContent = 'Texto editado manualmente'; $('source-meta').textContent = `${[...text].length.toLocaleString('es-MX')} caracteres · codificación UTF-8`; $('encoding-status').textContent = 'Texto editado · codificación UTF-8'; state.blob = null; } return true; }
  function analyze() {
    if (!readTextArea()) return; state.frequencies = computeFrequencies(state.text); const steps = []; state.root = buildTree(state.frequencies, steps); state.codes = generateCodes(state.root);
    const original = state.raw || encoder.encode(state.text), bits = [...state.text].reduce((n, s) => n + (state.codes.get(s) || '').length, 0); $('analysis-results').hidden = false;
    $('metrics').innerHTML = metric('TAMAÑO ORIGINAL', formatBytes(original.length), `${original.length.toLocaleString('es-MX')} bytes`) + metric('DATOS CODIFICADOS', formatBytes(Math.ceil(bits / 8)), `${bits.toLocaleString('es-MX')} bits válidos`) + metric('SÍMBOLOS ÚNICOS', state.frequencies.size.toLocaleString('es-MX'), `${[...state.text].length.toLocaleString('es-MX')} símbolos en total`) + metric('LONGITUD MEDIA', `${(bits / Math.max(1, [...state.text].length)).toFixed(3)} bits`, 'por símbolo · referencia: 8 bits', true);
    $('tree-view').innerHTML = treeSVG(state.root); const visibleSteps = steps.slice(0, 200); $('merge-steps').innerHTML = steps.length ? visibleSteps.map((s, i) => `<div class="step"><span class="step-n">${i + 1}</span><span class="step-text">${escapeHTML(nodeLabel(s.left))} (${s.left.freq}) + ${escapeHTML(nodeLabel(s.right))} (${s.right.freq}) → ${s.parent.freq}</span></div>`).join('') + (steps.length > visibleSteps.length ? `<div class="step-text">… ${steps.length - visibleSteps.length} fusiones adicionales omitidas en la vista.</div>` : '') : '<div class="muted">Solo hay un símbolo; se le asigna el código 0.</div>';
    renderTable(state.frequencies, state.codes, $('frequency-rows')); $('symbol-count').textContent = `${state.frequencies.size} símbolos`; setAlert('');
  }
  function nodeLabel(n) { return !n.left && !n.right ? `“${symbolLabel(n.symbol)}”` : 'nodo'; }
  function displayCompression(blob, nbits, codedBytes, rawSize, nUnique) {
    const compressed = blob.size, saved = rawSize - compressed, pct = rawSize ? saved / rawSize * 100 : 0, ratio = compressed ? rawSize / compressed : 0;
    $('metrics').innerHTML = metric('TAMAÑO ORIGINAL', formatBytes(rawSize), `${rawSize.toLocaleString('es-MX')} bytes`) + metric('ARCHIVO .HUFF', formatBytes(compressed), `${compressed.toLocaleString('es-MX')} bytes`) + metric(saved >= 0 ? 'ESPACIO AHORRADO' : 'DIFERENCIA', `${saved >= 0 ? '' : '−'}${formatBytes(Math.abs(saved))}`, `${pct.toFixed(2)} % ${pct >= 0 ? 'de reducción' : 'de aumento'}`, true) + metric('RAZÓN DE COMPRESIÓN', `${ratio.toFixed(3)} : 1`, `${nUnique} símbolos · ${nbits.toLocaleString('es-MX')} bits · datos ${formatBytes(codedBytes)}`);
    $('compression-success').hidden = false;
  }
  function download(blob, name) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = cleanName(name); a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); }
  async function compress() {
    if (!readTextArea()) return;
    try { if (!state.frequencies || state.text !== $('source-text').value) analyze(); if (!state.frequencies) return;
      state.raw = state.raw || encoder.encode(state.text);
      const packed = await packFile(state.raw, state.sourceName, state.frequencies, state.text, state.codes, state.encoding); state.blob = packed.blob;
      displayCompression(state.blob, packed.nbits, packed.codedBytes, state.raw.length, state.frequencies.size); $('download-huff').disabled = false; $('current-recovery').hidden = true; $('analysis-results').hidden = false; setAlert('');
    } catch (err) { setAlert(err.message || 'No se pudo comprimir el archivo.'); }
  }
  async function verifyCurrent() {
    if (!state.blob) return; const bytes = new Uint8Array(await state.blob.arrayBuffer()), info = parseFile(bytes, state.sourceName + '.huff'), recoveredText = decode(info), recovered = textToBytes(recoveredText, info.encoding), expected = state.raw || encoder.encode(state.text), a = await digest(recovered), b = await digest(expected), ok = a.every((v, i) => v === b[i]) && recovered.length === expected.length && recovered.every((v, i) => v === expected[i]);
    state.recovered = recovered; $('current-recovery').hidden = false; $('integrity-title').textContent = ok ? 'Integridad verificada · contenido idéntico' : 'La verificación de integridad falló'; $('integrity-detail').textContent = `${recovered.length.toLocaleString('es-MX')} bytes recuperados · SHA-256 ${ok ? 'coincide' : 'no coincide'} · comparación byte a byte ${ok ? 'idéntica' : 'diferente'}.`;
  }
  function downloadName(name) { const base = name.replace(/\.[^.]*$/, '') || 'recuperado'; return `${base}_recuperado.txt`; }
  function renderInspect(info) {
    $('inspector-empty').hidden = true; $('inspector-content').hidden = false; $('inspect-name').textContent = info.fileName;
    const saved = info.origSize - info.compressedSize, pct = info.origSize ? saved / info.origSize * 100 : 0;
    $('inspect-metrics').innerHTML = metric('TAMAÑO ORIGINAL', formatBytes(info.origSize), `${info.origSize.toLocaleString('es-MX')} bytes`) + metric('TAMAÑO .HUFF', formatBytes(info.compressedSize), `${info.compressedSize.toLocaleString('es-MX')} bytes`) + metric(saved >= 0 ? 'ESPACIO AHORRADO' : 'DIFERENCIA', `${saved >= 0 ? '' : '−'}${formatBytes(Math.abs(saved))}`, `${pct.toFixed(2)} % ${pct >= 0 ? 'de reducción' : 'de aumento'}`, true) + metric('SÍMBOLOS / BITS', `${info.nUnique} / ${info.nbits.toLocaleString('es-MX')}`, `datos empaquetados ${formatBytes(info.data.length)}`);
    const meta = [['Nombre original', info.name], ['Formato', 'HUFF · versión 1'], ['Codificación', info.encoding ? 'Latin-1' : 'UTF-8'], ['Símbolos originales', info.nchars.toLocaleString('es-MX')], ['Bytes cabecera + tabla', info.headerSize.toLocaleString('es-MX')], ['Bits válidos', info.nbits.toLocaleString('es-MX')], ['Último byte', `${info.nbits % 8 || (info.nbits ? 8 : 0)} bits válidos`], ['SHA-256 original', [...info.sha].map(b => b.toString(16).padStart(2, '0')).join('')]];
    $('metadata').innerHTML = meta.map(([k, v]) => `<div class="metadata-item"><span>${escapeHTML(k)}</span><strong>${escapeHTML(String(v))}</strong></div>`).join(''); $('inspect-tree').innerHTML = treeSVG(info.root); renderTable(info.freqs, info.codes, $('inspect-rows'));
    const maxBits = Math.min(info.nbits, 256); let bits = ''; for (let i = 0; i < maxBits; i++) bits += ((info.data[i >> 3] >> (7 - (i & 7))) & 1).toString(); $('binary-view').textContent = bits ? bits.match(/.{1,8}/g).join(' ') + (info.nbits > maxBits ? `\n\n… se muestran ${maxBits} de ${info.nbits.toLocaleString('es-MX')} bits.` : '') : 'El archivo no contiene datos codificados.';
  }
  function bookQuery(q) { return `https://gutendex.com/books/?search=${encodeURIComponent(q)}`; }
  async function searchBooks(event) {
    event.preventDefault(); const q = $('book-query').value.trim(); if (!q) return; const results = $('book-results'); results.textContent = 'Buscando obras…';
    try { const response = await fetch(bookQuery(q)); if (!response.ok) throw new Error(`Respuesta HTTP ${response.status}`); const data = await response.json(); const books = (data.results || []).map(b => { const fmts = b.formats || {}; const url = fmts['text/plain; charset=utf-8'] || Object.entries(fmts).find(([k, v]) => k.startsWith('text/plain') && /\.txt(\.\d+)?$/i.test(v))?.[1]; return url ? { title: b.title, author: (b.authors || []).map(a => a.name).join(', ') || 'Anónimo', url, id: b.id } : null; }).filter(Boolean).slice(0, 8);
      if (!books.length) { results.textContent = 'No hay resultados con texto plano disponible. Prueba con otra búsqueda.'; return; }
      results.replaceChildren(...books.map(book => { const row = document.createElement('div'); row.className = 'book-result'; const info = document.createElement('div'), title = document.createElement('strong'), author = document.createElement('span'), button = document.createElement('button'); title.textContent = book.title; author.textContent = book.author; button.textContent = 'Usar libro ↓'; button.addEventListener('click', () => loadBook(book)); info.append(title, author); row.append(info, button); return row; }));
    } catch (err) { results.textContent = 'No se pudo conectar con Gutendex. Revisa tu conexión y vuelve a intentar.'; }
  }
  async function loadBook(book) {
    setAlert(''); $('book-results').setAttribute('aria-busy', 'true');
    try { const response = await fetch(book.url); if (!response.ok) throw new Error('No se pudo descargar el texto.'); const raw = new Uint8Array(await response.arrayBuffer()); if (raw.length > MAX_FILE) throw new Error('El libro supera el límite de 20 MB para el navegador.'); let decoded = bytesToText(raw); if ($('strip-license').checked) { const start = /\*\*\*\s*START OF[^\n]*\*\*\*/i.exec(decoded.text), end = /\*\*\*\s*END OF/i.exec(decoded.text); if (start && end && end.index > start.index) decoded.text = decoded.text.slice(start.index + start[0].length, end.index).replace(/^\r?\n|\r?\n$/g, '') + '\n'; }
      setSource(decoded.text, `gutenberg_${book.id}.txt`, null, 0); $('source-meta').textContent = `${[...decoded.text].length.toLocaleString('es-MX')} caracteres · obra ${book.id}`; document.querySelector('[data-panel="compressor"]').click(); $('source-text').scrollIntoView({ behavior: 'smooth', block: 'center' });
    } catch (err) { setAlert(err.message || 'No se pudo cargar la obra.'); } finally { $('book-results').removeAttribute('aria-busy'); }
  }

  document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => { document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t === tab)); $('compressor').hidden = tab.dataset.panel !== 'compressor'; $('inspector').hidden = tab.dataset.panel !== 'inspector'; }));
  $('file-input').addEventListener('change', async (e) => { const f = e.target.files[0]; if (!f) return; if (f.size > MAX_FILE) { setAlert('El archivo supera el límite de 20 MB.'); return; } const raw = new Uint8Array(await f.arrayBuffer()), decoded = bytesToText(raw); setSource(decoded.text, f.name, raw, decoded.encoding); });
  $('dropzone').addEventListener('dragover', e => { e.preventDefault(); $('dropzone').classList.add('dragging'); }); $('dropzone').addEventListener('dragleave', () => $('dropzone').classList.remove('dragging')); $('dropzone').addEventListener('drop', async e => { e.preventDefault(); $('dropzone').classList.remove('dragging'); const f = e.dataTransfer.files[0]; if (!f) return; if (f.size > MAX_FILE) { setAlert('El archivo supera el límite de 20 MB.'); return; } const raw = new Uint8Array(await f.arrayBuffer()), decoded = bytesToText(raw); setSource(decoded.text, f.name, raw, decoded.encoding); });
  $('source-text').addEventListener('input', () => { $('build-button').disabled = !$('source-text').value.length; $('analyze-button').disabled = !$('source-text').value.length; if ($('source-text').value !== state.text) { state.blob = null; $('download-huff').disabled = true; } });
  $('analyze-button').addEventListener('click', analyze); $('build-button').addEventListener('click', compress); $('search-form').addEventListener('submit', searchBooks);
  $('download-huff').addEventListener('click', () => { if (state.blob) download(state.blob, state.sourceName.replace(/\.[^.]*$/, '') + '.huff'); });
  $('verify-current').addEventListener('click', () => verifyCurrent().catch(err => setAlert(err.message)));
  $('download-recovered').addEventListener('click', () => { if (state.recovered) download(new Blob([state.recovered], { type: 'text/plain' }), downloadName(state.sourceName)); });
  $('huff-input').addEventListener('change', async (e) => { const f = e.target.files[0]; if (!f) return; if (f.size > MAX_FILE) { $('inspector-empty').textContent = 'El archivo supera el límite de 20 MB.'; return; } try { state.inspected = parseFile(new Uint8Array(await f.arrayBuffer()), f.name); state.recovered = null; $('inspect-recovery').hidden = true; renderInspect(state.inspected); } catch (err) { $('inspector-content').hidden = true; $('inspector-empty').hidden = false; $('inspector-empty').textContent = err.message || 'No se pudo leer el archivo.'; } });
  $('decompress-button').addEventListener('click', async () => { try { const info = state.inspected; if (!info) return; const text = decode(info), recovered = textToBytes(text, info.encoding), expectedHash = info.sha, actualHash = await digest(recovered); const ok = recovered.length === info.origSize && actualHash.every((v, i) => v === expectedHash[i]); state.recovered = recovered; $('inspect-recovery').hidden = false; $('recovered-text').value = text; $('inspect-integrity-title').textContent = ok ? 'Integridad verificada · contenido recuperado' : 'Error de integridad'; $('inspect-integrity-detail').textContent = `${recovered.length.toLocaleString('es-MX')} bytes · SHA-256 ${ok ? 'coincide' : 'no coincide'} · contenido ${ok ? 'válido' : 'inválido'}.`; } catch (err) { $('inspect-integrity-title').textContent = 'No se pudo descomprimir'; $('inspect-integrity-detail').textContent = err.message; $('inspect-recovery').hidden = false; } });
  $('download-inspected').addEventListener('click', () => { if (state.recovered && state.inspected) download(new Blob([state.recovered], { type: 'text/plain' }), downloadName(state.inspected.name)); });
})();

