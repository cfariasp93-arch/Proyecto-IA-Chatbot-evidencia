import json
import time
from collections import Counter
from pathlib import Path

from pipeline_limpieza import procesar_texto
from cliente import consultar_modelo


POLITICAS = """
Según Valdivieso y Marchetti (2019), los modelos de clasificación supervisada tienden a sobreajustarse cuando el conjunto de entrenamiento carece de diversidad semántica. Por su parte, Okonkwo-Reyes (2021) sostiene que la métrica F1 es más fiable que la exactitud en contextos con clases desbalanceadas, ya que equilibra precisión y exhaustividad. Sin embargo, Lindqvist y Tarasova (2020) advierten que ninguna métrica por sí sola captura la totalidad del rendimiento de un sistema. En una revisión posterior, Brandão et al. (2022) demostraron que combinar F1 con curvas ROC mejora la interpretación de los resultados. Finalmente, Haddad y Quispe-Navarro (2023) proponen evaluar siempre los modelos con validación cruzada para reducir el sesgo de muestreo.
"""

INSTRUCCION = f"""Eres un asistente que responde preguntas sobre un texto académico. Responde en español en una o dos oraciones, usando solo el texto dado. No inventes información ni autores. Si el texto no lo indica, responde que el caso requiere revisión.

Texto:
{POLITICAS}"""


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {"precision": precision, "cobertura": cobertura, "f1": f1}


def calcular_metricas(texto_referencia, texto_respuesta):
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)

    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)


casos = [
    ("¿Qué sostienen Valdivieso y Marchetti sobre los modelos supervisados?", "Sostienen que los modelos de clasificación supervisada tienden a sobreajustarse cuando el conjunto de entrenamiento carece de diversidad semántica."),
    ("¿En qué año publicaron Valdivieso y Marchetti su trabajo?", "Valdivieso y Marchetti publicaron su trabajo en 2019."),
    ("¿Cuándo tienden a sobreajustarse los modelos de clasificación supervisada?", "Tienden a sobreajustarse cuando el conjunto de entrenamiento carece de diversidad semántica."),
    ("¿Qué afirma Okonkwo-Reyes sobre la métrica F1?", "Okonkwo-Reyes afirma que la métrica F1 es más fiable que la exactitud en contextos con clases desbalanceadas."),
    ("¿En qué año se publicó el trabajo de Okonkwo-Reyes?", "El trabajo de Okonkwo-Reyes se publicó en 2021."),
    ("¿Por qué la métrica F1 es más fiable que la exactitud con clases desbalanceadas?", "Porque la métrica F1 equilibra precisión y exhaustividad."),
    ("¿Qué dos medidas equilibra la métrica F1?", "La métrica F1 equilibra precisión y exhaustividad."),
    ("¿Qué advierten Lindqvist y Tarasova?", "Advierten que ninguna métrica por sí sola captura la totalidad del rendimiento de un sistema."),
    ("¿En qué año advirtieron Lindqvist y Tarasova sobre las métricas?", "Lindqvist y Tarasova lo advirtieron en 2020."),
    ("¿Basta una sola métrica para evaluar un sistema?", "No, ninguna métrica por sí sola captura la totalidad del rendimiento de un sistema."),
    ("¿Qué demostraron Brandão et al. en su revisión?", "Demostraron que combinar F1 con curvas ROC mejora la interpretación de los resultados."),
    ("¿En qué año publicaron Brandão et al. su revisión?", "Brandão et al. publicaron su revisión en 2022."),
    ("¿Con qué se recomienda combinar F1 para interpretar mejor los resultados?", "Se recomienda combinar F1 con curvas ROC."),
    ("¿Qué proponen Haddad y Quispe-Navarro?", "Proponen evaluar siempre los modelos con validación cruzada para reducir el sesgo de muestreo."),
    ("¿Para qué sirve la validación cruzada según el texto?", "Sirve para reducir el sesgo de muestreo."),
    ("¿En qué año se publicó el trabajo de Haddad y Quispe-Navarro?", "El trabajo de Haddad y Quispe-Navarro se publicó en 2023."),
    ("¿Qué autor publicó primero, Valdivieso y Marchetti o Haddad y Quispe-Navarro?", "Valdivieso y Marchetti publicaron primero, en 2019, y Haddad y Quispe-Navarro en 2023."),
    ("¿Qué autores mencionan la métrica F1 de forma directa?", "Okonkwo-Reyes y Brandão et al. mencionan la métrica F1."),
    ("¿Qué dice el texto sobre el uso de redes neuronales profundas?", "El texto no lo indica, así que el caso requiere revisión."),
    ("¿Qué opina Fernández (2024) sobre la validación cruzada?", "No encuentro a ese autor en el texto, así que el caso requiere revisión."),
]


def guardar_resultados(resultados):
    with open("resultados_metricas.json", "w", encoding="utf-8") as archivo:
        json.dump(
            sorted(resultados, key=lambda r: r["f1"]),
            archivo,
            indent=2,
            ensure_ascii=False,
        )


def resumir_metricas(resultados):
    if not resultados:
        return {
            "precision_promedio": 0,
            "cobertura_promedio": 0,
            "f1_promedio": 0,
        }
    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    }


resultados = []

for consulta, referencia in casos:
    respuesta = consultar_modelo(consulta, system_instruction=INSTRUCCION)
    time.sleep(13)

    metricas = calcular_metricas(referencia, respuesta)

    print("Consulta:", consulta)
    print("Respuesta:", respuesta)
    print("Métricas:", metricas)

    resultados.append({
        "consulta": consulta,
        "respuesta": respuesta,
        **metricas,
    })
    guardar_resultados(resultados)

print("Promedios")
print(resumir_metricas(resultados))

ordenados = sorted(resultados, key=lambda r: r["f1"])


def mostrar(titulo, lista_casos):
    print(f"\n{titulo}")
    for i, c in enumerate(lista_casos, 1):
        print(
            f"{i}. F1={c['f1']:.3f} | "
            f"P={c['precision']:.3f} | C={c['cobertura']:.3f}"
        )
        print(f"   Consulta:  {c['consulta']}")
        print(f"   Respuesta: {c['respuesta']}")


mostrar("5 PEORES", ordenados[:5])
mostrar("5 MEJORES", ordenados[::-1][:5])