import streamlit as st
from streamlit_feedback import streamlit_feedback

def mostrar_feedback():
    # Feedback en la barra lateral
    st.sidebar.header("¿Qué podríamos mejorar?")
    with st.sidebar.form(key='form_feedback_unique'):
        streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Tus comentarios aquí...",
            align="flex-start",
            key='feedback_k_unique_2'
        )
        submit_feedback = st.form_submit_button('Enviar Feedback')  

        # Manejo del feedback
        if submit_feedback:
            feedback = st.session_state.get('feedback_k_unique_2')
            if feedback:
                st.sidebar.success("✔️ ¡Feedback recibido! Gracias por colaborar.")
            else:
                st.sidebar.warning("⚠️ Selecciona una opción antes de enviar.")

