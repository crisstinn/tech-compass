"""App: ¿dónde invertir en tecnología en Europa?

Ejecutar:  python app.py   y abrir http://127.0.0.1:8050
"""
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

from src.indice import calcular_indice

# ---------- 1. Cargar los datos ----------
datos = pd.read_csv("datos/datos.csv").set_index("pais")
indicadores = pd.read_csv("datos/indicadores.csv")
paises = pd.read_csv("datos/paises.csv")
nombres = dict(zip(paises["codigo3"], paises["nombre"]))
PILARES = ["Talento", "Innovación", "Costes", "Entorno"]

# ---------- 2. Diseño de la página ----------
app = Dash(__name__, title="¿Dónde invertir en tecnología?")
server = app.server  # lo necesita Render

controles = html.Div([
    html.H3("¿Qué es más importante para ti?"),
    *[html.Div([html.Label(p), dcc.Slider(id=p, min=0, max=10, step=1, value=5)])
      for p in PILARES],
    html.H3("País a analizar"),
    dcc.Dropdown(id="pais", value="ESP", clearable=False,
                 options=[{"label": n, "value": c} for c, n in sorted(nombres.items(), key=lambda x: x[1])]),
], className="caja controles")

app.layout = html.Div([
    html.H1("¿Dónde invertir en tecnología en Europa?"),
    html.P("Ranking de los 27 países de la UE según talento, innovación, costes y entorno. "
           "Mueve los pesos para adaptarlo a tu empresa. Datos: Eurostat y Banco Mundial."),
    html.Div([controles, html.Div(dcc.Graph(id="ranking"), className="caja grande")], className="fila"),
    html.Div([html.Div(dcc.Graph(id="mapa"), className="caja"),
              html.Div([html.H3(id="titulo-pais"), dcc.Graph(id="perfil")], className="caja")],
             className="fila"),
])


# ---------- 3. Interactividad: cuando cambian los controles, se recalcula todo ----------
@app.callback(
    Output("ranking", "figure"), Output("mapa", "figure"),
    Output("perfil", "figure"), Output("titulo-pais", "children"),
    [Input(p, "value") for p in PILARES], Input("pais", "value"),
)
def actualizar(talento, innovacion, costes, entorno, pais):
    pesos = {"Talento": talento, "Innovación": innovacion, "Costes": costes, "Entorno": entorno}
    resultado = calcular_indice(datos, indicadores, pesos)
    resultado["nombre"] = resultado.index.map(nombres)

    # Gráfico 1: ranking de barras (el país elegido en naranja)
    colores = ["#f2a541" if c == pais else "#0f8b8d" for c in resultado.index]
    ranking = px.bar(resultado.iloc[::-1], x="nota", y="nombre", orientation="h",
                     text=resultado["nota"].iloc[::-1].round(0), height=650,
                     labels={"nota": "Nota (0-100)", "nombre": ""})
    ranking.update_traces(marker_color=colores[::-1])

    # Gráfico 2: mapa de Europa
    mapa = px.choropleth(resultado.reset_index(), locations="pais", color="nota",
                         hover_name="nombre", scope="europe", range_color=[0, 100],
                         color_continuous_scale="Teal", labels={"nota": "Nota"})
    mapa.update_geos(fitbounds="locations", visible=False)

    # Gráfico 3: el país elegido frente a la media de la UE en cada pilar
    comparacion = pd.DataFrame({
        "Pilar": PILARES * 2,
        "Nota": list(resultado.loc[pais, PILARES]) + list(resultado[PILARES].mean()),
        "Quién": [nombres[pais]] * 4 + ["Media UE"] * 4,
    })
    perfil = px.bar(comparacion, x="Pilar", y="Nota", color="Quién", barmode="group",
                    range_y=[0, 100], color_discrete_sequence=["#0f8b8d", "#c9d3e0"])

    titulo = f"{nombres[pais]}: puesto {resultado.loc[pais, 'puesto']} de 27"
    return ranking, mapa, perfil, titulo


if __name__ == "__main__":
    app.run(debug=True)
