import streamlit as st
from openai import OpenAI
import os

# 1. Configuración de la interfaz responsiva
st.set_page_config(
    page_title="Asistente Democracia Participativa - TS 2026", 
    page_icon="⚖️", 
    layout="centered"
)

st.title("🤖 Asistente Virtual: Ponencia Trabajo Social 2026")
st.subheader("Consultas basadas en la Teoría de Max-Neef, Ley 8364 y la propuesta de Democracia Participativa")

# 2. Conexión segura con la API Key (Secrets)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif "GROQ_API_KEY" in os.environ:
    api_key = os.environ["GROQ_API_KEY"]
else:
    st.error("⚠️ No se encontró la API Key. Configúrala como GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://groq.com")

# 3. Función automática para leer el archivo de contexto (.txt)
@st.cache_data
def cargar_contexto_documentos(nombre_archivo="documentos_contexto.txt"):
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("CONTEXTO DE LA PONENCIA:\n(Pega aquí tus documentos oficiales).")
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        return f.read()

CONTEXTO_INYECTADO = cargar_contexto_documentos()

# 5. Definición de la instrucción maestra del sistema
INSTRUCCION_SISTEMA = (
    "REGLAS ESTRICTAS DE OPERACIÓN:\n"
    "1. Tu ÚNICA fuente de verdad es el contexto provisto abajo. Prohibido usar conocimientos externos.\n"
    "2. Si la respuesta no está en el contexto, di exactamente: 'Lo lamento, pero esa información no se encuentra contemplada en los documentos oficiales de la propuesta ni en las referencias bibliográficas de la ponencia.'\n"
    "3. No respondas preguntas ajenas a esta investigación.\n\n"
    f"CONTEXTO EXCLUSIVO:\n{CONTEXTO_INYECTADO}"
)

# 6. Inicialización del Historial de Chat
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --- INTEGRACIÓN DEL BOTÓN DE REINICIO EN LA BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    if st.button("🔄 Reiniciar Conversación", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

# Mensaje de bienvenida inicial fijo
with st.chat_message("assistant"):
    st.write("¡Hola! He sido configurado para buscar información exclusivamente dentro de los documentos aportados. ¿Qué consulta deseas realizar?")

# Renderizar mensajes acumulados
for role, text in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.write(text)

# 7. Captura de la interacción del usuario
if user_query := st.chat_input("Escribe tu consulta académica o profesional aquí..."):
    st.session_state["chat_history"].append(("user", user_query))
    with st.chat_message("user"):
        st.write(user_query)
        
    payload_mensajes = [{"role": "system", "content": INSTRUCCION_SISTEMA}]
    for role, text in st.session_state["chat_history"]:
        payload_mensajes.append({"role": role, "content": text})
        
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=payload_mensajes,
                temperature=0.0
            )
            answer = chat_completion.choices.message.content
            response_placeholder.write(answer)
            st.session_state["chat_history"].append(("assistant", answer))
        except Exception as e:
            st.error(f"Ocurrió un error en la comunicación con el servidor: {e}")
