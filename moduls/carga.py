import pandas as pd
import geopandas as gpd
import json
from io import BytesIO
import streamlit as st
from huggingface_hub import hf_hub_download
import os
import requests

@st.cache_data(ttl=3600)
def load_data_from_huggingface(repo_id, token=None):
    """
    Carga los archivos desde Hugging Face.
    
    Args:
        repo_id (str): ID del repositorio en formato 'username/repository'
        token (str, optional): Token de acceso si el repositorio es privado
    
    Returns:
        tuple: (lista de dataframes, lista de fechas de modificación)
    """
    dfs = []
    file_dates = []
    
    # Lista de archivos a cargar
    files = [
        "capa_departamentos_2010.geojson",
        "departamentos_poblacion.csv",
        "vt_nomina_rep_dpto_localidad.parquet",
        "VT_NOMINA_REP_RECUPERO_X_ANIO.parquet"
    ]
    
    try:
        if not token:
            st.warning("No se proporcionó token de Hugging Face. Si el repositorio es privado, esto causará un error.")
            
        for file_name in files:
            try:
                # Descargar archivo desde Hugging Face
                file_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=file_name,
                    token=token,
                    repo_type="dataset"
                )
                
                if file_name.endswith('.parquet'):
                    df = pd.read_parquet(file_path)
                    df.name = file_name
                    dfs.append(df)
                    file_dates.append(os.path.getmtime(file_path))
                    
                elif file_name.endswith('.geojson'):
                    with open(file_path, 'r') as f:
                        geojson_dict = json.load(f)
                    gdf = gpd.GeoDataFrame.from_features(geojson_dict['features'])
                    if gdf.crs is None or gdf.crs.to_string() != 'EPSG:22174':
                        gdf = gdf.set_crs(epsg=22174)
                    gdf = gdf.to_crs(epsg=4326)
                    dfs.append(gdf.__geo_interface__)
                    file_dates.append(os.path.getmtime(file_path))
                    
                elif file_name.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    dfs.append(df)
                    file_dates.append(os.path.getmtime(file_path))
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    st.error(f"Error de autenticación al descargar {file_name}. Verifica tu token de Hugging Face.")
                elif e.response.status_code == 404:
                    st.error(f"No se encontró el archivo {file_name} en el repositorio.")
                else:
                    st.error(f"Error al descargar {file_name}: {str(e)}")
                raise
                
    except Exception as e:
        st.error(f"Error al cargar los datos desde Hugging Face: {str(e)}")
        raise e
    
    return dfs, file_dates