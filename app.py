import streamlit as st
from openai import OpenAI
import os
import glob

# 1. Interfaz
st.set_page_config(page_title="Asistente TS 2026", page_icon="⚖️", layout="centered")
st.title("🤖 Asistente Virtual: Ponencia Trabajo Social 2026")
st.subheader("Consultas basadas en Max-Neef, Ley 8364 y Democracia Participativa")

# 2. Credenciales
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://groq.com")

# 3. Buscador Ampliado Multi-archivo
@st.cache_data
def escanear_todos_los_contextos(consulta_usuario, max_bloques=8):
    """
    Busca palabras clave en TODOS los archivos .txt de la carpeta.
    Prioriza las coincidencias exactas para armar el mejor contexto posible.
    """
    archivos = glob.glob("*.txt")
    if not archivos:
        return "No se encontraron archivos de contexto (.txt)."

    palabras_clave = [p.lower() for p in consulta_usuario.split() if len(p) > 3]
    bloques_encontrados = []

    for ruta_archivo in archivos:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            # Dividir por líneas o bloques separados por doble espacio
            contenido = f.read()
            parrafos = [p.strip() for p in contenido.split("\n\n") if len(p.strip()) > 30]
            
            for parrafo in parrafos:
                # Calcular relevancia
                coincidencias = sum(1 for p in palabras_clave if p in parrafo.lower())
                if coincidencias > 0:
                    bloques_encontrados.append((coincidencias, f"[{ruta_archivo}]: {parrafo}"))

    # Ordenar de mayor a menor coincidencia
    bloques_encontrados.sort(key=lambda x: x[0], reverse=True)
    
    if bloques_encontrados:
        return "\n\n---\n\n".join([b[1] for b in bloques_encontrados[:max_bloques]])
    
    # Fallback: Si no hay palabras clave que coincidan, enviar fragmentos generales iniciales
    return "No se encontraron coincidencias específicas en los documentos. Responde usando tu conocimiento general en Trabajo Social."

# 4. Historial de Chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "¡Hola! Estoy listo. He cargado tus documentos base de Costa Rica, la Ley 8364 y Max-Neef. ¿Qué deseas consultar?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

import urllib.parse  # Requerido para codificar los caracteres de la consulta en la URL

# ... (Mantener las secciones 1, 2, 3 y 4 del script multi-archivo anterior) ...

# 5. Interacción del usuario y procesamiento
if user_query := st.chat_input("Escribe tu consulta aquí..."):
    with st.chat_message("user"):
        st.write(user_query)
    
    # 🔍 DETECCIÓN JURÍDICA: Verificar si la consulta pide leyes, artículos o normativas de Costa Rica
    conceptos_legales = ["ley", "articulo", "constitución", "decreto", "reforma", "normativa", "8364", "artí"]
    es_consulta_legal = any(palabra in user_query.lower() for palabra in conceptos_legales)
    
    # Buscar primero coincidencias locales en tus archivos .txt cargados
    contexto_dinamico = escanear_todos_los_contextos(user_query)
    
    prompt_sistema = {
        "role": "system",
        "content": (
            "Eres un asistente académico de nivel doctoral experto en Trabajo Social y Gestión Pública en Costa Rica.\n\n"
            "INSTRUCCIONES DE BÚSQUEDA Y RESPUESTA:\n"
            "1. Revisa primero este contexto extraído de nuestros documentos oficiales:\n"
            f"{contexto_dinamico}\n\n"
            "2. Si la respuesta está en los documentos, priorízala y cítala formalmente.\n"
            "3. Si la información no es suficiente, complementa con tu conocimiento general institucional.\n"
            "4. Sé riguroso, ético y crítico. Si el usuario te pregunta por leyes vigentes, recuérdale "
            "amablemente verificar la última versión publicada en el diario oficial La Gaceta o SINALEVI."
        )
    }
    
    historial_reciente = st.session_state.messages[-4:]
    mensajes_para_api = [prompt_sistema] + historial_reciente + [{"role": "user", "content": user_query}]
    
    with st.chat_message("assistant"):
        try:
            # 1. Generar respuesta del LLM en tiempo real
            stream = client.chat.completions.create(
                        try:
            # CORRECCIÓN: Cambiar a un identificador 100% activo en el endpoint de Groq
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Modelo estable, veloz y con soporte total de streaming
                messages=mensajes_para_api,
                temperature=0.2,
                stream=True
            )
            
            # Renderizar respuesta fluida
            answer = st.write_stream(stream)
            
            # (El resto del código de guardado en st.session_state se mantiene igual)
                messages=mensajes_para_api,
                temperature=0.2,
                stream=True
            )
            answer = st.write_stream(stream)
            
            # 2. Inyección dinámica del validador SINALEVI si la consulta es de orden jurídico
            if es_consulta_legal:
                # Limpiar y formatear la consulta para construir un query string seguro para la URL
                query_codificado = urllib.parse.quote_plus(user_query)
                # URL base de búsqueda por texto libre en el Sistema Nacional de Leyes Vigentes de Costa Rica
                url_sinalevi = f"http://sinalevi.go.cr{query_codificado}"
                
                st.markdown("---")
                st.caption("⚖️ **Validación Jurídica en Tiempo Real (Costa Rica):**")
                st.info(
                    "Para asegurar que la norma consultada no haya sufrido reformas recientes, "
                    f"puedes verificar directamente los términos de tu consulta en el [Buscador del Sistema Nacional de Leyes Vigentes (SINALEVI)]({url_sinalevi} \"Búsqueda SINALEVI\")."
                )
            
            # Guardar la interacción en el historial interno
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Error de comunicación: {e}")