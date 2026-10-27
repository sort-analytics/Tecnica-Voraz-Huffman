# Formato HUFF, versión 1

El formato propio usa la extensión `.huff` y la firma ASCII `HUFF`. Todos los enteros multibyte se almacenan en orden big-endian. La cabecera y la tabla preceden a los datos comprimidos.

| Desplazamiento | Tamaño | Campo | Descripción |
| ---: | ---: | --- | --- |
| 0 | 4 bytes | Firma | `HUFF` |
| 4 | 1 byte | Versión | `1` |
| 5 | 1 byte | Codificación | `0` UTF-8; `1` Latin-1 |
| 6 | 1 byte | Flags | Reservado; debe ser `0` |
| 7 | 8 bytes | Tamaño original | Bytes antes de comprimir |
| 15 | 8 bytes | Cantidad de símbolos | Caracteres Unicode del texto |
| 23 | 32 bytes | SHA-256 | Hash del contenido original en bytes |
| 55 | 4 bytes | Símbolos únicos | Número de filas de la tabla |
| 59 | 8 bytes | Bits válidos | Número de bits Huffman, sin padding |
| 67 | 2 bytes | Longitud del nombre | Bytes UTF-8 del nombre de origen |
| 69 | variable | Nombre | Nombre UTF-8 de origen, limitado a 65 535 bytes |
| Después del nombre | 8 bytes × símbolos únicos | Tabla | Por fila: código Unicode del símbolo (uint32) y frecuencia (uint32) |
| Después de la tabla | `ceil(bits válidos / 8)` bytes | Datos | Bits Huffman empaquetados, primero el bit más significativo |

La longitud exacta del archivo debe ser la cabecera más nombre más tabla más `ceil(bits válidos / 8)`. Los bits sobrantes del último byte son padding y se ignoran. La tabla se ordena por punto de código Unicode. La reconstrucción aplica el mismo algoritmo determinista: ante frecuencias iguales se conserva el orden de inserción; las hojas se insertan en orden Unicode ascendente. En un árbol de un solo símbolo, el código convencional usado por el proyecto es `0`.

La integridad se comprueba calculando SHA-256 sobre los bytes recuperados, además de comparar su longitud con el tamaño original. No hay texto original duplicado en el archivo. El hash sirve para detectar corrupción, no para autenticar el emisor.

## Correspondencia con Python

`Code_huffman/huffman_core.py` implementa la misma cabecera con `HEADER_FMT = ">4sBBBQQ32sIQH"`; `Code_huffman/web/app.js` genera y lee los mismos campos. Esto permite que un archivo `.huff` producido por cualquiera de las versiones sea leído por la otra.

