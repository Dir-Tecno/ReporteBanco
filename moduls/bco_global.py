import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from funciones import mostrar_feedback

def mostrar_global(geojson_data, df_departamentos, df_global, df_recupero):
    # Agregar título y fecha del archivo
    st.title("Análisis Global de Formularios")

    # Conversión de columnas de fecha con validación de rango
    date_columns = ['FECHA_INGRESO', 'FEC_INICIO_PAGO', 'FEC_FIN_PAGO']
    min_date = pd.Timestamp.min
    max_date = pd.Timestamp.max

    for col in date_columns:
        if col in df_global.columns:
            df_global[col] = pd.to_datetime(df_global[col], errors='coerce')
            df_global.loc[(df_global[col] < min_date) | (df_global[col] > max_date), col] = pd.NaT

    # Eliminar filas con fechas inválidas
    df_global = df_global.dropna(subset=['FECHA_INGRESO'])

    if df_global.empty:
        st.warning("No hay datos válidos después de procesar las fechas. Verifica los datos cargados.")
        return

    # Filtrar los datos por las fechas seleccionadas (sin barra lateral)
    df_filtrado_global = df_global  # Inicialmente el dataframe completo

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

    # Línea divisoria en gris claro
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # Serie Histórica
    st.subheader("Serie Histórica: Evolución de Formularios a lo Largo del Tiempo")
    serie_historica = df_filtrado_global.groupby(df_filtrado_global['FECHA_INGRESO'].dt.to_period('M')).size().reset_index(name='Cantidad')
    serie_historica['FECHA_INGRESO'] = serie_historica['FECHA_INGRESO'].apply(
        lambda x: x.start_time if min_date <= x.start_time <= max_date else pd.NaT
    )
    serie_historica = serie_historica.dropna(subset=['FECHA_INGRESO'])

    fig_historia = px.line(
        serie_historica, 
        x='FECHA_INGRESO', 
        y='Cantidad', 
        title='Evolución de Formularios por Mes',
        labels={'Cantidad': 'Cantidad de Formularios', 'FECHA_INGRESO': 'Fecha'},
        markers=True
    )
    st.plotly_chart(fig_historia)

    # Línea divisoria en gris claro
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

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

    # Línea divisoria en gris claro
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # Filtros de fecha al final de la página en un formato compacto
    st.subheader("Filtros de Fecha para Global")

    # Convertir fechas de entrada a tipo datetime
    min_date = df_global['FECHA_INGRESO'].min().date()
    max_date = df_global['FECHA_INGRESO'].max().date()

    # Utilizando una sola fila para los filtros
    col_inicio, col_fin = st.columns(2)

    with col_inicio:
        fecha_inicio_global = st.date_input("Fecha de Inicio", min_date)

    with col_fin:
        fecha_fin_global = st.date_input("Fecha de Fin", max_date)

    # Verificar que las fechas seleccionadas sean válidas
    if fecha_inicio_global > fecha_fin_global:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        return  # Detener la ejecución si las fechas son inválidas

    # Filtrar los datos por las fechas seleccionadas
    df_filtrado_global = df_global[
        (df_global['FECHA_INGRESO'] >= pd.to_datetime(fecha_inicio_global)) & 
        (df_global['FECHA_INGRESO'] <= pd.to_datetime(fecha_fin_global))
    ]

    # Confirmar filtro con un botón
    if st.button("Aplicar Filtros"):
        st.success(f"Filtros aplicados: desde {fecha_inicio_global} hasta {fecha_fin_global}.")

    # Buzón de mensajes y valoración del reporte
    st.sidebar.header("📝 Buzón de Mensajes")
    st.sidebar.caption("Dirección de Tecnología y Análisis de Datos")

    # Área de texto para comentarios
    comentario = st.sidebar.text_area("Para poder ofrecerte los mejores reportes posibles, tu opinión es muy valiosa. Nos encantaría recibir tus comentarios y saber en qué aspectos podemos mejorarlo.", "", height=100)

    # Selector de valoración
    valoracion = st.sidebar.selectbox("Valora el reporte:", [1, 2, 3, 4, 5])

    # Botón para enviar el mensaje
    if st.sidebar.button("Enviar"):
        if comentario:
            # Intentar enviar a Slack
            if mostrar_feedback(comentario, valoracion):
                st.sidebar.success("✅ Gracias por tu comentario! El mensaje ha sido enviado.")
                st.sidebar.write(f"**Comentario:** {comentario}")
                st.sidebar.write(f"**Valoración:** {valoracion} estrellas")
            else:
                st.sidebar.error("❌ Hubo un error al enviar el mensaje a Slack.")
        else:
            st.sidebar.warning("⚠️ Por favor, escribe un comentario antes de enviar.")
