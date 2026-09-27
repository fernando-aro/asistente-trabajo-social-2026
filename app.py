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

# Base de conocimiento estricta inyectada (Blindaje contra alucinaciones)
CONOCIMIENTO_BLINDADO = """
CONOCIMIENTO JURÍDICO OFICIAL DE COSTA RICA:
- Ley N° 8364 (Año 2003): Es la Ley de Reforma Constitucional del Artículo 9 de la Constitución Política de Costa Rica. Su único y principal objetivo histórico fue incorporar de forma explícita el concepto de "participativo" a la definición del Gobierno de la República.
- Artículo 9 de la Constitución Política (Texto Vigente): "El Gobierno de la República es popular, representativo, participativo, alternativo y responsable. Lo ejercen tres Poderes distintos e independientes entre sí: el Legislativo, el Ejecutivo y el Judicial. Ninguno de los Poderes puede delegar el ejercicio de funciones que le son propias..."
- Relación con Trabajo Social 2026: Esta reforma constitucional dota de un blindaje y fundamento jurídico de rango constitucional a todas las propuestas de Democracia Participativa, auditoría ciudadana, presupuestos participativos y al Modelo del Órgano Colegiado propuesto para la ponencia.
"""

# 4. Buscador inteligente de archivos locales
@st.cache_data
def escanear_todos_los_contextos(consulta_usuario, max_bloques=2):
    archivos = glob.glob("*.txt")
    if not archivos:
        return "No se encontraron archivos de contexto (.txt) locales adicionales."

    palabras_clave = [p.lower() for p in consulta_usuario.split() if len(p) > 3]
    bloques_encontrados = []

    for ruta_archivo in archivos:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            parrafos = [p.strip() for p in contenido.split("\n\n") if len(p.strip()) > 30]
            
            for parrafo in parrafos:
                coincidencias = sum(1 for p in palabras_clave if p in parrafo.lower())
                if coincidencias > 0:
                    bloques_encontrados.append((coincidencias, f"[{ruta_archivo}]: {parrafo}"))

    bloques_encontrados.sort(key=lambda x: x[0], reverse=True)
    
    if bloques_encontrados:
        textos_filtrados = [b for a, b in bloques_encontrados[:max_bloques]]
        return "\n\n---\n\n".join(textos_filtrados)
    
    return "No se encontraron coincidencias específicas en los documentos locales."

# 5. Inicialización del historial de chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": (
                "¡Hola! El asistente de tu ponencia está listo. "
                "Puedes consultar con total seguridad sobre la Ley 8364, el Artículo 9 de la Constitución, "
                "la Teoría de Max-Neef o el Modelo de Órgano Colegiado. ¿Qué deseas analizar hoy?"
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
            "INSTRUCCIONES DE VERACIDAD ABSOLUTA:\n"
            "1. Utiliza obligatoriamente esta base de conocimiento verídica:\n"
            f"{CONOCIMIENTO_BLINDADO}\n\n"
            "2. Complementa únicamente con la información extraída de los archivos locales si es oportuno:\n"
            f"{contexto_dinamico}\n\n"
            "3. Si te preguntan por la Ley 8364, aclara firmemente que es la Reforma Constitucional que añadió el término 'participativo' al Artículo 9 de la Constitución Política. No inventes ninguna relación con la Defensoría de los Habitantes.\n"
            "4. Responde de forma resumida, directa y técnica."
        )
    }
    
    historial_reciente = st.session_state.messages[-2:]
    mensajes_para_api = [prompt_sistema] + historial_reciente + [{"role": "user", "content": user_query}]
    
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="qwen/qwen3.8-27b",  
                messages=mensajes_para_api,
                temperature=0.0,  # Temperatura en 0.0 para evitar cualquier asomo de invención o alucinación
                max_tokens=500,     
                stream=True                    
            )
            
            def generar_respuesta():
                for chunk in stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield delta.content

            answer = st.write_stream(generar_respuesta())
            
            if es_consulta_legal:
                st.markdown("---")
                st.caption("⚖️ **Validación Jurídica Oficial (Costa Rica):**")
                st.info(
                    "Para asegurar que la norma consultada no haya sufrido reformas recientes, "
                    "puedes verificar las últimas actualizaciones oficiales directamente en el portal del SCIJ."
                )
                # URL raíz segura de SINALEVI que elude todas las restricciones del navegador
                st.link_button(
                    label="🔗 Abrir Buscador del Sistema Nacional de Leyes Vigentes (SINALEVI)",
                    url="https://sinalevi.go.cr/",
                    use_container_width=True
                )
            
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Error de comunicación: {e}")