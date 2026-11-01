"""
Prueba de consistencia del banco de prompts de "Chatbot Evidencia".

Ejecuta cada prompt del banco varias veces contra la API real, intenta interpretar
cada respuesta como JSON con la estructura esperada y guarda el resultado en
prompts/registro_resultados.json (junto a este archivo).

Ejecutar desde la raíz del proyecto, con el venv activo:
    python -m prompts.test_consistencia
"""

import json
import sys
import time
from pathlib import Path

# La raíz del proyecto debe estar en el path para poder importar src/consumir_gemini.py
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import consumir_gemini

try:
    from .banco import BANCO_DE_PROMPTS
except ImportError:  # ejecución directa como script
    from banco import BANCO_DE_PROMPTS

MODELO_BANCO = "gemini-3.1-flash-lite"   # el modelo elegido en la ficha de arquitectura
REPETICIONES = 5                          # el mínimo de la actividad es 3
PAUSA = 5                                 # segundos entre llamadas (límite gratuito: 15 por minuto)
REINTENTOS_SERVICIO = 2                   # reintentos si la API responde 429 / 503
RUTA_REGISTRO = Path(__file__).resolve().parent / "registro_resultados.json"

TIPOS_SIMPLES = {"STRING": str, "BOOLEAN": bool, "ARRAY": list, "OBJECT": dict}


def validar(valor, schema):
    """Devuelve None si el valor cumple el schema, o un texto con el problema."""
    tipo = schema["type"]
    if tipo in ("NUMBER", "INTEGER"):
        permitido = (int,) if tipo == "INTEGER" else (int, float)
        if isinstance(valor, bool) or not isinstance(valor, permitido):
            return f"se esperaba {tipo}"
    elif not isinstance(valor, TIPOS_SIMPLES[tipo]):
        return f"se esperaba {tipo}"
    if "enum" in schema and valor not in schema["enum"]:
        return f"valor {valor!r} fuera de {schema['enum']}"
    if tipo == "OBJECT":
        for clave in schema.get("required", []):
            if clave not in valor:
                return f"falta la clave '{clave}'"
        for clave, sub in schema.get("properties", {}).items():
            if clave in valor:
                problema = validar(valor[clave], sub)
                if problema:
                    return f"'{clave}': {problema}"
    if tipo == "ARRAY":
        for i, item in enumerate(valor):
            problema = validar(item, schema["items"])
            if problema:
                return f"elemento {i}: {problema}"
    return None


def llamar_modelo(prompt):
    """Una petición real. Reintenta si la API falla por cuota o demanda."""
    ultimo_error = ""
    for n in range(REINTENTOS_SERVICIO + 1):
        try:
            url, body = consumir_gemini.armar_peticion(
                prompt["ejemplo_usuario"],
                modelo=MODELO_BANCO,
                system_instruction=prompt["system_instruction"],
                response_schema=prompt.get("response_schema"),
            )
            respuesta = consumir_gemini.enviar_peticion(url, body)
            return consumir_gemini.extraer_texto(respuesta)
        except RuntimeError as error:
            ultimo_error = str(error)
            if "per day" in ultimo_error or n == REINTENTOS_SERVICIO:
                break  # cuota diaria agotada, o se acabaron los reintentos
            espera = 30 if "quota" in ultimo_error.lower() else 10
            print(f"  error de servicio, reintento en {espera} s: {ultimo_error[:90]}")
            time.sleep(espera)
    raise RuntimeError(ultimo_error)


def main():
    registro = {}

    for prompt in BANCO_DE_PROMPTS:
        exitos = fallos_formato = errores_servicio = contenido_ok = 0
        print(f"\n=== {prompt['nombre']} ({MODELO_BANCO}) ===")

        for intento in range(1, REPETICIONES + 1):
            try:
                texto = llamar_modelo(prompt)
            except RuntimeError as error:
                # Un error de la API no es un fallo del prompt: se cuenta aparte
                errores_servicio += 1
                print(f"  intento {intento}: error de servicio (no cuenta como fallo): {str(error)[:120]}")
                time.sleep(PAUSA)
                continue

            try:
                datos = consumir_gemini.parsear_respuesta_json(texto)
                faltan = [c for c in prompt["claves_esperadas"] if c not in datos]
                if faltan:
                    raise ValueError(f"faltan claves: {faltan}")
                if prompt.get("response_schema"):
                    problema = validar(datos, prompt["response_schema"])
                    if problema:
                        raise ValueError(f"estructura incorrecta, {problema}")
            except ValueError as error:
                fallos_formato += 1
                print(f"  intento {intento} falló: {error}")
            else:
                exitos += 1
                esperados = prompt.get("valores_esperados", {})
                distintos = {k: datos.get(k) for k, v in esperados.items() if datos.get(k) != v}
                if distintos:
                    print(f"  intento {intento}: JSON válido, pero contenido distinto al esperado: {distintos}")
                else:
                    contenido_ok += 1
            time.sleep(PAUSA)

        medidos = REPETICIONES - errores_servicio
        print(f"{prompt['nombre']}: {exitos}/{medidos} respuestas válidas "
              f"({contenido_ok} con el contenido esperado, {errores_servicio} errores de servicio)")
        registro[prompt["nombre"]] = {
            "exitos": exitos,
            "intentos": medidos,
            "fallos_formato": fallos_formato,
            "errores_servicio": errores_servicio,
            "contenido_esperado": contenido_ok,
            "modelo": MODELO_BANCO,
        }

    RUTA_REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_REGISTRO, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)
    print(f"\nRegistro guardado en: {RUTA_REGISTRO}")

    poco_consistentes = [n for n, r in registro.items() if r["intentos"] and r["exitos"] / r["intentos"] < 2 / 3]
    if poco_consistentes:
        print(f"Atención: por debajo de 2/3 de respuestas válidas -> {poco_consistentes}. "
              "Ajusta su prompt, vuelve a correr la prueba y documenta el cambio.")


if __name__ == "__main__":
    main()