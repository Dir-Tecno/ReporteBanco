import streamlit as st
import pandas as pd
import plotly.express as px


def mostrar_recupero(df_recupero_localidad, df_global, file_date, geojson_data):
    
    # Manejo de error si la columna no existe
    if 'FECHA_INGRESO' in df_recupero_localidad.columns:
        # Convertir la columna a tipo datetime
        df_recupero_localidad['FECHA_INGRESO'] = pd.to_datetime(df_recupero_localidad['FECHA_INGRESO'], errors='coerce')
        
        # Eliminar filas con fechas NaT
        df_recupero_localidad = df_recupero_localidad.dropna(subset=['FECHA_INGRESO'])
        
        # Filtro de fechas en la barra lateral
        st.sidebar.header("Filtros de Fecha para  Recupero")
        fecha_inicio = st.sidebar.date_input("Fecha de Inicio", df_recupero_localidad['FECHA_INGRESO'].min().date(), key="fecha_inicio_recupero")
        fecha_fin = st.sidebar.date_input("Fecha de Fin", df_recupero_localidad['FECHA_INGRESO'].max().date(), key="fecha_fin_recupero")
        
        if fecha_inicio > fecha_fin:
            st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        else:
            # Aplicar filtro de fechas
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            df_filtrado = df_recupero_localidad[(df_recupero_localidad['FECHA_INGRESO'] >= fecha_inicio_dt) & 
                                                 (df_recupero_localidad['FECHA_INGRESO'] <= fecha_fin_dt)]

            # Definir las categorías y sus ID
            estado_categorias = {
                "Pagados": [13, 14, 16, 17, 18, 20, 21, 7],
                "Créditos con Deuda": [21],
                "Impagos/Bajas": [23, 22, 15],
                "Finalizados": [7],
            }

            # Contar formularios por estado
            conteo_estados = {
                categoria: df_filtrado[df_filtrado['ID_ESTADO_PRESTAMO'].isin(estados)].shape[0]
                for categoria, estados in estado_categorias.items()
            }

            # Diseño de columnas y cuadros
            col1, col2, col3, col4 = st.columns(4)
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
                    titulo="Pagados",
                    cantidad="{:,.0f}".format(conteo_estados["Pagados"]),
                    bg_color="#dff0d8", text_color="#3c763d"), unsafe_allow_html=True)

            with col2:
                st.markdown(cuadro_estilo.format(
                    titulo="Créditos con Deuda",
                    cantidad="{:,.0f}".format(conteo_estados["Créditos con Deuda"]),
                    bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

            with col3:
                st.markdown(cuadro_estilo.format(
                    titulo="Impagos/Bajas",
                    cantidad="{:,.0f}".format(conteo_estados["Impagos/Bajas"]),
                    bg_color="#d9edf7", text_color="#31708f"), unsafe_allow_html=True)

            with col4:
                st.markdown(cuadro_estilo.format(
                    titulo="Finalizados",
                    cantidad="{:,.0f}".format(conteo_estados["Finalizados"]),
                    bg_color="#dff0d8", text_color="#3c763d"), unsafe_allow_html=True)
                
            # Línea divisoria en gris claro
            st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

            # Gráfico de Barras: Formularios por Estado
            st.subheader("Gráfico de Barras: Formularios por Estado")
            grafico_barras = df_filtrado.groupby('N_ESTADO_PRESTAMO').size().reset_index(name='Cantidad')
            bar_chart = px.bar(
                grafico_barras,
                x='N_ESTADO_PRESTAMO',
                y='Cantidad',
                title='Cantidad de Formularios por Estado',
                labels={'Cantidad': 'Número de Formularios', 'N_ESTADO_PRESTAMO': 'Estado del Préstamo'},
                color='Cantidad',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(bar_chart)

            # Top 10 Localidades para Formularios por Estado
            st.subheader("Top 10 Localidades para Formularios por Estado")
            top_10_estados = df_filtrado.groupby('N_ESTADO_PRESTAMO')['N_LOCALIDAD'].value_counts().reset_index()
            top_10_estados.columns = ['N_ESTADO_PRESTAMO', 'N_LOCALIDAD', 'Cantidad']
            top_10_estados = top_10_estados.groupby('N_ESTADO_PRESTAMO').head(10)
            top_10_estados_pivot = top_10_estados.pivot(index='N_ESTADO_PRESTAMO', columns='N_LOCALIDAD', values='Cantidad').fillna(0)
            st.bar_chart(top_10_estados_pivot)

            # Línea divisoria en gris claro
            st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

            # Gráfico de Barras: Conteo de Localidades
            st.subheader("Gráfico de Barras: Conteo de Localidades")
            conteo_localidades = df_filtrado['N_LOCALIDAD'].value_counts().reset_index()
            conteo_localidades.columns = ['N_LOCALIDAD', 'Cantidad']
            bar_chart_localidades = px.bar(
                conteo_localidades,
                x='N_LOCALIDAD',
                y='Cantidad',
                title='Conteo de Localidades',
                labels={'Cantidad': 'Número de Localidades'},
                color='Cantidad',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(bar_chart_localidades)

            # Top 10 Localidades para Conteo de Localidades
            st.subheader("Top 10 Localidades para Conteo de Localidades")
            top_10_localidades_conteo = conteo_localidades.head(10)
            st.bar_chart(top_10_localidades_conteo)

            # Línea divisoria en gris claro
            st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

            # Gráfico de Barras: Localidades por Estados
            st.subheader("Gráfico de Barras: Localidades por Estados")
            localidades_por_estado = df_filtrado.groupby('ID_ESTADO_PRESTAMO')['N_LOCALIDAD'].nunique().reset_index()
            localidades_por_estado.columns = ['ID_ESTADO_PRESTAMO', 'Cantidad']
            bar_chart_localidades_estado = px.bar(
                localidades_por_estado,
                x='ID_ESTADO_PRESTAMO',
                y='Cantidad',
                title='Cantidad de Localidades por Estado',
                labels={'Cantidad': 'Número de Localidades'},
                color='Cantidad',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(bar_chart_localidades_estado)

            # Top 10 Localidades para Localidades por Estados
            st.subheader("Top 10 Localidades para Localidades por Estados")
            top_10_localidades_estado = df_filtrado.groupby('ID_ESTADO_PRESTAMO')['N_LOCALIDAD'].value_counts().reset_index()
            top_10_localidades_estado.columns = ['ID_ESTADO_PRESTAMO', 'N_LOCALIDAD', 'Cantidad']
            top_10_localidades_estado = top_10_localidades_estado.groupby('ID_ESTADO_PRESTAMO').head(10)
            top_10_localidades_estado_pivot = top_10_localidades_estado.pivot(index='ID_ESTADO_PRESTAMO', columns='N_LOCALIDAD', values='Cantidad').fillna(0)
            st.bar_chart(top_10_localidades_estado_pivot)

            
