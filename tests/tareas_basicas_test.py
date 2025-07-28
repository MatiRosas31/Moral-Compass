class Tarea:
    def __init__(self, nombre, urgencia, prioridad, duracion, tipo):
        self.nombre = nombre
        self.urgencia = urgencia
        self.prioridad = prioridad
        self.duracion = duracion  # en minutos
        self.tipo = tipo

    def puntaje(self):
        return self.urgencia * 1.5 + self.prioridad
    #El puntaje se calcula como una combinación ponderada de urgencia y prioridad

    def __repr__(self):
        return f"{self.nombre} ({self.duracion} min, puntaje: {self.puntaje():.1f})"


def tareas_basicas(data, dia_actual):
    tareas = []
    
    res = data.get("resuelveComida", "n").lower()
    #res = input("¿Tienes resuelta la comida de esta noche? (s/n): ").lower()
    if res == "n":
        ing = data.get("tienesIngredientes", "n").lower()
        #ing = input("¿Ya tienes los ingredientes? (s/n): ").lower()
        if ing == "n":
            tareas.append(Tarea("Ir al supermercado", urgencia=8, prioridad=7, duracion=30, tipo="necesidad"))
        tareas.append(Tarea("Cocinar", urgencia=6, prioridad=7, duracion=40, tipo="necesidad"))

    examen = data.get("tienesExamen", "n").lower()
   # examen = input("¿Tienes un examen o entrevista cercana? (s/n): ").lower()
    if examen == "s":
        tareas.append(Tarea("Estudiar / Preparar entrevista", urgencia=9, prioridad=10, duracion=120, tipo="obligación"))
    else:
        duracion_matematicas = 90 if (dia_actual == "sábado" or dia_actual == "domingo") else 60
        tareas.append(Tarea("Estudiar Matematicas / Programacion", urgencia=5, prioridad=6, duracion=duracion_matematicas, tipo="obligación"))
    energia = data.get("energia", 5)  # Valor por defecto 5
    #energia = int(input("¿Cuánta energía tienes ahora mismo? (0 a 10): "))
    if energia < 4:
        tareas.append(Tarea("Descansar / Siesta", urgencia=5, prioridad=8, duracion=30, tipo="personal"))

    
    personal = data.get("tienesTareasPersonales", "n").lower()
    #personal = input("¿Tienes alguna tarea personal pendiente? (Algun curso, aprender algo de programacion nuevo, etc.) (separa por coma): ")
    for personal in personal.split(","):
        personal = personal.strip()
        if personal:
            duracion_personal = 90 if (dia_actual == "sábado" or dia_actual == "domingo") else 45
            # Aumentar duración de tareas personales los sábados y domingos
            tareas.append(Tarea(personal, urgencia=4, prioridad=6, duracion=duracion_personal, tipo="personal"))
    deseos = data.get("deseos", "n").lower()
    #deseos = input("¿Qué te gustaría hacer hoy por placer? (separa por coma): ")
    for deseo in deseos.split(","):
        deseo = deseo.strip()
        if deseo:
            duracion_deseo = 120 if (dia_actual == "sábado" or dia_actual == "domingo") else 60
            # Aumentar duración de deseos los sábados y domingos
            tareas.append(Tarea(deseo, urgencia=3, prioridad=5, duracion=duracion_deseo, tipo="deseo"))

    for tarea in tareas:
        print(f" - {tarea}")

    return tareas

# Ejemplo de uso
dic_json = {
  'resuelveComida': "n",
  'tieneIngredientes': "n",
  'examenCercano': "s",
  'energia': 3,
  'tareasPersonales': "Aprender Flask, Revisar apuntes de React",
  'deseos': "Ver una película, Salir a caminar"
}

dia_actual = "lunes"

print(tareas_basicas(dic_json, dia_actual))