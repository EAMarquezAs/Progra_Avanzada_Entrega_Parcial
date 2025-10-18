import streamlit as st
import folium
from processing import df
from viz import map_sin, map_fallecidos

st.title("Prueba")

st.write("Tabla")
st.table(df.head())

st.write("Mapas")
st.components.v1.html(folium.Figure().add_child(map_sin).render(), height=500)
