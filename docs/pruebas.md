# Pruebas de aceptación y evidencias

Registra fecha, navegador/sistema, archivo de entrada, tamaños mostrados, resultado SHA-256 y captura o grabación en GitHub antes de entregar. No se deben completar resultados con datos supuestos.

| Caso | Procedimiento | Resultado esperado | Evidencia |
| --- | --- | --- | --- |
| Texto manual pequeño | Escribe `abracadabra`, analiza y compara frecuencias/costo con el cálculo manual. | `a:5`, `b:2`, `r:2`, `c:1`, `d:1`; costo óptimo de 23 bits. Los códigos pueden variar si cambia el desempate, pero el costo debe coincidir. | Pendiente |
| TXT UTF-8 | Carga un texto con tildes, ñ, emoji, saltos de línea y BOM opcional; comprime y verifica. | El tamaño binario recuperado es igual y SHA-256 coincide; descarga TXT recuperable. | Pendiente |
| TXT Latin-1 | Carga un archivo no válido como UTF-8 con bytes de 0 a 255 o texto Latin-1; comprime y verifica. | Codificación identificada como Latin-1 y bytes recuperados idénticos. | Pendiente |
| Libro Gutenberg | Busca por título o autor, carga texto plano y comprime. | El texto seleccionado se analiza y descarga; el archivo recuperado verifica integridad. | Pendiente |
| Inspector independiente | Cierra/recarga la página, abre un `.huff` guardado sin cargar el original. | Muestra cabecera, tamaños, ahorro, tabla/códigos, árbol, bits y permite descomprimir después de inspeccionar. | Pendiente |
| Archivo distinto al de desarrollo | Carga un TXT nuevo proporcionado por otra persona y completa todo el flujo. | No depende de una muestra fija; recuperación byte a byte idéntica. | Pendiente |
| Archivo inválido | Abre un `.txt` o un `.huff` truncado como archivo comprimido. | Se muestra un mensaje claro; la página sigue operativa. | Pendiente |

## Validaciones realizadas en desarrollo

- 27 oct 2026 — `py test_huffman.py`: **TODAS LAS PRUEBAS OK**. Incluye `abracadabra`, vacío, un símbolo, Unicode, bytes 0–255, datos aleatorios, texto repetitivo y el ejemplo MST existente.
- 27 oct 2026 — prueba manual en navegador de `abracadabra`: cinco símbolos, frecuencias/códigos mostrados, 23 bits codificados y recuperación verificada con SHA-256 y comparación byte a byte. En este texto pequeño el archivo `.huff` ocupa más que el original; la interfaz muestra el aumento.
- 27 oct 2026 — compatibilidad cruzada del formato: JavaScript leyó un archivo generado por Python y recuperó `abracadabra`; Python leyó un archivo generado por JavaScript con Unicode y emoji, y validó SHA-256.
- `node --check Code_huffman/web/app.js`: sin errores de sintaxis.

Las pruebas de Gutenberg, carga de archivos por el selector del navegador, archivo ajeno al desarrollo y deployment público siguen pendientes de realizar y guardar con capturas/evidencias del equipo.

## Resultado de prueba incluido en el núcleo de referencia

`Code_huffman/test_huffman.py` contiene casos automatizados para texto pequeño, archivo vacío, un solo símbolo, Unicode, bytes 0–255, bytes aleatorios y texto repetitivo. También compara los pesos obtenidos por Prim y Kruskal en el módulo MST legado. Ejecuta `py test_huffman.py` desde `Code_huffman/` y registra aquí salida, fecha y responsable antes de publicar.

## Evidencia de integridad

Para cada prueba de ida y vuelta, conserva el nombre del original y recuperado, tamaños exactos, resultado del SHA-256, comparación byte a byte, captura del inspector y archivo comprimido de ejemplo si se permite su distribución. Evita publicar libros con restricciones ajenas al dominio público.

