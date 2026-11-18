# ==============================================================================
# AUTOMATIZACIÓN COMPLETA DE HADOOP + HDFS + MAPREDUCE EN DOCKER (RETO 2)
# Equipo: Eduardo Gabriel Viscarra Quisbert y Ezequiel Adrian Velasquez Cordova
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "1. Levantando clúster de Hadoop (NameNode, DataNode, ResourceManager, NodeManager)..." -ForegroundColor Cyan
docker compose up -d

Write-Host "2. Esperando a que HDFS NameNode esté listo y salga de Safe Mode..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
docker exec namenode hdfs dfsadmin -safemode wait

Write-Host "3. Verificando Python 3 en los contenedores de Hadoop..." -ForegroundColor Cyan
docker exec namenode bash -c "which python3 || (sed -i 's/deb.debian.org/archive.debian.org/g; s|security.debian.org|archive.debian.org/debian-security|g; /stretch-updates/d' /etc/apt/sources.list && apt-get update -o Acquire::Check-Valid-Until=false && apt-get install -y --allow-unauthenticated python3)"
docker exec nodemanager bash -c "which python3 || (sed -i 's/deb.debian.org/archive.debian.org/g; s|security.debian.org|archive.debian.org/debian-security|g; /stretch-updates/d' /etc/apt/sources.list && apt-get update -o Acquire::Check-Valid-Until=false && apt-get install -y --allow-unauthenticated python3)"

Write-Host "4. [Reto 2.1] Creando carpeta /data/netflix/clean/ y subiendo netflix_clean.csv a HDFS..." -ForegroundColor Green
docker exec namenode bash -c "cd /workspace && hdfs dfs -mkdir -p /data/netflix/clean/ && hdfs dfs -put -f netflix_clean.csv /data/netflix/clean/ && hdfs dfs -ls -h /data/netflix/clean/"

Write-Host "5. [Reto 2.3] Ejecutando trabajo MapReduce con Hadoop Streaming..." -ForegroundColor Green
docker exec namenode bash -c "cd /workspace && chmod +x 02_mapper_actores.py 02_reducer_actores.py && hdfs dfs -rm -r -f /data/netflix/results/actores/ && hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar -files 02_mapper_actores.py,02_reducer_actores.py -mapper 'python3 02_mapper_actores.py' -reducer 'python3 02_reducer_actores.py' -input /data/netflix/clean/netflix_clean.csv -output /data/netflix/results/actores/"

Write-Host "6. Comprobando salida en HDFS y descargando archivos part-*..." -ForegroundColor Green
docker exec namenode bash -c "cd /workspace && hdfs dfs -ls -h /data/netflix/results/actores/ && mkdir -p actores && hdfs dfs -get -f /data/netflix/results/actores/part-* actores/"

Write-Host "7. Ejecutando 02_exportar_resultado.py con Pandas para consolidar mapreduce_actores.csv..." -ForegroundColor Cyan
python 02_exportar_resultado.py
