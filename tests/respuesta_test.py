from flask import Flask, request, jsonify
import sys
from moral_compass import hora_actual, convertir_dia, bloques_libres, tareas_basicas, planificar_tareas
import datetime


def respuesta(data):
    dia_raw, hora_now = hora_actual()
    dia_raw = dia_raw.lower()
    dia = convertir_dia(dia_raw) # "domingo" #
    hora_now = 10.10  # Hora actual en formato decimal (19:01)
    
    bloques = bloques_libres(dia, hora_now)
    
    data = request.get_json()
    
    respuestas = {
        "message_tareas": "",
        "message_plan_4_today": "",
        "plan_today": ""
        }
    tareas = tareas_basicas(data)
    if not tareas:
        print("No se han registrado tareas.")
        respuestas['message_tareas'] = "No se han registrado tareas."
        return jsonify(respuestas)

    plan = planificar_tareas(tareas, bloques)

    print("\n✅ Plan sugerido para hoy:")
    respuestas['message_plan_4_today'] = "✅ Plan sugerido para hoy:"
    for hora, tarea in plan:
        h = int(hora)
        m = int((hora - h) * 60)
        print(f" - {h:02}:{m:02} → {tarea.nombre} ({tarea.duracion} min)")
        respuestas['plan_today'] = f" - {h:02}:{m:02} → {tarea.nombre} ({tarea.duracion} min)"
    return jsonify(respuestas)


falso_json =  {"resuelveComida": "n",
 "tienesIngredientes": "n",
    "tienesExamen": "s",
    "energia": 5,
    "tienesTareasPersonales": "Aprender Flask, Revisar apuntes de React",
    "deseos": "Ver una película, Salir a caminar"
}

print(respuesta(falso_json))