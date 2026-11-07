# Límites de la métrica de evaluación

## Qué mide

La métrica compara las palabras de una respuesta con una referencia, contando repeticiones después de limpiar y tokenizar ambos textos. Reporta precisión, cobertura y F1.

En la corrida revisada (20 casos) los promedios fueron: precisión 0.592, cobertura 0.943 y F1 0.709. La cobertura es alta y la precisión es baja de forma sistemática: el modelo casi siempre incluye lo que dice la referencia, pero agrega palabras que la referencia no tiene.

## Modos de falla conocidos

* **Penaliza respuestas correctas que dicen más de lo preguntado.** Caso: 9, "¿En qué año advirtieron Lindqvist y Tarasova sobre las métricas?". Referencia: "Lindqvist y Tarasova lo advirtieron en 2020." Respuesta: "Lindqvist y Tarasova advirtieron en el año 2020 que ninguna métrica por sí sola captura la totalidad del rendimiento de un sistema." F1: 0.414 (precisión 0.273, cobertura 0.857). Hallazgo: al leerla, la respuesta es correcta: da el año 2020 y repite fielmente la advertencia del texto. Es el puntaje más bajo de los 20 porque solo 6 de sus 22 tokens aparecen en la referencia. En cambio, el caso 2, una pregunta de año igual de bien respondida pero con respuesta corta, obtiene 0.889. La diferencia de casi 0.47 puntos refleja la longitud de la respuesta, no su calidad.

* **Penaliza el encuadre de la respuesta (repetir la pregunta, citar la fuente, "en el año").** Caso: 13, "¿Con qué se recomienda combinar F1 para interpretar mejor los resultados?". Referencia: "Se recomienda combinar F1 con curvas ROC." Respuesta: "Según Brandão et al. (2022), se recomienda combinar la métrica F1 con curvas ROC para mejorar la interpretación de los resultados." F1: 0.500 (precisión 0.333, cobertura 1.0). Hallazgo: toda la referencia está contenida en la respuesta y la atribución a Brandão et al. (2022) es correcta, pero 14 de sus 21 tokens son adicionales. El caso 6 muestra lo mismo: la respuesta repite la pregunta y añade "según sostiene Okonkwo-Reyes (2021)", con cobertura 1.0, precisión 0.32 y F1 0.485. Incluso frases mínimas pesan: las respuestas de los casos 2 y 12 son idénticas a su referencia salvo por "el año" y quedan en 0.889 en vez de 1.0.

* **El puntaje depende de la calidad de la referencia, no de lo que dice el texto.** Caso: 15, "¿Para qué sirve la validación cruzada según el texto?". Referencia: "Sirve para reducir el sesgo de muestreo." Respuesta: "Según el texto, la validación cruzada sirve para evaluar los modelos y reducir el sesgo de muestreo." F1: 0.583 (precisión 0.412, cobertura 1.0). Hallazgo: el texto dice que Haddad y Quispe-Navarro proponen "evaluar siempre los modelos con validación cruzada para reducir el sesgo de muestreo", así que la respuesta es correcta y más completa que la referencia. La métrica la trata como exceso porque solo mide parecido con la referencia. Una referencia incompleta castiga a la mejor respuesta.

* **No distingue una paráfrasis imprecisa de un exceso inocuo.** Caso: 10, "¿Basta una sola métrica para evaluar un sistema?". Referencia: "No, ninguna métrica por sí sola captura la totalidad del rendimiento de un sistema." Respuesta: "No, según Lindqvist y Tarasova (2020), ninguna métrica por sí sola captura la totalidad del rendimiento de un sistema. Por ello, investigaciones como la de Brandão et al. (2022) sugieren combinar distintas métricas para mejorar la interpretación de los resultados." F1: 0.519 (precisión 0.350, cobertura 1.0). Hallazgo: la primera oración es correcta. La segunda generaliza a Brandão et al.: el texto dice que combinar F1 con curvas ROC mejora la interpretación, no que se combinen "distintas métricas" en general. Es la única imprecisión de contenido de la muestra y el F1 no la señala: queda en 0.519, en la misma banda que los casos 6 (0.485), 13 (0.500) y 15 (0.583), que son correctos. La cobertura de 1.0 tampoco dice nada sobre la afirmación añadida.

* **Una respuesta perfecta no llega a 1.0, así que no sirve un umbral absoluto.** Caso: 1, "¿Qué sostienen Valdivieso y Marchetti sobre los modelos supervisados?". Referencia: "Sostienen que los modelos de clasificación supervisada tienden a sobreajustarse cuando el conjunto de entrenamiento carece de diversidad semántica." Respuesta: "Valdivieso y Marchetti sostienen que los modelos de clasificación supervisada tienden a sobreajustarse cuando el conjunto de entrenamiento carece de diversidad semántica." F1: 0.927 (precisión 0.864, cobertura 1.0). Hallazgo: es el mejor puntaje de los 20 y la respuesta es correcta y completa, pero la única diferencia con la referencia es que nombra el sujeto. Los cinco F1 más altos (0.889 a 0.927) son respuestas correctas y cortas. Los cinco más bajos (0.414 a 0.583) también son correctos, salvo la imprecisión del caso 10. Con respuestas correctas repartidas entre 0.41 y 0.93, un corte de aprobado/reprobado no discrimina calidad.


## Muestra revisada

Se revisaron 10 casos de un conjunto de 20 respuestas generadas con consultar_modelo.
La muestra combina los cinco F1 más bajos y los cinco más altos.
Casos revisados: 1, 2, 6, 9, 10, 12, 13, 14, 15, 16 (numerados según su posición en la lista `casos`). Fecha de revisión: 7 de noviembre de 2026.
Se aplicó la rúbrica de corrección factual, completitud y contradicción, con una justificación por caso.

| Caso | F1 | Corrección factual | Completitud | Contradicción | Justificación |
|---|---|---|---|---|---|
| 9 | 0.414 | Correcta | Completa | No | El año 2020 coincide con el texto y la advertencia añadida es una paráfrasis fiel. |
| 6 | 0.485 | Correcta | Completa | No | Explica el motivo (equilibra precisión y exhaustividad) y atribuye bien a Okonkwo-Reyes (2021). |
| 13 | 0.500 | Correcta | Completa | No | Indica curvas ROC y atribuye bien a Brandão et al. (2022). |
| 10 | 0.519 | Parcial | Completa | No contradice, pero generaliza | La primera oración es fiel; la segunda convierte "F1 con curvas ROC" en "distintas métricas". |
| 15 | 0.583 | Correcta | Completa (más que la referencia) | No | Incluye "evaluar los modelos", que el texto sí dice. |
| 1 | 0.927 | Correcta | Completa | No | Reproduce el contenido del texto; solo agrega el sujeto. |
| 16 | 0.909 | Correcta | Completa | No | El año 2023 coincide con el texto. |
| 14 | 0.903 | Correcta | Completa | No | Reproduce la propuesta de validación cruzada y el motivo. |
| 12 | 0.889 | Correcta | Completa | No | El año 2022 coincide con el texto. |
| 2 | 0.889 | Correcta | Completa | No | El año 2019 coincide con el texto. |

Resultado de la rúbrica: 9 de 10 respuestas son plenamente correctas y una (caso 10) es parcialmente imprecisa. Ninguna omite información pedida ni contradice el texto.

## Recomendación de uso

**Para qué sirve.** Es útil para comparar dos versiones del pipeline (otra `INSTRUCCION`, otro modelo) sobre los mismos 20 casos y las mismas referencias: si cambia el promedio, cambió la longitud o el contenido de las respuestas. También sirve para ordenar la lectura, empezando por los F1 más bajos. En esta corrida la debilidad es la precisión (0.592 frente a una cobertura de 0.943), así que la comparación más informativa sería probar si una instrucción que pida responder solo lo preguntado, sin repetir la pregunta ni citar autores, sube la precisión sin bajar la cobertura. Es una hipótesis por comprobar, no un resultado. No conviene usar el F1 como criterio de aprobado/reprobado.

**Qué necesita revisión humana.**

* Respuestas con precisión baja y cobertura alta. En la muestra, los cinco casos con precisión menor a 0.5 (9, 6, 13, 10 y 15) tenían cobertura de 0.857 o más: la respuesta contiene la referencia y agrega texto. Hay que leer lo agregado, porque ahí estaba el único error de contenido (caso 10) y los otros cuatro eran correctos.
* Respuestas que citan autores o años que la pregunta no pidió. Verificarlas contra el texto fuente, como en el caso 10.
* Respuestas de tipo "requiere revisión". Fuera de la muestra revisada, los casos 19 y 20 obtuvieron F1 0.643 cada uno: el modelo respondió como se le pidió, pero el puntaje queda en rango medio. Conviene evaluarlas con una regla (aparece o no la frase "requiere revisión") y no con F1.
* Preguntas de sí/no. Revisar la polaridad a mano, porque la métrica no la detecta.
* Cobertura baja. Fuera de la muestra, el caso 5 tiene cobertura 0.75 y F1 0.667 solo porque el modelo dijo "fue publicado" en lugar de "se publicó". Antes de asumir que falta información, comprobar si es una paráfrasis.
