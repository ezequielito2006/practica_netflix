#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reto 2.2. Mapper para contar títulos por actor en Netflix
Programa: 02_mapper_actores.py
Recibe: Registros de netflix_clean.csv por la entrada estándar (stdin)
Realiza: Reconoce y omite la cabecera; interpreta las filas con el módulo csv; separa los actores de cast
Entrega: Pares actor\tshow_id separados por tabulación
Autores: Eduardo Gabriel Viscarra Quisbert, Ezequiel Adrian Velasquez Cordova
"""

import csv
import io
import sys


def main() -> None:
    # Garantizar lectura y escritura en UTF-8 para conservar tildes y caracteres especiales
    entrada = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    salida = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

    lector = csv.reader(entrada, delimiter=",", quotechar='"')

    for fila in lector:
        if not fila or len(fila) < 5:
            continue

        show_id = fila[0].strip()
        cast_raw = fila[4].strip()

        # Reconocer y omitir la cabecera (incluso si el archivo se divide en varios bloques en HDFS)
        if show_id == "show_id" and fila[1].strip() == "type":
            continue

        if not show_id or not cast_raw:
            continue

        # Separar los actores de cast por comas, eliminar espacios sobrantes y excluir vacíos
        for actor in cast_raw.split(","):
            nombre_actor = actor.strip()
            if nombre_actor:
                salida.write(f"{nombre_actor}\t{show_id}\n")


if __name__ == "__main__":
    main()
