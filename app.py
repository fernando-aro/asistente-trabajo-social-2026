import streamlit as st
from openai import OpenAI
import os

# 1. Configuración de la interfaz responsiva para web, tablets y dispositivos móviles
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

# 3. Inicialización del cliente OpenAI apuntando al endpoint compatible de Groq
client = OpenAI(
    api_key=api_key,
    base_url="https://groq.com"
)

# 4. Función automática para leer el archivo de contexto externo (.txt)
@st.cache_data
def cargar_contexto_documentos(nombre_archivo="documentos_contexto.txt"):
    """
    Carga de forma automática las normativas, propuestas y referencias bibliográficas 
    guardadas en el archivo externo de texto plano.
    """
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("CONTEXTO DE LA PONENCIA:\n(Por favor, pega aquí el contenido de tus propuestas y normativas).")
    
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        return f.read()

# Carga previa del documento externo (Previene NameError)
CONTEXTO_INYECTADO = cargar_contexto_documentos()

# 5. Definición de la instrucción maestra del sistema para el blindaje de búsqueda
INSTRUCCION_SISTEMA = (
    "REGLAS ESTRICTAS DE OPERACIÓN:\n"
    "1. Actúa como un asistente académico riguroso para la ponencia de Trabajo Social 2026.\n"
    "2. Tu ÚNICA fuente de verdad es el contexto provisto al final de estas instrucciones. Está terminantemente prohibido usar conocimientos externos o inventar datos.\n"
    "3. Si la respuesta a la pregunta del usuario NO se encuentra explícitamente detallada, sugerida o referenciada en el contexto provisto, debes responder exactamente: 'Lo lamento, pero esa información no se encuentra contemplada en los documentos oficiales de la propuesta ni en las referencias bibliográficas de la ponencia.'\n"
    "4. No respondas bajo ninguna circunstancia preguntas de cultura general, código, recetas, matemáticas o cualquier tema ajeno a esta investigación.\n\n"
    f"CONTEXTO EXCLUSIVO DE BÚSQUEDA:\n{CONTEXTO_INYECTADO}"
)

# 6. Inicialización y renderizado del historial del Chat en la sesión de Streamlit
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Mensaje de bienvenida inicial fijo en pantalla
with st.chat_message("assistant"):
    st.write(
        "¡Hola! He sido configurado para buscar información exclusivamente dentro de los documentos aportados, "
        "las normativas internacionales citadas y las referencias bibliográficas de la ponencia. ¿Qué consulta puntual "
        "deseas realizar sobre el Órgano Colegiado, MIDEPLAN, el IMAS o la teoría de Max-Neef?"
    )

# Renderizar los mensajes acumulados en la sesión activa
for role, text in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.write(text)

# 7. Captura de la interacción y consulta del usuario (Inferencia Blindada)
if user_query := st.chat_input("Escribe tu consulta académica o profesional aquí..."):
    # Guardar y mostrar el mensaje del usuario
    st.session_state["chat_history"].append(("user", user_query))
    with st.chat_message("user"):
        st.write(user_query)
        
    # Construcción dinámica inyectando el System Prompt fresco para evitar evasión de reglas
    payload_mensajes = [{"role": "system", "content": INSTRUCCION_SISTEMA}]
    for role, text in st.session_state["chat_history"]:
        payload_mensajes.append({"role": role, "content": text})
        
    # Consulta al motor de inferencia compatible con OpenAI
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            # MODELO ACTUALIZADO Y ACTIVO: Llama 3.3 70B Versatile
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=payload_mensajes,
                temperature=0.0  # Fuerza el apego matemático al documento de texto plano
            )
            answer = chat_completion.choices.message.content
            response_placeholder.write(answer)
            
            # Guardar la respuesta generada en el historial
            st.session_state["chat_history"].append(("assistant", answer))
        except Exception as e:
            # Conservamos tu bloque original de monitoreo
            st.error(f"Ocurrió un error en la comunicación con el servidor: {e}")
