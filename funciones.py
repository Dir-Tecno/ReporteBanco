import streamlit as st
import requests

# Función para enviar comentarios a Slack
def mostrar_feedback(comentario, valoracion):
    if not comentario or valoracion < 1 or valoracion > 5:
        st.error("Por favor, ingrese un comentario válido y una valoración entre 1 y 5 estrellas.")
        return False
    
    slack_webhook_url = st.secrets["slack"]["webhook_url"]
    
    mensaje = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📝 Nuevo Comentario Recibido"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Comentario:*\n{comentario}"},
                    {"type": "mrkdwn", "text": f"*Valoración:*\n{'⭐' * valoracion}"}
                ]
            }
        ]
    }

    with st.spinner("Enviando feedback..."):
        try:
            response = requests.post(slack_webhook_url, json=mensaje)
            if response.status_code == 200:
                st.success("Comentario enviado exitosamente a Slack.")
                return True
            else:
                st.error(f"Error al enviar el mensaje. Código de estado: {response.status_code}.")
                return False
        except requests.exceptions.RequestException as e:
            st.error(f"Error al enviar a Slack: {str(e)}")
            return False
