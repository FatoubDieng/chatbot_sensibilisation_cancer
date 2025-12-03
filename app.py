import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"  

# ---- UI CONFIG ----
st.set_page_config(
    page_title="FabiBot – Sensibilisation au Cancer",
    page_icon="image1.png",  
    layout="centered"
)

# ---- TITLE AVEC LOGO ROND ----
col1, col2 = st.columns([0.18, 1])
with col1:
    st.image("image1.png", width=60)
with col2:
    st.markdown(
        """
        <h1 style="margin:0px;">FabiBot – Assistante de Sensibilisation au Cancer</h1>
        """,
        unsafe_allow_html=True
    )

# ---- Chat History ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique 
for msg in st.session_state.messages:
    if msg["role"] == "user":
    
        with st.chat_message("assistant", avatar="👤"): 
            st.write(msg["content"])
    else:
        
        with st.chat_message("user", avatar="image.png"):
            st.write(msg["content"])

# ---- Input utilisateur ----
user_input = st.chat_input("Pose une question en lien avec le cancer…")

if user_input:
    # Ajout au chat local
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Envoi à l'API
    try:
        response = requests.post(API_URL, json={"question": user_input})

        if response.status_code == 200:
            bot_reply = response.json().get("reponse", "Réponse introuvable.")
        else:
            bot_reply = "Erreur : Impossible de contacter l’API."
    except Exception as e:
        bot_reply = f" Erreur de connexion : {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})


    st.rerun() 
