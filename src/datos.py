"""Descarga los datos de Eurostat y del Banco Mundial.

Para cada indicador de datos/indicadores.csv se pide el dato de los 27 países
y se guarda el valor más reciente de cada país en datos/datos.csv.

Ejecutar desde la carpeta del proyecto:   python src/datos.py
"""
import pandas as pd
import requests

URL_EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
URL_BANCO_MUNDIAL = "https://api.worldbank.org/v2/country/"


def leer_filtros(texto):
    """Convierte 'unit=PC_EMP;sex=T' en {'unit': 'PC_EMP', 'sex': 'T'}."""
    if pd.isna(texto):
        return {}
    return dict(parte.split("=") for parte in texto.split(";"))


def descargar_eurostat(codigo, filtros, paises):
    """Devuelve una tabla con columnas: pais (2 letras), año, valor."""
    parametros = {"format": "JSON", "lang": "EN", "geo": paises, **filtros}
    respuesta = requests.get(URL_EUROSTAT + codigo, params=parametros, timeout=60).json()

    # Eurostat devuelve los países, los años y los valores por separado
    lista_paises = list(respuesta["dimension"]["geo"]["category"]["index"])
    lista_años = list(respuesta["dimension"]["time"]["category"]["index"])
    valores = respuesta["value"]  # {"posición": valor}

    filas = []
    for i, pais in enumerate(lista_paises):
        for j, año in enumerate(lista_años):
            posicion = str(i * len(lista_años) + j)
            if posicion in valores:
                filas.append({"pais": pais, "año": int(año[:4]), "valor": valores[posicion]})
    # Algunos datos son semestrales (la luz): se hace la media de cada año
    return pd.DataFrame(filas).groupby(["pais", "año"], as_index=False)["valor"].mean()


def descargar_banco_mundial(codigo, filtros, paises):
    """Devuelve una tabla con columnas: pais (3 letras), año, valor."""
    url = URL_BANCO_MUNDIAL + ";".join(paises) + "/indicator/" + codigo
    parametros = {"format": "json", "per_page": 5000, "date": "2015:2026", **filtros}
    respuesta = requests.get(url, params=parametros, timeout=60).json()

    filas = [{"pais": d["countryiso3code"], "año": int(d["date"]), "valor": d["value"]}
             for d in respuesta[1] if d["value"] is not None]
    return pd.DataFrame(filas)


def descargar_todo():
    indicadores = pd.read_csv("datos/indicadores.csv")
    paises = pd.read_csv("datos/paises.csv")
    tabla = pd.DataFrame({"pais": paises["codigo3"]})

    for ind in indicadores.itertuples():
        print("Descargando", ind.nombre)
        filtros = leer_filtros(ind.filtros)
        if ind.fuente == "eurostat":
            datos = descargar_eurostat(ind.codigo, filtros, list(paises["codigo2"]))
            # Eurostat usa códigos de 2 letras: los pasamos a 3 letras
            datos["pais"] = datos["pais"].map(dict(zip(paises["codigo2"], paises["codigo3"])))
        else:
            datos = descargar_banco_mundial(ind.codigo, filtros, list(paises["codigo3"]))

        # Nos quedamos con el dato más reciente de cada país
        ultimo = datos.sort_values("año").groupby("pais").last()
        tabla[ind.id] = tabla["pais"].map(ultimo["valor"])
        tabla["año_" + ind.id] = tabla["pais"].map(ultimo["año"])

    tabla.to_csv("datos/datos.csv", index=False)
    print("Guardado en datos/datos.csv")


if __name__ == "__main__":
    descargar_todo()
