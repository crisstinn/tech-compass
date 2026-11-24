"""Calcula el índice: convierte cada indicador a una nota de 0 a 100,
hace la media por pilar y luego la media ponderada de los pilares."""
import pandas as pd


def normalizar(columna, sentido):
    """Escala 0-100: el peor país saca 0 y el mejor 100.
    Si el sentido es -1 (costes), se invierte: el más barato saca 100."""
    nota = (columna - columna.min()) / (columna.max() - columna.min()) * 100
    if sentido == -1:
        nota = 100 - nota
    return nota


def calcular_indice(datos, indicadores, pesos, activos=None):
    """datos: una fila por país. pesos: {"Talento": 5, "Costes": 5, ...}
    activos: lista de indicadores que el usuario quiere usar (None = todos)."""
    if activos is not None:
        indicadores = indicadores[indicadores["id"].isin(activos)]
    resultado = pd.DataFrame(index=datos.index)

    # 1. Nota de 0 a 100 de cada indicador
    notas = pd.DataFrame(index=datos.index)
    for ind in indicadores.itertuples():
        notas[ind.id] = normalizar(datos[ind.id], ind.sentido)

    # 2. Nota de cada pilar = media de sus indicadores
    for pilar in pesos:
        ids = indicadores.loc[indicadores["pilar"] == pilar, "id"]
        resultado[pilar] = notas[ids].mean(axis=1)

    # 3. Nota final = media ponderada de los pilares
    #    (si el usuario ha quitado todos los indicadores de un pilar, ese pilar no cuenta)
    pesos = {p: w for p, w in pesos.items() if resultado[p].notna().all()}
    total_pesos = sum(pesos.values()) or 1
    resultado["nota"] = sum(resultado[p] * w for p, w in pesos.items()) / total_pesos

    resultado["puesto"] = resultado["nota"].rank(ascending=False).astype(int)
    return resultado.sort_values("nota", ascending=False)
