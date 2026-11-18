# Proyecto de Ingeniería de Datos y Big Data: Análisis del Catálogo de Netflix

**Asignatura:** Tecnologías Emergentes I — **Unidad 3:** Big Data y Herramientas Esenciales  
**Fechas de Realización y Exposición:** Lunes 16 y Miércoles 18 de noviembre de 2026  
**Equipo e Integrantes:**
- **Eduardo Gabriel Viscarra Quisbert**
- **Ezequiel Adrian Velasquez Cordova**

---

## 1. Versiones de Software y Entorno Técnico

| Componente / Herramienta | Versión Utilizada | Propósito en el Proyecto |
| :--- | :--- | :--- |
| **Python** | `3.14.4` (compatible con `3.10+` en Hadoop/Databricks) | Lenguaje base para limpieza, MapReduce (`csv`/`sys`) y PySpark |
| **Pandas** | `3.1.1` | Limpieza del catálogo (`01_limpiar_netflix.py`) y consolidación MapReduce (`02_exportar_resultado.py`) |
| **Apache Hadoop / HDFS** | `3.2.1` (Hadoop Streaming) | Almacenamiento distribuido en `/data/netflix/clean/` y ejecución MapReduce |
| **Java Runtime (JRE/JDK)** | `1.8.0_401` (Java 8) | Entorno de ejecución para demonios de Hadoop (NameNode, DataNode, YARN) |
| **Apache Spark (Databricks)** | `3.5.x` (Databricks Runtime LTS / Serverless) | Procesamiento distribuido en memoria con Spark SQL y PySpark (`03_analisis_netflix.ipynb`) |
| **Matplotlib** | `3.10.x` | Visualización de datos en el notebook de Databricks (Reto 4.1) |

---

## 2. Inventario de Archivos del Proyecto

```text
practica_netflix/
├── netflix_titles.csv                      # [Entrada Reto 1] Dataset original de Kaggle (8,807 registros, 12 columnas)
├── 01_limpiar_netflix.py                   # [Reto 1] Programa de limpieza secuencial con Pandas y generación de Tabla 1
├── netflix_clean.csv                       # [Salida Reto 1] Catálogo limpio en UTF-8 (5,700 registros, 13 columnas)
├── 02_mapper_actores.py                    # [Reto 2] Mapper en Python para Hadoop Streaming (emite actor\tshow_id)
├── 02_reducer_actores.py                   # [Reto 2] Reducer en Python para Hadoop Streaming (cuenta show_id distintos)
├── 02_ejecutar_mapreduce.txt               # [Reto 2] Comandos exactos de carga en HDFS y ejecución de Hadoop Streaming
├── 02_exportar_resultado.py                # [Reto 2] Programa en Python/Pandas que reúne part-* en mapreduce_actores.csv
├── mapreduce_actores.csv                   # [Salida Reto 2] Conteo de títulos distintos por actor (26,725 actores únicos)
├── 03_analisis_netflix.ipynb               # [Reto 3 y 4] Notebook de Databricks exportado con código, tablas, gráficos y salidas visibles
├── Informe_Netflix_Viscarra_Velasquez.pdf  # [Entregable] Documento técnico completo con todas las tablas y evidencias numeradas
├── Presentacion_Netflix_Grupo.pdf          # [Entregable] Diapositivas 16:9 para la exposición y defensa de 15 minutos
├── docker-compose.yml                      # [DevOps] Orquestación del clúster Hadoop 3.2.1 (NameNode, DataNode, YARN)
├── hadoop.env                              # [DevOps] Variables de configuración del clúster Hadoop en Docker
├── 02_automatizar_hadoop_docker.ps1        # [DevOps] Script automatizado para ejecutar todo el Reto 2 en Docker con un comando
└── README.md                               # [Entregable] Guía de versiones y pasos de ejecución en orden estricto
```

---

## 3. Pasos de Ejecución en Orden (Estrictamente Desde Cero)

### Paso 1 — Reto 1: Limpieza del archivo original con Python y Pandas
Ejecutar el programa `01_limpiar_netflix.py` en el directorio donde se encuentra `netflix_titles.csv`:

```bash
python 01_limpiar_netflix.py
```

- **Operaciones realizadas en orden:**
  1. Elimina espacios iniciales y finales (`strip`) en todos los campos de texto.
  2. Sustituye saltos de línea (`\r\n`, `\n`, `\r`) y tabulaciones (`\t`) por espacios simples para que cada registro ocupe exactamente una línea en el CSV de salida.
  3. Convierte textos vacíos en valores nulos (`NA`).
  4. Elimina filas completamente duplicadas (`0` eliminadas).
  5. Elimina registros sin `show_id` (`0` eliminados).
  6. Conserva la primera aparición si un `show_id` se repite (`0` eliminados).
  7. Convierte `date_added` al formato `dd/mm/aaaa` (`8,797` fechas actualizadas; `5,700` en el archivo limpio final).
  8. Elimina registros sin `director` (`2,634` eliminados).
  9. Elimina registros sin `cast` (`473` eliminados adicionales).
  10. Crea la columna entera anulable `duration_min` (`Int64`) extrayendo los minutos de `duration` únicamente cuando `type == 'Movie'` (`5,519` películas con duración `> 0` y `3` películas sin duración numérica válida: `s5542`, `s5795`, `s5814`).
  11. Conserva las 12 columnas originales y agrega `duration_min` al final (13 columnas).
  12. Guarda `netflix_clean.csv` en codificación `UTF-8`, con cabecera, separado por comas y sin índice (`5,700` registros limpios, `5,701` líneas físicas).

---

### Paso 2 — Reto 2: Carga en HDFS y Conteo de Títulos por Actor con MapReduce

#### 2.1. Cargar `netflix_clean.csv` en HDFS
En la terminal del nodo maestro de Hadoop (`namenode`):

```bash
hdfs dfs -mkdir -p /data/netflix/clean/
hdfs dfs -put -f netflix_clean.csv /data/netflix/clean/
hdfs dfs -ls -h /data/netflix/clean/
```

#### 2.2 y 2.3. Ejecutar el trabajo MapReduce con Hadoop Streaming
```bash
hdfs dfs -rm -r -f /data/netflix/results/actores/
chmod +x 02_mapper_actores.py 02_reducer_actores.py

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files 02_mapper_actores.py,02_reducer_actores.py \
  -mapper "python3 02_mapper_actores.py" \
  -reducer "python3 02_reducer_actores.py" \
  -input /data/netflix/clean/netflix_clean.csv \
  -output /data/netflix/results/actores/
```

#### 2.4. Descargar las partes del resultado y exportar `mapreduce_actores.csv`
```bash
mkdir -p actores
hdfs dfs -get -f /data/netflix/results/actores/part-* actores/
python 02_exportar_resultado.py
```
- **Salida generada:** `mapreduce_actores.csv` con `26,725` actores únicos ordenados por `cantidad_titulos` descendente y `actor` ascendente (Top 1: `Anupam Kher` con `42` títulos distintos).

> **Nota de automatización en Docker:** Si se utiliza Docker Desktop en Windows, todo el Paso 2 puede ejecutarse automáticamente con:
> ```powershell
> .\02_automatizar_hadoop_docker.ps1
> ```

---

### Paso 3 — Reto 3: Análisis con SQL y PySpark y Verificación en Databricks

1. Ingresar a **Databricks** y dirigirse a **Catalog -> Add data -> Create or modify table**.
2. Subir los archivos `netflix_clean.csv` y `mapreduce_actores.csv` en el catálogo `workspace`, esquema `default`, creando las tablas:
   - `workspace.default.netflix_clean` (activando *First row contains the header* y opciones avanzadas `multiLine = true` y `escape = "\""`).
   - `workspace.default.mapreduce_actores` (activando *First row contains the header*).
3. Importar el notebook `03_analisis_netflix.ipynb` en el Workspace de Databricks.
4. Ejecutar secuencialmente las celdas del notebook (**Run All**):
   - **Sección 3.1:** Comprueba cabeceras, lectura correcta de comas internas (`show_id = 's8'`), conteo exacto de `5,700` filas en `netflix_clean` y `26,725` actores en `mapreduce_actores`, y muestra 5 registros de cada tabla.
   - **Sección 3.2:** Ejecuta las 6 consultas (SQL y PySpark para los Análisis A, B y C) y construye la **Tabla 3**, verificando coincidencia del `100%` (`0` valores diferentes y `0` filas en una sola salida).
   - **Sección 3.3:** Ejecuta el `FULL OUTER JOIN` entre `mapreduce_actores` y `actores_pyspark`, generando las **Tablas 4 y 5** (`26,725` actores con cantidades idénticas y `0` diferencias).

---

### Paso 4 — Reto 4: Visualización de Hallazgos y Conclusiones en Databricks

En la parte final del mismo notebook `03_analisis_netflix.ipynb`, ejecutar las celdas correspondientes al Reto 4:
1. **Gráfico 1 (Barras verticales):** Cantidad y porcentaje de películas (`5,522` — `96.88%`) y series (`178` — `3.12%`).
2. **Gráfico 2 (Barras horizontales):** Top 10 actores con mayor cantidad de títulos (mayor cantidad arriba y desempate alfabético ascendente).
3. **Tabla 6:** Top 10 países con mayor cantidad de películas utilizadas en el cálculo y su duración promedio en minutos redondeada a 2 decimales (`United States`: `2,444` películas, `95.98` min; `India`: `932` películas, `127.29` min).
4. **Diagrama del Proceso y Conclusiones:** Diagrama de flujo con archivos transferidos y conclusiones en `218` palabras (cumpliendo el límite `< 250` palabras).
