import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# --- 1. CONFIGURACIÓN INICIAL Y PREPROCESAMIENTO DE DATOS ---

@st.cache_data
def load_data(file_path):
    """
    Carga, limpia y preprocesa el dataset de siniestros fatales.
    Utiliza @st.cache_data para evitar recargar y reprocesar la data en cada interacción.
    """
    try:
        # Cargar el archivo, saltando las 3 filas de metadatos del encabezado original.
        # Se usa 'latin1' para manejar la codificación de caracteres especiales en español.
        df = pd.read_csv(file_path, header=3, encoding="latin1")
    except FileNotFoundError:
        st.error(f"Error: El archivo '{file_path}' no se encontró. Asegúrate de que esté en la misma carpeta.")
        return pd.DataFrame(), pd.DataFrame()

    # Mapeo para corregir nombres de columnas mal codificados
    column_name_map = {
        'CÃDIGO SINIESTRO': 'CÓDIGO SINIESTRO',
        'CÃDIGO VEHÃCULO': 'CÓDIGO VEHÍCULO',
        'CÃDIGO PERSONA': 'CÓDIGO PERSONA',
        'LUGAR ATENCIÃN LESIONADO': 'LUGAR ATENCIÓN LESIONADO',
        'LUGAR DE DEFUNCIÃN': 'LUGAR DE DEFUNCIÓN',
        'SITUACIÃN DE PERSONA': 'SITUACIÓN DE PERSONA',
        'PAÃS DE NACIONALIDAD': 'PAÍS DE NACIONALIDAD',
        'OTRO PAÃS DE NACIONALIDAD': 'OTRO PAÍS DE NACIONALIDAD',
        'AÃO': 'AÑO',
        'VEHÃCULO': 'VEHÍCULO',
        'TIPO DE VÃA': 'TIPO DE VÍA',
        'CÃDIGO DE CARRETERA': 'CÓDIGO DE CARRETERA',
        'Â¿SE SOMETIÃ A DOSAJE ETÃLICO CUALITATIVO?': 'DOSAJE ETÍLICO CUALITATIVO',
        'RESULTADO DEL DOSAJE ETÃLICO CUALITATIVO': 'RESULTADO DOSAJE ETÍLICO CUALITATIVO',
        'Â¿SE SOMETIÃ A DOSAJE ETÃLICO CUANTITATIVO?': 'DOSAJE ETÍLICO CUANTITATIVO',
    }
    df.rename(columns=column_name_map, inplace=True)
    
    # Limpiar espacios en los nombres de columna
    df.columns = df.columns.str.strip()

    # Función genérica para corregir codificación de valores de texto
    def fix_encoding(text):
        if pd.isna(text):
            return text
        text = str(text)
        text = text.replace('Ã‘', 'Ñ').replace('Ã\x93', 'Ó').replace('Ã\x8d', 'Í')
        text = text.replace('Ã\x81', 'Á').replace('Ã\x9a', 'Ú').replace('Ã\x89', 'É')
        text = text.replace('Ã\xad', 'í').replace('Ã\x91', 'Ñ')
        text = text.replace('CAÃ\x8dDA', 'CAÍDA').replace('PEATÃ\x93N', 'PEATÓN')
        text = text.replace('PERÃ\x9a', 'PERÚ').replace('CAMIÃ\x93N', 'CAMIÓN')
        return text.strip()

    # Aplicar corrección a las principales columnas categóricas
    columns_to_clean = [
        'TIPO PERSONA', 'GRAVEDAD', 'MES', 'CLASE DE SINIESTRO', 'CAUSA',
        'CAUSA ESPECIFICA', 'TIPO DE VÍA', 'DEPARTAMENTO', 'PROVINCIA',
        'DISTRITO', 'SEXO', 'VEHÍCULO', 'ESTADO LICENCIA', 'CLASE_LICENCIA'
    ]
    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(fix_encoding)

    # 2. Limpieza de 'EDAD' y Creación de Rangos
    df['EDAD'] = df['EDAD'].replace('NO INDICA', np.nan)
    df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce')

    bins = [0, 18, 30, 45, 60, 75, 120]
    labels = ['0-17', '18-29', '30-44', '45-59', '60-74', '75+']
    df['RANGO DE EDAD'] = pd.cut(df['EDAD'], bins=bins, labels=labels, right=False, include_lowest=True)

    # 3. Filtrado para el Análisis Principal: Personas Fallecidas
    df_fallecido = df[df['GRAVEDAD'] == 'FALLECIDO'].copy()

    # 4. Manejo contextual de NULLs en la data de fallecidos
    
    # RANGO DE EDAD: Imputar a 'EDAD DESCONOCIDA' (7.8% de NULLs)
    df_fallecido['RANGO DE EDAD'] = df_fallecido['RANGO DE EDAD'].cat.add_categories('EDAD DESCONOCIDA')
    df_fallecido['RANGO DE EDAD'] = df_fallecido['RANGO DE EDAD'].fillna('EDAD DESCONOCIDA')
    
    # VEHÍCULO: Eliminar 9 filas (0.1% de NULLs)
    df_fallecido.dropna(subset=['VEHÍCULO'], inplace=True)
    
    # DOSAJE y LICENCIA: Imputar a 'SIN INFORMACIÓN' para análisis futuros (no usados en estos 4 gráficos)
    # df_fallecido['RESULTADO DOSAJE ETÍLICO CUALITATIVO'].fillna('SIN INFORMACIÓN', inplace=True)
    # df_fallecido['POSEE LICENCIA'].fillna('SIN INFORMACIÓN', inplace=True)

    return df, df_fallecido

# --- 2. CARGA DE DATOS Y DEFINICIÓN DE VARIABLES ---

# Nombre del archivo CSV a cargar
FILE_PATH = "BBDD ONSV - PERSONAS 2021-2023.xlsx - PERSONAS INVOLUCRADAS.csv"
df_completo, df_fallecido = load_data(FILE_PATH)

if df_completo.empty or df_fallecido.empty:
    st.stop() # Detiene la ejecución si hay un error de carga

# --- 3. FUNCIONES PARA GENERAR GRÁFICOS (ALTAIR) ---

def create_chart_1_tendencia(data):
    """Gráfico 1: Tendencia Anual de la Gravedad de los Siniestros"""
    chart_data = data.groupby(['AÑO', 'GRAVEDAD']).size().reset_index(name='COUNT')
    
    # Define la paleta de colores para las categorías de gravedad
    gravedad_colors = alt.Scale(
        domain=['FALLECIDO', 'LESIONADO', 'ILESO', 'NO SE CONOCE'],
        range=['#DC2626', '#FBBF24', '#10B981', '#6B7280']
    )

    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('AÑO:N', title='Año', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('COUNT', title='Cantidad de Personas Involucradas'),
        color=alt.Color('GRAVEDAD', title='Gravedad', scale=gravedad_colors),
        tooltip=['AÑO', 'GRAVEDAD', 'COUNT']
    ).properties(
        title='1. Personas Involucradas en Siniestros Fatales por Gravedad y Año (2021-2023)'
    ).interactive()
    
    return chart

def create_chart_2_top_departamentos(data):
    """Gráfico 2: Top 10 Departamentos con Mayor Cantidad de Fallecidos"""
    
    # Contar y seleccionar los 10 principales
    top_10_dptos = data['DEPARTAMENTO'].value_counts().nlargest(10).index.tolist()
    chart_data = data[data['DEPARTAMENTO'].isin(top_10_dptos)].groupby('DEPARTAMENTO').size().reset_index(name='FALLECIDOS')

    chart = alt.Chart(chart_data).mark_bar(color='#0EA5E9').encode(
        # Ordenar el eje Y por la cantidad de fallecidos (FALLECIDOS)
        y=alt.Y('DEPARTAMENTO', sort='-x', title='Departamento'),
        x=alt.X('FALLECIDOS', title='Cantidad de Fallecidos'),
        tooltip=['DEPARTAMENTO', 'FALLECIDOS'],
        # Añadir texto con el valor exacto
        text=alt.Text('FALLECIDOS') 
    ).properties(
        title='2. Top 10 Departamentos con Mayor Cantidad de Fallecidos'
    )
    
    return chart

def create_chart_3_clase_siniestro(data):
    """Gráfico 3: Distribución de Fallecidos por Clase de Siniestro (Causas más letales)"""
    
    chart_data = data.groupby('CLASE DE SINIESTRO').size().reset_index(name='FALLECIDOS')
    
    chart = alt.Chart(chart_data).mark_bar(color='#14B8A6').encode(
        x=alt.X('CLASE DE SINIESTRO', sort='-y', title='Clase de Siniestro', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('FALLECIDOS', title='Cantidad de Fallecidos'),
        tooltip=['CLASE DE SINIESTRO', 'FALLECIDOS']
    ).properties(
        title='3. Fallecidos por Clase de Siniestro'
    )
    
    return chart

def create_chart_4_edad_sexo(data):
    """Gráfico 4: Distribución de Fallecidos por Rango de Edad y Sexo"""
    
    chart_data = data.groupby(['RANGO DE EDAD', 'SEXO']).size().reset_index(name='FALLECIDOS')
    
    # Define un orden explícito para el eje X (incluyendo la categoría NULL imputada)
    age_order = ['0-17', '18-29', '30-44', '45-59', '60-74', '75+', 'EDAD DESCONOCIDA']
    
    sexo_colors = alt.Scale(
        domain=['MASCULINO', 'FEMENINO', 'NO INDICA'],
        range=['#3B82F6', '#EC4899', '#A3A3A3'] # Azul, Rosa, Gris
    )

    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('RANGO DE EDAD', sort=age_order, title='Rango de Edad', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('FALLECIDOS', title='Cantidad de Fallecidos'),
        color=alt.Color('SEXO', title='Sexo', scale=sexo_colors),
        column=alt.Column('SEXO', header=alt.Header(titleOrient="bottom", labelOrient="bottom"), title=''),
        tooltip=['RANGO DE EDAD', 'SEXO', 'FALLECIDOS']
    ).properties(
        title='4. Fallecidos por Rango de Edad y Sexo'
    ).resolve_scale(
        y='shared' # Compartir el eje Y para que la comparación sea directa
    )
    
    return chart

# --- 4. STREAMLIT UI ---

st.set_page_config(layout="wide", page_title="Análisis de Fatalidades Viales")

st.title("🛣️ Análisis de Personas Fallecidas en Siniestros de Tránsito (2021-2023)")
st.caption("Fuente de datos: ONSV (preliminar)")

st.sidebar.header("Filtros Globales de la Data")
# Selector de Año (Aplica al Gráfico 2, 3 y 4)
years = sorted(df_fallecido['AÑO'].unique())
selected_years = st.sidebar.multiselect(
    "Selecciona Año(s) para los gráficos 2, 3 y 4:",
    options=years,
    default=years
)

# Aplicar filtro de año a la data de fallecidos
df_filtered = df_fallecido[df_fallecido['AÑO'].isin(selected_years)]


# --- Presentación de Métricas Clave ---
col1, col2, col3 = st.columns(3)

col1.metric("Total de Registros de Siniestros", f"{len(df_completo.drop_duplicates(subset=['CÓDIGO SINIESTRO'])):,}")
col2.metric("Personas Fallecidas (2021-2023)", f"{len(df_fallecido):,}")
col3.metric("Fallecidos en la Selección Actual", f"{len(df_filtered):,}")

st.markdown("---")


# --- Presentación de Gráficos ---

# Gráfico 1 (Usa la data completa, no la filtrada por sidebar, para ver la tendencia)
st.altair_chart(create_chart_1_tendencia(df_completo), use_container_width=True)

st.markdown("---")

# Gráfico 2
st.altair_chart(create_chart_2_top_departamentos(df_filtered), use_container_width=True)

st.markdown("---")

# Gráfico 3
st.altair_chart(create_chart_3_clase_siniestro(df_filtered), use_container_width=True)

st.markdown("---")

# Gráfico 4
st.altair_chart(create_chart_4_edad_sexo(df_filtered), use_container_width=True)

st.markdown("---")

st.subheader("Información Adicional del Análisis")
st.info(
    """
    **Manejo de Valores Nulos:**
    Para el análisis de la edad, las categorías 'NO INDICA' (aproximadamente 7.8% de los fallecidos)
    fueron imputadas a la categoría **'EDAD DESCONOCIDA'** para asegurar que el total de fallecidos
    se mantenga en los gráficos de distribución, revelando la proporción de datos faltantes.
    Otras columnas con alta proporción de NULLs (ej. Dosaje Etílico, Licencia)
    indican posibles vacíos en los procedimientos de recolección de datos o aplicabilidad
    del campo (ej. peatones sin licencia).
    """
)

# Opcional: Mostrar el DataFrame filtrado para inspección
if st.checkbox("Mostrar DataFrame de Fallecidos filtrado"):
    st.dataframe(df_filtered)

