import streamlit as st
from moduls.carga import load_data_from_huggingface
from moduls.bco_global import mostrar_global
from moduls.recupero import mostrar_recupero
from moduls.rechazo import mostrar_rechazados

# Configuración de la página
st.set_page_config(page_title="Reporte Banco de la Gente", layout="wide")

# Configuración de Hugging Face
REPO_ID = "Dir-Tecno/BancoGente"  # Reemplazar con tu usuario y nombre del dataset
HF_TOKEN = st.secrets["HuggingFace"]["huggingface_token"]  # Corregido para usar la sección correcta

# Cargar datos desde Hugging Face
try:
    dfs, file_dates = load_data_from_huggingface(REPO_ID, token=HF_TOKEN)
    
    if dfs and len(dfs) >= 4:  # Verificar que tengamos todos los dataframes necesarios
        # Asignar los DataFrames según el orden de los archivos
        geojson_data = dfs[0]  # capa_departamentos_2010.geojson
        df_departamentos = dfs[1]  # departamentos_poblacion.csv
        df_global = dfs[2]  # vt_nomina_rep_dpto_localidad.parquet
        df_recupero = dfs[3]  # VT_NOMINA_REP_RECUPERO_X_ANIO.parquet

        # Crear las pestañas
        tab1, tab2, tab3 = st.tabs(["Global", "Recupero", "Rechazados"])

        with tab1:
            mostrar_global(geojson_data, df_departamentos, df_global, df_recupero)

        with tab2:
            mostrar_recupero(df_recupero, df_departamentos, geojson_data)  

        with tab3:
            mostrar_rechazados(df_global, geojson_data, df_departamentos)  
    else:
        st.error("No se pudieron cargar todos los archivos necesarios")
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
