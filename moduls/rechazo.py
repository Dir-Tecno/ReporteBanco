import streamlit as st
import pandas as pd
import plotly.express as px
from funciones import mostrar_feedback


def mostrar_rechazados(df_recupero_localidad, file_date, geojson_data):
    # Convertir la columna a tipo datetime
    if 'FECHA_INGRESO' in df_recupero_localidad.columns:
        df_recupero_localidad['FECHA_INGRESO'] = pd.to_datetime(df_recupero_localidad['FECHA_INGRESO'], errors='coerce')

        # Eliminar filas con fechas NaT
        df_recupero_localidad = df_recupero_localidad.dropna(subset=['FECHA_INGRESO'])

        if df_recupero_localidad.empty:
            st.warning("No hay datos disponibles después de filtrar por fecha.")
            return
        
        # Filtros de fecha
        st.sidebar.header("Filtros de Fecha para  Rechazados")
        fecha_inicio = st.sidebar.date_input("Fecha de Inicio", df_recupero_localidad['FECHA_INGRESO'].min().date(), key="fecha_inicio_rechazados")
        fecha_fin = st.sidebar.date_input("Fecha de Fin", df_recupero_localidad['FECHA_INGRESO'].max().date(), key="fecha_fin_rechazados")

        if fecha_inicio > fecha_fin:
            st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        else:
            # Aplicar filtro de fechas
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            df_filtrado = df_recupero_localidad[(df_recupero_localidad['FECHA_INGRESO'] >= fecha_inicio_dt) & 
                                                 (df_recupero_localidad['FECHA_INGRESO'] <= fecha_fin_dt)]
            
            # Verificar que haya datos filtrados
            if df_filtrado.empty:
                st.warning("No hay datos disponibles para el rango de fechas seleccionado.")
                return

            # Definir las categorías de rechazo y sus ID
            categoria_rechazo = {
                "Rechazo": [4, 33, 18, 14, 17, 20, 30, 31, 32, 35, 13, 28, 29, 36, 22],
                "Impago": [11, 12],
                "Desistido": [6],
            }

            # Contar rechazos por categoría
            conteo_rechazos = {categoria: df_filtrado[df_filtrado['ID_ESTADO_FORMULARIO'].isin(ids)].shape[0]
                               for categoria, ids in categoria_rechazo.items()}

            # Diseño de columnas y cuadros
            col1, col2, col3 = st.columns(3)
            cuadro_estilo = """
                <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: {bg_color}; color: {text_color};
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
                    <h3 style="text-align: center; font-size: 18px;">{titulo}</h3>
                    <p style="text-align: center; font-size: 32px; font-weight: bold;">{cantidad}</p>
                </div>
            """

            # Mostrar cuadros en las columnas
            with col1:
                st.markdown(cuadro_estilo.format(
                    titulo="Rechazo",
                    cantidad="{:,.0f}".format(conteo_rechazos["Rechazo"]),
                    bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

            with col2:
                st.markdown(cuadro_estilo.format(
                    titulo="Impago",
                    cantidad="{:,.0f}".format(conteo_rechazos["Impago"]),
                    bg_color="#dff0d8", text_color="#3c763d"), unsafe_allow_html=True)

            with col3:
                st.markdown(cuadro_estilo.format(
                    titulo="Desistido",
                    cantidad="{:,.0f}".format(conteo_rechazos["Desistido"]),
                    bg_color="#d9edf7", text_color="#31708f"), unsafe_allow_html=True)

            # Línea divisoria en gris claro
            st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

            # Gráfico de Barras: Rechazos por Categoría
            st.subheader("Gráfico de Barras: Rechazos por Categoría")
            grafico_barras_rechazos = df_filtrado.groupby('N_ESTADO_FORMULARIO').size().reset_index(name='Cantidad')
            bar_chart_rechazos = px.bar(
                grafico_barras_rechazos,
                x='N_ESTADO_FORMULARIO',
                y='Cantidad',
                title='Cantidad de Rechazos por Categoría',
                labels={'Cantidad': 'Número de Rechazos', 'N_ESTADO_FORMULARIO': 'Tipo Rechazo'},
                color='Cantidad',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(bar_chart_rechazos)

            # Gráfico de Barras: Conteo de Localidades Rechazadas
            st.subheader("Gráfico de Barras: Conteo de Localidades Rechazadas")
            conteo_localidades_rechazados = df_filtrado['N_LOCALIDAD'].value_counts().reset_index()
            conteo_localidades_rechazados.columns = ['N_LOCALIDAD', 'Cantidad']
            bar_chart_localidades_rechazados = px.bar(
                conteo_localidades_rechazados,
                x='N_LOCALIDAD',
                y='Cantidad',
                title='Conteo de Localidades Rechazadas',
                labels={'Cantidad': 'Número de Localidades Rechazadas'},
                color='Cantidad',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(bar_chart_localidades_rechazados)

        #feedback
            mostrar_feedback()