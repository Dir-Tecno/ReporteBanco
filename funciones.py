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

# Función para crear tarjetas en Trello
def crear_tarjeta_trello(titulo, descripcion, lista_id):
    if not titulo or not lista_id:
        st.error("Por favor, ingrese un título válido y seleccione una lista.")
        return False

    api_key = st.secrets["trello"]["api_key"]
    token = st.secrets["trello"]["token"]
    url = f"https://api.trello.com/1/cards"

    params = {
        'key': api_key,
        'token': token,
        'idList': lista_id,
        'name': titulo,
        'desc': descripcion
    }

    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            tarjeta = response.json()
            st.success("Tarjeta creada exitosamente en Trello.")
            st.write("### Tarjeta Creada:")
            st.write(f"**Título:** {tarjeta['name']}")
            st.write(f"**Descripción:** {tarjeta['desc']}")
            st.write(f"**Enlace:** [Ver Tarjeta en Trello]({tarjeta['shortUrl']})")
            return True
        else:
            st.error(f"Error al crear la tarjeta. Código de estado: {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error al enviar a Trello: {str(e)}")
        return False

# Función para obtener listas de un tablero
def obtener_listas_trello(tablero_id):
    api_key = st.secrets["trello"]["api_key"]
    token = st.secrets["trello"]["token"]
    url = f"https://api.trello.com/1/boards/{tablero_id}/lists"

    params = {'key': api_key, 'token': token}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error al obtener las listas. Código de estado: {response.status_code}.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con Trello: {str(e)}")
        return []

# Función para obtener tableros de Trello
def obtener_tableros_trello():
    api_key = st.secrets["trello"]["api_key"]
    token = st.secrets["trello"]["token"]
    url = f"https://api.trello.com/1/members/me/boards"

    params = {'key': api_key, 'token': token}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error al obtener los tableros. Código de estado: {response.status_code}.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con Trello: {str(e)}")
        return []

