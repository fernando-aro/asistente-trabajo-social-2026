import streamlit as st
from openai import OpenAI
import os

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="Asistente Democracia Participativa - TS 2026", 
    page_icon="⚖️", 
    layout="centered"
)

st.title("🤖 Asistente Virtual: Ponencia Trabajo Social 2026")
st.subheader("Consultas basadas en la Teoría de Max-Neef, Ley 8364 y la propuesta de Democracia Participativa")

# 2. Conexión segura con la API Key
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
elif "GROQ_API_KEY" in os.environ:
    api_key = os.environ["GROQ_API_KEY"]
else:
    st.error("⚠️ No se encontró la API Key. Configúrala como GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. Inicialización del cliente
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# 4. Buscador inteligente de texto plano (Evita el desborde de tokens)
@st.cache_data
def obtener_contexto_relevante(consulta_usuario, nombre_archivo="documentos_contexto.txt", max_parrafos=6):
    """
    Lee el archivo pesado y extrae únicamente los párrafos que contienen 
    palabras clave asociadas a la pregunta del usuario.
    """
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("CONTEXTO DE LA PONENCIA:\n(Pega aquí tus propuestas, Ley 8364 y teoría de Max-Neef).")
        return "Archivo vacío creado."

    with open(nombre_archivo, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    # Limpieza básica y separación por párrafos/bloques
    bloques = [b.strip() for b in lineas if len(b.strip()) > 20]
    
    # Extraer palabras clave de la consulta del usuario
    palabras = [p.lower() for p in consulta_usuario.split() if len(p) > 3]
    
    # Puntuar bloques basados en coincidencias
    bloques_puntuados = []
    for bloque in bloques:
        puntos = sum(1 for p in palabras if p in bloque.lower())
        if puntos > 0:
            bloques_puntuados.append((puntos, bloque))
            
    # Ordenar por relevancia
    bloques_puntuados.sort(key=lambda x: x[0], reverse=True)
    
    # Si encuentra coincidencias, devuelve los mejores bloques; si no, toma los primeros como fallback
    if bloques_puntuados:
        fragmentos = [b[1] for b in bloques_puntuados[:max_parrafos]]
    else:
        fragmentos = bloques[:max_parrafos]
        
    return "\n\n".join(fragmentos)

# 5. Inicialización básica del historial de chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": (
                "¡Hola! El bot asistente con arquitectura optimizada está listo. "
                "Puedes consultar sobre el modelo del Órgano Colegiado, el Artículo 9 de la Constitución, la Ley 8364, "
                "los recortes presupuestarios en inversión social o la crítica a Max-Neef. ¿Qué deseas consultar?"
            )
        }
    ]

# 6. Renderizar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. Captura de interacción y consulta filtrada
if user_query := st.chat_input("Escribe tu consulta académica o profesional aquí..."):
    # Mostrar consulta del usuario en pantalla
    with st.chat_message("user"):
        st.write(user_query)
    
    # Extraer SOLAMENTE el fragmento de texto relacionado con lo que el usuario preguntó
    contexto_filtrado = obtener_contexto_relevante(user_query)
    
    # Construcción dinámica de la instrucción para esta pregunta específica
    prompt_sistema = {
        "role": "system",
        "content": (
            "Eres un asistente académico experto en Trabajo Social, Gestión Pública y Derechos Humanos. "
            "Responde de forma concisa basándote estrictamente en este fragmento extraído de tus documentos:\n\n"
            f"{contexto_filtrado}"
        )
    }
    
    # Preparar el paquete de mensajes: Sistema + Historial Reciente + Pregunta Actual
    # Tomamos solo las últimas 3 interacciones para proteger el límite de tokens
    historial_reciente = st.session_state.messages[-3:]
    mensajes_para_api = [prompt_sistema] + historial_reciente + [{"role": "user", "content": user_query}]
    
    # Consulta al motor de inferencia
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b",  # Cambia por "llama-3.1-8b-instant" si deseas mayor velocidad
                messages=mensajes_para_api,
                temperature=0.2,
                stream=True
            )
            
            # Renderizar respuesta fluida
            answer = st.write_stream(stream)
            
            # Guardar en el historial de sesión la conversación real
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Ocurrió un error en la comunicación con el servidor: {e}")