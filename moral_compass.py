import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS # Importa Flask-CORS
import os # Importa el módulo os para acceder a variables de entorno
import pytz # Importa la biblioteca pytz

app = Flask(__name__)
CORS(app) # Habilita CORS para todas las rutas de tu aplicación

# Define el huso horario de Uruguay
URUGUAY_TIMEZONE = pytz.timezone('America/Montevideo')

"""""
1) Redefinir los bloques en los dias libres para que sean mas largos [CCOMPLETADO]
2) Siempre se debe dejar un bloque de 1 hora par estudiar en la semana[COMPLETADO]
2) Los sabados luego de las 19:00 se pueden hacer cosas de ocio. O sea, no se puede estudiar ni trabajar.
"""""
# -------------------------------
# CONFIGURACIÓN INICIAL
# python moral_compass.py 
# -------------------------------
"""""
Preguntas al usuario:
1) Trabajas? (Si es asi, se definen los horarios ocupados)
2) Que dias de la semana trabajas?
3) De que hora a que hora trabajas en estos dias?
4) Estudias? (Si es asi, se definen los horarios ocupados)
5) Que dias de la semana estudias?
6) De que hora a que hora estudias en estos dias?
7) Haces ejercicio? (Si es asi, se definen los horarios ocupados)
8) Que dias de la semana haces ejercicio?
9) De que hora a que hora haces ejercicio en estos dias?
10) Realizas alguna otra actividad de ocio? (Si es asi, se definen los horarios ocupados)
# 11) Que dias de la semana realizas esta actividad?
# 12) De que hora a que hora realizas esta actividad en estos dias?

"""


def horarios_ocupados(dias: list[str], horas: list[int]):
    """
    Esta función recibe el nombre de la actividad, los días de la semana y las horas ocupadas.
    Devuelve un diccionario con los horarios ocupados.
    """
    horarios = {}
    for dia, hora in zip(dias, horas):
        horarios[dia] = hora
    return horarios



#Horarios ocupados
# Se definen los horarios ocupados para estudio, trabajo y tenis
HORARIO_ESTUDIO_TRABAJO = {"lunes": [8, 19], "martes": [8, 19], "miércoles": [8, 19], "jueves": [8, 19], "viernes": [8, 19]}
HORARIO_TENIS = {"martes": [19.5, 23], "jueves": [19.5, 23]}
HORARIO_FIN_DE_SEMANA = {"sábado": [19, 23], "domingo": [19, 23]}


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
    #El puntaje se calcula como una combinación ponderada de urgencia y prioridad

    def __repr__(self):
        return f"{self.nombre} ({self.duracion} min, puntaje: {self.puntaje():.1f})"

# -------------------------------
# UTILIDADES DE TIEMPO
# -------------------------------

def hora_actual():
    # Obtiene la hora actual en el huso horario de Uruguay
    ahora_utc = datetime.datetime.now(pytz.utc)
    ahora_uruguay = ahora_utc.astimezone(URUGUAY_TIMEZONE)
    return ahora_uruguay.strftime('%A').lower(), ahora_uruguay.hour + ahora_uruguay.minute / 60
    # devuelve: wednesday
    #           14.75

def hora_actual_decimal():
    # Obtiene la hora actual en el huso horario de Uruguay
    ahora_utc = datetime.datetime.now(pytz.utc)
    ahora_uruguay = ahora_utc.astimezone(URUGUAY_TIMEZONE)
    return ahora_uruguay.hour + ahora_uruguay.minute / 60  # Hora actual en formato decimal

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
    # Se consideran horarios de estudio, trabajo y tenis
    # Si el día es sábado o domingo, se ignoran los horarios de estudio y trabajo
    ocupados = []
    if dia in HORARIO_ESTUDIO_TRABAJO:
        ocupados.append(HORARIO_ESTUDIO_TRABAJO[dia])
    if dia in HORARIO_TENIS:
        ocupados.append(HORARIO_TENIS[dia])
    if dia in HORARIO_FIN_DE_SEMANA:
        ocupados.append(HORARIO_FIN_DE_SEMANA[dia])
# Si el dia no esta dentro de ninguno de los horarios, se considera que no hay ocupación
    inicio = 10.0
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
    # Obtiene la hora actual en el huso horario de Uruguay
    ahora_utc = datetime.datetime.now(pytz.utc)
    ahora_uruguay = ahora_utc.astimezone(URUGUAY_TIMEZONE)
    hora_actual = ahora_uruguay.hour + ahora_uruguay.minute / 60  # 19.01 # *(Para testear)
    final_bloque = b[1]
    inicio_bloque = b[0] if hora_actual < b[0] else hora_actual
    return int((final_bloque - inicio_bloque) * 60) 

def porcentaje_bloque_disponible(b):
    # Obtiene la hora actual en el huso horario de Uruguay
    ahora_utc = datetime.datetime.now(pytz.utc)
    ahora_uruguay = ahora_utc.astimezone(URUGUAY_TIMEZONE)
    hora_actual = ahora_uruguay.hour + ahora_uruguay.minute / 60

    inicio_bloque = b[0]
    fin_bloque = b[1]
    duracion_total = fin_bloque - inicio_bloque

    if hora_actual >= fin_bloque:
        return 0  # Ya terminó el bloque
    elif hora_actual <= inicio_bloque:
        return 100  # Todavía no empezó, está todo disponible

    restante = fin_bloque - hora_actual
    porcentaje = (restante / duracion_total) * 100
    return round(porcentaje)
# -------------------------------
# GENERACIÓN DE TAREAS
# -------------------------------

def tareas_basicas(data):
    dia_actual, _ = hora_actual()
    dia_actual = convertir_dia(dia_actual)
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

    
    personal = data.get("tareasPersonales", "n").lower()
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


# -------------------------------
# PLANIFICADOR PRINCIPAL
# -------------------------------

def planificar_tareas(tareas, bloques):
    #Aqui las tareas se ordenan por puntaje, de mayor a menor
    tareas_ordenadas = sorted(tareas, key=lambda t: t.puntaje(), reverse=True)
    plan = []

    for bloque in bloques:
        tiempo_restante = duracion_bloque(bloque)
        hora_inicio = hora_actual_decimal()
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
@app.route('/', methods=["GET"])
def main():
    welcome = {
        "status": "success",
        "today": "",
        "message_time": "",
        "message_time2": "",
        "tiempo_restante": "",
        "tiempo_restante_porcentaje": ""
    }
    dia_raw, hora_now = hora_actual()
    dia_raw = dia_raw.lower()
    dia = convertir_dia(dia_raw)
    
    # Obtiene la hora actual en el huso horario de Uruguay para mostrar
    ahora_utc = datetime.datetime.now(pytz.utc)
    now = ahora_utc.astimezone(URUGUAY_TIMEZONE)
    now_time = f"{now.hour:02}:{now.minute:02}"
    
    print(f"\n📅 Hoy es {dia.capitalize()} — Hora actual: {now_time}")
    welcome['today'] = f"📅 Hoy es {dia.capitalize()} — Hora actual: {now_time}"
    bloques = bloques_libres(dia, hora_now)
    if not bloques:
        print("No tienes tiempo libre disponible hoy 💤")
        welcome['message_time'] =f"No tienes tiempo libre disponible hoy 💤"
        return jsonify(welcome)

    print(f"🕒 Bloques libres detectados:")
    welcome['message_time'] = f"🕒 Bloques libres detectados:"
    for b in bloques:
        # Obtiene la hora actual en el huso horario de Uruguay para mostrar
        ahora_utc_b = datetime.datetime.now(pytz.utc)
        ahora_uruguay_b = ahora_utc_b.astimezone(URUGUAY_TIMEZONE)
        horita = f"{ahora_uruguay_b.hour:02}:{ahora_uruguay_b.minute:02}"
        horita_decimal = hora_actual_decimal()
        print(f" - De {b[0]:.2f} a {b[1]:.2f} hs")
        welcome['message_time2'] = f" - De {b[0]:.2f} a {b[1]:.2f} hs"
    print(f"Tiempo restante del bloque ⚠️  De {horita if horita_decimal > b[0] else b[0]} a {b[1]:.2f} hs ({duracion_bloque(b)} min)")
    welcome['tiempo_restante'] = f"De {horita if horita_decimal > b[0] else b[0]} a {b[1]:.2f} hs ({duracion_bloque(b)} min)"
    print(f"Porcentaje de tiempo restante del bloque ⚠️: {porcentaje_bloque_disponible(b)}%")
    welcome['tiempo_restante_porcentaje'] = f"{porcentaje_bloque_disponible(b)}"
    return jsonify(welcome)

@app.route('/respuesta', methods=["POST"])
def respuesta():
    dia_raw, hora_now = hora_actual()
    dia_raw = dia_raw.lower()
    dia = convertir_dia(dia_raw)
    
    bloques = bloques_libres(dia, hora_now)
    
    data = request.get_json()
    
    respuestas = {
        "message_tareas": "",
        "message_plan_4_today": "",
        "plan_today": []  
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
        respuestas['plan_today'].append(f" - {h:02}:{m:02} → {tarea.nombre} ({tarea.duracion} min)") 
    return jsonify(respuestas)

if __name__ == "__main__":
    # Obtiene el puerto de la variable de entorno PORT, o usa 5000 como fallback
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 