import streamlit as st
from groq import Groq
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

# 2. Conexión segura con la API Key
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ No se encontró la API Key. Configúrala como GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. Inicialización del cliente NATIVO de Groq
client = Groq(api_key=api_key)

# 4. Buscador inteligente de texto restringido para Planes Gratuitos (Anti Error 413/429)
@st.cache_data
def escanear_todos_los_contextos(consulta_usuario, max_bloques=2):
    """
    Busca palabras clave en TODOS los archivos .txt de la carpeta.
    Extrae los fragmentos más específicos para enviárselos al modelo de IA.
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
                if  coincidencias > 0:
                    bloques_encontrados.append((coincidencias, f"[{ruta_archivo}]: {parrafo}"))

    # Ordenar de mayor a menor coincidencia
    bloques_encontrados.sort(key=lambda x: x, reverse=True)
    
    if bloques_encontrados:
        textos_filtrados = [b for a, b in bloques_encontrados[:max_bloques]]
        return "\n\n---\n\n".join(textos_filtrados)
    
    return f"Los documentos locales actuales no contienen datos explícitos para la consulta: '{consulta_usuario}'."

# 5. Inicialización del historial de chat
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

# 6. Renderizar el historial de conversación
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
            "Eres un asistente académico experto en Trabajo Social y Legislación en Costa Rica.\n\n"
            "INSTRUCCIONES DE FIDELIDAD TEXTUAL:\n"
            "1. Analiza este contenido extraído de tus archivos locales:\n"
            f"{contexto_dinamico}\n\n"
            "2. Responde basándote prioritariamente en los datos anteriores. Si el contexto indica explícitamente "
            "que la información no está en los archivos locales, indícalo amablemente y procede a responder de forma concisa "
            "haciendo uso de tus conocimientos generales actualizados sobre el marco legal de Costa Rica.\n"
            "3. Mantén la respuesta compacta y precisa."
        )
    }
    
    historial_reciente = st.session_state.messages[-2:]
    mensajes_para_api = [prompt_sistema] + historial_reciente + [{"role": "user", "content": user_query}]
    
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="qwen/qwen3.8-27b",  
                messages=mensajes_para_api,
                temperature=0.2,  
                max_tokens=600,     
                stream=True                    
            )
            
            # CORRECCIÓN DEFINITIVA INTERNA: Extracción híbrida Segura (Objeto o Diccionario)
            def generar_respuesta():
                for chunk in stream:
                    if hasattr(chunk, 'choices') and chunk.choices:
                        # Extraer el primer elemento de la lista choices
                        choice = chunk.choices[0]
                        
                        # Manejo seguro si es un objeto con atributos o diccionario
                        if hasattr(choice, 'delta'):
                            delta = choice.delta
                            if hasattr(delta, 'content') and delta.content:
                                yield delta.content
                        elif isinstance(choice, dict) and 'delta' in choice:
                            delta = choice['delta']
                            if isinstance(delta, dict) and 'content' in delta and delta['content']:
                                yield delta['content']

            answer = st.write_stream(generar_respuesta())
            
            # Inyección limpia del enlace jurídico corregido
            if es_consulta_legal:
                query_codificado = urllib.parse.quote_plus(user_query)
                url_sinalevi = f"https://google.com+{query_codificado}"
                
                st.markdown("---")
                st.caption("⚖️ **Validación Jurídica Oficial (Costa Rica):**")
                st.link_button(
                    label="🔍 Verificar actualizaciones en SINALEVI",
                    url=url_sinalevi,
                    use_container_width=True
                )
            
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Error de comunicación: {e}")