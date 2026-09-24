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

# 2. Conexión segura con la API Key (Almacenada en los Secrets de Streamlit)
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif "GROQ_API_KEY" in os.environ:
    api_key = os.environ["GROQ_API_KEY"]
else:
    st.error("⚠️ No se encontró la API Key. Configúrala como GROQ_API_KEY en los Secrets de Streamlit Community Cloud.")
    st.stop()

# 3. Inicialización del cliente OpenAI apuntando a los servidores rápidos de Groq
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"  # Endpoint de compatibilidad OpenAI
)

# 4. Inicialización del historial de chat BLINDADO en la sesión de Streamlit
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system", 
            "content": (
                "REGLAS ESTRICTAS DE OPERACIÓN:\n"
                "1. Actúa como un asistente académico riguroso para la ponencia de Trabajo Social 2026.\n"
                "2. Tu ÚNICA fuente de verdad es el contexto provisto a continuación. Está terminantemente prohibido usar conocimientos externos o inventar datos.\n"
                "3. Si la respuesta a la pregunta del usuario NO se encuentra explícitamente detallada, sugerida o referenciada en el contexto provisto, debes responder exactamente: 'Lo lamento, pero esa información no se encuentra contemplada en los documentos oficiales de la propuesta ni en las referencias bibliográficas de la ponencia.'\n"
                "4. No respondas preguntas de cultura general, código, matemáticas o cualquier tema ajeno a esta investigación.\n\n"
                f"CONTEXTO EXCLUSIVO DE BÚSQUEDA:\n{CONTEXTO_INYECTADO}"
            )
        },
        {
            "role": "assistant", 
            "content": (
                "¡Hola! He sido configurado para buscar información exclusivamente dentro de los documentos aportados, "
                "las normativas internacionales citadas y las referencias bibliográficas de la ponencia. ¿Qué consulta puntual "
                "deseas realizar sobre el Órgano Colegiado, MIDEPLAN, el IMAS o la teoría de Max-Neef?"
            )
        }
    ]

# [ ... Código intermedio idéntico: renderizado de mensajes en pantalla ... ]

# 5. Inicialización del historial de chat en la sesión de Streamlit
if "messages" not in st.session_state:
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

# 6. Renderizar el historial de conversación en pantalla
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 7. Captura de la interacción y consulta del usuario (Inferencia Blindada)
if user_query := st.chat_input("Escribe tu consulta académica o profesional aquí..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)
        
    with St.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=st.session_state.messages,
                temperature=0.0  # <--- CRUCIAL: Temperatura 0.0 anula la creatividad del modelo
            )
            answer = chat_completion.choices.message.content
            response_placeholder.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Ocurrió un error en la comunicación con el servidor: {e}")