"""App: ¿dónde invertir en tecnología en Europa?

Ejecutar:  python app.py   y abrir http://127.0.0.1:8050
API REST:  http://127.0.0.1:8050/api/ranking   (ver src/api.py)
"""
import pandas as pd
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update

from src import graficos
from src.api import crear_api
from src.indice import calcular_indice
from src.modelo import agrupar_paises
from src.perfiles import PERFILES

# ---------- 1. Cargar los datos ----------
datos = pd.read_csv("datos/datos.csv").set_index("pais")
indicadores = pd.read_csv("datos/indicadores.csv")
paises = pd.read_csv("datos/paises.csv")
nombres = dict(zip(paises["codigo3"], paises["nombre"]))
codigos2 = dict(zip(paises["codigo3"], paises["codigo2"]))
PILARES = ["Talento", "Innovación", "Costes", "Entorno"]
TODOS = {p: list(indicadores.loc[indicadores["pilar"] == p, "id"]) for p in PILARES}

# Años de los datos (cada indicador usa el último año disponible)
años = datos.filter(like="año_").stack()
AÑOS_DATOS = f"{int(años.min())}–{int(años.max())}"

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
                         value=TODOS[pilar])


# ---------- 2. Diseño de la página ----------
app = Dash(__name__, title="¿Dónde invertir en tecnología?")
SIN_BARRA = {"displayModeBar": False}  # oculta la barra de herramientas de Plotly
server = app.server  # lo necesita Render
crear_api(server, datos, indicadores, nombres, PILARES)  # API REST en /api/...

OPCIONES_PAIS = [{"label": n, "value": c} for c, n in sorted(nombres.items(), key=lambda x: x[1])]

guia = html.Details([
    html.Summary("¿Cómo se usa? (guía rápida)"),
    html.Ol([
        html.Li("Elige el tipo de empresa o mueve los sliders según lo que más te importe."),
        html.Li("Desmarca un indicador si no quieres tenerlo en cuenta."),
        html.Li("Mira el ranking y el podio: las flechas ▲▼ indican cuántos puestos sube o baja "
                "cada país respecto a darle el mismo peso a todo."),
        html.Li("Elige un país (o haz clic en el mapa) para ver en qué está por encima o por debajo de la media."),
        html.Li("Descarga tus resultados en CSV con el botón de la derecha."),
    ]),
], className="guia")

calculo = html.Details([
    html.Summary("¿Cómo se calcula la nota?"),
    html.Ol([
        html.Li(["Se descargan ", html.B("8 indicadores"), " de Eurostat y del Banco Mundial para los 27 países "
                 "(el dato más reciente de cada uno)."]),
        html.Li(["Cada indicador se pasa a una ", html.B("nota de 0 a 100"), ": el peor país saca 0 y el mejor 100. "
                 "En los costes se invierte: el más barato saca 100."]),
        html.Li(["La nota de cada ", html.B("pilar"), " es la media de sus indicadores."]),
        html.Li(["La ", html.B("nota final"), " es la media ponderada de los pilares con los pesos que eliges en los sliders."]),
    ]),
    html.P("Ejemplo: con todos los pesos a 5, la nota final es la media simple de los 4 pilares.", className="descripcion"),
], className="guia")

# Fila de controles: tipo de empresa + una caja por pilar con su slider y sus casillas
cabecera_controles = html.H3("¿Qué es más importante para ti?", className="subtitulo")

# Tipo de empresa: entre los sliders y el ranking
tipo_empresa = html.Div([
    html.Label("Tipo de empresa:"),
    dcc.Dropdown(id="tipo-empresa", value="equilibrado", clearable=False, className="selector-perfil",
                 options=[{"label": v["nombre"], "value": k} for k, v in PERFILES.items()]),
    html.Span("Ajusta los sliders automáticamente según el tipo de empresa.", className="descripcion"),
    html.Button("Restablecer", id="restablecer", className="boton"),
], className="caja cabecera fila-empresa")

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
    guia,
    calculo,
    # Barra fija: se queda arriba al bajar por la página
    html.Div([cabecera_controles, controles], className="barra-fija"),
    tipo_empresa,
    # En medio: ranking a la izquierda y podio en vertical a la derecha
    html.Div([
        html.Div([html.H3("Ranking"), dcc.Graph(id="ranking", config=SIN_BARRA)], className="caja grande"),
        html.Div([
            html.Div(id="podio", className="columna-podio"),
            # Explicación de los textos del podio (se abre al hacer clic)
            html.Details(id="explicacion", children=[
                html.Summary("ⓘ ¿Qué significa esto?"),
                html.P([html.B("✔ Destaca en: "), "el pilar en el que el país está más por encima de la media "
                        "de los 27 países de la UE. Ej.: «Innovación (+44)» = 44 puntos más que la media."]),
                html.P([html.B("✘ Flojea en: "), "el pilar en el que el país está más por debajo de la media. "
                        "Ej.: «Talento (−20)» = 20 puntos menos que la media."]),
                html.P([html.B("• Punto menos fuerte: "), "su pilar con la nota más baja, pero que aun así está "
                        "por encima de la media. No es una debilidad, solo lo que menos destaca."]),
                html.P([html.B("+X sobre el siguiente: "), "puntos de ventaja sobre el país que va detrás."]),
                html.P("Las notas de los pilares van de 0 a 100: 0 = peor país de la UE en ese pilar, "
                       "100 = mejor país.", className="descripcion"),
            ], className="caja explicacion"),
            # Selector de país debajo del tercer puesto
            html.Div([html.Label("País a analizar"),
                      html.P("Se marca en naranja. También puedes hacer clic en el mapa.", className="descripcion"),
                      dcc.Dropdown(id="pais", value="ESP", clearable=False, options=OPCIONES_PAIS)],
                     className="caja"),
            html.Button("⬇ Descargar mis resultados (CSV)", id="descargar", className="boton"),
            dcc.Download(id="descarga"),
        ], className="columna-derecha"),
    ], className="fila"),
    # Abajo: mapa a la izquierda y comparación del país a la derecha
    html.Div([
        html.Div([
            html.Div([html.H3("Mapa"), html.Span("Pinta en el mapa:", className="descripcion"),
                      dcc.Dropdown(id="columna-mapa", value="nota", clearable=False, className="selector",
                                   options=[{"label": "Nota global", "value": "nota"}]
                                   + [{"label": p, "value": p} for p in PILARES]
                                   + [{"label": "Grupos de países similares (K-Means)", "value": "grupo"}])],
                     className="cabecera"),
            html.P("Pasa el ratón por un país para ver su ficha; haz clic para analizarlo.", className="descripcion"),
            dcc.Graph(id="mapa", config=SIN_BARRA),
        ], className="caja mapa"),
        html.Div([
            html.Div([html.H3(id="titulo-pais"),
                      dcc.Dropdown(id="pais-abajo", value="ESP", clearable=False, options=OPCIONES_PAIS,
                                   className="selector")], className="cabecera"),
            html.P("Diferencia con la media de la UE en cada pilar: verde = mejor, rojo = peor.",
                   className="descripcion"),
            dcc.Graph(id="perfil", config=SIN_BARRA),
            html.H4("Datos reales del país", className="subtitulo-tabla"),
            html.P("Verde = mejor que la media de la UE; rojo = peor (en costes, más barato es mejor).",
                   className="descripcion"),
            html.Div(id="tabla-pais"),
        ], className="caja"),
    ], className="fila"),
    html.Footer(f"Fuentes: Eurostat y Banco Mundial (dato más reciente de cada indicador, años {AÑOS_DATOS}). "
                "API con los resultados en /api/ranking.", className="pie"),
])


# ---------- 3. Interactividad ----------
def calcular(pesos_lista, listas_activos):
    """Calcula el índice con los pesos de los sliders y los indicadores marcados."""
    pesos = dict(zip(PILARES, pesos_lista))
    activos = sum(listas_activos, [])  # junta las 4 listas de casillas en una
    resultado = calcular_indice(datos, indicadores, pesos, activos)
    resultado["nombre"] = resultado.index.map(nombres)
    return resultado, activos


@app.callback(
    [Output(p, "value") for p in PILARES],
    [Output("ind-" + p, "value") for p in PILARES],
    Output("tipo-empresa", "value"),
    Input("tipo-empresa", "value"), Input("restablecer", "n_clicks"),
    prevent_initial_call=True,
)
def aplicar_perfil(perfil, _clics):
    """El tipo de empresa mueve los sliders; 'Restablecer' vuelve a pesos iguales y todo marcado."""
    if ctx.triggered_id == "restablecer":
        perfil = "equilibrado"
    pesos = PERFILES[perfil]["pesos"]
    return [pesos[p] for p in PILARES] + [TODOS[p] for p in PILARES] + [perfil]


@app.callback(
    Output("podio", "children"), Output("ranking", "figure"), Output("mapa", "figure"),
    Output("perfil", "figure"), Output("titulo-pais", "children"), Output("tabla-pais", "children"),
    [Input(p, "value") for p in PILARES],
    [Input("ind-" + p, "value") for p in PILARES],
    Input("pais", "value"), Input("columna-mapa", "value"),
)
def actualizar(talento, innovacion, costes, entorno, ind_t, ind_i, ind_c, ind_e, pais, columna):
    """Cuando cambia cualquier control, se recalcula el índice y se redibuja todo."""
    resultado, activos = calcular([talento, innovacion, costes, entorno], [ind_t, ind_i, ind_c, ind_e])

    # Puesto con pesos iguales, para ver quién sube o baja con los pesos elegidos
    base = calcular_indice(datos, indicadores, dict.fromkeys(PILARES, 5), activos)["puesto"]

    if columna == "grupo":
        resultado["grupo"] = agrupar_paises(resultado, PILARES)

    titulo = f"{nombres[pais]}: puesto {resultado.loc[pais, 'puesto']} de 27 ({resultado.loc[pais, 'nota']:.2f} puntos)"
    return (graficos.podio(resultado, nombres, codigos2, PILARES),
            graficos.ranking(resultado, pais, base),
            graficos.mapa(resultado, pais, columna),
            graficos.perfil(resultado, pais, nombres[pais], PILARES),
            titulo,
            graficos.tabla_pais(datos, indicadores, pais, nombres[pais]))


@app.callback(
    Output("descarga", "data"),
    Input("descargar", "n_clicks"),
    [State(p, "value") for p in PILARES],
    [State("ind-" + p, "value") for p in PILARES],
    State("tipo-empresa", "value"),
    prevent_initial_call=True,
)
def descargar(_clics, talento, innovacion, costes, entorno, ind_t, ind_i, ind_c, ind_e, perfil):
    """Descarga un CSV con las preferencias del usuario y el ranking resultante."""
    resultado, activos = calcular([talento, innovacion, costes, entorno], [ind_t, ind_i, ind_c, ind_e])
    tabla = resultado[["puesto", "nombre", "nota", *PILARES]].round(2)
    cabecera = (f"# Tipo de empresa: {PERFILES[perfil]['nombre']}\n"
                f"# Pesos: Talento={talento}, Innovación={innovacion}, Costes={costes}, Entorno={entorno}\n"
                f"# Indicadores usados: {', '.join(activos)}\n")
    return dcc.send_string(cabecera + tabla.to_csv(index=False), "tech_compass_resultados.csv")


@app.callback(
    Output("explicacion", "open"),
    Input({"tipo": "ayuda", "clave": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def abrir_explicacion(clics):
    """Al hacer clic en una línea del podio, se abre la explicación (y la página baja hasta ella)."""
    return True if any(clics) else no_update


@app.callback(
    Output("pais", "value"), Output("pais-abajo", "value"),
    Input("pais", "value"), Input("pais-abajo", "value"), Input("mapa", "clickData"),
    prevent_initial_call=True,
)
def sincronizar_pais(arriba, abajo, clic):
    """Los dos selectores de país y el clic en el mapa muestran siempre el mismo país."""
    if ctx.triggered_id == "pais":
        return no_update, arriba
    if ctx.triggered_id == "pais-abajo":
        return abajo, no_update
    pais = clic["points"][0].get("location") if clic else None  # clic en el mapa
    return (pais, pais) if pais in nombres else (no_update, no_update)


if __name__ == "__main__":
    app.run(debug=True)
