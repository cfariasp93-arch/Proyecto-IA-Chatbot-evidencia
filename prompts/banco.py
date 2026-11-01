"""
Banco de prompts de "Chatbot Evidencia".

Cada prompt tiene: nombre, system_instruction, ejemplo_usuario, claves_esperadas,
response_schema (estructura JSON esperada) y, opcionalmente, valores_esperados
(valores exactos que debería devolver el ejemplo, para medir también el contenido).

Los documentos son FICTICIOS a propósito (los mismos de la prueba de modelos):
así el modelo solo puede acertar leyendo el contexto, no con lo que ya sabe.
"""

DOCUMENTOS = [
    {
        "id": "D1",
        "titulo": "Evaluación del programa 'Aula Abierta' (Chile, 2021) [ficticio]",
        "texto": (
            "El programa instaló co-docencia entre profesor regular y profesor "
            "especialista en 45 escuelas básicas. Con un diseño cuasi-experimental, "
            "tras dos años se observó un aumento de 0,18 desviaciones estándar en "
            "lectura en estudiantes con necesidades educativas especiales. No hubo "
            "efecto significativo en matemática. Los mejores resultados se dieron en "
            "escuelas donde la pareja docente tuvo al menos 2 horas semanales de "
            "planificación conjunta."
        ),
    },
    {
        "id": "D2",
        "titulo": "Revisión sistemática sobre Diseño Universal para el Aprendizaje, DUA (2022) [ficticio]",
        "texto": (
            "Revisión de 23 estudios en educación básica. El efecto promedio sobre la "
            "participación en clase fue positivo (0,25 desviaciones estándar). La "
            "evidencia sobre logros de aprendizaje a largo plazo es limitada. La mayoría "
            "de los estudios se realizó en países de ingresos altos. Los programas que "
            "incluyeron al menos 40 horas de capacitación docente mostraron mayores efectos."
        ),
    },
    {
        "id": "D3",
        "titulo": "Informe del programa 'Tutores Pares' (Colombia, 2020) [ficticio]",
        "texto": (
            "Tutoría entre pares evaluada con un ensayo controlado aleatorizado en 30 "
            "colegios rurales. La comprensión lectora mejoró 0,12 desviaciones estándar. "
            "El ausentismo de estudiantes con discapacidad bajó 10%. El costo fue de "
            "USD 35 por estudiante al año."
        ),
    },
]


def _documentos_texto():
    return "\n\n".join(f"[{d['id']}] {d['titulo']}\n{d['texto']}" for d in DOCUMENTOS)


def _con_documentos(etiqueta, contenido):
    """Entrada de usuario = documentos recuperados + la pregunta o afirmación."""
    return f"DOCUMENTOS DISPONIBLES:\n{_documentos_texto()}\n\n{etiqueta}:\n{contenido}"


BANCO_DE_PROMPTS = [
    # 1. Núcleo de la app: responder con evidencia citada, o decir que no hay información
    {
        "nombre": "responder_con_evidencia",
        "system_instruction": (
            "Eres el asistente de 'Chatbot Evidencia', que ayuda a investigadores y "
            "tomadores de decisiones a encontrar programas o políticas que han funcionado "
            "en otros contextos. El tema documentado es: prácticas pedagógicas inclusivas. "
            "Responde SOLO con la información de los DOCUMENTOS DISPONIBLES, sin usar "
            "conocimiento externo, y cita en la respuesta el id de cada documento usado "
            "entre corchetes, por ejemplo [D1]. Si los documentos no contienen la respuesta "
            "o la pregunta es de otro tema, usa el estado 'sin_informacion', di brevemente "
            "que no tienes esa información y deja 'fuentes' vacía. No agregues "
            "justificaciones que no estén en los documentos. Escribe en español, de forma "
            "clara y precisa. Responde únicamente con un JSON con las claves 'estado' "
            "('respondida' o 'sin_informacion'), 'respuesta' (texto) y 'fuentes' "
            "(lista con los ids de los documentos citados)."
        ),
        "ejemplo_usuario": _con_documentos(
            "PREGUNTA DEL USUARIO",
            "¿Qué efecto tuvo la co-docencia en el programa Aula Abierta y bajo qué "
            "condiciones funcionó mejor?",
        ),
        "claves_esperadas": ["estado", "respuesta", "fuentes"],
        "valores_esperados": {"estado": "respondida"},
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "estado": {"type": "STRING", "enum": ["respondida", "sin_informacion"]},
                "respuesta": {"type": "STRING"},
                "fuentes": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["estado", "respuesta", "fuentes"],
        },
    },
    # 2. Filtro previo a la búsqueda: ¿está en el alcance? ¿qué tipo de consulta es?
    {
        "nombre": "clasificar_consulta",
        "system_instruction": (
            "Clasificas las consultas que recibe 'Chatbot Evidencia', cuyo tema documentado "
            "es: prácticas pedagógicas inclusivas. Responde únicamente con un JSON con las "
            "claves 'dentro_del_alcance' (true si la consulta trata sobre prácticas "
            "pedagógicas inclusivas o su evidencia, false si no), 'tipo_consulta' ('efecto', "
            "'costo', 'condiciones_de_exito', 'comparacion' u 'otro') y 'palabras_clave' "
            "(lista de 2 a 5 términos en español para buscar en los documentos)."
        ),
        "ejemplo_usuario": "¿Cuánto cuesta implementar tutoría entre pares en colegios rurales?",
        "claves_esperadas": ["dentro_del_alcance", "tipo_consulta", "palabras_clave"],
        "valores_esperados": {"dentro_del_alcance": True, "tipo_consulta": "costo"},
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "dentro_del_alcance": {"type": "BOOLEAN"},
                "tipo_consulta": {
                    "type": "STRING",
                    "enum": ["efecto", "costo", "condiciones_de_exito", "comparacion", "otro"],
                },
                "palabras_clave": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["dentro_del_alcance", "tipo_consulta", "palabras_clave"],
        },
    },
    # 3. Alimentar la base de conocimiento: extraer una ficha de un documento
    {
        "nombre": "extraer_ficha_programa",
        "system_instruction": (
            "Extraes datos de un fragmento de documento sobre un programa o política "
            "educativa. Usa solo lo que dice el texto; si un dato no aparece, escribe "
            "'No informado'. Responde únicamente con un JSON con las claves 'programa', "
            "'pais', 'diseno_evaluacion', 'resultado_principal' y 'condiciones_de_exito', "
            "todas con texto."
        ),
        "ejemplo_usuario": f"[{DOCUMENTOS[0]['id']}] {DOCUMENTOS[0]['titulo']}\n{DOCUMENTOS[0]['texto']}",
        "claves_esperadas": [
            "programa", "pais", "diseno_evaluacion", "resultado_principal", "condiciones_de_exito",
        ],
        "valores_esperados": {"pais": "Chile"},
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "programa": {"type": "STRING"},
                "pais": {"type": "STRING"},
                "diseno_evaluacion": {"type": "STRING"},
                "resultado_principal": {"type": "STRING"},
                "condiciones_de_exito": {"type": "STRING"},
            },
            "required": [
                "programa", "pais", "diseno_evaluacion", "resultado_principal", "condiciones_de_exito",
            ],
        },
    },
    # 4. Resistencia a premisas falsas: contrastar una afirmación con los documentos
    {
        "nombre": "verificar_afirmacion",
        "system_instruction": (
            "Contrastas una afirmación del usuario con los DOCUMENTOS DISPONIBLES, sin usar "
            "conocimiento externo. Responde únicamente con un JSON con las claves 'veredicto' "
            "('respalda' si los documentos confirman la afirmación, 'contradice' si sus datos "
            "difieren de los documentos, 'sin_informacion' si los documentos no tratan el "
            "tema), 'explicacion' (texto breve en español que cita el id del documento entre "
            "corchetes, por ejemplo [D3]) y 'fuentes' (lista con los ids citados, vacía si no "
            "hay información)."
        ),
        "ejemplo_usuario": _con_documentos(
            "AFIRMACIÓN DEL USUARIO",
            "El programa Tutores Pares logró una mejora de 40% en comprensión lectora.",
        ),
        "claves_esperadas": ["veredicto", "explicacion", "fuentes"],
        "valores_esperados": {"veredicto": "contradice"},
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "veredicto": {"type": "STRING", "enum": ["respalda", "contradice", "sin_informacion"]},
                "explicacion": {"type": "STRING"},
                "fuentes": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["veredicto", "explicacion", "fuentes"],
        },
    },
]