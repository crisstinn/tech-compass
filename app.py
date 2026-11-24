"""App: ¿dónde invertir en tecnología en Europa?

Ejecutar:  python app.py   y abrir http://127.0.0.1:8050
"""
import pandas as pd
from dash import Dash, Input, Output, dcc, html

from src import graficos
from src.indice import calcular_indice

# ---------- 1. Cargar los datos ----------
datos = pd.read_csv("datos/datos.csv").set_index("pais")
indicadores = pd.read_csv("datos/indicadores.csv")
paises = pd.read_csv("datos/paises.csv")
nombres = dict(zip(paises["codigo3"], paises["nombre"]))
codigos2 = dict(zip(paises["codigo3"], paises["codigo2"]))
PILARES = ["Talento", "Innovación", "Costes", "Entorno"]

# Explicación de cada pilar que se muestra al usuario debajo de su slider
DESCRIPCIONES = {
    "Talento": "¿Hay gente preparada para contratar?",
    "Innovación": "¿Las empresas del país innovan?",
    "Costes": "¿Cuánto cuesta operar? Más barato = mejor nota.",
    "Entorno": "¿Es un país rico y seguro para invertir?",
}


def casillas(pilar):
    """Una casilla por cada indicador del pilar, todas marcadas al empezar."""
    del_pilar = indicadores[indicadores["pilar"] == pilar]
    return dcc.Checklist(id="ind-" + pilar, className="casillas",
                         options=[{"label": n, "value": i} for i, n in zip(del_pilar["id"], del_pilar["nombre"])],
                         value=list(del_pilar["id"]))

# ---------- 2. Diseño de la página ----------
app = Dash(__name__, title="¿Dónde invertir en tecnología?")
SIN_BARRA = {"displayModeBar": False}  # oculta la barra de herramientas de Plotly
server = app.server  # lo necesita Render

# Fila de controles: una caja por pilar con su slider y sus casillas
controles = html.Div([
    html.Div([html.Label(p), html.P(DESCRIPCIONES[p], className="descripcion"),
              dcc.Slider(id=p, min=0, max=10, step=1, value=5), casillas(p)],
             className="caja")
    for p in PILARES
], className="fila")

app.layout = html.Div([
    html.H1("¿Dónde invertir en tecnología en Europa?"),
    html.P("Ranking de los 27 países de la UE según talento, innovación, costes y entorno. "
           "Mueve los pesos para adaptarlo a tu empresa. Datos: Eurostat y Banco Mundial."),
    # Arriba: los sliders de los 4 pilares en horizontal
    html.H3("¿Qué es más importante para ti?", className="subtitulo"),
    controles,
    # En medio: ranking a la izquierda y podio en vertical a la derecha
    html.Div([
        html.Div([html.H3("Ranking"), dcc.Graph(id="ranking", config=SIN_BARRA)], className="caja grande"),
        html.Div(id="podio", className="columna-podio"),
    ], className="fila"),
    # Abajo: mapa a la izquierda y comparación del país a la derecha
    html.Div([
        html.Div([
            html.Div([html.H3("Mapa"), html.Span("Pinta en el mapa:", className="descripcion"),
                      dcc.Dropdown(id="columna-mapa", value="nota", clearable=False, className="selector",
                                   options=[{"label": "Nota global", "value": "nota"}]
                                   + [{"label": p, "value": p} for p in PILARES])],
                     className="cabecera"),
            html.P("Pasa el ratón por un país para ver su ficha; haz clic para analizarlo.", className="descripcion"),
            dcc.Graph(id="mapa", config=SIN_BARRA),
        ], className="caja mapa"),
        html.Div([
            html.H3(id="titulo-pais"),
            html.Span("País a analizar:", className="descripcion"),
            dcc.Dropdown(id="pais", value="ESP", clearable=False,
                         options=[{"label": n, "value": c}
                                  for c, n in sorted(nombres.items(), key=lambda x: x[1])]),
            dcc.Graph(id="perfil", config=SIN_BARRA),
        ], className="caja"),
    ], className="fila"),
])


# ---------- 3. Interactividad ----------
@app.callback(
    Output("podio", "children"), Output("ranking", "figure"), Output("mapa", "figure"),
    Output("perfil", "figure"), Output("titulo-pais", "children"),
    [Input(p, "value") for p in PILARES],
    [Input("ind-" + p, "value") for p in PILARES],
    Input("pais", "value"), Input("columna-mapa", "value"),
)
def actualizar(talento, innovacion, costes, entorno, ind_t, ind_i, ind_c, ind_e, pais, columna):
    """Cuando cambia cualquier control, se recalcula el índice y se redibuja todo."""
    pesos = {"Talento": talento, "Innovación": innovacion, "Costes": costes, "Entorno": entorno}
    activos = ind_t + ind_i + ind_c + ind_e  # indicadores marcados por el usuario
    resultado = calcular_indice(datos, indicadores, pesos, activos)
    resultado["nombre"] = resultado.index.map(nombres)

    titulo = f"{nombres[pais]}: puesto {resultado.loc[pais, 'puesto']} de 27 ({resultado.loc[pais, 'nota']:.2f} puntos)"
    return (graficos.podio(resultado, nombres, codigos2, PILARES),
            graficos.ranking(resultado, pais),
            graficos.mapa(resultado, pais, columna),
            graficos.perfil(resultado, pais, nombres[pais], PILARES),
            titulo)


@app.callback(Output("pais", "value"), Input("mapa", "clickData"), prevent_initial_call=True)
def clic_en_mapa(clic):
    """Al hacer clic en un país del mapa, se selecciona en el desplegable."""
    return clic["points"][0]["location"]


if __name__ == "__main__":
    app.run(debug=True)
