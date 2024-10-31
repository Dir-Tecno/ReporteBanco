import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import io
import pydeck as pdk
import plotly.express as px

def mostrar_global(df_global, df_recupero_localidad, file_date, geojson_data):
    # Convertir columnas de fecha si están en el DataFrame
    date_columns = ['FEC_FORM', 'FEC_INICIO_PAGO', 'FEC_FIN_PAGO']
    for col in date_columns:
        if col in df_global.columns:
            df_global[col] = pd.to_datetime(df_global[col], errors='coerce')
    
    # Eliminar filas donde las columnas clave de fecha sean NaT después de la conversión
    df_global = df_global.dropna(subset=['FEC_FORM', 'FEC_INICIO_PAGO', 'FEC_FIN_PAGO'])

    # Agregar filtro de fechas
    st.sidebar.header("Filtros de Fecha")
    fecha_inicio = st.sidebar.date_input("Fecha de Inicio", df_global['FEC_FORM'].min())
    fecha_fin = st.sidebar.date_input("Fecha de Fin", df_global['FEC_FORM'].max())

    if fecha_inicio > fecha_fin:
        st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
    else:
        # Filtrar el DataFrame según las fechas seleccionadas
        mask = (df_global['FEC_FORM'] >= pd.to_datetime(fecha_inicio)) & (df_global['FEC_FORM'] <= pd.to_datetime(fecha_fin))
        df_filtrado = df_global.loc[mask]

        # Filtrar y contar los formularios en cada categoría
        formularios_evaluacion = df_filtrado[df_filtrado['ID_ESTADO_PRESTAMO'].isin([1, 2, 5])].shape[0]
        formularios_rechazados = df_filtrado[df_filtrado['ID_ESTADO_PRESTAMO'] == 3].shape[0]
        formularios_a_pagar = df_filtrado[df_filtrado['ID_ESTADO_PRESTAMO'].isin([4, 9, 10])].shape[0]

        # Crear columnas para los cuadros
        col1, col2, col3 = st.columns(3)

        # Definir el estilo de los cuadros
        cuadro_estilo = """
            <div style="margin: 10px; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h3 style="text-align: center;">{titulo}</h3>
                <p style="text-align: center; font-size: 36px; color: {color};">{cantidad}</p>
            </div>
        """

        # Mostrar los cuadros en las columnas
        with col1:
            st.markdown(cuadro_estilo.format(titulo="Formularios en Evaluación", cantidad=formularios_evaluacion, color="#1f77b4"), unsafe_allow_html=True)

        with col2:
            st.markdown(cuadro_estilo.format(titulo="Formularios Rechazados", cantidad=formularios_rechazados, color="#b22222"), unsafe_allow_html=True)

        with col3:
            st.markdown(cuadro_estilo.format(titulo="Formularios A Pagar", cantidad=formularios_a_pagar, color="#228b22"), unsafe_allow_html=True)

        st.markdown("---")

        # Crear una tabla markdown con los datos filtrados
        st.header("Detalle de Formularios")

        # Seleccionar columnas relevantes para la tabla
        columnas_tabla = ['FEC_FORM', 'ID_ESTADO_PRESTAMO', 'NRO_FORMULARIO']  # Reemplaza 'OTRAS_COLUMNAS' con las columnas que desees mostrar

        # Asegurarse de que las columnas existan en el DataFrame filtrado
        columnas_tabla = [col for col in columnas_tabla if col in df_filtrado.columns]

        df_tabla = df_filtrado[columnas_tabla]

        # Convertir el DataFrame a Markdown
        if not df_tabla.empty:
            st.markdown(df_tabla.to_markdown(index=False), unsafe_allow_html=True)
        else:
            st.info("No hay datos disponibles para el rango de fechas seleccionado.")