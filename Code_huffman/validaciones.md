# Validaciones adicionales — Persona 1

## Archivos y ubicación
Colocar `test_archivos.py` en la carpeta `Code_huffman/`, al mismo nivel que:
- `huffman_core.py`
- `mst.py`
- `test_huffman.py`

## 1. Ejecutar pruebas automatizadas de Python

Desde una terminal ubicada en `Code_huffman/`:

```bash
python test_huffman.py
python test_archivos.py
```

En Windows puede ser necesario usar `py` en lugar de `python`.

La segunda prueba verifica:
- Texto ASCII.
- Tildes, ñ, emoji y saltos de línea UTF-8.
- Texto repetitivo.
- Bytes 0 a 255.
- Archivo vacío.
- Un solo símbolo.
- Archivos truncados.
- Firma y versión incorrectas.
- Compatibilidad de lectura de un archivo generado desde la web (si se proporciona).

Si falla una prueba de archivo dañado, no oculten el fallo: revisen `parse_file()` en `huffman_core.py` y registren la corrección realizada.

## 2. Compatibilidad JavaScript → Python

1. Abrir la aplicación web local.
2. Cargar un TXT que contenga: `¡Hola, señor! 😀`.
3. Comprimir y descargar el archivo `.huff`.
4. Copiarlo a `Code_huffman/huff_generado_web.huff`.
5. Ejecutar `python test_archivos.py`.
6. Confirmar que la prueba `test_archivo_generado_por_javascript` pasa.

## 3. Compatibilidad Python → JavaScript

1. Ejecutar el programa Python o generar un `.huff` usando `huffman_core.py`.
2. Abrir la aplicación web.
3. Entrar al Inspector y abrir el `.huff`.
4. Descomprimir.
5. Comparar el texto recuperado con el original, incluyendo tildes y emoji.

## 4. Pruebas manuales obligatorias en navegador

| Caso | Procedimiento | Resultado que se debe comprobar |
|---|---|---|
| TXT pequeño | Cargar `abracadabra` | Frecuencias: a=5, b=2, r=2, c=1, d=1; costo Huffman 23 bits |
| TXT UTF-8 | Cargar texto con á, é, ñ, emoji y saltos de línea | Recuperación idéntica |
| TXT grande | Cargar un TXT de varios MB | La página no se bloquea ni produce errores |
| Gutenberg | Buscar un título o autor y descargar un libro | Aparece el texto y puede comprimirse |
| Inspector independiente | Recargar la página y abrir un `.huff` guardado | Muestra metadatos y permite descomprimir |
| Archivo incorrecto | Abrir un `.txt` como si fuera `.huff` | Muestra error entendible y la página sigue funcionando |
| Archivo truncado | Abrir una copia de `.huff` a la que se le quitaron bytes | Rechaza el archivo sin romper la página |
| Límite de tamaño | Intentar cargar un archivo mayor al límite documentado | Muestra un mensaje claro |

## 5. Evidencias que deben guardar

Crear una carpeta `evidencias/` y guardar capturas de:
1. Resultado de `python test_huffman.py`.
2. Resultado de `python test_archivos.py`.
3. Análisis de `abracadabra`.
4. Métricas después de comprimir.
5. Inspector mostrando un `.huff`.
6. Texto recuperado y verificación de integridad.
7. Búsqueda y descarga de Gutenberg.
8. Mensaje de error al abrir un archivo inválido.

No escriban “prueba exitosa” si no se ejecutó realmente. Anoten navegador, sistema operativo y fecha de ejecución.
