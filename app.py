import streamlit as st
from openai import OpenAI
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

# 3. Inicialización del cliente apuntando a los servidores de Groq
client = OpenAI(
    api_key=api_key,
    base_url="https://groq.com"  # Endpoint de compatibilidad OpenAI en Groq
)

# 4. Buscador inteligente de texto en múltiples archivos (Evita desborde de tokens)
@st.cache_data
def escanear_todos_los_contextos(consulta_usuario, max_bloques=8):
    """
    Busca palabras clave en TODOS los archivos .txt de la carpeta.
    Prioriza las coincidencias exactas para armar el mejor contexto dinámico.
    """
    archivos = glob.glob("*.txt")
    if not archivos:
        return "No se encontraron archivos de contexto (.txt) locales."

    palabras_clave = [p.lower() for p in consulta_usuario.split() if len(p) > 3]
    bloques_encontrados = []

    for ruta_archivo in archivos:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            # Dividir los textos por párrafos basados en doble salto de línea
            parrafos = [p.strip() for p in contenido.split("\n\n") if len(p.strip()) > 30]
            
            for parrafo in parrafos:
                # Calcular relevancia por coincidencia de términos
                coincidencias = sum(1 for p in palabras_clave if p in parrafo.lower())
                if %s_coincidencias := coincidencias > 0:
                    bloques_encontrados.append((coincidencias, f"[{ruta_archivo}]: {parrafo}"))

    # Ordenar de mayor a menor coincidencia
    bloques_encontrados.sort(key=lambda x: x[0], reverse=True)
    
    if bloques_encontrados:
        return "\n\n---\n\n".join([b[1] for b in bloques_encontrados[:max_bloques]])
    
    # Fallback si no hay palabras clave que coincidan directamente
    return "No se encontraron coincidencias específicas en los documentos. Responde usando tu conocimiento general en Trabajo Social."

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
    # Mostrar de inmediato la consulta en la interfaz de usuario
    with st.chat_message("user"):
        st.write(user_query)
    
    # 🔍 DETECCIÓN JURÍDICA: Verificar si la consulta pide leyes o normativas de Costa Rica
    conceptos_legales = ["ley", "articulo", "constitución", "decreto", "reforma", "normativa", "8364", "artí", "sinalevi"]
    es_consulta_legal = any(palabra in user_query.lower() for palabra in conceptos_legales)
    
    # Extraer el fragmento de texto relacionado de los archivos de texto locales
    contexto_dinamico = escanear_todos_los_contextos(user_query)
    
    # Instrucciones estrictas para el comportamiento del modelo de lenguaje
    prompt_sistema = {
        "role": "system",
        "content": (
            "Eres un asistente académico de nivel doctoral experto en Trabajo Social y Gestión Pública en Costa Rica.\n\n"
            "INSTRUCCIONES DE BÚSQUEDA Y RESPUESTA:\n"
            "1. Revisa primero este contexto extraído de nuestros documentos oficiales:\n"
            f"{contexto_dinamico}\n\n"
            "2. Si la respuesta está en los documentos, priorízala y cítala formalmente.\n"
            "3. Si la información local no es suficiente, complementa con tu conocimiento general institucional.\n"
            "4. Sé riguroso, ético y crítico. Mantén un enfoque alineado con los Derechos Humanos y la Democracia Participativa."
        )
    }
    
    # Limitar el historial enviado a la API a los últimos 4 mensajes para optimizar el consumo de tokens
    historial_reciente = st.session_state.messages[-4:]
    mensajes_para_api = [prompt_sistema] + historial_reciente + [{"role": "user", "content": user_query}]
    
    # Consulta al motor de inferencia de producción estable en Groq
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Reemplazo oficial estable y veloz con soporte streaming
                messages=mensajes_para_api,
                temperature=0.2,               # Temperatura baja para garantizar fidelidad académica
                stream=True                    # Habilitación de flujo de texto en tiempo real
            )
            
            # st.write_stream muestra el texto palabra por palabra conforme se genera
            answer = st.write_stream(stream)
            
            # 🔗 Inyección dinámica de validación jurídica externa (SINALEVI)
            if es_consulta_legal:
                query_codificado = urllib.parse.quote_plus(user_query)
                url_sinalevi = f"http://sinalevi.go.cr{query_codificado}"
                
                st.markdown("---")
                st.caption("⚖️ **Validación Jurídica en Tiempo Real (Costa Rica):**")
                st.info(
                    "Para asegurar que la norma consultada no haya sufrido reformas recientes, "
                    f"puedes verificar directamente los términos de tu consulta en el [Buscador del Sistema Nacional de Leyes Vigentes (SINALEVI)]({url_sinalevi} \"Búsqueda SINALEVI\")."
                )
            
            # Guardar la conversación real completa en el historial de sesión de Streamlit
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Error de comunicación: {e}")