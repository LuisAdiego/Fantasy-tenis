# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 12:08:18 2026

@author: rotci
"""

from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
m = pd.read_csv(DATA / "atp_matches_2026.csv")

g = m[["winner_id", "winner_name", "winner_ioc", "winner_hand", "winner_ht"]]
p = m[["loser_id", "loser_name", "loser_ioc", "loser_hand", "loser_ht"]]
g.columns = p.columns = ["jugador_id", "nombre", "pais", "mano", "altura"]

jug = pd.concat([g, p]).drop_duplicates("jugador_id").sort_values("jugador_id")
jug.to_csv(DATA / "jugadores.csv", index=False, encoding="utf-8")
print(len(jug), "jugadores guardados")