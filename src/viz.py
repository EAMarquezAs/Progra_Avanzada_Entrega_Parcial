import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
from processing import df


def mapa(df):
  map = folium.Map(location=(df['LAT'].mean(), df['LON'].mean()), zoom_start=5)
  cluster = MarkerCluster().add_to(map)
  for index, row in df.iterrows():
    if not pd.isna(row['LAT']) and not pd.isna(row['LON']):
      folium.Marker(location=[row['LAT'], row['LON']]).add_to(cluster)
  return map


def barchart(df, colx, coly, titlex, titley, sortx=None, sorty=None):
  chart = alt.Chart(df).mark_bar().encode(
        # Ordenar el eje Y por la cantidad de fallecidos (FALLECIDOS)
        y=alt.Y(coly, sort=sorty, title=titley),
        x=alt.X(colx, sort=sortx, title=titlex),
        tooltip=[coly, colx],
        # Añadir texto con el valor exacto
        text=alt.Text(colx) 
  )
  return chart


def pie(df, categories, values):
  chart = alt.Chart(df).encode(
    theta=alt.Theta(f"{values}:Q", stack=True), color=alt.Color(f"{categories}:N")
  ).mark_arc(outerRadius=110)
  text = chart.mark_text(radius=140, size=15).encode(text=f"{values}:N")
  return chart+text


def hist(df, colx, titlex, titley):
  chart = alt.Chart(df).mark_bar().encode(x=alt.X(colx, bin=True, title=titlex), y=alt.Y('count()', title=titley))
  return chart
