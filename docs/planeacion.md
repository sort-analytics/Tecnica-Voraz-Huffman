# Planeación inicial de la actividad

Completar estos datos en reunión de equipo. El PDF pide que las tareas incluyan responsable, resultado esperado y estado; por eso las personas y enlaces se dejan pendientes de forma explícita.

## Datos que debe acordar el equipo

- Nombre del equipo: **pendiente**
- Integrantes (máximo 4) y responsable de coordinación: **pendiente**
- Repositorio GitHub: <https://github.com/sort-analytics/Tecnica-Voraz-Huffman>
- GitHub Projects: [Backlog-Visualizador web de algoritmos](https://github.com/orgs/sort-analytics/projects/3), tablero existente de la organización con tareas de la actividad previa. Acordar con el equipo si se reutiliza y agregar allí las tareas Huffman con estado y responsable.
- Tecnología: HTML, CSS y JavaScript en navegador; Python existente como referencia y pruebas.
- Hosting: Render Static Site, definido en `render.yaml`; despliega `Code_huffman/web/` desde la rama conectada.
- Formato propuesto: `.huff`, firma `HUFF`, versión 1. Especificación en [formato-huff.md](formato-huff.md).
- Boceto: encabezado oscuro y flujo guiado; panel de entrada (TXT/Gutenberg), análisis con tabla y árbol, mediciones y pestaña de inspector separado.
- Reunión y acuerdos: **agregar fecha, participantes, decisiones y breve evidencia**.

## Backlog para trasladar a GitHub Projects

| Estado inicial | Tarea / resultado esperado | Responsable |
| --- | --- | --- |
| Terminado en código; pendiente de validar | Calcular frecuencias y fijar desempates reproducibles | Por asignar |
| Terminado en código; pendiente de validar | Construir árbol voraz y tabla de códigos | Por asignar |
| Terminado en código; pendiente de validar | Empaquetar bits y gestionar bits válidos del último byte | Por asignar |
| Terminado en código; pendiente de validar | Documentar formato propio `.huff` y campos de cabecera | Por asignar |
| Terminado en código; pendiente de validar | Recuperar archivo desde `.huff` y verificar tamaño/SHA-256 | Por asignar |
| Terminado en código; pendiente de validar | Crear interfaz de entrada, métricas, tabla y visualización | Por asignar |
| Terminado en código; pendiente de validar | Conectar búsqueda y descarga de Project Gutenberg | Por asignar |
| Por hacer | Completar casos de prueba web, incluido TXT nuevo y Latin-1 | Por asignar |
| Por hacer | Registrar capturas, medidas y evidencia de integridad | Por asignar |
| Por hacer | Completar integrantes y reporte técnico breve PDF | Por asignar |
| Por hacer | Publicar repo GitHub y configurar GitHub Projects | Por asignar |
| Por hacer | Desplegar sitio estático en Render, verificarlo y registrar URL pública | Por asignar |

En GitHub Projects, crear las columnas equivalentes a **Backlog → Por hacer → En progreso → En revisión → Terminado** y asignar una persona real a cada tarjeta. Las tareas listadas no sustituyen el historial de commits de cada integrante.

## Plan de publicación gratuita

La aplicación es un sitio estático: Render puede publicar directamente los archivos de `Code_huffman/web/` sin servidor ni base de datos. El Blueprint `render.yaml` fija la carpeta raíz, el paso de build sin compilación y el auto despliegue por commit. Falta crear el Static Site en el dashboard de Render, conectar el repositorio y la rama `main`, registrar la URL `*.onrender.com` y probar carga, compresión, descarga e inspector desde HTTPS.
