import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import pandas as pd
from processing import df


def mapa(df):
  map = folium.Map(location=(df['LAT'].mean(), df['LON'].mean()), zoom_start=5)
  cluster = MarkerCluster().add_to(map)
  for index, row in df.iterrows():
    if not pd.isna(row['LAT']) and not pd.isna(row['LON']):
      folium.Marker(location=[row['LAT'], row['LON']]).add_to(cluster)
  return map


map_sin = mapa(df.drop_duplicates(subset=['CÓDIGO SINIESTRO']))
map_fallecidos = mapa(df[df['GRAVEDAD']=='FALLECIDO'])
