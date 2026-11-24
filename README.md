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

## Cómo funciona

1. **Datos** (`src/datos.py`): descarga 8 indicadores de Eurostat y del Banco Mundial
   (lista en `datos/indicadores.csv`) y guarda el dato más reciente de cada país en `datos/datos.csv`.
2. **Índice** (`src/indice.py`): pasa cada indicador a una nota de 0 a 100 (en los costes, más barato = mejor),
   hace la media de cada pilar y la media ponderada de los pilares con los pesos del usuario.
3. **App** (`app.py`): sliders de pesos, ranking, mapa y comparación de un país con la media de la UE.

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
- [ ] Mejoras de diseño
- [ ] Añadir más indicadores y años
