from moral_compass import Tarea

import random
def planificar_tareas(tareas, bloque):
    #Aqui las tareas se ordenan por puntaje, de mayor a menor
    tareas_ordenadas = sorted(tareas, key=lambda t: t.puntaje(), reverse=True)
    plan = []

    tiempo_restante =  random.randint(0,780)#duracion_bloque(bloque)
    hora_inicio = random.randint(7, 22) + random.randint(0, 59) / 60  #hora_actual_decimal()
    while tiempo_restante > 0 and tareas_ordenadas:
            tarea = tareas_ordenadas[0]
            if tarea.duracion <= tiempo_restante:
                plan.append((hora_inicio, tarea))
                hora_inicio += tarea.duracion / 60
                tiempo_restante -= tarea.duracion
                tareas_ordenadas.pop(0)
            else:
                break

    return plan

urgencia_random = random.randint(1, 10)
prioridad_random = random.randint(1, 10)
duracion_random = random.randint(30, 120)  # Duración en minutos


tareas_test = [
            Tarea("Tarea 1", urgencia=urgencia_random, prioridad=prioridad_random, duracion=duracion_random, tipo="obligación"),
            Tarea("Tarea 2", urgencia=urgencia_random, prioridad=prioridad_random, duracion=duracion_random, tipo="personal"),
        ]

resultado = planificar_tareas(tareas_test, [10.0, 23.0])
print(f"Se han ordenado de la siguiente manera las tareas: {resultado}")