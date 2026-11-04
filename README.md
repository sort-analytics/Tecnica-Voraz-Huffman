# Huffman Lab — Compresor de texto mediante el algoritmo de Huffman

## 1. Descripción del proyecto

**Huffman Lab** es una aplicación web académica desarrollada para estudiar e implementar el algoritmo de Huffman, una técnica de compresión sin pérdida basada en la estrategia voraz (*Greedy Algorithm*).

El sistema permite analizar textos, calcular frecuencias de aparición, construir el árbol de Huffman, generar códigos binarios y crear archivos comprimidos con formato propio `.huff`. También permite inspeccionar la estructura de un archivo comprimido y recuperar el contenido original.

El proyecto se desarrolla para la asignatura **Análisis de Algoritmos, periodo 2026B**, con el propósito de relacionar los conceptos teóricos de algoritmos voraces con una implementación funcional.

## 2. Objetivos

### Objetivo general

Desarrollar una aplicación web que implemente el algoritmo de Huffman para comprimir y descomprimir archivos de texto, permitiendo visualizar el procedimiento, evaluar la eficiencia de la compresión y verificar la integridad de los datos recuperados.

### Objetivos específicos

- Calcular la frecuencia de aparición de los símbolos de un texto.
- Construir un árbol binario mediante selecciones voraces.
- Asignar códigos binarios a los símbolos.
- Empaquetar los bits y generar archivos `.huff`.
- Medir el tamaño original, el tamaño comprimido y el ahorro obtenido.
- Inspeccionar archivos comprimidos sin necesitar el texto original.
- Recuperar el contenido y comprobar su integridad.
- Permitir el uso de archivos TXT y textos disponibles mediante Project Gutenberg.

## 3. Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| Carga de archivos | Permite seleccionar archivos de texto `.txt` desde el equipo. |
| Búsqueda de libros | Consulta obras disponibles mediante Gutendex y Project Gutenberg. |
| Análisis de frecuencias | Cuenta las apariciones de los símbolos del texto. |
| Construcción del árbol | Combina los nodos con menor frecuencia mediante la estrategia voraz. |
| Generación de códigos | Asigna códigos binarios a cada símbolo. |
| Compresión | Genera un archivo binario con extensión `.huff`. |
| Métricas | Muestra tamaños, ahorro, porcentaje de reducción y cantidad de símbolos. |
| Visualización | Presenta la tabla de frecuencias, los códigos y el árbol de Huffman. |
| Inspector | Examina la cabecera, la tabla, los bits y los metadatos de un archivo `.huff`. |
| Descompresión | Recupera el contenido sin depender del TXT original. |
| Integridad | Comprueba el tamaño recuperado y el hash SHA-256. |

## 4. Tecnologías utilizadas

- **HTML5:** estructura de la interfaz.
- **CSS3:** diseño y presentación visual.
- **JavaScript:** implementación web del algoritmo, compresión, inspección y recuperación.
- **Python 3:** implementación de referencia, pruebas automatizadas y validación del formato.
- **Web Crypto API:** cálculo de SHA-256 en el navegador.
- **Gutendex / Project Gutenberg:** consulta de obras disponibles para utilizar como entrada.
- **Git y GitHub:** control de versiones y colaboración.
- **Render Static Site:** plataforma prevista para publicar la aplicación.

La compresión y la inspección se realizan en el navegador. La búsqueda de obras necesita conexión a Internet.

## 5. Funcionamiento del algoritmo

El algoritmo de Huffman genera códigos de longitud variable a partir de las frecuencias de los símbolos.

El procedimiento general es:

1. Leer el texto de entrada y contar las apariciones de cada símbolo.
2. Crear un nodo por cada símbolo, utilizando su frecuencia como peso.
3. Seleccionar los dos nodos de menor frecuencia.
4. Crear un nodo padre cuya frecuencia sea la suma de ambos nodos.
5. Repetir las fusiones hasta obtener un único árbol.
6. Asignar `0` a las ramas izquierdas y `1` a las ramas derechas.
7. Recorrer el árbol para obtener el código de cada símbolo.
8. Sustituir los símbolos del texto por sus códigos binarios.
9. Empaquetar los bits en bytes y guardar los datos junto con la información necesaria para reconstruir el árbol.

Los desempates se resuelven de forma determinista para que las implementaciones compatibles puedan reconstruir el mismo árbol. Para un texto compuesto por un único símbolo, el proyecto utiliza el código `0`.

Huffman es una técnica de compresión sin pérdida: cuando el archivo se recupera correctamente, los bytes originales deben conservarse exactamente.

## 6. Formato de archivo `.huff`

El proyecto utiliza un formato binario propio denominado **HUFF versión 1**.

Su estructura contiene:

| Campo | Propósito |
|---|---|
| Firma `HUFF` | Identifica el formato. |
| Versión | Permite identificar la versión del archivo. |
| Codificación | Indica UTF-8 o Latin-1. |
| Flags | Campo reservado que debe ser cero. |
| Tamaño original | Número de bytes del contenido original. |
| Cantidad de símbolos | Número de caracteres Unicode del texto. |
| SHA-256 | Permite comprobar la integridad del contenido recuperado. |
| Símbolos únicos | Número de entradas de la tabla. |
| Bits válidos | Cantidad exacta de bits Huffman, excluyendo el padding. |
| Nombre de origen | Nombre original codificado en UTF-8. |
| Tabla de frecuencias | Código Unicode y frecuencia de cada símbolo. |
| Datos comprimidos | Secuencia de bits Huffman empaquetada en bytes. |

Los enteros multibyte se almacenan en orden *big-endian*. Los bits se empaquetan empezando por el más significativo de cada byte.

El archivo comprimido no contiene una copia del texto original. La tabla de frecuencias permite reconstruir el árbol mediante el algoritmo determinista del proyecto.

La especificación completa se encuentra en [`docs/formato-huff.md`](docs/formato-huff.md).

## 7. Métricas de compresión

La aplicación compara el tamaño del archivo original con el tamaño del archivo `.huff`.

Las métricas principales son:

- **Tamaño original:** cantidad de bytes del contenido de entrada.
- **Tamaño comprimido:** cantidad de bytes del archivo `.huff`, incluidos su cabecera, nombre, tabla y datos.
- **Ahorro:** tamaño original menos tamaño comprimido.
- **Reducción porcentual:** ahorro dividido entre el tamaño original, multiplicado por 100.
- **Símbolos únicos:** cantidad de símbolos diferentes presentes en el texto.

La reducción porcentual se calcula mediante:

`((tamaño original - tamaño comprimido) / tamaño original) × 100`

Un ahorro negativo significa que el archivo comprimido ocupa más espacio que el original. Esto puede ocurrir con textos pequeños, debido al coste de la cabecera y de la tabla de frecuencias.

## 8. Inspector y recuperación

El inspector permite cargar un archivo `.huff` sin seleccionar previamente el TXT original.

A partir de la información almacenada, puede examinarse la cabecera, las métricas, la tabla de frecuencias, los códigos reconstruidos, el árbol y una representación de los bits comprimidos.

Después de inspeccionar el archivo, el usuario puede ejecutar explícitamente la descompresión y descargar el contenido recuperado.

La integridad se comprueba mediante el tamaño original y el hash SHA-256 de los bytes recuperados. SHA-256 sirve para detectar modificaciones accidentales o corrupción; no autentica al autor del archivo.

## 9. Instalación y ejecución local

### Requisitos

- Python 3 instalado.
- Un navegador web moderno.
- Git, si se desea clonar el repositorio.

### Iniciar la aplicación

Desde la carpeta del repositorio, ejecuta:

```bash
cd Code_huffman/web
python3 -m http.server 8000
```

En Windows también puede utilizarse:

```powershell
py -m http.server 8000
```

Abre en el navegador:

http://localhost:8000

Se recomienda acceder mediante `localhost` o HTTPS para disponer de las funciones criptográficas del navegador.

### Ejecutar las pruebas de Python

Desde la raíz del repositorio:

```bash
cd Code_huffman
python3 test_huffman.py
python3 test_archivos.py
```

En Windows se puede utilizar `py` en lugar de `python3`, según la instalación.

## 10. Pruebas y validación

Durante las pruebas de desarrollo se obtuvieron los siguientes resultados:

| Prueba | Resultado registrado |
|---|---|
| Pruebas del núcleo Huffman | Todas las pruebas incluidas en `test_huffman.py` finalizaron correctamente. |
| Texto `abracadabra` | Se obtuvieron las frecuencias y códigos esperados por la implementación. |
| Texto repetitivo | Se probó la codificación y recuperación de un texto de mayor tamaño. |
| Archivo vacío | Superó la prueba automatizada. |
| Un solo símbolo | Superó la prueba automatizada. |
| Unicode, tildes y emoji | Superó la prueba automatizada. |
| Bytes Latin-1 | Superó la prueba automatizada. |
| Firma o versión inválida | Los archivos inválidos fueron rechazados en las pruebas. |
| Archivo truncado | Fue rechazado en las pruebas. |
| Compatibilidad Python-JavaScript | Se validó mediante un archivo `.huff` generado desde la aplicación web. |

Las pruebas anteriores corresponden a resultados registrados durante el desarrollo. Las pruebas con Project Gutenberg, un archivo nuevo proporcionado por otra persona y el sitio público deben documentarse con fecha y evidencia cuando se realicen.

El registro de casos de aceptación se encuentra en [`docs/pruebas.md`](docs/pruebas.md).

## 11. Estructura del repositorio

```text
Tecnica-Voraz-Huffman/
├── Code_huffman/
│   ├── app.py
│   ├── gutenberg.py
│   ├── huffman_core.py
│   ├── mst.py
│   ├── test_huffman.py
│   ├── test_archivos.py
│   ├── validaciones.md
│   └── web/
├── docs/
│   ├── formato-huff.md
│   ├── planeacion.md
│   └── pruebas.md
├── README.md
├── render.yaml
└── .gitignore
```

Los archivos de documentación y la configuración deben mantenerse sincronizados con el estado real del proyecto.

## 12. Publicación

La aplicación está preparada para publicarse como sitio estático mediante Render, utilizando la configuración de `render.yaml`.

**URL pública:** pendiente de confirmar después del despliegue y de las pruebas de funcionamiento.

Una vez publicado el sitio, se debe verificar:

- Acceso mediante HTTPS.
- Carga de archivos TXT.
- Búsqueda y selección de obras.
- Compresión y descarga del archivo `.huff`.
- Inspección y descompresión.
- Comprobación de integridad.

## 13. Organización del equipo

Integrantes:

López Olivera Alejandro Esaú

Ramirez Perez Oscar Emiliano

Rodriguez Hernandez Luis Giovanni

Ruiz López Carlos Aarón

Repositorio: https://github.com/sort-analytics/Tecnica-Voraz-Huffman

GitHub Projects: https://github.com/orgs/sort-analytics/projects/3

Reporte técnico: incorporar el PDF final cuando esté elaborado.

Evidencias: registrar capturas, resultados de las pruebas y verificaciones de integridad en el repositorio.

El tablero de GitHub Projects debe reflejar el estado real de cada tarea, su responsable y el resultado esperado.

## 14. Uso de inteligencia artificial

Se utilizaron herramientas de inteligencia artificial como apoyo para analizar los requisitos, desarrollar y revisar partes de la implementación, organizar la documentación y resolver problemas durante las pruebas.

Los resultados deben validarse mediante ejecución del código, pruebas automatizadas y comprobaciones de integridad. Los integrantes son responsables de comprender y poder explicar el funcionamiento del algoritmo, la construcción del árbol, el empaquetado de bits, el formato binario y la recuperación del archivo.

## 15. Limitaciones conocidas

- Los archivos pequeños pueden aumentar de tamaño debido a los metadatos y la tabla.
- La búsqueda y descarga de obras requieren conexión a Internet.
- La aplicación tiene un límite de entrada de 20 MiB, según la implementación documentada.
- La compatibilidad del formato depende del cumplimiento de la especificación HUFF v1.
- La publicación pública, las pruebas pendientes y las evidencias finales deben confirmarse antes de la entrega.

---

**Proyecto académico — Análisis de Algoritmos, 2026B.**
