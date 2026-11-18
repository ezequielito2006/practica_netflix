# -*- coding: utf-8 -*-
"""
Reto 2.3. Reunir las partes del resultado de MapReduce y exportar mapreduce_actores.csv
Programa: 02_exportar_resultado.py
Entrada: Archivos part-* descargados de HDFS (/data/netflix/results/actores/)
Salida: mapreduce_actores.csv
Autores: Eduardo Gabriel Viscarra Quisbert, Ezequiel Adrian Velasquez Cordova
"""

import glob
import os
import pandas as pd


def exportar_resultado_mapreduce(
    patron_busqueda: str = "actores/part-*",
    ruta_salida: str = "mapreduce_actores.csv",
) -> pd.DataFrame:
    # Buscar archivos part-* en la carpeta descargada o en el directorio actual
    archivos_partes = sorted(glob.glob(patron_busqueda))
    if not archivos_partes:
        archivos_partes = sorted(glob.glob("part-*"))
    if not archivos_partes:
        raise FileNotFoundError(
            "No se encontraron archivos 'part-*'. Verifique la descarga desde HDFS (/data/netflix/results/actores/)."
        )

    lista_df = []
    for ruta in archivos_partes:
        if os.path.getsize(ruta) > 0:
            df_parte = pd.read_csv(
                ruta,
                sep="\t",
                header=None,
                names=["actor", "cantidad_titulos"],
                encoding="utf-8",
                dtype={"actor": str, "cantidad_titulos": "int64"},
                quoting=3,  # csv.QUOTE_NONE para no alterar comillas en nombres de actores
            )
            lista_df.append(df_parte)

    if not lista_df:
        df_final = pd.DataFrame(columns=["actor", "cantidad_titulos"])
    else:
        df_final = pd.concat(lista_df, ignore_index=True)

    # Limpieza preventiva y ordenamiento: cantidad_titulos DESC, actor ASC
    df_final["actor"] = df_final["actor"].str.strip()
    df_final["cantidad_titulos"] = df_final["cantidad_titulos"].astype("int64")
    df_final = df_final.sort_values(
        by=["cantidad_titulos", "actor"],
        ascending=[False, True],
        kind="mergesort",
    ).reset_index(drop=True)

    # Exportar a CSV en UTF-8 con cabecera y sin índice
    df_final.to_csv(ruta_salida, index=False, encoding="utf-8", lineterminator="\n")

    # Mostrar resumen y Tabla 2 (Top 10 actores)
    print("=" * 75)
    print(f"Archivo generado exitosamente: {ruta_salida}")
    print(f"Partes procesadas: {archivos_partes}")
    print(f"Total de actores únicos: {len(df_final)}")
    print("=" * 75)
    print("TABLA 2. RESULTADO DE MAPREDUCE (10 PRIMEROS ACTORES)")
    print("=" * 75)
    print(f"{'Posición':<10} | {'Actor':<35} | {'Cantidad de títulos distintos':>25}")
    print("-" * 75)
    for idx, fila in df_final.head(10).iterrows():
        print(f"{idx + 1:<10} | {fila['actor']:<35} | {int(fila['cantidad_titulos']):>25}")
    print("=" * 75)

    return df_final


if __name__ == "__main__":
    exportar_resultado_mapreduce()
