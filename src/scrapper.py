import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from supabase import create_client
from supabase import PostgrestAPIError
import numpy as np


def get_values(tag_list):
    new_list = []
    for tag in tag_list[:5]:
        new_list.append(tag.stripped_strings.__next__()) # Como por cada elemento de la fila solo hay un string
    return new_list


def filtrar_accidentes_de_transito(df):
    """
    Filtra el DataFrame para incluir solo incidentes relacionados con vehículos de tránsito.

    Busca las palabras 'AUTOMOVIL', 'CAMIONETA', 'MOTO', 'VEHICULAR'
    en la columna 'Tipo' de forma insensible a mayúsculas/minúsculas.
    """

    patrones_vehiculos = 'AUTOMOVIL|CAMIONETA|MOTO|VEHICULAR'

    # 2. Aplicar el filtro a la columna 'Tipo'
    # .str.contains() busca el patrón
    # case=False hace que la búsqueda no distinga entre mayúsculas y minúsculas
    # na=False asegura que las filas vacías no se incluyan
    df_filtrado = df[
        df['Tipo'].str.contains(patrones_vehiculos, case=False, na=False)
    ].copy()

    return df_filtrado


def extraer_coordenadas(s: str):
    match_coords = re.search(r'\(([-]?\d+\.\d+),([-]?\d+\.\d+)\)', s)
    if match_coords:
        return match_coords.group(1)+"|"+match_coords.group(2)
    

# Recolección de los datos

url = "https://sgonorte.bomberosperu.gob.pe/24horas"
r = requests.get(url)
if r.status_code != 200:
    raise Exception("Error al acceder a los datos")
soup = BeautifulSoup(r.text)

x = soup.find("thead").find_all("th")
columns = list(map(lambda s: s.string, x[1:-2]))

x = soup.find("tbody").find_all("tr")
data = list(map(lambda s: s.find_all("td"), x))
data = list(map(get_values, data))


df = pd.DataFrame(data, columns=columns)

df = filtrar_accidentes_de_transito(df)

df["coords"] = df["Dirección / Distrito"].apply(extraer_coordenadas)
df[["lat", "lon"]] = df["coords"].str.split("|", expand=True)
df["lat"] = df["lat"].astype(float)
df["lon"] = df["lon"].astype(float)
df.drop(columns="coords", inplace=True)

df['fecha'] = df["Fecha y hora"].str[:10]
# Para que esté en formato YYYY-MM-DD
df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True).dt.date
df['fecha'] = df["fecha"].astype(str)


# Inserción de los datos al Supabase
def update_data():
    url = "https://ntkbropqoaliyvoziqyz.supabase.co"
    apikey = "sb_publishable_ChXTotbmNNA7RyEOcPrZEw_deMjmAbX"
    supabase = create_client(url, apikey)
    
    values_list = df[["Nro Parte", "lat", "lon", "fecha"]].values.tolist()

    if len(values_list) == 0:
        return None
    if len(values_list) == 1:
        values_list = [values_list]
    
    for i in values_list[1:3]:
        try:
            if pd.isna(i[1]) or pd.isna(i[2]):
                r = (supabase.table("siniestros")
                    .insert({
                        "cod_sin": i[0],
                        "fecha": i[3]
                    })
                    .execute()
                )
            else:
                r = (supabase.table("siniestros")
                    .insert({
                        "cod_sin": i[0],
                        "lat": i[1],
                        "lon": i[2],
                        "fecha": i[3]
                    })
                    .execute()
                )
        except PostgrestAPIError:
            continue

