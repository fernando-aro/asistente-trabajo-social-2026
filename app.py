# [ ... Código anterior idéntico: configuración, API key y lectura del archivo .txt ... ]

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
