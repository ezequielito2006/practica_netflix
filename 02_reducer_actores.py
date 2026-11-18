#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reto 2.2. Reducer para contar títulos distintos por actor en Netflix
Programa: 02_reducer_actores.py
Recibe: Pares actor\tshow_id agrupados por actor desde Hadoop Streaming (stdin)
Realiza: Cuenta los identificadores (show_id) distintos de cada actor
Entrega: actor\tcantidad_titulos separados por tabulación
Autores: Eduardo Gabriel Viscarra Quisbert, Ezequiel Adrian Velasquez Cordova
"""

import io
import sys


def main() -> None:
    # Garantizar lectura y escritura en UTF-8 para conservar tildes y caracteres especiales
    entrada = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    salida = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

    actor_actual = None
    shows_distintos = set()

    for linea in entrada:
        linea = linea.rstrip("\r\n")
        if not linea:
            continue

        partes = linea.split("\t", 1)
        if len(partes) != 2:
            continue

        actor, show_id = partes[0].strip(), partes[1].strip()
        if not actor or not show_id:
            continue

        if actor == actor_actual:
            shows_distintos.add(show_id)
        else:
            if actor_actual is not None:
                salida.write(f"{actor_actual}\t{len(shows_distintos)}\n")
            actor_actual = actor
            shows_distintos = {show_id}

    # Emitir el último actor procesado
    if actor_actual is not None:
        salida.write(f"{actor_actual}\t{len(shows_distintos)}\n")


if __name__ == "__main__":
    main()
