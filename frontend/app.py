import streamlit as st
import sys
import os
from dotenv import load_dotenv

load_dotenv()

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from llm_client import process_image
from pdf_generator import create_invoice_pdf
from database import (
    init_db, 
    create_conversation, 
    save_message, 
    load_conversations, 
    load_conversation_messages,
    delete_conversation,
    clear_all_history
)
from datetime import datetime

init_db()

st.set_page_config(page_title="Générateur de Facture", page_icon="📄")

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.session_state.last_uploaded_file = None

st.sidebar.title("Conversations")

if st.sidebar.button("➕ Nouvelle Session", use_container_width=True):
    st.session_state.current_conversation_id = create_conversation()
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()

conversations = load_conversations()

for conv in conversations:
    updated_dt = datetime.fromisoformat(conv["updated_at"])
    display_text = updated_dt.strftime("%d/%m/%Y %H:%M")
    
    col1, col2 = st.sidebar.columns([4, 1])
    
    with col1:
        if st.button(display_text, key=f"conv_{conv['id']}", use_container_width=True):
            st.session_state.current_conversation_id = conv["id"]
            st.session_state.messages = load_conversation_messages(conv["id"])
            st.rerun()
    
    with col2:
        if st.button("🗑️", key=f"del_{conv['id']}"):
            delete_conversation(conv["id"])
            if st.session_state.current_conversation_id == conv["id"]:
                st.session_state.current_conversation_id = None
                st.session_state.messages = []
            st.rerun()

st.sidebar.divider()

if st.sidebar.button("🗑️ Effacer Tout", use_container_width=True):
    clear_all_history()
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.rerun()

st.title("Générateur de Facture à partir d'Image")

if not st.session_state.current_conversation_id:
    st.info("👈 Cliquez sur 'Nouvelle Session' pour commencer ou sélectionnez une conversation existante")
else:
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"])
            if "pdf" in message:
                st.download_button(
                    label="Télécharger la Facture PDF",
                    data=message["pdf"],
                    file_name=message["filename"],
                    mime="application/pdf",
                    key=f"download_btn_{idx}"
                )

    uploaded_file = st.file_uploader("Télécharger une image de facture", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if st.session_state.last_uploaded_file != file_id:
            st.session_state.last_uploaded_file = file_id
            image_bytes = uploaded_file.read()
        
        user_msg = {
            "role": "user",
            "content": f"Téléchargé: {uploaded_file.name}",
            "image": image_bytes
        }
        st.session_state.messages.append(user_msg)
        save_message(st.session_state.current_conversation_id, user_msg["role"], user_msg["content"], image=image_bytes)
        
        with st.chat_message("user"):
            st.markdown(f"Téléchargé: {uploaded_file.name}")
            st.image(image_bytes)
        
        with st.chat_message("assistant"):
            status = st.empty()
            status.markdown("Traitement de l'image...")
            
            try:
                invoice_data = process_image(image_bytes)
                status.markdown("Génération du PDF...")
                
                pdf_buffer = create_invoice_pdf(invoice_data)
                pdf_bytes = pdf_buffer.getvalue()
                
                invoice_num = invoice_data.get("invoice_number", "facture")
                filename = f"facture_{invoice_num}.pdf"
                
                status.markdown("Facture générée avec succès!")
                
                st.download_button(
                    label="Télécharger la Facture PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_btn_new_{len(st.session_state.messages)}"
                )
                
                assistant_msg = {
                    "role": "assistant",
                    "content": "Facture générée avec succès!",
                    "pdf": pdf_bytes,
                    "filename": filename
                }
                st.session_state.messages.append(assistant_msg)
                save_message(st.session_state.current_conversation_id, assistant_msg["role"], assistant_msg["content"], pdf=pdf_bytes, filename=filename)
                
            except Exception as e:
                error_msg = f"Erreur: {str(e)}"
                status.markdown(error_msg)
                assistant_error = {
                    "role": "assistant",
                    "content": error_msg
                }
                st.session_state.messages.append(assistant_error)
                save_message(st.session_state.current_conversation_id, assistant_error["role"], assistant_error["content"])
