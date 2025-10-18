import streamlit as st
from processing import df
from viz import map_sin, map_fallecidos

st.title("Prueba")

st.write("Tabla")
st.table(df)

st.write("Mapas")
st_folium(map_sin)
st_folium(map_fallecidos)
