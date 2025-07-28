import datetime

# -------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------

HORARIO_ESTUDIO = {"lunes": [8, 10], "martes": [8, 10], "miércoles": [8, 10], "jueves": [8, 10], "viernes": [8, 10]}
HORARIO_TRABAJO = {"lunes": [10, 19], "martes": [10, 19], "miércoles": [10, 19], "jueves": [10, 19], "viernes": [10, 19]}
HORARIO_TENIS = {"martes": [19.5, 23], "jueves": [19.5, 23]}


# -------------------------------
# MODELO DE TAREA
# -------------------------------

class Tarea:
    def __init__(self, nombre, urgencia, prioridad, duracion, tipo):
        self.nombre = nombre
        self.urgencia = urgencia
        self.prioridad = prioridad
        self.duracion = duracion  # en minutos
        self.tipo = tipo

    def puntaje(self):
        return self.urgencia * 1.5 + self.prioridad

    def __repr__(self):
        return f"{self.nombre} ({self.duracion} min, puntaje: {self.puntaje():.1f})"


# -------------------------------
# UTILIDADES DE TIEMPO
# -------------------------------

def hora_actual():
    ahora = datetime.datetime.now()
    return ahora.strftime('%A').lower(), ahora.hour + ahora.minute / 60


def convertir_dia(dia):
    mapa = {
        "monday": "lunes",
        "tuesday": "martes",
        "wednesday": "miércoles",
        "thursday": "jueves",
        "friday": "viernes",
        "saturday": "sábado",
        "sunday": "domingo"
    }
    return mapa[dia]


def bloques_libres(dia, hora_now):
    bloques = []

    # Bloques predefinidos ocupados
    ocupados = []
    if dia in HORARIO_ESTUDIO:
        ocupados.append(HORARIO_ESTUDIO[dia])
    if dia in HORARIO_TRABAJO:
        ocupados.append(HORARIO_TRABAJO[dia])
    if dia in HORARIO_TENIS:
        ocupados.append(HORARIO_TENIS[dia])

    inicio = 7.0
    fin = 23.0

    for bloque in sorted(ocupados):
        if inicio < bloque[0]:
            bloques.append([inicio, bloque[0]])
        inicio = max(inicio, bloque[1])
    if inicio < fin:
        bloques.append([inicio, fin])

    # Filtrar bloques anteriores a la hora actual
    return [b for b in bloques if b[1] > hora_now]


def duracion_bloque(b):
    return int((b[1] - b[0]) * 60)


# -------------------------------
# GENERACIÓN DE TAREAS
# -------------------------------

def tareas_basicas():
    tareas = []

    res = input("¿Tienes resuelta la comida de esta noche? (s/n): ").lower()
    if res == "n":
        ing = input("¿Ya tienes los ingredientes? (s/n): ").lower()
        if ing == "n":
            tareas.append(Tarea("Ir al supermercado", urgencia=8, prioridad=7, duracion=30, tipo="necesidad"))
        tareas.append(Tarea("Cocinar", urgencia=6, prioridad=7, duracion=40, tipo="necesidad"))

    examen = input("¿Tienes un examen o entrevista cercana? (s/n): ").lower()
    if examen == "s":
        tareas.append(Tarea("Estudiar / Preparar entrevista", urgencia=9, prioridad=10, duracion=120, tipo="obligación"))

    energia = int(input("¿Cuánta energía tienes ahora mismo? (0 a 10): "))
    if energia < 4:
        tareas.append(Tarea("Descansar / Siesta", urgencia=5, prioridad=8, duracion=30, tipo="personal"))

    deseos = input("¿Qué te gustaría hacer hoy por placer? (separa por coma): ")
    for deseo in deseos.split(","):
        deseo = deseo.strip()
        if deseo:
            tareas.append(Tarea(deseo, urgencia=3, prioridad=5, duracion=30, tipo="deseo"))

    return tareas


# -------------------------------
# PLANIFICADOR PRINCIPAL
# -------------------------------

def planificar_tareas(tareas, bloques):
    tareas_ordenadas = sorted(tareas, key=lambda t: t.puntaje(), reverse=True)
    plan = []

    for bloque in bloques:
        tiempo_restante = duracion_bloque(bloque)
        hora_inicio = bloque[0]
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


# -------------------------------
# MAIN
# -------------------------------

def main():
    dia_raw, hora_now = hora_actual()
    dia = convertir_dia(dia_raw)

    print(f"\n📅 Hoy es {dia.capitalize()} — Hora actual: {hora_now:.2f}")
    bloques = bloques_libres(dia, hora_now)

    if not bloques:
        print("No tienes tiempo libre disponible hoy 💤")
        return

    print(f"🕒 Bloques libres detectados:")
    for b in bloques:
        print(f" - De {b[0]:.2f} a {b[1]:.2f} hs ({duracion_bloque(b)} min)")

    tareas = tareas_basicas()
    if not tareas:
        print("No se han registrado tareas.")
        return

    plan = planificar_tareas(tareas, bloques)

    print("\n✅ Plan sugerido para hoy:")
    for hora, tarea in plan:
        h = int(hora)
        m = int((hora - h) * 60)
        print(f" - {h:02}:{m:02} → {tarea.nombre} ({tarea.duracion} min)")

if __name__ == "__main__":
    main()
