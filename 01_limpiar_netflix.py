# -*- coding: utf-8 -*-
"""
Reto 1. Generar el archivo limpio
Programa: 01_limpiar_netflix.py
Entrada: netflix_titles.csv
Salida: netflix_clean.csv
Autores: Eduardo Gabriel Viscarra Quisbert, Ezequiel Adrian Velasquez Cordova
"""

import pandas as pd


def limpiar_netflix(ruta_entrada: str = "netflix_titles.csv", ruta_salida: str = "netflix_clean.csv") -> None:
    # 1. Leer el archivo original con Pandas y registrar su cantidad de filas y columnas
    df = pd.read_csv(ruta_entrada)
    registros_originales = len(df)
    columnas_originales = len(df.columns)
    orden_columnas_originales = list(df.columns)

    # Identificar columnas de texto
    columnas_texto = df.select_dtypes(include=["object", "string"]).columns

    # Operación 1: Eliminar espacios al inicio y al final de los campos de texto
    for col in columnas_texto:
        df[col] = df[col].str.strip()

    # Operación 2: Sustituir saltos de línea y tabulaciones dentro de los textos por espacios
    for col in columnas_texto:
        df[col] = (
            df[col]
            .str.replace("\r\n", " ", regex=False)
            .str.replace("\n", " ", regex=False)
            .str.replace("\r", " ", regex=False)
            .str.replace("\t", " ", regex=False)
            .str.strip()
        )

    # Operación 3: Convertir los textos vacíos en valores nulos
    for col in columnas_texto:
        df[col] = df[col].replace("", pd.NA)

    # Operación 4: Eliminar filas completamente duplicadas
    antes = len(df)
    df = df.drop_duplicates()
    duplicadas_eliminadas = antes - len(df)

    # Operación 5: Eliminar registros sin show_id
    antes = len(df)
    df = df.dropna(subset=["show_id"])
    sin_show_id_eliminados = antes - len(df)

    # Operación 6: Si un show_id aparece varias veces, conservar su primera aparición
    antes = len(df)
    df = df.drop_duplicates(subset=["show_id"], keep="first")
    show_id_repetidos_eliminados = antes - len(df)

    # Operación 7: Convertir date_added al formato dd/mm/aaaa.
    # Dejar vacío el campo cuando esté ausente o no pueda interpretarse.
    fechas_parseadas = pd.to_datetime(df["date_added"], format="mixed", errors="coerce")
    registros_fecha_actualizada = int(fechas_parseadas.notna().sum())
    df["date_added"] = fechas_parseadas.dt.strftime("%d/%m/%Y")

    # Operación 8: Eliminar registros sin Director
    antes = len(df)
    df = df.dropna(subset=["director"])
    sin_director_eliminados = antes - len(df)

    # Operación 9: Eliminar registros sin Actores
    antes = len(df)
    df = df.dropna(subset=["cast"])
    sin_actores_eliminados = antes - len(df)

    # Operación 10: Crear duration_min: extraer la cantidad de minutos de duration
    # únicamente para registros cuyo type sea Movie. Utilizar un entero que admita valores nulos.
    es_pelicula = df["type"] == "Movie"
    minutos_extraidos = df.loc[es_pelicula, "duration"].str.extract(r"^(\d+)\s*min$", expand=False)
    df["duration_min"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    df.loc[es_pelicula, "duration_min"] = pd.to_numeric(minutos_extraidos, errors="coerce").astype("Int64")

    # Operación 11: Conservar las columnas originales y agregar duration_min al final
    columnas_finales = orden_columnas_originales + ["duration_min"]
    df = df[columnas_finales]

    # Operación 12: Guardar netflix_clean.csv en UTF-8, con cabecera, separado por comas y sin el índice de Pandas
    df.to_csv(ruta_salida, index=False, encoding="utf-8", lineterminator="\n")

    # Cálculos para la Tabla 1 de comprobación
    registros_eliminados = (
        duplicadas_eliminadas
        + sin_show_id_eliminados
        + show_id_repetidos_eliminados
        + sin_director_eliminados
        + sin_actores_eliminados
    )
    registros_limpios = len(df)
    registros_fecha_en_limpio = int(df["date_added"].notna().sum())

    peliculas_duracion_valida = int(
        ((df["type"] == "Movie") & (df["duration_min"].notna()) & (df["duration_min"] > 0)).sum()
    )
    peliculas_sin_duracion_valida = int(
        ((df["type"] == "Movie") & ((df["duration_min"].isna()) | (df["duration_min"] <= 0))).sum()
    )

    # 1.2. Mostrar en pantalla la cantidad inicial de registros, las eliminaciones realizadas y la cantidad final
    tabla_resumen = [
        ("Registros del archivo original, sin cabecera", registros_originales),
        ("Columnas del archivo original", columnas_originales),
        ("Filas completamente duplicadas eliminadas", duplicadas_eliminadas),
        ("Registros sin show_id eliminados después de retirar duplicados", sin_show_id_eliminados),
        ("Registros con show_id repetido eliminados posteriormente", show_id_repetidos_eliminados),
        ("Registro donde se actualizó el formato de la fecha", registros_fecha_actualizada),
        ("Registros sin Director", sin_director_eliminados),
        ("Registros sin Actores", sin_actores_eliminados),
        ("Registros eliminados", registros_eliminados),
        ("Registros del archivo limpio", registros_limpios),
        ("Películas con duration_min numérica mayor que cero", peliculas_duracion_valida),
        ("Películas sin una duración numérica mayor que cero", peliculas_sin_duracion_valida),
    ]

    print("=" * 80)
    print("TABLA 1. RESULTADO DE LA LIMPIEZA (netflix_clean.csv)")
    print("=" * 80)
    print(f"{'Indicador':<65} | {'Cantidad':>10}")
    print("-" * 80)
    for indicador, cantidad in tabla_resumen:
        print(f"{indicador:<65} | {cantidad:>10}")
    print("=" * 80)
    print(f"Nota: De los {registros_fecha_actualizada} registros con fecha actualizada en el paso 7,")
    print(f"      {registros_fecha_en_limpio} permanecen en el archivo limpio final ({ruta_salida}).")


if __name__ == "__main__":
    limpiar_netflix()
