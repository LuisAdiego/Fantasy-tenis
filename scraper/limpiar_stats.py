# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 11:30:42 2026

@author: rotci
"""

import re
import sys
from pathlib import Path
from ids import asignar_ids

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
NUM = r"[\d.,]+%?|\d+/\d+ \([\d.,]+%\)"


def categoria_desde_nombre(path):
    nombre = path.stem.replace("sofascore_stats_", "")
    nombre = re.sub(r"_p\d+$", "", nombre)          # quita _p1, _p2...
    return "1er_servicio" if nombre == "defecto" else nombre


def parsear(path):
    lineas = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    filas = []
    for i in range(len(lineas) - 2):
        pos, nombre, valor = lineas[i], lineas[i + 1], lineas[i + 2]
        if (re.fullmatch(r"\d{1,2}", pos)
                and re.fullmatch(NUM, valor)
                and not re.fullmatch(NUM, nombre)):
            filas.append({
                "categoria": categoria_desde_nombre(path),
                "posicion": int(pos),
                "jugador": nombre,
                "valor_texto": valor,
            })
    return filas


def convertir(v):
    m = re.fullmatch(r"(\d+)/(\d+) \(([\d.,]+)%\)", v)
    if m:
        return pd.Series([float(m.group(3).replace(",", ".")), True, int(m.group(1)), int(m.group(2))])
    return pd.Series([float(v.replace("%", "").replace(",", ".")), v.endswith("%"), None, None])



def main():
    filas = []
    for f in sorted(DATA.glob("sofascore_stats_*.txt")):
        filas += parsear(f)

    df = pd.DataFrame(filas).drop_duplicates(subset=["categoria", "posicion", "jugador"])
    df = df[~df["jugador"].str.match(r"^(ATP|WTA) \d+º$")]
    df = df[~df["jugador"].isin(["Tiempo reglamentario", "Partidos"])]
    df = df[~df["jugador"].str.contains("por partido|quiebre|servicio", case=False)]
    df[["valor", "es_porcentaje", "aciertos", "intentos"]] = df["valor_texto"].apply(convertir)
    df = df.drop(columns="valor_texto").sort_values(["categoria", "posicion"])

# filtros
    df = df[df["categoria"] != "1er_servicio"]
    df = df[~df["jugador"].isin(["-", "FT"])]

# torneo e ids
    torneo = sys.argv[1] if len(sys.argv) > 1 else "shanghai_2026"
    df["torneo"] = torneo
    mapa = asignar_ids(df["jugador"].tolist())
    df["jugador_id"] = df["jugador"].map(mapa)
    df = df.drop(columns="jugador")

# guardar acumulando
    salida = DATA / "estadisticas.csv"
    if salida.exists():
        antiguo = pd.read_csv(salida)
        antiguo = antiguo[antiguo["torneo"] != torneo]
        df = pd.concat([antiguo, df], ignore_index=True)
    df.to_csv(salida, index=False, encoding="utf-8")

    print(df.groupby("categoria").size())
    print(f"\nGuardado en {salida}")



if __name__ == "__main__":
    main()