"""Gráficos y tarjetas de la app."""
import plotly.express as px
import plotly.graph_objects as go
from dash import html

AZUL = "#0f8b8d"
NARANJA = "#f2a541"
VERDE = "#2a9d8f"
ROJO = "#e76f51"
COLORES_GRUPOS = ["#08306b", "#4fb3bf", "#f2a541", "#e76f51"]
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
        # Por qué se recomienda: en qué está más por encima y más por debajo de la media
        vs_media = (fila[pilares].astype(float) - resultado[pilares].mean()).dropna()
        if vs_media.empty:  # el usuario ha desmarcado todos los indicadores
            return []
        ventaja, desventaja = vs_media.idxmax(), vs_media.idxmin()
        diferencia = fila["nota"] - resultado.iloc[i + 1]["nota"]
        tarjetas.append(html.Div([
            html.Div([medallas[i], " ", bandera(codigos2[pais]), " ", nombres[pais]], className="podio-pais"),
            html.Div(f"{fila['nota']:.2f}", className="podio-nota"),
            html.Div(f"✔ Destaca en {ventaja} ({vs_media[ventaja]:+.0f} vs. media)", className="ventaja"),
            # Si su peor pilar sigue por encima de la media, no "flojea": es su punto menos fuerte
            html.Div(f"✘ Flojea en {desventaja} ({vs_media[desventaja]:+.0f} vs. media)", className="desventaja")
            if vs_media[desventaja] < 0 else
            html.Div(f"• Punto menos fuerte: {desventaja} ({vs_media[desventaja]:+.0f} vs. media)",
                     className="descripcion"),
            html.Div(f"+{diferencia:.2f} sobre el siguiente", className="descripcion"),
        ], className="caja podio"))
    return tarjetas


def flecha(cambio):
    """▲3 si el país sube 3 puestos, ▼2 si baja 2, nada si se queda igual."""
    return f"  ▲{cambio}" if cambio > 0 else f"  ▼{-cambio}" if cambio < 0 else ""


def ranking(resultado, pais, puesto_base):
    """Barras ordenadas. puesto_base: puesto de cada país con pesos iguales (para las flechas)."""
    colores = [NARANJA if c == pais else AZUL for c in resultado.index]
    cambio = (puesto_base - resultado["puesto"]).reindex(resultado.index)
    textos = [f"{n:.1f}{flecha(c)}" for n, c in zip(resultado["nota"], cambio)]
    fig = px.bar(resultado.iloc[::-1], x="nota", y="nombre", orientation="h",
                 text=textos[::-1], height=500,
                 labels={"nota": "Nota (0-100)", "nombre": ""})
    fig.update_traces(marker_color=colores[::-1], textposition="outside", hovertemplate="%{y}: %{x:.2f}<extra></extra>")
    fig.update_layout(margin=dict(l=10, r=40, t=10, b=10), xaxis_range=[0, 100])
    fig.update_yaxes(dtick=1, tickfont_size=11)  # que se vean los 27 nombres
    return fig


def mapa(resultado, pais, columna):
    """Mapa coloreado por la columna elegida: nota global, un pilar o el grupo (clustering)."""
    df = resultado.reset_index()
    media, lider = df["nota"].mean(), df["nota"].max()
    df["dif_media"] = df["nota"] - media
    df["dif_lider"] = df["nota"] - lider

    if columna == "grupo":
        # Colores por grupo (categorías), con leyenda
        fig = px.choropleth(df.sort_values("grupo"), locations="pais", color="grupo",
                            color_discrete_sequence=COLORES_GRUPOS, hover_name="nombre",
                            hover_data={"pais": False, "nota": ":.2f", "puesto": True},
                            labels={"grupo": "Grupo"})
        fig.update_traces(marker_line_color="white", marker_line_width=0.6)
        fig.update_layout(legend=dict(orientation="h", y=-0.02, x=0, title=None))
        return _decorar_mapa(fig, df, pais, leyenda=True)

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
    return _decorar_mapa(fig, df, pais)


def _decorar_mapa(fig, df, pais, leyenda=False):
    """Borde naranja del país elegido, siglas de los países y estilo del fondo."""
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
                      showlegend=leyenda)
    fig.update_traces(showlegend=False, selector=dict(type="scattergeo"))
    return fig


def perfil(resultado, pais, nombre, pilares):
    """Diferencia del país con la media de la UE en cada pilar: verde = mejor, rojo = peor."""
    nota_pais = resultado.loc[pais, pilares].astype(float)
    media = resultado[pilares].mean()
    diferencia = nota_pais - media
    fig = go.Figure(go.Bar(
        x=pilares, y=diferencia, marker_color=[VERDE if d >= 0 else ROJO for d in diferencia],
        text=[f"{d:+.1f}" for d in diferencia], textposition="outside",
        customdata=list(zip(nota_pais, media)),
        hovertemplate=("<b>%{x}</b><br>" + nombre + ": %{customdata[0]:.2f}<br>"
                       "Media UE: %{customdata[1]:.2f}<br>Diferencia: %{y:+.2f}<extra></extra>"),
    ))
    fig.add_hline(y=0, line_color="#1b2a41", line_width=1)
    limite = max(10, abs(diferencia).max() * 1.3)
    fig.update_layout(height=420, yaxis_range=[-limite, limite],
                      yaxis_title=f"Puntos respecto a la media UE", margin=dict(t=20))
    return fig
