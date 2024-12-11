import streamlit as st
from supabase import create_client
from moduls.carga import load_data_from_bucket
from moduls.bco_global import mostrar_global
from moduls.recupero import mostrar_recupero
from moduls.rechazo import mostrar_rechazados

# Configuración de la página
st.set_page_config(page_title="Reporte Banco de la Gente", layout="wide")

# Cargar datos desde Supabase
try:
    dfs, file_dates = load_data_from_bucket("Banco", st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Asignar los DataFrames según el orden de los archivos en el bucket
geojson_data = dfs[0]  # capa_departamentos_2010.geojson
df_departamentos = dfs[1]  # departamentos_poblacion.csv
df_global = dfs[2]  # vt_nomina_rep_dpto_localidad.parquet
df_recupero = dfs[3]  # VT_NOMINA_REP_RECUPERO_X_ANIO.parquet

# Crear las pestañas
tab1, tab2, tab3 = st.tabs(["Global", "Recupero", "Rechazados"])

with tab1:
    mostrar_global( dfs[0],  dfs[1], dfs[2], dfs[3])

with tab2:
    mostrar_recupero(dfs[3],  dfs[1],  dfs[0])  

with tab3:
    mostrar_rechazados(dfs[2],  dfs[0], dfs[1])  

