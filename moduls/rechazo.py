import streamlit as st
import pandas as pd
from streamlit_feedback import streamlit_feedback

def mostrar_rechazos(df_rechazos):
    # Conversión de columnas de fecha
    date_columns = ['FEC_RECHAZO', 'FEC_INICIO', 'FEC_FIN']
    for col in date_columns:
        if col in df_rechazos.columns:
            df_rechazos[col] = pd.to_datetime(df_rechazos[col], errors='coerce')
    df_rechazos = df_rechazos.dropna(subset=['FEC_RECHAZO'])

    # Filtro de fechas en la barra lateral
    st.sidebar.header("Filtros de Fecha")
    fecha_inicio = st.sidebar.date_input("Fecha de Inicio", df_rechazos['FEC_RECHAZO'].min().date())
    fecha_fin = st.sidebar.date_input("Fecha de Fin", df_rechazos['FEC_RECHAZO'].max().date())

    if fecha_inicio > fecha_fin:
        st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
    else:
        # Aplicar filtro de fechas
        fecha_inicio_dt = pd.to_datetime(fecha_inicio)
        fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_filtrado = df_rechazos[(df_rechazos['FEC_RECHAZO'] >= fecha_inicio_dt) & 
                                   (df_rechazos['FEC_RECHAZO'] <= fecha_fin_dt)]
        
        # Definir las categorías y sus ID
        estado_categorias = {
            "Pagados": [13, 14, 20],
            "Créditos con Deuda": [16, 17, 18, 21],
            "Impagos/Bajas": [23, 22, 15],
            "Finalizados": [7],
        }

        # Contar formularios por estado
        conteo_estados = {
            categoria: df_filtrado[df_filtrado['ID_ESTADO_PRESTAMO'].isin(estados)].shape[0]
            for categoria, estados in estado_categorias.items()
        }

        # Diseño de columnas y cuadros con estilo mejorado
        col1, col2, col3, col4 = st.columns(4)

        cuadro_estilo = """
            <div style="margin: 10px; padding: 15px; border-radius: 12px; background-color: {bg_color}; 
            color: {text_color}; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); font-family: Arial, sans-serif;">
                <h3 style="text-align: center; font-size: 18px;">{titulo}</h3>
                <p style="text-align: center; font-size: 28px; font-weight: bold;">{cantidad}</p>
            </div>
        """

        # Mostrar cuadros en las columnas
        with col1:
            st.markdown(cuadro_estilo.format(
                titulo="Pagados",
                cantidad="{:,.0f}".format(conteo_estados["Pagados"]),
                bg_color="#4CAF50", text_color="white"), unsafe_allow_html=True)

        with col2:
            st.markdown(cuadro_estilo.format(
                titulo="Créditos con Deuda",
                cantidad="{:,.0f}".format(conteo_estados["Créditos con Deuda"]),
                bg_color="#FF5722", text_color="white"), unsafe_allow_html=True)

        with col3:
            st.markdown(cuadro_estilo.format(
                titulo="Impagos/Bajas",
                cantidad="{:,.0f}".format(conteo_estados["Impagos/Bajas"]),
                bg_color="#2196F3", text_color="white"), unsafe_allow_html=True)

        with col4:
            st.markdown(cuadro_estilo.format(
                titulo="Finalizados",
                cantidad="{:,.0f}".format(conteo_estados["Finalizados"]),
                bg_color="#FFC107", text_color="white"), unsafe_allow_html=True)

        # Gráficos
        st.subheader("Gráfico de Barras: Formularios por Estado", anchor="barras")
        grafico_barras = df_filtrado.groupby('ID_ESTADO_PRESTAMO').size().reset_index(name='Cantidad')
        st.bar_chart(grafico_barras.set_index('ID_ESTADO_PRESTAMO'))

        st.subheader("Gráfico de Pastel: Formularios por Línea de Rechazo", anchor="pastel")
        grafico_pastel = df_filtrado.groupby('N_LINEA_RECHAZO').size().reset_index(name='Cantidad')
        st.write(grafico_pastel.set_index('N_LINEA_RECHAZO').plot.pie(y='Cantidad', autopct='%1.1f%%'))

    # Feedback en la barra lateral
    st.sidebar.header("¿Qué podríamos mejorar?")
    with st.sidebar.form(key='form_feedback'):
        streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Tus comentarios aquí...",
            align="flex-start",
            key='feedback_k'
        )
        submit_feedback = st.form_submit_button('Enviar Feedback')

        if submit_feedback:
            feedback = st.session_state.get('feedback_k')
            if feedback:
                st.sidebar.success("✔️ ¡Feedback recibido! Gracias por colaborar.")
            else:
                st.sidebar.warning("⚠️ Selecciona una opción antes de enviar.")
