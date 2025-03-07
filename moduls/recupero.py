import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def mostrar_recupero(df_recupero, df_detalle_recupero, df_departamentos, geojson_data):
    """
    Muestra un resumen de la información de recupero, incluyendo totales de deuda,
    evolución de la deuda vencida y otros indicadores clave.

    Args:
        df_recupero (pd.DataFrame): DataFrame con datos generales de recupero.
        df_detalle_recupero (pd.DataFrame): DataFrame con el detalle de recupero, 
                                            incluyendo cuotas y deudas por formulario.
        df_departamentos (pd.DataFrame): DataFrame con información de departamentos.
        geojson_data (dict): Datos geoespaciales en formato GeoJSON.
    """

    # --- Procesamiento y Validación de df_recupero ---
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

    # --- Cálculo de solicitudes en las últimas 24 horas ---
    fecha_actual = datetime.now()
    fecha_24hs_antes = fecha_actual - timedelta(days=1)
    solicitudes_ultimas_24hs = df_recupero[df_recupero['FEC_FORM'] >= fecha_24hs_antes]
    cantidad_solicitudes_24hs = solicitudes_ultimas_24hs.shape[0]

    # --- Categorías de estado ---
    estado_categorias = {
        "Pagados": [13, 14, 15, 16, 17, 18, 20, 21, 7],
        "Créditos con Deuda": [21],
        "Impagos/Bajas": [23, 22],
        "Finalizados": [7],
    }

    # Conteo por categoría
    conteo_estados = {
        categoria: df_recupero[df_recupero['ID_ESTADO_PRESTAMO'].isin(estados)].shape[0]
        for categoria, estados in estado_categorias.items()
    }

    # --- Diseño de columnas y cuadros de resumen ---
    col1, col2, col3, col4,col5 = st.columns(5)
    cuadro_estilo = """
        <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: {bg_color}; color: {text_color};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
            <h3 style="text-align: center; font-size: 18px;">{titulo}</h3>
            <p style="text-align: center; font-size: 32px; font-weight: bold;">{cantidad}</p>
        </div>
    """

    # --- Mostrar cuadros de resumen ---
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
        
    with col5:
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
        
    ## --- Divisor ---
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # --- Calculo de deuda total y prescripta desde df_detalle_recupero ---
    if df_detalle_recupero is not None and not df_detalle_recupero.empty:
        deuda_total_detalle = df_detalle_recupero['DEUDA_TOTAL'].sum() if 'DEUDA_TOTAL' in df_detalle_recupero.columns else 0
        deuda_prescripta_detalle = df_detalle_recupero['DEUDA_PRESCRIPTA'].sum() if 'DEUDA_PRESCRIPTA' in df_detalle_recupero.columns else 0
        deuda_vencida_detalle = df_detalle_recupero['DEUDA_VENCIDA'].sum() if 'DEUDA_VENCIDA' in df_detalle_recupero.columns else 0
        deuda_no_vencida_detalle = df_detalle_recupero['DEUDA_NO_VENCIDA'].sum() if 'DEUDA_NO_VENCIDA' in df_detalle_recupero.columns else 0

    else:
        deuda_total_detalle = 0
        deuda_prescripta_detalle = 0
        deuda_vencida_detalle = 0
        deuda_no_vencida_detalle = 0
        st.warning("df_detalle_recupero esta vacio, no se pueden mostrar los datos de Deuda Total y deuda Prescripta")


    # --- Mostrar tarjetas de DEUDA VENCIDA, DEUDA NO VENCIDA, DEUDA TOTAL Y PRESCRIPTA---
    col5, col6, col8, col9 = st.columns(4)

    with col5:
        st.markdown(cuadro_estilo.format(
            titulo="DEUDA VENCIDA",
            cantidad="${:,.2f}".format(deuda_vencida_detalle),
            bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

    with col6:
        st.markdown(cuadro_estilo.format(
            titulo="DEUDA NO VENCIDA",
            cantidad="${:,.2f}".format(deuda_no_vencida_detalle),
            bg_color="#d9edf7", text_color="#31708f"), unsafe_allow_html=True)
    
    with col8:
        st.markdown(cuadro_estilo.format(
            titulo="DEUDA TOTAL",
            cantidad="${:,.2f}".format(deuda_total_detalle),
            bg_color="#f2dede", text_color="#a94442"), unsafe_allow_html=True)

    with col9:
            st.markdown(cuadro_estilo.format(
                titulo="DEUDA PRESCRIPTA",
                cantidad="${:,.2f}".format(deuda_prescripta_detalle),
                bg_color="#f9e79f", text_color="#8a6d3b"), unsafe_allow_html=True)

   
    ## --- Divisor ---
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # --- Serie de tiempo ---
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


    ## --- Divisor ---
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # --- Nueva Tabla: Agrupación de Formularios por Cuotas Prescriptas ---
    st.subheader("Cantidad de Formularios por Rangos de Cuotas Prescriptas")

    if df_detalle_recupero is not None and not df_detalle_recupero.empty and 'CUOTAS_PRESCRIPTAS' in df_detalle_recupero.columns:
        # Definir los rangos de cuotas
        bins = [0, 5, 10, 15, 20, float('inf')]
        labels = ['1 a 5', '6 a 10', '11 a 15', '16 a 20', 'Más de 20']

        # Crear una nueva columna con los rangos
        df_detalle_recupero['Rango_Cuotas'] = pd.cut(df_detalle_recupero['CUOTAS_PRESCRIPTAS'], bins=bins, labels=labels, right=False)

        # Agrupar por rangos y contar la cantidad de formularios
        if 'ID_FORMULARIO' in df_detalle_recupero.columns:
          conteo_por_rango = df_detalle_recupero.groupby('Rango_Cuotas')['ID_FORMULARIO'].nunique().reset_index()
          conteo_por_rango.rename(columns={'ID_FORMULARIO': 'Cantidad de Formularios'}, inplace=True)
        elif 'ID_FORMULARIO_LINEA' in df_detalle_recupero.columns:
          conteo_por_rango = df_detalle_recupero.groupby('Rango_Cuotas')['ID_FORMULARIO_LINEA'].nunique().reset_index()
          conteo_por_rango.rename(columns={'ID_FORMULARIO_LINEA': 'Cantidad de Formularios'}, inplace=True)
        elif 'id_formulario_linea' in df_detalle_recupero.columns:
          conteo_por_rango = df_detalle_recupero.groupby('Rango_Cuotas')['id_formulario_linea'].nunique().reset_index()
          conteo_por_rango.rename(columns={'id_formulario_linea': 'Cantidad de Formularios'}, inplace=True)

        
        else:
          st.error("No se encontró una columna que identifique de forma única a los formularios en 'df_detalle_recupero'. Se intentó con: ID_FORMULARIO , ID_FORMULARIO_LINEA, id_formulario_linea .")
          return

        
        # Elimino el ultimo label para no mostrar  "Mas de 20" , ya que la consiga del trabajo es solo mostrar hasta 20
        conteo_por_rango = conteo_por_rango[conteo_por_rango['Rango_Cuotas'] != 'Más de 20']

        # Mostrar la tabla en Streamlit
        st.dataframe(conteo_por_rango, hide_index=True)


    else:
        st.warning("No se puede mostrar la tabla de rangos de cuotas prescriptas.  Verifica que el DataFrame 'df_detalle_recupero' este cargado y contenga la columna 'CUOTAS_PRESCRIPTAS'.")