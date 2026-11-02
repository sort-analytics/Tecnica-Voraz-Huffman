# Planeación del proyecto: Técnica Voraz de Huffman

## 1. Objetivo del proyecto

Desarrollar una aplicación web que permita comprender y experimentar con la técnica voraz de compresión de datos mediante el algoritmo de Huffman.

La aplicación permitirá introducir texto desde un archivo `.txt` o desde un libro de Project Gutenberg, analizar sus frecuencias, construir el árbol de Huffman, generar códigos binarios, comprimir el contenido en un archivo propio `.huff` y recuperar posteriormente el texto original.

Además, se mostrarán métricas de compresión y se permitirá inspeccionar los metadatos de un archivo comprimido sin necesidad de cargar previamente el texto original.

## 2. Datos generales del equipo

- **Nombre del equipo:** Pendiente de acordar.
- **Integrantes:** Pendiente de completar con los nombres de los integrantes.
- **Responsable de coordinación:** Pendiente de acordar.
- **Repositorio de GitHub:** https://github.com/sort-analytics/Tecnica-Voraz-Huffman
- **GitHub Projects:** https://github.com/orgs/sort-analytics/projects/3
- **Tecnologías principales:** HTML, CSS y JavaScript para la aplicación web; Python como implementación de referencia y apoyo para las pruebas.
- **Plataforma de publicación:** Render Static Site.
- **Directorio de la aplicación web:** `Code_huffman/web/`
- **Formato de archivo propio:** `.huff`, versión 1, con firma `HUFF`.
- **Especificación del formato:** [`formato-huff.md`](formato-huff.md)

### Organización del trabajo

Para facilitar la coordinación, se propone dividir las actividades entre dos responsables de trabajo, sin excluir la colaboración y revisión mutua.

- **Persona 1:** apoyo en la implementación, pruebas automatizadas, validación de archivos y registro de resultados.
- **Persona 2:** documentación técnica, actualización de la planeación, evidencias, seguimiento del tablero y apoyo en la publicación de la aplicación.

Los nombres definitivos y la distribución acordada deberán registrarse en el tablero de GitHub Projects.

## 3. Alcance y funcionalidades

La aplicación debe cubrir las siguientes funcionalidades:

1. **Entrada de datos:** permitir cargar archivos `.txt` desde el equipo y obtener texto de Project Gutenberg.
2. **Análisis de frecuencias:** calcular las frecuencias de los caracteres del texto de entrada.
3. **Construcción del árbol:** aplicar el algoritmo voraz de Huffman y generar códigos binarios reproducibles.
4. **Compresión:** empaquetar los bits y generar un archivo `.huff` con su cabecera y tabla de frecuencias.
5. **Inspección:** mostrar los metadatos, la tabla de símbolos y la información de compresión del archivo.
6. **Descompresión:** recuperar el contenido original a partir del archivo `.huff`.
7. **Verificación de integridad:** comprobar el tamaño esperado y el hash SHA-256 del contenido recuperado.
8. **Métricas:** mostrar el tamaño original, el tamaño comprimido, la cantidad de bits codificados y la relación de compresión.
9. **Visualización:** presentar la tabla de frecuencias, los códigos asignados y el árbol de Huffman.
10. **Validación:** ejecutar pruebas con textos pequeños, archivos externos y libros de mayor tamaño.

## 4. Diseño general de la interfaz

La interfaz se organizará en un flujo de trabajo guiado:

- **Entrada:** selección de un archivo de texto o carga de contenido de Project Gutenberg.
- **Análisis:** presentación de las frecuencias, los códigos y el árbol de Huffman.
- **Resultados:** visualización de las métricas y descarga del archivo comprimido.
- **Inspector:** lectura de la información contenida en un archivo `.huff` seleccionado de forma independiente.
- **Recuperación:** descompresión explícita y comprobación de integridad.

El diseño propuesto utiliza un encabezado oscuro, paneles diferenciados y tablas para facilitar la lectura de los resultados.

## 5. Backlog de actividades

Los estados indicados representan la situación conocida al preparar esta planeación. Antes de la entrega, el equipo deberá actualizar cada tarjeta con el resultado de su validación.

| Actividad | Resultado esperado | Responsable propuesto | Estado |
|---|---|---|---|
| Calcular las frecuencias de los caracteres | Tabla de frecuencias correcta para el texto de entrada | Persona 1 | Implementado; validar |
| Construir el árbol voraz de Huffman | Árbol y códigos reproducibles, incluidos los casos de empate | Persona 1 | Implementado; validar |
| Codificar y empaquetar los bits | Flujo binario y manejo correcto de los bits válidos del último byte | Persona 1 | Implementado; validar |
| Definir el formato `.huff` | Especificación documentada de cabecera, tabla y datos comprimidos | Persona 2 | Documentado; revisar |
| Descomprimir y verificar integridad | Recuperación del texto y comprobación de tamaño y SHA-256 | Persona 1 | Implementado; validar |
| Integrar la interfaz web | Entrada, análisis, métricas, tablas y visualización | Persona 1 | Implementado; validar |
| Integrar Project Gutenberg | Búsqueda, selección y carga de un texto de prueba | Persona 2 | Implementado; validar |
| Probar un archivo TXT externo | Evidencia de carga y procesamiento de un archivo nuevo | Persona 1 | Pendiente de evidencia |
| Probar un libro de Project Gutenberg | Resultado documentado de compresión y recuperación de un libro | Persona 2 | Pendiente de evidencia |
| Probar casos límite y codificaciones | Pruebas para texto pequeño, archivo vacío si aplica, un solo símbolo y Latin-1 | Persona 1 | Pendiente de completar |
| Documentar los resultados de las pruebas | Casos, resultados obtenidos, errores y capturas en `docs/pruebas.md` | Persona 2 | En proceso |
| Revisar la documentación principal | README coherente con las funciones, instrucciones y estado real del proyecto | Persona 2 | En proceso |
| Actualizar el tablero de GitHub Projects | Tareas con responsables, estados y resultados esperados | Persona 2 | Pendiente de revisar |
| Completar los datos del equipo | Integrantes, coordinación y acuerdos registrados | Todo el equipo | Pendiente |
| Publicar la aplicación en Render | URL pública funcional y pruebas realizadas desde HTTPS | Persona 2 | Pendiente de confirmar |
| Preparar el reporte técnico en PDF | Documento final con explicación, resultados, evidencias y enlaces | Todo el equipo | Pendiente de confirmar |

**Nota:** los responsables son una propuesta de distribución. El equipo debe confirmar que corresponden a las tareas realmente realizadas y actualizar los estados de acuerdo con la evidencia disponible.

## 6. Plan de pruebas y validación

La validación se realizará en Python y desde la aplicación web. Se contemplan los siguientes escenarios:

- Texto pequeño, como `abracadabra`, para revisar los códigos generados.
- Texto repetitivo para comprobar el comportamiento con frecuencias desiguales.
- Archivo `.txt` nuevo, seleccionado desde el navegador.
- Libro de Project Gutenberg.
- Archivo `.huff` generado por la aplicación web e inspeccionado por separado.
- Descompresión y comparación del texto recuperado con el original.
- Comprobación del tamaño y del SHA-256.
- Validación de codificaciones admitidas y casos límite.

Los comandos de ejecución, los resultados reales y las evidencias se registrarán en [`pruebas.md`](pruebas.md).

No se considerará una prueba completada únicamente porque el código exista: debe ejecutarse y registrarse su resultado.

## 7. Seguimiento mediante GitHub Projects

Se utilizará el tablero del equipo disponible en:

https://github.com/orgs/sort-analytics/projects/3

El equipo deberá confirmar si se reutiliza el tablero existente y agregar las tareas correspondientes a este proyecto.

Se propone utilizar las siguientes columnas:

1. **Backlog:** actividades identificadas que todavía no se han priorizado.
2. **Por hacer:** actividades seleccionadas que aún no comienzan.
3. **En progreso:** actividades en desarrollo.
4. **En revisión:** actividades implementadas que requieren pruebas o validación.
5. **Terminado:** actividades verificadas y respaldadas por resultados o evidencias.

Cada tarjeta deberá incluir, cuando corresponda, un responsable, una descripción, el resultado esperado y su estado. El tablero complementa el historial de cambios del repositorio, pero no lo sustituye.

## 8. Plan de publicación en Render

La aplicación web está organizada como un sitio estático. La configuración prevista se encuentra en `render.yaml` y apunta al directorio `Code_huffman/web/`.

Pasos para la publicación:

1. Acceder al panel de Render.
2. Crear un servicio **Static Site** conectado al repositorio de GitHub.
3. Seleccionar la rama `main`.
4. Verificar que el directorio publicado sea `Code_huffman/web/`.
5. Confirmar que la configuración de compilación y publicación corresponda con `render.yaml`.
6. Esperar a que finalice el despliegue.
7. Registrar la URL pública asignada por Render.
8. Abrir la aplicación desde esa URL y probar la carga de texto, la compresión, la descarga, el inspector y la descompresión.
9. Documentar los resultados y cualquier problema encontrado.

**Estado de publicación:** pendiente de confirmar hasta que exista una URL pública accesible y se hayan completado las pruebas en el sitio desplegado.

## 9. Acuerdos y registro de reuniones

- **Fecha de reunión:** Pendiente de completar.
- **Participantes:** Pendiente de completar.
- **Acuerdos sobre responsables:** Pendiente de confirmar.
- **Acuerdos sobre el tablero:** Pendiente de confirmar.
- **Problemas identificados y soluciones:** Registrar durante el trabajo.
- **Evidencias o enlaces de seguimiento:** Agregar cuando estén disponibles.

## 10. Criterios de finalización

El proyecto se considerará listo para entregar cuando el equipo haya comprobado y documentado que:

- La aplicación web funciona y está publicada en una URL accesible.
- La compresión y la descompresión funcionan con archivos de prueba.
- El formato `.huff` está documentado y puede inspeccionarse sin cargar el texto original.
- Las métricas y la verificación de integridad presentan resultados correctos.
- Se han ejecutado los casos de prueba requeridos y se han guardado sus evidencias.
- El README y los documentos técnicos reflejan el estado real del proyecto.
- GitHub Projects muestra las tareas, los responsables y los estados actualizados.
- El reporte técnico en PDF y los enlaces solicitados están preparados para la entrega.
- Se incluye la declaración correspondiente sobre el uso de herramientas de inteligencia artificial, según las indicaciones de la actividad.
