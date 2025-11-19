import streamlit as st
import folium
import datetime
import pandas as pd
import viz
import requests
from scrapper import update_data


def get_data(table:str = "personas", **kwargs) -> pd.DataFrame:
    url = "https://ntkbropqoaliyvoziqyz.supabase.co/rest/v1/"
    headers = {
        "apikey": "sb_publishable_ChXTotbmNNA7RyEOcPrZEw_deMjmAbX",
        "Authorization": "Bearer sb_publishable_ChXTotbmNNA7RyEOcPrZEw_deMjmAbX"
    }
    kwargs.setdefault("select", "*, ...vehiculos!inner(*, ...siniestros!inner(*))")
    r = requests.get(url=url+table, headers=headers, params=kwargs)
    if r.status_code != 200:
        raise Exception("Hubo un error en la recolección de datos")
    return pd.DataFrame(r.json())


def update(w1, w2, range=False):
    if (len(st.session_state[w1]) == 2 and len(st.session_state[w2]) == 2) or not range:
        st.session_state[w1] = st.session_state[w2]
    else:
        st.session_state[w1] = st.session_state[w1]


# Get Dataframe
df = get_data()
df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

df_siniestros = get_data("siniestros", select="*")
df_siniestros["fecha"] = pd.to_datetime(df_siniestros["fecha"]).dt.date


# Título
st.set_page_config(page_title="Personas - Accidentes de Tránsito")
st.title("Personas Involucradas en Accidentes de Tránsito")
st.caption("Fuente ONSV: https://www.onsv.gob.pe/estaticos/excel/BBDD%20ONSV%20-%20PERSONAS%202021-2023.xlsx")
st.caption("Fuente UBIGEO: https://github.com/jmcastagnetto/ubigeo-peru-aumentado/blob/main/ubigeo_distrito.csv")
st.caption("Fuente Bomberos: https://sgonorte.bomberosperu.gob.pe/24horas")


# Medidas
st.write("Número de Datos Antes de Procesamiento")
col1, col2 = st.columns(2)
col1.metric(label="Total de Personas", value=18464)
col2.metric(label="Total de Siniestros", value=6705)
st.metric(label="Número de Siniestros (últimas 24 horas)", value=df_siniestros.loc[df_siniestros["fecha"] >= datetime.date.today() - datetime.timedelta(days=1)].shape[0])


# Botón para actualizar
st.sidebar.write('Recolectar Datos de Base de los Bomberos')
st.sidebar.button("Actualizar datos", on_click=update_data)


# Filtro por Gravedad
grav_pills = st.sidebar.pills("Gravedad", options=map(lambda x: x.capitalize(), df['gravedad'].unique()),
                        selection_mode='multi', default=map(lambda x: x.capitalize(), df['gravedad'].unique()))
filter_grav = df['gravedad'].isin(map(lambda x: x.upper(), grav_pills))


# Filtro por Sexo
sex_radio = st.sidebar.segmented_control("Sexo", options=map(lambda x: x.capitalize(), df['sexo'].unique()), selection_mode='multi',
                                 default=map(lambda x: x.capitalize(), df['sexo'].unique()))
filter_sex = df['sexo'].isin(map(lambda x: x.upper(), sex_radio))


# Filtro por Tipo Persona
tip_per = st.sidebar.multiselect("Tipo de Persona", options=map(lambda x: x.capitalize(), df['tipo_per'].unique()),
                                 placeholder="All")
if len(tip_per) == 0:
        filter_tipper = True
else:
        filter_tipper = df['tipo_per'].isin(map(lambda x: x.upper(), tip_per))


# Filtro por Causa
causa_mulsel = st.sidebar.multiselect("Causa", options=map(lambda x: x.capitalize(), df['causa'].unique()),
                                 placeholder="All")
if len(causa_mulsel) == 0:
        filter_causa = True
        filter_causa_sin = True
else:
        filter_causa = df['causa'].isin(map(lambda x: x.upper(), causa_mulsel))
        filter_causa_sin = df_siniestros['causa'].isin(map(lambda x: x.upper(), causa_mulsel))


# Filtro por Fecha
if 'sliderfecha' not in st.session_state:
        st.session_state.sliderfecha = (datetime.date(2021, 1, 1), datetime.date(2023, 12, 31))
if 'boxfecha' not in st.session_state:
        st.session_state.boxfecha = (datetime.date(2021, 1, 1), datetime.date(2023, 12, 31))
slider_fecha = st.sidebar.slider(label='Fecha', min_value=datetime.date(2021, 1, 1), max_value=datetime.date(2023, 12, 31), 
                                key='sliderfecha', on_change=update, args=('boxfecha', 'sliderfecha', True))
box_fecha = st.sidebar.date_input(label="", min_value=datetime.date(2021, 1, 1), max_value=datetime.date(2023, 12, 31),
                                key='boxfecha', on_change=update, args=('sliderfecha', 'boxfecha', True))
filter_fecha = (df['fecha'] >= slider_fecha[0]) & (df['fecha'] <= slider_fecha[1])


# Descargar archivos originales
st.sidebar.write('Archivos Originales')
with open("data\BBDD ONSV - PERSONAS 2021-2023.xlsx", 'rb') as file:
        st.sidebar.download_button("BBDD ONSV", data=file,
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   file_name="BBDD ONSV - PERSONAS 2021-2023.xlsx")
with open("data/ubigeo_distrito.csv", 'rb') as file:
        st.sidebar.download_button("Ubigeo", data = file, mime="text/csv",
                                   file_name="ubigeo_distrito.csv")


# Todos los filtros
filters = filter_grav & filter_fecha & filter_sex & filter_tipper & filter_causa


# Medidas para Datos Filtrados
st.write("Número de Datos con Filtros Aplicados")
col1, col2, col3 = st.columns(3)
col1.metric(label="Total de Personas", value=df.loc[filters].shape[0])
col2.metric(label="Total de Siniestros (base ONSV)", value=df.loc[filters].drop_duplicates(subset="cod_sin").shape[0])
col3.metric(label="Total de Siniestros (base Bomberos)", value=df_siniestros.loc[(pd.to_datetime(df_siniestros["fecha"]).dt.year>=2024) & filter_causa_sin].shape[0])
st.divider()



# Top Departamentos
st.header(f"Top 10 Departamentos con más Personas Involucradas en Accidentes de Tránsito")
top_dep = df.loc[filters].groupby(by='departamento').count().reset_index()
top_dep = top_dep.nlargest(10, columns='cod_per')
st.altair_chart(viz.barchart(top_dep, 'cod_per', 'departamento', 'Número de Personas', 'Departamento', sorty='-x'))


# Tipo de vehículo
st.header(f"Distribución de Personas Involucradas en Accidentes de Tránsito por Tipo de Vehículo")
veh = df.loc[filters].groupby(by='vehiculo').count().reset_index() 
st.altair_chart(viz.barchart(veh, 'vehiculo', 'cod_per', 'Tipo de Vehículo', 'Número de Personas', sortx='-y'))


# Edad
st.header(f"Distribución de la Edad Personas Involucradas en Accidentes de Tránsito por Clase de Siniestro")
st.altair_chart(viz.hist(df.loc[filters], 'edad', 'Edad', 'Número de Personas'))


# Mapas
map_sin = viz.mapa(df_siniestros.loc[(pd.to_datetime(df_siniestros["fecha"]).dt.year>=2024) & filter_causa_sin])
st.header(f"Mapa de Accidentes de Tránsito (últimas 24 horas)")
st.components.v1.html(folium.Figure().add_child(map_sin).render(), height=500)

map_per = viz.mapa(df.loc[filters])
st.header(f"Mapa de Personas Involucradas en Accidentes de Tránsito")
st.components.v1.html(folium.Figure().add_child(map_per).render(), height=500)


# Dataframe
# Dataframe
st.header("Tabla Filtrada")
st.dataframe((pd.concat([df, df_siniestros.loc[(pd.to_datetime(df_siniestros["fecha"]).dt.year>=2024)]])).loc[filters])
