import streamlit as st
import folium
from processing import df, total_per, total_sin
import datetime
import viz


def update(w1, w2, range=False):
    if (len(st.session_state[w1]) == 2 and len(st.session_state[w2]) == 2) or not range:
        st.session_state[w1] = st.session_state[w2]
    else:
        st.session_state[w1] = st.session_state[w1]


# Título
st.set_page_config(page_title="Personas - Siniestros Fatales (2021 - 2023)")
st.title("Personas Involucradas en Siniestros Fatales (2021 - 2023)")
st.caption("Fuente: https://www.onsv.gob.pe/estaticos/excel/BBDD%20ONSV%20-%20PERSONAS%202021-2023.xlsx")


# Medidas
st.write("Número de Datos sin Aplicar Filtros")
col1, col2 = st.columns(2)
col1.metric(label="Total de Personas", value=total_per)
col2.metric(label="Total de Siniestros", value=total_sin)

# Filtro por Gravedad
grav_pills = st.sidebar.pills("Gravedad", options=map(lambda x: x.capitalize(), df['GRAVEDAD'].unique()),
                        selection_mode='multi', default=map(lambda x: x.capitalize(), df['GRAVEDAD'].unique()))
filter_grav = df['GRAVEDAD'].isin(map(lambda x: x.upper(), grav_pills))

# Filtro por Fecha
if 'sliderfecha' not in st.session_state:
        st.session_state.sliderfecha = (datetime.date(2021, 1, 1), datetime.date(2023, 12, 31))
if 'boxfecha' not in st.session_state:
        st.session_state.boxfecha = (datetime.date(2021, 1, 1), datetime.date(2023, 12, 31))
slider_fecha = st.sidebar.slider(label='Fecha', min_value=datetime.date(2021, 1, 1), max_value=datetime.date(2023, 12, 31), 
                                key='sliderfecha', on_change=update, args=('boxfecha', 'sliderfecha', True))
box_fecha = st.sidebar.date_input(label="", min_value=datetime.date(2021, 1, 1), max_value=datetime.date(2023, 12, 31),
                                key='boxfecha', on_change=update, args=('sliderfecha', 'boxfecha', True))
filter_fecha = (df['FECHA'] >= slider_fecha[0]) & (df['FECHA'] <= slider_fecha[1])

# Todos los filtros
filters = filter_grav & filter_fecha

# Medidas para Datos Filtrados
st.write("Número de Datos con Filtros Aplicados")
col1, col2 = st.columns(2)
col1.metric(label="Total de Personas", value=df.loc[filters].shape[0])
col2.metric(label="Total de Siniestros", value=df.loc[filters].drop_duplicates(subset="CÓDIGO SINIESTRO").shape[0])
st.divider()

# Top Departamentos
st.header(f"Top 10 Departamentos con más Personas Involucradas en Siniestros Fatales")
st.caption(f"Filtro de Gravedad: {grav_pills}")
st.caption(f"Filtro de Fecha: {slider_fecha[0]} - {slider_fecha[1]}")
top_dep = df.loc[filters].groupby(by='DEPARTAMENTO').count().reset_index()
top_dep = top_dep.nlargest(10, columns='CÓDIGO PERSONA')
st.altair_chart(viz.barchart(top_dep, 'CÓDIGO PERSONA', 'DEPARTAMENTO', 'Número de Personas', 'Departamento', sorty='-x'))

# Tipo de vehículo
st.header(f"Distribución de Personas Involucradas en Siniestros Fatales por Tipo de Vehículo")
st.caption(f"Filtro de Gravedad: {grav_pills}")
st.caption(f"Filtro de Fecha: {slider_fecha[0]} - {slider_fecha[1]}")
veh = df.groupby(by='VEHÍCULO').count().reset_index() 
st.altair_chart(viz.barchart(veh, 'VEHÍCULO', 'CÓDIGO PERSONA', 'Tipo de Vehículo', 'Número de Personas', sortx='-y'))

# Tipo de Siniestro
st.header(f"Personas Involucradas en Siniestros Fatales por Clase de Siniestro")
st.caption(f"Filtro de Gravedad: {grav_pills}")
st.caption(f"Filtro de Fecha: {slider_fecha[0]} - {slider_fecha[1]}")
tip_sin = df.loc[filters].groupby(by='CLASE DE SINIESTRO').count().reset_index()
st.altair_chart(viz.pie(tip_sin, 'CLASE DE SINIESTRO', 'CÓDIGO PERSONA'))

# Edad
st.header(f"Distribución de la Edad Personas Involucradas en Siniestros Fatales por Clase de Siniestro")
st.caption(f"Filtro de Gravedad: {grav_pills}")
st.caption(f"Filtro de Fecha: {slider_fecha[0]} - {slider_fecha[1]}")
st.altair_chart(viz.hist(df.loc[filters], 'EDAD', 'Edad', 'Número de Personas'))

# Mapa
map_per = viz.mapa(df.loc[filters])
st.header(f"Mapa de Personas Involucradas en Siniestros Fatales")
st.caption(f"Filtro de Gravedad: {grav_pills}")
st.caption(f"Filtro de Fecha: {slider_fecha[0]} - {slider_fecha[1]}")
st.components.v1.html(folium.Figure().add_child(map_per).render(), height=500)

# Dataframe
st.header("Tabla Filtrada")
st.dataframe(df.loc[filters])
