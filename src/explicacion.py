"""Desplegable "¿Cómo se calcula la nota?".

Los ejemplos se calculan con los datos reales al arrancar la app, así los números
coinciden siempre con lo que se ve en el ranking (aunque se actualicen los datos).
"""
from dash import html

from src.indice import calcular_indice
from src.perfiles import PERFILES


def num(x, decimales=1):
    """Número con coma decimal: 35.9 -> '35,9'."""
    return f"{x:.{decimales}f}".replace(".", ",")


def explicacion_calculo(datos, indicadores, nombres, pilares, pais="ESP"):
    nombre = nombres[pais]

    # Paso 1: los 8 indicadores, agrupados por pilar
    lista_indicadores = html.Ul([
        html.Li([html.B(p + ": "), ", ".join(indicadores.loc[indicadores["pilar"] == p, "nombre"])])
        for p in pilares
    ])

    # Paso 2: ejemplo de nota 0-100 (normal y con costes, que se invierte)
    tic = datos["especialistas_tic"]
    nota_tic = (tic[pais] - tic.min()) / (tic.max() - tic.min()) * 100
    coste = datos["coste_laboral"]
    nota_coste = 100 - (coste[pais] - coste.min()) / (coste.max() - coste.min()) * 100

    # Pasos 3 y 4: notas de los pilares y nota final con dos juegos de pesos
    iguales = {p: 5 for p in pilares}
    startup = PERFILES["startup"]["pesos"]
    r_iguales = calcular_indice(datos, indicadores, iguales).loc[pais]
    r_startup = calcular_indice(datos, indicadores, startup).loc[pais]
    notas = {p: r_iguales[p] for p in pilares}
    suma_pesos = sum(startup.values())
    formula = " + ".join(f"{num(notas[p])}×{startup[p]}" for p in pilares)

    return html.Details([
        html.Summary("¿Cómo se calcula la nota?"),
        html.Ol([
            html.Li([html.B("Datos. "), "Se descargan 8 indicadores de Eurostat y del Banco Mundial para los 27 países "
                     "(el dato más reciente de cada uno), agrupados en 4 pilares:", lista_indicadores]),
            html.Li([html.B("Nota de 0 a 100 de cada indicador. "), "El peor país saca 0 y el mejor 100; "
                     "los demás quedan en proporción. ",
                     html.Br(), html.I("Ejemplo: "),
                     f"en especialistas TIC el mínimo es {nombres[tic.idxmin()]} ({num(tic.min())} %) y el máximo "
                     f"{nombres[tic.idxmax()]} ({num(tic.max())} %). {nombre} tiene {num(tic[pais])} %, así que saca ",
                     html.B(f"{num(nota_tic)}"), ".",
                     html.Br(), html.I("En los costes se invierte: "),
                     f"el más barato saca 100. {nombre} paga {num(coste[pais])} €/h (mínimo {num(coste.min())}, "
                     f"máximo {num(coste.max())}), así que saca ", html.B(f"{num(nota_coste)}"), "."]),
            html.Li([html.B("Nota de cada pilar. "), "Es la media de sus indicadores. ",
                     html.I("Ejemplo: "), f"{nombre} saca " +
                     ", ".join(f"{p} {num(notas[p])}" for p in pilares) + "."]),
            html.Li([html.B("Nota final. "), "Es la media ponderada de los pilares con los pesos de los sliders: "
                     "cada pilar se multiplica por su peso y se divide entre la suma de los pesos.",
                     html.Br(), html.I("Con todos los pesos a 5: "),
                     f"es la media simple → {nombre} saca ", html.B(num(r_iguales["nota"])), ".",
                     html.Br(), html.I("Con el perfil «Startup tecnológica» "),
                     f"(Talento {startup['Talento']}, Innovación {startup['Innovación']}, "
                     f"Costes {startup['Costes']}, Entorno {startup['Entorno']}): ",
                     html.Code(f"({formula}) / {suma_pesos}"), " = ", html.B(num(r_startup["nota"])),
                     ". Sube porque los costes, su punto fuerte, pesan más y el entorno, su punto débil, menos."]),
        ]),
    ], className="guia")
