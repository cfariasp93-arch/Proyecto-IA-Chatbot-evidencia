#El nombre de la estudiante
#La calificación del curso
#El titulo de la segunda tarea
#Si la primera tarea está completada
estudiante = {
    "nombre": "Ana",
    "edad": 24,
    "curso": {
        "nombre": "Python",
        "calificacion": 92
    },
    "tareas": [
        {
            "titulo": "Variables",
            "completada": true
        },
        {
            "titulo": "Consumo de APIs",
            "completada": false
        }
    ]
}

print(Nombre, Calificacion, titulo [1], completada  )

print(estudiantes["nombre"])

print(estudiantes["curso"]["calificacion"])

print(estudiantes["tareas"][1]["titulo"])

print(estudiantes["tareas"][0]["completada"])

if estudiantes["tareas"][0]["completada"]:
    print("La primera tarea esta completada")
    

print("La primera tarea está completada?", "Sí" if estudiante["tareas"][0]["completada"] else "No esta")



