import streamlit as st
from google.oauth2 import service_account
import json
import geopandas as gpd
from moduls.carga import load_data_from_bucket, download_geojson_from_bucket
from moduls.bco_global import mostrar_global
from moduls.recupero import mostrar_recupero
from moduls.rechazo import mostrar_rechazados


# Configuración de las credenciales
credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Configuración de la página
st.set_page_config(page_title="Reporte Banco de la Gente", layout="wide")

# Nombres de los archivos en el bucket
bucket_name = "direccion"
blob_names = [
    "VT_NOMINA_REP_RECUPERO_X_ANIO.csv",  # df 0
    "vt_nomina_rep_dpto_localidad.csv",     # df 1
]

# Cargar datos desde el bucket
try:
    dfs, file_dates = load_data_from_bucket(blob_names, bucket_name, credentials)
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Descargar el archivo GeoJSON
try:
    geojson_bytes = download_geojson_from_bucket("Copia de capa_departamentos_2010.geojson", bucket_name, credentials)
    geojson_dict = json.loads(geojson_bytes.decode("utf-8")) if isinstance(geojson_bytes, bytes) else geojson_bytes
except Exception as e:
    st.error(f"Error al descargar el archivo GeoJSON: {e}")

# Crear un GeoDataFrame desde las características del GeoJSON
gdf = gpd.GeoDataFrame.from_features(geojson_dict["features"])

# Verificar y asignar el CRS original si es necesario
if gdf.crs is None or gdf.crs.to_string() != "EPSG:22174":
    gdf = gdf.set_crs(epsg=22174)

# Convertir a WGS 84 para la visualización (EPSG:4326)
gdf = gdf.to_crs(epsg=4326)

# Convertir el GeoDataFrame a GeoJSON para la visualización
geojson_data = gdf.__geo_interface__

# Crear las pestañas
tab1, tab2, tab3 = st.tabs(["Global", "Recupero", "Rechazados"])

with tab1:
    st.header("Global")
    mostrar_global(dfs[0], dfs[1], file_dates[0], geojson_data)

with tab2:
    st.header("Recupero")
    mostrar_recupero(dfs[1], dfs[0], file_dates[0], geojson_data)  

with tab3:
     st.header("Rechazados")
     mostrar_rechazados(dfs[1], file_dates[1],geojson_data)  

