import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def mostrar_recupero(df_recupero, df_departamentos, geojson_data):
    
    if 'FEC_FORM' not in df_recupero.columns:
        st.error("La columna 'FEC_FORM' no se encuentra en el DataFrame.")
        st.write("Columnas disponibles:", df_recupero.columns.tolist())
        return
    
    # Conversión de columnas de fecha con validación de rango
    date_columns = ['FEC_FORM', 'FEC_INICIO_PAGO', 'FEC_FIN_PAGO']
    min_date = pd.Timestamp.min
    max_date = pd.Timestamp.max

    # Validar columnas de fechas necesarias
    for col in date_columns:
        if col in df_recupero.columns:
            df_recupero[col] = pd.to_datetime(df_recupero[col], errors='coerce')
            df_recupero.loc[(df_recupero[col] < min_date) | (df_recupero[col] > max_date), col] = pd.NaT

    # Eliminar filas con fechas inválidas
    df_recupero = df_recupero.dropna(subset=['FEC_FORM'])

    if df_recupero.empty:
        st.warning("No hay datos válidos después de procesar las fechas. Verifica los datos cargados.")
        return
    
    # Cálculo de solicitudes en las últimas 24 horas
    fecha_actual = datetime.now()
    fecha_24hs_antes = fecha_actual - timedelta(days=1)
    solicitudes_ultimas_24hs = df_recupero[df_recupero['FEC_FORM'] >= fecha_24hs_antes]
    cantidad_solicitudes_24hs = solicitudes_ultimas_24hs.shape[0]

    # Diseño para mostrar los círculos informativos con descripción
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; flex-direction: column; align-items: center; margin-bottom: 30px;">
            <div style="width: 120px; height: 120px; background-color: #1E9AD8; color: white; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-size: 32px; font-weight: bold;">
                {cantidad_solicitudes_24hs}
            </div>
            <p style="text-align: center; font-size: 16px; margin-top: 10px;">Solicitudes en las últimas 24 horas</p>
        </div>
        """, unsafe_allow_html=True)

    # Categorías de estado
    estado_categorias = {
        "Pagados": [13, 14, 16, 17, 18, 20, 21, 7],
        "Créditos con Deuda": [21],
        "Impagos/Bajas": [23, 22, 15],
        "Finalizados": [7],
    }

    # Conteo por categoría
    conteo_estados = {
        categoria: df_recupero[df_recupero['ID_ESTADO_PRESTAMO'].isin(estados)].shape[0]
        for categoria, estados in estado_categorias.items()
    }

    # Diseño de columnas y cuadros de resumen
    col1, col2, col3, col4 = st.columns(4)
    cuadro_estilo = """
        <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: {bg_color}; color: {text_color};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
            <h3 style="text-align: center; font-size: 18px;">{titulo}</h3>
            <p style="text-align: center; font-size: 32px; font-weight: bold;">{cantidad}</p>
        </div>
    """

    # Mostrar cuadros de resumen
    with col1:
        st.markdown(cuadro_estilo.format(
            titulo="Pagados",
            cantidad="{:,.0f}".format(conteo_estados["Pagados"]),
            bg_color="#d9edf7", text_color="#31708f"), unsafe_allow_html=True)

    with col2:
        st.markdown(cuadro_estilo.format(
            titulo="Créditos con Deuda",
            cantidad="{:,.0f}".format(conteo_estados["Créditos con Deuda"]),
            bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

    with col3:
        st.markdown(cuadro_estilo.format(
            titulo="Impagos/Bajas",
            cantidad="{:,.0f}".format(conteo_estados["Impagos/Bajas"]),
            bg_color="#f9e79f", text_color="#8a6d3b"), unsafe_allow_html=True)

    with col4:
        st.markdown(cuadro_estilo.format(
            titulo="Finalizados",
            cantidad="{:,.0f}".format(conteo_estados["Finalizados"]),
            bg_color="#dff0d8", text_color="#3c763d"), unsafe_allow_html=True)

    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)
    
    # Calcular DEUDA VENCIDA y DEUDA NO VENCIDA
    deuda_vencida = df_recupero['DEUDA'].sum() if 'DEUDA' in df_recupero.columns else 0
    deuda_no_vencida = df_recupero['DEUDA_NO_VENCIDA'].sum() if 'DEUDA_NO_VENCIDA' in df_recupero.columns else 0

    # Mostrar tarjetas de DEUDA VENCIDA y DEUDA NO VENCIDA
    col5, col6 = st.columns(2)

    with col5:
        st.markdown(cuadro_estilo.format(
            titulo="DEUDA VENCIDA",
            cantidad="${:,.2f}".format(deuda_vencida),
            bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

    with col6:
        st.markdown(cuadro_estilo.format(
            titulo="DEUDA NO VENCIDA",
            cantidad="${:,.2f}".format(deuda_no_vencida),
            bg_color="#d9edf7", text_color="#31708f"), unsafe_allow_html=True)

    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)


    # Filtro de fechas
    st.subheader("Filtrar por Fecha")
    fecha_inicio = st.date_input("Fecha de Inicio", df_recupero['FEC_FORM'].min().date(), key="fecha_inicio")
    fecha_fin = st.date_input("Fecha de Fin", df_recupero['FEC_FORM'].max().date())

    if fecha_inicio > fecha_fin:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        return

    fecha_inicio_dt = pd.to_datetime(fecha_inicio)
    fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df_filtrado = df_recupero[(df_recupero['FEC_FORM'] >= fecha_inicio_dt) & 
                              (df_recupero['FEC_FORM'] <= fecha_fin_dt)]

    if df_filtrado.empty:
        st.warning("No hay datos disponibles para el rango de fechas seleccionado.")
        return

    # Gráfico de barras
    st.subheader("Gráfico de Barras: Formularios por Estado")
    grafico_barras = df_filtrado.groupby('N_ESTADO_PRESTAMO').size().reset_index(name='Cantidad')

    if not grafico_barras.empty:
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
    else:
        st.warning("No se encontraron datos para generar el gráfico de barras.")

    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # Serie de tiempo
    st.subheader("Evolución de la Deuda Vencida")
    if 'DEUDA' in df_recupero.columns and 'FEC_FORM' in df_recupero.columns:
        df_filtrado_deuda = df_recupero.dropna(subset=['FEC_FORM', 'DEUDA'])
        deuda_por_fecha = df_filtrado_deuda.groupby(df_filtrado_deuda['FEC_FORM'].dt.date)['DEUDA'].sum().reset_index()
        deuda_por_fecha.columns = ['Fecha', 'Deuda Total']

        if not deuda_por_fecha.empty:
            line_chart = px.line(
                deuda_por_fecha,
                x='Fecha',
                y='Deuda Total',
                labels={'Fecha': 'Fecha', 'Deuda Total': 'Deuda Vencida'},
                title='Evolución de la Deuda Vencida'
            )
            st.plotly_chart(line_chart)
        else:
            st.warning("No se encontraron datos para la serie de tiempo.")
    else:
        st.warning("No se encontró la columna 'DEUDA' para generar la serie de tiempo.")


   

