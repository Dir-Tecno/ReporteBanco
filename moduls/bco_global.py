import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

def mostrar_global(df_global, df_recupero_localidad, file_date, geojson_data):
    # Conversión de columnas de fecha
    date_columns = ['FEC_FORM', 'FEC_INICIO_PAGO', 'FEC_FIN_PAGO']
    for col in date_columns:
        if col in df_global.columns:
            df_global[col] = pd.to_datetime(df_global[col], errors='coerce')
    df_global = df_global.dropna(subset=['FEC_FORM'])  

    # Filtro de fechas en la barra lateral
    st.sidebar.header("Filtros de Fecha para Global")
    min_date = df_global['FEC_FORM'].min().date()
    max_date = df_global['FEC_FORM'].max().date()
    
    # Convertir fechas de entrada a tipo datetime
    fecha_inicio_global = pd.to_datetime(st.sidebar.date_input("Fecha de Inicio", min_date, key="fecha_inicio_global"))
    fecha_fin_global = pd.to_datetime(st.sidebar.date_input("Fecha de Fin", max_date, key="fecha_fin_global"))

    # Validación de fechas
    if fecha_inicio_global > fecha_fin_global:
        st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.", key='error_date_unique')
    else:
        # Aplicar filtro de fechas
        df_filtrado_global = df_global[
            (df_global['FEC_FORM'] >= fecha_inicio_global) & 
            (df_global['FEC_FORM'] <= fecha_fin_global)
        ]


        # Conteo de formularios por estado utilizando groupby con un diccionario de categorías
        estado_categorias = {
            "En Evaluación": [1, 2, 5],
            "Rechazados": [3, 6, 7, 15, 23],
            "A Pagar": [4, 9, 10, 11, 12, 13, 19, 20]
        }

        conteo_estados = (
            df_filtrado_global.groupby("ID_ESTADO_PRESTAMO")
            .size()
            .rename("conteo")
            .reset_index()
        )

        # Crear el diccionario de resultados con los totales para cada categoría
        resultados = {
            categoria: conteo_estados[conteo_estados["ID_ESTADO_PRESTAMO"].isin(estados)]['conteo'].sum()
            for categoria, estados in estado_categorias.items()
        }

        # Diseño de columnas y cuadros de resumen
        col1, col2, col3 = st.columns(3)
        cuadro_estilo = """
            <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: {bg_color}; color: {text_color};
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
                <h3 style="text-align: center; font-size: 18px;">{titulo}</h3>
                <p style="text-align: center; font-size: 32px; font-weight: bold;">{cantidad}</p>
            </div>
        """
        
        with col1:
            st.markdown(cuadro_estilo.format(
                titulo="Formularios en Evaluación",
                cantidad="{:,.0f}".format(resultados["En Evaluación"]),
                bg_color="#d9edf7", text_color="#31708f"), unsafe_allow_html=True)

        with col2:
            st.markdown(cuadro_estilo.format(
                titulo="Formularios Rechazados",
                cantidad="{:,.0f}".format(resultados["Rechazados"]),
                bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

        with col3:
            st.markdown(cuadro_estilo.format(
                titulo="Formularios A Pagar",
                cantidad="{:,.0f}".format(resultados["A Pagar"]),
                bg_color="#dff0d8", text_color="#3c763d"), unsafe_allow_html=True)

        # Gráfico de Barras
        st.subheader("Gráfico de Barras: Formularios por Línea de Préstamo")
        grafico_barras = df_filtrado_global.groupby('N_LINEA_PRESTAMO').size().reset_index(name='Cantidad')
        
        bar_chart = px.bar(
            grafico_barras, 
            x='N_LINEA_PRESTAMO', 
            y='Cantidad', 
            title='Cantidad de Formularios por Línea de Préstamo',
            labels={'Cantidad': 'Número de Formularios', 'N_LINEA_PRESTAMO': 'Número de Línea de Préstamo'},
            color='Cantidad',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(bar_chart)

        # Gráfico de Torta
        st.subheader("Gráfico de Torta: Distribución de Formularios por Línea de Préstamo")
        grafico_torta = df_filtrado_global.groupby('N_LINEA_PRESTAMO').size().reset_index(name='Cantidad')
        
        fig_torta = px.pie(
            grafico_torta, 
            names='N_LINEA_PRESTAMO', 
            values='Cantidad', 
            title='Distribución de Formularios por Línea de Préstamo',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_torta)

        # Serie Histórica
        st.subheader("Serie Histórica: Evolución de Formularios a lo Largo del Tiempo")
        serie_historica = df_filtrado_global.groupby(df_filtrado_global['FEC_FORM'].dt.to_period('M')).size().reset_index(name='Cantidad')
        serie_historica['FEC_FORM'] = serie_historica['FEC_FORM'].dt.to_timestamp()
        
        fig_historia = px.line(
            serie_historica, 
            x='FEC_FORM', 
            y='Cantidad', 
            title='Evolución de Formularios por Mes',
            labels={'Cantidad': 'Cantidad de Formularios', 'FEC_FORM': 'Fecha'},
            markers=True
        )
        st.plotly_chart(fig_historia)

