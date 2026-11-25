"""Modelo de machine learning: agrupa los países en grupos parecidos (clustering).

Se usa K-Means (aprendizaje no supervisado, scikit-learn) sobre la nota de cada
pilar. Países del mismo grupo tienen un perfil parecido: por ejemplo, "mucho
talento e innovación pero caros" o "baratos pero con poca innovación".
"""
import pandas as pd
from sklearn.cluster import KMeans


def agrupar_paises(resultado, pilares, n_grupos=4):
    """Devuelve, para cada país, el nombre de su grupo."""
    # Solo los pilares que tienen nota (el usuario puede haber quitado indicadores)
    X = resultado[pilares].dropna(axis=1, how="all")

    modelo = KMeans(n_clusters=n_grupos, n_init=10, random_state=42)
    grupo = pd.Series(modelo.fit_predict(X), index=X.index)

    # Ordenamos los grupos de mejor a peor nota media, para que el Grupo 1 sea el mejor
    orden = resultado.groupby(grupo)["nota"].mean().sort_values(ascending=False).index
    numero = {g: i + 1 for i, g in enumerate(orden)}

    # Nombre de cada grupo: el pilar en el que más destaca y en el que más flojea
    centros = pd.DataFrame(modelo.cluster_centers_, columns=X.columns)
    nombres = {}
    for g, centro in centros.iterrows():
        diferencia = centro - X.mean()
        nombres[g] = f"Grupo {numero[g]}: + {diferencia.idxmax()}, − {diferencia.idxmin()}"
    return grupo.map(nombres)
