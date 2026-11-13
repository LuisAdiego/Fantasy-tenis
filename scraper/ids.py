# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:43:32 2026

@author: rotci
"""

import unicodedata
from pathlib import Path

import pandas as pd

RUTA = Path(__file__).resolve().parent.parent / "data" / "jugadores.csv"
COLUMNAS = ["jugador_id", "nombre", "pais", "mano", "altura"]
ID_PROPIO = 900000   # los ids de Sackmann son menores, así no chocan


def normalizar(nombre):
    s = unicodedata.normalize("NFKD", nombre)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("-", " ")
    return " ".join(sorted(s.split()))


def cargar():
    if RUTA.exists():
        return pd.read_csv(RUTA)
    return pd.DataFrame(columns=COLUMNAS)


def asignar_ids(nombres):
    tabla = cargar()
    existentes = {normalizar(n): i for n, i in zip(tabla["nombre"], tabla["jugador_id"])}
    propios = tabla.loc[tabla["jugador_id"] >= ID_PROPIO, "jugador_id"]
    siguiente = int(propios.max()) + 1 if len(propios) else ID_PROPIO

    nuevos = []
    for n in dict.fromkeys(nombres):
        clave = normalizar(n)
        if clave not in existentes:
            existentes[clave] = siguiente
            nuevos.append({"jugador_id": siguiente, "nombre": n,
                           "pais": None, "mano": None, "altura": None})
            siguiente += 1

    if nuevos:
        print("Jugadores SIN id de Sackmann (revisa que no sean abreviaturas):")
        for f in nuevos:
            print("  ", f["jugador_id"], f["nombre"])
        tabla = pd.concat([tabla, pd.DataFrame(nuevos)], ignore_index=True)
        tabla.to_csv(RUTA, index=False, encoding="utf-8")

    return {n: existentes[normalizar(n)] for n in nombres}