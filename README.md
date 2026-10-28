# Huffman Lab — compresor web voraz

Aplicación web académica para analizar, comprimir, inspeccionar y recuperar archivos de texto usando una implementación propia del algoritmo de Huffman. La interfaz está en `Code_huffman/web/` y no necesita backend para la compresión: el texto permanece en el navegador. La búsqueda y descarga de obras consulta el servicio gratuito Gutendex y los textos disponibles de Project Gutenberg.

## Ejecutar localmente

Requiere un navegador moderno y Python 3 para servir los archivos estáticos. Desde `Code_huffman/web/`:

```powershell
py -m http.server 8000
```

Abre <http://localhost:8000>. También se puede ejecutar con cualquier servidor estático. Para usar SHA-256, el navegador debe estar en un contexto seguro (`localhost` o HTTPS); abrir `index.html` directamente como `file://` puede desactivar Web Crypto.

## Flujo de uso

1. Carga un `.txt` local o busca una obra por título, autor o palabra clave.
2. Pulsa **Analizar texto** para ver frecuencias, códigos, fusiones voraces y árbol.
3. Pulsa **Construir árbol y comprimir** para crear el archivo binario `.huff` y revisar las métricas.
4. Descarga el `.huff` y, si quieres, verifica la recuperación byte a byte.
5. En **Inspector .huff**, abre únicamente el archivo comprimido para consultar cabecera, tabla, árbol y una muestra de bits. Pulsa **Descomprimir archivo** para mostrar y descargar el texto recuperado.

## Algoritmo

Se cuentan caracteres Unicode. Una cola de prioridad selecciona los dos nodos de menor frecuencia y los fusiona hasta que queda la raíz. El orden de símbolos y un contador de inserción resuelven empates de forma determinista. Las aristas izquierda y derecha representan `0` y `1`. La secuencia se empaqueta en bits de mayor a menor dentro de cada byte. Un archivo con un solo símbolo usa el código `0`.

El formato almacena tabla de frecuencias, tamaño y codificación original, cantidad exacta de símbolos y bits, nombre de origen y SHA-256 del contenido. El `.txt` original no se guarda dentro del archivo. Consulta [la especificación HUFF v1](docs/formato-huff.md).

## Verificación y pruebas

El repositorio incluye el núcleo Python original y su prueba de ida y vuelta:

```powershell
cd Code_huffman
py test_huffman.py
```

Casos mínimos de aceptación y evidencias requeridas están en [docs/pruebas.md](docs/pruebas.md). La aplicación web implementa el mismo contrato binario que `huffman_core.py`, así que el `.huff` se puede inspeccionar y recuperar desde ambas implementaciones.

## Tecnologías

- HTML, CSS y JavaScript sin framework ni servicio de pago.
- Web Crypto API para SHA-256.
- Gutendex / Project Gutenberg para buscar obras de dominio público con texto disponible.
- Python del repositorio conservado como implementación de referencia del formato.

## Equipo y entrega

- Equipo e integrantes: **pendiente de completar por el equipo**.
- Repositorio GitHub: <https://github.com/sort-analytics/Tecnica-Voraz-Huffman>.
- GitHub Projects: [Backlog-Visualizador web de algoritmos](https://github.com/orgs/sort-analytics/projects/3), proyecto previo visible de la organización; falta incorporar el backlog Huffman y acordar responsables con el equipo.
- Hosting: **Render Static Site**. La configuración Blueprint está en [`render.yaml`](render.yaml); publica `Code_huffman/web/` sin paso de compilación y se actualiza con cada commit a `main`.
- URL pública: **pendiente de crear el servicio en Render**. Abre [New Static Site en Render](https://dashboard.render.com/select-repo?type=static), conecta `sort-analytics/Tecnica-Voraz-Huffman`, selecciona `main` y confirma la configuración detectada. Tras el primer deploy, copia aquí la URL `*.onrender.com` y verifica carga, compresión, descarga e inspector sobre HTTPS.
- Reporte técnico PDF y evidencias: **pendientes de generar tras las pruebas reales**.

La lista de trabajo inicial, campos de responsables y decisiones pendientes está en [docs/planeacion.md](docs/planeacion.md). No se deben presentar los enlaces o evidencias pendientes como si ya existieran.

Render sirve el sitio estático desde su CDN con HTTPS y puede desplegarlo automáticamente al recibir commits en la rama conectada. No necesita servidor de aplicación, secretos ni paso de compilación. La búsqueda en Gutendex sí necesita conexión a Internet desde el navegador.

## Uso de IA y limitaciones

IA generativa apoyó la extracción de requisitos, el diseño de interfaz, la implementación inicial y la documentación. El equipo debe validar los casos de prueba y comprender especialmente la cola de prioridad, el empaquetado de bits, los campos del archivo y la verificación SHA-256 antes de entregar.

La interfaz necesita conexión para Gutendex y para descargar libros; la compresión e inspección del archivo `.huff` funcionan localmente. Se limita la entrada a 20 MiB por navegador. Huffman puede aumentar archivos pequeños o datos de alta entropía porque la cabecera y tabla tienen coste; las métricas muestran ese resultado real.
