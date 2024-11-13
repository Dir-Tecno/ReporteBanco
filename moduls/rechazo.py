import streamlit as st
import pandas as pd
import plotly.express as px
from funciones import mostrar_feedback

def mostrar_rechazados(df_recupero_localidad, file_date, geojson_data):
    st.write(f"Datos actualizados al: {file_date.strftime('%d/%m/%Y %H:%M:%S')}")

    # Convertir la columna a tipo datetime y filtrar NaT
    if 'FECHA_INGRESO' in df_recupero_localidad.columns:
        df_recupero_localidad['FECHA_INGRESO'] = pd.to_datetime(df_recupero_localidad['FECHA_INGRESO'], errors='coerce')
        df_recupero_localidad = df_recupero_localidad.dropna(subset=['FECHA_INGRESO'])

    # Revisar si hay datos después de limpiar
    if df_recupero_localidad.empty:
        st.warning("No hay datos disponibles después de filtrar por fecha.")
        return

    # Definir las categorías de rechazo y sus ID
    categoria_rechazo = {
        "Rechazo": [4, 33, 18, 14, 17, 20, 30, 31, 32, 35, 13, 28, 29, 36, 22],
        "Impago": [11, 12],
        "Desistido": [6],
    }

    # Contar rechazos por categoría
    conteo_rechazos = {categoria: df_recupero_localidad[df_recupero_localidad['ID_ESTADO_FORMULARIO'].isin(ids)].shape[0]
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

    # Gráficos de barras por categoría y por localidad
    st.subheader("Gráfico de Barras: Rechazos por Categoría")
    grafico_barras_rechazos = df_recupero_localidad.groupby('N_ESTADO_FORMULARIO').size().reset_index(name='Cantidad')
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

    # Top 10 Localidades Rechazadas
    st.subheader("Top 10 Localidades Rechazadas")
    conteo_localidades_rechazados = df_recupero_localidad['N_LOCALIDAD'].value_counts().reset_index()
    conteo_localidades_rechazados.columns = ['N_LOCALIDAD', 'Cantidad']
    conteo_localidades_rechazados = conteo_localidades_rechazados.sort_values(by='Cantidad', ascending=False).head(10)

    bar_chart_localidades_rechazados = px.bar(
        conteo_localidades_rechazados,
        x='N_LOCALIDAD',
        y='Cantidad',
        title='Top 10 Localidades Rechazadas',
        labels={'Cantidad': 'Número de Localidades Rechazadas'},
        color='Cantidad',
        color_continuous_scale='Reds'
    )
    bar_chart_localidades_rechazados.update_traces(texttemplate='%{y}', textposition='outside')
    st.plotly_chart(bar_chart_localidades_rechazados)

    # Filtro de Fechas Compacto al Final
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)
    st.subheader("Filtrar por Fecha")

    fecha_inicio = st.date_input("Fecha de Inicio", df_recupero_localidad['FECHA_INGRESO'].min().date(), key="fecha_inicio_rechazo")
    fecha_fin = st.date_input("Fecha de Fin", df_recupero_localidad['FECHA_INGRESO'].max().date(), key="fecha_fin_rechazo")


    if fecha_inicio > fecha_fin:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
    else:
        # Filtrar el DataFrame según las fechas seleccionadas
        fecha_inicio_dt = pd.to_datetime(fecha_inicio)
        fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_filtrado = df_recupero_localidad[(df_recupero_localidad['FECHA_INGRESO'] >= fecha_inicio_dt) & 
                                             (df_recupero_localidad['FECHA_INGRESO'] <= fecha_fin_dt)]
        
        if df_filtrado.empty:
            st.warning("No hay datos disponibles para el rango de fechas seleccionado.")

    # Feedback: Captura de comentario y valoración
    comentario = st.text_area("Deja tu comentario")
    valoracion = st.slider("Valoración", 1, 5, 3, help="Valora entre 1 y 5 estrellas")

    if st.button("Enviar Comentario"):
        if comentario:
            # Llamar a la función de feedback con los parámetros adecuados
            if mostrar_feedback(comentario, valoracion):
                st.success("¡Comentario enviado exitosamente!")
        else:
            st.error("Por favor, ingrese un comentario antes de enviar.")


