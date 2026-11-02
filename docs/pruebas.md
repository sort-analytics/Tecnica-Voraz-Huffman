# Pruebas y evidencias del proyecto Huffman

## 1. Objetivo

Documentar las pruebas realizadas sobre la aplicación web y la implementación de referencia en Python para verificar el funcionamiento del algoritmo de Huffman, la generación y lectura del formato `.huff`, la recuperación del contenido y la comprobación de integridad.

Los resultados registrados deben corresponder a ejecuciones reales. Los casos pendientes se marcarán como tales hasta que se ejecuten y se agreguen sus evidencias.

## 2. Entorno de pruebas

Completar esta información al ejecutar las pruebas de aceptación:

- **Fecha de ejecución:** Pendiente de registrar por cada sesión.
- **Sistema operativo:** Pendiente de registrar.
- **Navegador y versión:** Pendiente de registrar para las pruebas web.
- **Versión de Python:** Pendiente de registrar para las pruebas de referencia.
- **Versión de Node.js:** Pendiente de registrar cuando se use `node --check`.
- **Repositorio:** https://github.com/sort-analytics/Tecnica-Voraz-Huffman
- **Aplicación pública:** Pendiente de agregar la URL de Render cuando esté disponible.

## 3. Casos de prueba de aceptación

| ID | Caso | Procedimiento | Resultado esperado | Estado |
|---|---|---|---|---|
| P01 | Texto manual pequeño | Introducir `abracadabra`, analizar frecuencias, comprimir y descomprimir. | Frecuencias correctas, costo óptimo de 23 bits y recuperación del contenido original. | Prueba manual realizada; adjuntar evidencia |
| P02 | Archivo TXT UTF-8 | Cargar un archivo con tildes, `ñ`, emoji y saltos de línea; comprimir y recuperar. | Recuperación exacta de los bytes admitidos y SHA-256 coincidente. | Pendiente de evidencia |
| P03 | Archivo TXT Latin-1 | Cargar un archivo codificado en Latin-1 que no sea UTF-8 válido. | Identificación o selección correcta de la codificación y recuperación de los bytes originales. | Pendiente de evidencia |
| P04 | Libro de Project Gutenberg | Buscar un libro por título o autor, cargar el texto y ejecutar el flujo de compresión y recuperación. | Texto analizado correctamente y archivo recuperado con integridad verificada. | Pendiente de evidencia |
| P05 | Inspector independiente | Guardar un archivo `.huff`, recargar la página y abrir el archivo sin cargar el texto original. | Mostrar los metadatos disponibles, la tabla de símbolos, la información de compresión y permitir la descompresión. | Pendiente de evidencia |
| P06 | TXT externo | Probar un archivo nuevo proporcionado por una persona distinta de quien desarrolló la función. | Procesamiento correcto sin depender de una muestra fija y recuperación exacta del contenido. | Pendiente de evidencia |
| P07 | Archivo comprimido inválido | Intentar abrir un `.huff` truncado, corrupto o con cabecera inválida. | Mostrar un error comprensible sin bloquear la aplicación. | Pendiente de evidencia |
| P08 | Archivo vacío | Comprimir y recuperar un archivo sin contenido, si la interfaz admite este caso. | Comportamiento definido y recuperación correcta del contenido vacío. | Prueba automatizada incluida; validar interfaz |
| P09 | Texto de un solo símbolo | Probar una entrada formada por repeticiones de un mismo carácter. | Codificación y recuperación correctas, sin errores en la construcción del árbol. | Prueba automatizada incluida |
| P10 | Compatibilidad entre Python y JavaScript | Leer en un lenguaje un archivo `.huff` generado por el otro. | Lectura compatible y verificación correcta del contenido recuperado. | Prueba cruzada realizada en desarrollo; adjuntar evidencia |

## 4. Validaciones automatizadas realizadas

Según los resultados registrados durante el desarrollo, el 27 de octubre de 2026 se ejecutó el conjunto de pruebas del núcleo de Huffman.

### Núcleo de Huffman en Python

Comando ejecutado desde el directorio `Code_huffman/`:

```bash
python3 test_huffman.py
```

Resultado registrado:

```text
abracadabra: {'a': '0', 'c': '100', 'd': '101', 'b': '110', 'r': '111'}
repetitivo: (120000, 59234)
TODAS LAS PRUEBAS OK
```

Los casos incluidos contemplan texto pequeño, contenido vacío, un solo símbolo, Unicode, bytes de 0 a 255, datos aleatorios y texto repetitivo. El archivo de pruebas también compara los pesos obtenidos por Prim y Kruskal en el módulo MST existente.

**Nota:** los códigos concretos pueden cambiar si se modifica el criterio de desempate; lo importante es que sean válidos, reproducibles bajo el criterio definido y que la codificación y decodificación sean consistentes. Para `abracadabra`, el costo registrado es de 23 bits.

### Sintaxis de JavaScript

Comando registrado:

```bash
node --check Code_huffman/web/app.js
```

Resultado registrado: no se detectaron errores de sintaxis.

Esta comprobación valida la sintaxis del archivo, pero no sustituye las pruebas funcionales desde el navegador.

## 5. Pruebas manuales y compatibilidad del formato

Durante el desarrollo se registraron las siguientes comprobaciones:

- **Texto `abracadabra`:** se observó el análisis de los cinco símbolos, la codificación de 23 bits y la recuperación del texto con verificación SHA-256 y comparación byte a byte.
- **Tamaño del archivo:** el archivo `.huff` generado para este texto pequeño ocupó más espacio que el original debido a la cabecera y la tabla de símbolos. Esto es esperable en entradas pequeñas.
- **Python a JavaScript:** la aplicación JavaScript leyó un archivo generado por Python y recuperó `abracadabra`.
- **JavaScript a Python:** Python leyó un archivo generado por JavaScript con Unicode y emoji y validó el SHA-256.

Estas pruebas se consideran registradas en desarrollo. Antes de la entrega se deben adjuntar capturas o salidas reproducibles y registrar el entorno de ejecución cuando esté disponible.

## 6. Procedimiento para registrar cada prueba

Para cada ejecución, anotar:

1. ID y nombre del caso.
2. Fecha y hora de la prueba.
3. Responsable.
4. Sistema operativo y navegador, cuando corresponda.
5. Nombre y codificación del archivo de entrada.
6. Tamaño original en bytes.
7. Tamaño del archivo `.huff` en bytes.
8. Cantidad de bits codificados, cuando aplique.
9. Tamaño del contenido recuperado.
10. Resultado de SHA-256 y comparación byte a byte.
11. Resultado obtenido: aprobado, fallido o bloqueado.
12. Enlace a la captura, grabación o archivo de evidencia.

No se deben inventar tamaños, hashes, fechas, capturas ni resultados. Si un dato no se recopiló durante la prueba, debe marcarse como pendiente.

## 7. Evidencias pendientes

Antes de entregar, completar las siguientes actividades:

- [ ] Guardar una captura del análisis y la recuperación de `abracadabra`.
- [ ] Probar un TXT UTF-8 con tildes, emoji y saltos de línea.
- [ ] Probar un archivo Latin-1 y documentar el comportamiento observado.
- [ ] Probar un libro de Project Gutenberg.
- [ ] Abrir un `.huff` desde el inspector después de recargar la página y sin cargar el original.
- [ ] Probar un TXT nuevo proporcionado por otra persona.
- [ ] Probar el manejo de un archivo `.huff` inválido o truncado.
- [ ] Registrar la comparación de tamaños, la verificación SHA-256 y la comparación byte a byte.
- [ ] Probar la aplicación publicada en Render y registrar su URL pública.
- [ ] Adjuntar capturas o grabaciones y enlazarlas desde este documento.

## 8. Ubicación y organización de las evidencias

Se recomienda guardar las evidencias del equipo en una carpeta organizada dentro del repositorio, por ejemplo:

```text
docs/
├── planeacion.md
├── formato-huff.md
├── pruebas.md
└── evidencias/
    ├── P01-abracadabra.png
    ├── P02-txt-utf8.png
    ├── P03-txt-latin1.png
    ├── P04-gutenberg.png
    ├── P05-inspector.png
    ├── P06-txt-externo.png
    ├── P07-archivo-invalido.png
    └── P10-compatibilidad.png
```

Esta estructura es una propuesta: los nombres deben corresponder a archivos de evidencia que realmente existan. No se deben crear archivos vacíos para aparentar que una prueba está documentada.

## 9. Criterios generales de aceptación

La validación final debe confirmar que:

- El algoritmo genera códigos válidos y permite recuperar el contenido.
- Los archivos `.huff` cumplen el formato documentado en [`formato-huff.md`](formato-huff.md).
- La información de tamaño y SHA-256 se verifica durante la recuperación.
- El inspector puede analizar un archivo comprimido sin necesitar el original.
- Los errores de archivos inválidos se manejan de forma controlada.
- Las pruebas requeridas están ejecutadas y respaldadas por evidencia.
- La aplicación desplegada funciona desde su URL pública.
