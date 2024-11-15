import streamlit as st
import pandas as pd
import plotly.express as px
from funciones import mostrar_feedback


def mostrar_recupero(df_recupero_localidad, df_global, file_date, geojson_data):
    st.write(f"Datos actualizados al: {file_date.strftime('%d/%m/%Y %H:%M:%S')}")

    # Manejo de error si la columna no existe
    if 'FECHA_INGRESO' in df_recupero_localidad.columns:
        # Convertir la columna a tipo datetime
        df_recupero_localidad['FECHA_INGRESO'] = pd.to_datetime(df_recupero_localidad['FECHA_INGRESO'], errors='coerce')
        
        # Eliminar filas con fechas NaT
        df_recupero_localidad = df_recupero_localidad.dropna(subset=['FECHA_INGRESO'])

        # Definir las categorías y sus ID
        estado_categorias = {
            "Pagados": [13, 14, 16, 17, 18, 20, 21, 7],
            "Créditos con Deuda": [21],
            "Impagos/Bajas": [23, 22, 15],
            "Finalizados": [7],
        }

        # Contar formularios por estado
        conteo_estados = {
            categoria: df_recupero_localidad[df_recupero_localidad['ID_ESTADO_PRESTAMO'].isin(estados)].shape[0]
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
        grafico_barras = df_recupero_localidad.groupby('N_ESTADO_PRESTAMO').size().reset_index(name='Cantidad')
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

        # Línea divisoria en gris claro
        st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

        # Filtro de fechas compacto al final
        st.subheader("Filtrar por Fecha")
        fecha_inicio = st.date_input("Fecha de Inicio", df_recupero_localidad['FECHA_INGRESO'].min().date(), key="fecha_inicio_final")
        fecha_fin = st.date_input("Fecha de Fin", df_recupero_localidad['FECHA_INGRESO'].max().date(), key="fecha_fin_final")

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

 # Línea divisoria en gris claro
        st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

        # Asegurarse de que las columnas necesarias están en formato numérico
        df_global['MONTO_OTORGADO'] = pd.to_numeric(df_global['MONTO_OTORGADO'], errors='coerce')
        df_global['DEUDA'] = pd.to_numeric(df_global['DEUDA'], errors='coerce')
        df_global['DEUDA_NO_VENCIDA'] = pd.to_numeric(df_global['DEUDA_NO_VENCIDA'], errors='coerce')

        # Sumar MONTO_OTORGADO por ID_FORMULARIO_LINEA
        monto_otorgado_total = df_global.groupby('ID_FORMULARIO_LINEA')['MONTO_OTORGADO'].sum().sum()

        # Sumar DEUDA y DEUDA_NO_VENCIDA por ID_FORMULARIO_LINEA
        df_global['DEUDA_TOTAL'] = df_global['DEUDA'] + df_global['DEUDA_NO_VENCIDA']
        deuda_total = df_global.groupby('ID_FORMULARIO_LINEA')['DEUDA_TOTAL'].sum().sum()
        deuda_no_vencida_total = df_global.groupby('ID_FORMULARIO_LINEA')['DEUDA_NO_VENCIDA'].sum().sum()

        # Diseño de grid para las tarjetas de deuda
        st.subheader("Resumen de Deudas y Montos")

        # Crear un grid para las tarjetas de montos otorgados y deudas
        grid = st.columns(3)

        # Mostrar tarjetas en el grid
        with grid[0]:
            st.markdown("""
                <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: #dff0d8; color: #3c763d;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
                    <h3 style="text-align: center; font-size: 18px;">Monto Otorgado Total</h3>
                    <p style="text-align: center; font-size: 32px; font-weight: bold;">{:,.0f}</p>
                </div>
            """.format(monto_otorgado_total), unsafe_allow_html=True)

        with grid[1]:
            st.markdown("""
                <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: #f2dede; color: #a94442;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
                    <h3 style="text-align: center; font-size: 18px;">Deuda Total</h3>
                    <p style="text-align: center; font-size: 32px; font-weight: bold;">{:,.0f}</p>
                </div>
            """.format(deuda_total), unsafe_allow_html=True)

        with grid[2]:
            st.markdown("""
                <div style="margin: 10px; padding: 15px; border-radius: 8px; background-color: #d9edf7; color: #31708f;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
                    <h3 style="text-align: center; font-size: 18px;">Deuda No Vencida Total</h3>
                    <p style="text-align: center; font-size: 32px; font-weight: bold;">{:,.0f}</p>
                </div>
            """.format(deuda_no_vencida_total), unsafe_allow_html=True)

        # Asegurarse de que los valores no sean NaN antes de mostrarlos
        if pd.isna(monto_otorgado_total) or pd.isna(deuda_total) or pd.isna(deuda_no_vencida_total):
            st.warning("Algunos de los totales no pudieron ser calculados debido a datos faltantes o incorrectos.")


       # Línea divisoria en gris claro
    st.markdown("<hr style='border: 2px solid #cccccc;'>", unsafe_allow_html=True)

    # Serie de Tiempo: Evolución de la Deuda usando FEC_FORM
    st.subheader("Evolución de la Deuda Vencida")

    # Verificar que las columnas necesarias existan y no tengan todos los valores nulos
    if {'DEUDA', 'FEC_FORM', 'ID_ESTADO_PRESTAMO'}.issubset(df_global.columns):
        df_global['FEC_FORM'] = pd.to_datetime(df_global['FEC_FORM'], errors='coerce')

        # Filtrar por los valores de ID_ESTADO_PRESTAMO
        estados_filtrados = [13, 14, 16, 17, 18, 21]
        df_filtrado = df_global[df_global['ID_ESTADO_PRESTAMO'].isin(estados_filtrados)]
        
        # Asegurarse de que no haya NaN en las columnas necesarias
        df_filtrado = df_filtrado.dropna(subset=['FEC_FORM', 'DEUDA'])

        # Agrupar por fecha y sumar las deudas
        deuda_por_fecha = df_filtrado.groupby(df_filtrado['FEC_FORM'].dt.date)['DEUDA'].sum().reset_index()
        deuda_por_fecha.columns = ['Fecha', 'Deuda Total']

        # Crear gráfico de línea
        line_chart = px.line(
            deuda_por_fecha,
            x='Fecha',
            y='Deuda Total',
            labels={'Fecha': 'Fecha', 'Deuda Total': 'Deuda Total ($)'},
            line_shape='spline',
            markers=True
        )

        st.plotly_chart(line_chart)
    else:
        st.warning("No se encontraron datos válidos para generar la serie de tiempo.")

