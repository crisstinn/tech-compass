# ¿Dónde invertir en tecnología en Europa?

App interactiva que ordena los 27 países de la UE según lo atractivos que son para una empresa
tecnológica. El usuario decide qué le importa más (talento, innovación, costes o entorno) y el
ranking se recalcula al momento.

Proyecto de *Desarrollo de Aplicaciones para la Visualización de Datos* (ICAI).

**App desplegada:** https://tech-compass-cog9.onrender.com

_(La versión gratuita de Render se duerme si nadie la usa: la primera carga puede tardar unos 50 segundos.)_

## Objetivos

- Ayudar a una empresa tecnológica a comparar países europeos para invertir o abrir una sede.
- Que el usuario decida qué le importa más (talento, innovación, costes o entorno) y vea el ranking al momento.
- Usar datos oficiales y públicos, descargados automáticamente.

## Funcionalidades

- **Pesos ajustables** por pilar (talento, innovación, costes y entorno) y **perfiles de empresa**
  predefinidos (startup, expansión, I+D, reducir costes, buscar talento), con botón para restablecer.
- **Elección de indicadores** dentro de cada pilar.
- **Ranking** con flechas ▲▼ que indican cuántos puestos sube o baja cada país respecto a pesos iguales.
- **Podio** con los tres mejores países y por qué se recomiendan (en qué destacan y en qué flojean).
- **Mapa interactivo**: nota global, cada pilar o **grupos de países similares** (clustering K-Means).
- **Comparación con la media de la UE** del país elegido (verde = mejor, rojo = peor).
- **Descarga** de los resultados en CSV con las preferencias elegidas.
- **API REST** con los resultados en JSON.

## Cómo funciona

1. **Datos** (`src/datos.py`): descarga 8 indicadores de Eurostat y del Banco Mundial
   (lista en `datos/indicadores.csv`) y guarda el dato más reciente de cada país en `datos/datos.csv`.
2. **Índice** (`src/indice.py`): pasa cada indicador a una nota de 0 a 100 (en los costes, más barato = mejor),
   hace la media de cada pilar y la media ponderada de los pilares con los pesos del usuario.
3. **Modelo** (`src/modelo.py`): K-Means (scikit-learn) agrupa los países con un perfil parecido.
4. **Perfiles** (`src/perfiles.py`): pesos predefinidos para cada tipo de empresa.
5. **Gráficos** (`src/graficos.py`): ranking, mapa, podio y comparación (Plotly).
6. **API REST** (`src/api.py`, Flask-RESTful):
   - `GET /api/ranking` → ranking con pesos iguales
   - `GET /api/ranking/<perfil>` → ranking de un perfil (`startup`, `expansion`, `id`, `costes`, `talento`)
   - `GET /api/pais/<codigo>` → ficha de un país (por ejemplo `/api/pais/ESP`)
7. **App** (`app.py`): diseño de la página y callbacks de Dash.

## Ejecutar

```
pip install -r requirements.txt
python app.py
```

Para actualizar los datos: `python src/datos.py`

## Plan de trabajo

- [x] Elegir los indicadores y las fuentes de datos
- [x] Descarga automática desde Eurostat y Banco Mundial
- [x] Cálculo del índice con pesos ajustables
- [x] App interactiva con ranking, mapa y perfil por país
- [x] Despliegue en Render
- [x] Mejoras de diseño: mapa interactivo, podio, perfiles de empresa
- [x] Clustering de países y API REST
- [ ] Añadir más indicadores y años
