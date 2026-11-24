"""Gráficos y tarjetas de la app."""
import plotly.express as px
import plotly.graph_objects as go
from dash import html

AZUL = "#0f8b8d"
NARANJA = "#f2a541"
ESCALA = [[0, "#e0f3f8"], [0.5, "#4fb3bf"], [1, "#08306b"]]  # azul claro -> turquesa -> azul oscuro


def bandera(codigo2):
    """Imagen de la bandera a partir del código de 2 letras (Grecia es EL en Eurostat)."""
    codigo2 = "gr" if codigo2 == "EL" else codigo2.lower()
    return html.Img(src=f"https://flagcdn.com/24x18/{codigo2}.png", className="bandera")


def podio(resultado, nombres, codigos2, pilares):
    """Tres tarjetas con los tres primeros países."""
    medallas = ["🥇", "🥈", "🥉"]
    tarjetas = []
    for i in range(3):
        pais = resultado.index[i]
        fila = resultado.iloc[i]
        fortaleza = fila[pilares].astype(float).idxmax()
        diferencia = fila["nota"] - resultado.iloc[i + 1]["nota"]
        tarjetas.append(html.Div([
            html.Div([medallas[i], " ", bandera(codigos2[pais]), " ", nombres[pais]], className="podio-pais"),
            html.Div(f"{fila['nota']:.2f}", className="podio-nota"),
            html.Div(f"Fortaleza: {fortaleza}"),
            html.Div(f"+{diferencia:.2f} sobre el siguiente", className="descripcion"),
        ], className="caja podio"))
    return tarjetas


def ranking(resultado, pais):
    colores = [NARANJA if c == pais else AZUL for c in resultado.index]
    fig = px.bar(resultado.iloc[::-1], x="nota", y="nombre", orientation="h",
                 text=resultado["nota"].iloc[::-1].round(1), height=500,
                 labels={"nota": "Nota (0-100)", "nombre": ""})
    fig.update_traces(marker_color=colores[::-1], textposition="outside", hovertemplate="%{y}: %{x:.2f}<extra></extra>")
    fig.update_layout(margin=dict(l=10, r=40, t=10, b=10), xaxis_range=[0, 100])
    fig.update_yaxes(dtick=1, tickfont_size=11)  # que se vean los 27 nombres
    return fig


def mapa(resultado, pais, columna):
    """Mapa coloreado por la columna elegida (nota global o un pilar)."""
    df = resultado.reset_index()
    media, lider = df["nota"].mean(), df["nota"].max()
    df["dif_media"] = df["nota"] - media
    df["dif_lider"] = df["nota"] - lider

    fig = go.Figure(go.Choropleth(
        locations=df["pais"], z=df[columna], zmin=0, zmax=100, colorscale=ESCALA,
        marker_line_color="white", marker_line_width=0.6,
        colorbar=dict(title=columna if columna != "nota" else "Nota", thickness=12,
                      tickvals=[0, 25, 50, 75, 100],
                      ticktext=["0 bajo", "25", "50 medio", "75", "100 alto"]),
        customdata=df[["nombre", "nota", "puesto", "dif_media", "dif_lider"]],
        hovertemplate=("<b>%{customdata[0]}</b><br>"
                       "Nota global: %{customdata[1]:.2f} / 100<br>"
                       "Puesto: %{customdata[2]} de 27<br>"
                       "Vs. media UE: %{customdata[3]:+.2f}<br>"
                       "Vs. líder: %{customdata[4]:+.2f}<extra></extra>"),
    ))
    # País seleccionado: borde naranja grueso
    fig.add_trace(go.Choropleth(
        locations=[pais], z=[1], colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False, marker_line_color=NARANJA, marker_line_width=3, hoverinfo="skip"))
    # Siglas de los países encima del mapa
    fig.add_trace(go.Scattergeo(
        locations=df["pais"], text=df["pais"], mode="text", hoverinfo="skip",
        textfont=dict(size=9, color="#1b2a41")))

    fig.update_geos(fitbounds="locations", visible=False, bgcolor="#eaf2f8",
                    showland=True, landcolor="#f7f9fb")
    fig.update_layout(height=430, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#eaf2f8",
                      showlegend=False)
    return fig


def perfil(resultado, pais, nombre, pilares):
    """Barras del país elegido frente a la media de la UE en cada pilar."""
    fig = go.Figure([
        go.Bar(name=nombre, x=pilares, y=resultado.loc[pais, pilares], marker_color=AZUL),
        go.Bar(name="Media UE", x=pilares, y=resultado[pilares].mean(), marker_color="#c9d3e0"),
    ])
    fig.update_traces(hovertemplate="%{x}: %{y:.2f}<extra></extra>")
    fig.update_layout(barmode="group", yaxis_range=[0, 100], height=420,
                      legend=dict(orientation="h", y=1.1))
    return fig
