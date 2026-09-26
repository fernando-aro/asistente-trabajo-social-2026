import streamlit as st
from openai import OpenAI
import os
# 1. Configuración de la interfaz adaptativa para web y dispositivos móviles
st.set_page_config(
    page_title="Asistente Democracia Participativa - TS 2026", 
    page_icon="⚖️", 
    layout="centered"
)

st.title("🤖 Asistente Virtual: Ponencia Trabajo Social 2026")
st.subheader("Consultas basadas en la Teoría de Max-Neef, Ley 8364 y la propuesta de Democracia Participativa")
# 2. Conexión segura con la API Key (Almacenada en los Secrets de Streamlit)if "GROQ_API_KEY" in st.secrets:
    api_key = 
st.secrets["GROQ_API_KEY"]
    elif "GROQ_API_KEY" in os.environ:
    api_key = os.environ["GROQ_API_KEY"]else:
    st.error("⚠️ No se encontró la API Key. Configúrala como GROQ_API_KEY en los Secrets de Streamlit Community Cloud.")
    st.stop()
# 3. Inicialización del cliente OpenAI apuntando a los servidores rápidos de Groqclient = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"  # Endpoint de compatibilidad OpenAI)

# 4. Función automática para leer el archivo de contexto externo (.txt)
@st.cache_datadef cargar_contexto_documentos(nombre_archivo="documentos_contexto.txt"):
    """
    Carga de forma automática las normativas, propuestas y referencias bibliográficas 
    guardadas en el archivo externo de texto plano.
    """
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("CONTEXTO DE LA PONENCIA:\n(Por favor, pega aquí el contenido de tus propuestas y normativas).")
    
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        return f.read()
# Inyección del texto de los documentos aportadosCONTEXTO_INYECTADO = cargar_contexto_documentos()
# 5. Inicialización del historial de chat en la sesión de Streamlitif "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system", 
            "content": (
                "Eres un asistente académico experto en Trabajo Social, Gestión Pública y Derechos Humanos. "
                "Responde las dudas de estudiantes y profesionales basándote estrictamente en el siguiente contexto legal, "
                f"teórico y bibliográfico inyectado desde tus documentos oficiales:\n\n{CONTEXTO_INYECTADO}"
            )
        },
        {
            "role": "assistant", 
            "content": (
                "¡Hola! El bot asistente (con arquitectura OpenAI-Groq) está listo para responder tus consultas en tiempo real. "
                "Puedes preguntar sobre el modelo del Órgano Colegiado, el Artículo 9 de la Constitución de Costa Rica, la Ley 8364, "
                "los recortes presupuestarios en inversión social o la crítica a los seudo-satisfactores del IMAS y MIDEPLAN. ¿Qué deseas consultar?"
            )
        }
    ]
# 6. Renderizar el historial de conversación en pantallafor msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
# 7. Captura de la interacción y consulta del usuarioif user_query := st.chat_input("Escribe tu consulta académica o profesional aquí..."):
    # Guardar y mostrar el mensaje enviado por el usuario
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)
        
    # Consulta al motor de inferencia compatible con OpenAI
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            # Llamada estándar usando el catálogo actualizado de Groq
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",  # Modelo oficial de alta capacidad con Prompt Caching
                messages=st.session_state.messages,
                temperature=0.2  # Temperatura baja para garantizar fidelidad estricta al texto
            )
            answer = chat_completion.choices[0].message.content
            response_placeholder.write(answer)
            
            # Guardar la respuesta generada en el historial de sesión
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Ocurrió un error en la comunicación con el servidor: {e}")
