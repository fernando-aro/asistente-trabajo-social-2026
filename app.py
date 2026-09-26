import streamlit as st
from groq import Groq  # Migración a la librería oficial nativa de Groq
import os
import glob
import urllib.parse

# 1. Configuración de la interfaz adaptativa para web y dispositivos móviles
st.set_page_config(
    page_title="Asistente Democracia Participativa - TS 2026", 
    page_icon="⚖️", 
    layout="centered"
)

st.title("🤖 Asistente Virtual: Ponencia Trabajo Social 2026")
st.subheader("Consultas basadas en la Teoría de Max-Neef, Ley 8364 y la propuesta de Democracia Participativa")

# 2. Conexión segura con la API Key (Secrets de Streamlit o variables de entorno)
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ No se encontró la API Key. Configúrala como GROQ_API_KEY en los Secrets de Streamlit Community Cloud.")
    st.stop()

# 3. Inicialización del cliente NATIVO de Groq (Elimina el error 405)
client = Groq(api_key=api_key)

# 4. Buscador inteligente de texto restringido para Planes Gratuitos (Anti Error 413)
@st.cache_data
def escanear_todos_los_contextos(consulta_usuario, max_bloques=2):
    """
    Busca palabras clave en TODOS los archivos .txt de la carpeta.
    Limita estrictamente el contexto enviado para no saturar el límite TPM de tokens.
    """
    archivos = glob.glob("*.txt")
    if not archivos:
        return "No se encontraron archivos de contexto (.txt) locales."

    palabras_clave = [p.lower() for p in consulta_usuario.split() if len(p) > 3]
    bloques_encontrados = []

    for ruta_archivo in archivos:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            parrafos = [p.strip() for p in contenido.split("\n\n") if len(p.strip()) > 30]
            
            for parrafo in parrafos:
                coincidencias = sum(1 for p in palabras_clave if p in parrafo.lower())
                if modificaciones := coincidencias > 0:
                    bloques_encontrados.append((coincidencias, f"[{ruta_archivo}]: {parrafo}"))

    # Ordenar de mayor a menor coincidencia
    bloques_encontrados.sort(key=lambda x: x[0], reverse=True)
    
    if bloques_encontrados:
        # Extraemos solo el texto (segundo elemento de la tupla)
        textos_filtrados = [b[1] for b in bloques_encontrados[:max_bloques]]
        return "\n\n---\n\n".join(textos_filtrados)
    
    return "No se encontraron coincidencias específicas. Responde de forma muy concisa usando tu conocimiento general."

# 5. Inicialización del historial de chat en la sesión de Streamlit
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": (
                "¡Hola! He cargado el entorno de análisis de tus documentos base. "
                "Puedes preguntar sobre el modelo del Órgano Colegiado, el Artículo 9 de la Constitución de Costa Rica, la Ley 8364, "
                "los recortes presupuestarios en inversión social o la crítica a los seudo-satisfactores del IMAS y MIDEPLAN. ¿Qué deseas consultar?"
            )
        }
    ]

# 6. Renderizar el historial de conversación en pantalla
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. Captura de la interacción y consulta del usuario
if user_query := st.chat_input("Escribe tu consulta académica o profesional aquí..."):
    with st.chat_message("user"):
        st.write(user_query)
    
    conceptos_legales = ["ley", "articulo", "constitución", "decreto", "reforma", "normativa", "8364", "artí", "sinalevi"]
    es_consulta_legal = any(palabra in user_query.lower() for palabra in conceptos_legales)
    
    contexto_dinamico = escanear_todos_los_contextos(user_query)
    
    prompt_sistema = {
        "role": "system",
        "content": (
            "Eres un asistente académico experto en Trabajo Social en Costa Rica.\n"
            "INSTRUCCIONES DIRECTAS:\n"
            "Responde de forma muy breve, directa y resumida utilizando este contexto:\n"
            f"{contexto_dinamico}\n\n"
            "Evita introducciones largas para no consumir tokens innecesarios."
        )
    }
    
    historial_reciente = st.session_state.messages[-2:]
    mensajes_para_api = [prompt_sistema] + historial_reciente + [{"role": "user", "content": user_query}]
    
    with st.chat_message("assistant"):
        try:
            # Llamada nativa utilizando el motor oficial de Groq
            stream = client.chat.completions.create(
                model="llama3-8b-8192",  # Modelo estable, gratuito y de producción masiva en Groq
                messages=mensajes_para_api,
                temperature=0.2,               
                stream=True                    
            )
            
            answer = st.write_stream(stream)
            
            if es_consulta_legal:
                query_codificado = urllib.parse.quote_plus(user_query)
                url_sinalevi = f"http://sinalevi.go.cr{query_codificado}"
                
                st.markdown("---")
                st.caption("⚖️ **Validación Jurídica en Tiempo Real (Costa Rica):**")
                st.info(
                    "Para asegurar que la norma consultada no haya sufrido reformas recientes, "
                    f"puedes verificar directamente los términos de tu consulta en el [Buscador del Sistema Nacional de Leyes Vigentes (SINALEVI)]({url_sinalevi} \"Búsqueda SINALEVI\")."
                )
            
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Error de comunicación: {e}")