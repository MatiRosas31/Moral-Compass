import datetime
import os
import functools
from flask import Flask, request, jsonify
from flask_cors import CORS
import pytz
import bcrypt
import jwt
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()

app = Flask(__name__)
CORS(app)

# Define el huso horario de Uruguay
URUGUAY_TIMEZONE = pytz.timezone('America/Montevideo')

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "moral_compass_secret_key_2025")


# -------------------------------
# DECORADOR DE AUTENTICACIÓN
# -------------------------------

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"status": "error", "message": "Token no proporcionado."}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "error", "message": "El token ha expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "error", "message": "Token inválido."}), 401

        return f(user_id, *args, **kwargs)
    return decorated


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


def bloques_libres(dia, hora_now, user_availability_for_day):
    """
    Retorna los bloques libres del usuario para el día dado,
    filtrados por la hora actual.
    user_availability_for_day es una lista de [start, end] que representan
    los horarios en los que el usuario está LIBRE.
    """
    # Filtrar bloques anteriores a la hora actual
    return [b for b in user_availability_for_day if b[1] > hora_now]


def duracion_bloque(b):
    # Obtiene la hora actual en el huso horario de Uruguay
    ahora_utc = datetime.datetime.now(pytz.utc)
    ahora_uruguay = ahora_utc.astimezone(URUGUAY_TIMEZONE)
    hora_actual = ahora_uruguay.hour + ahora_uruguay.minute / 60
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
    
    res = data.get("comidaResuelta", "null").lower()
    #res = input("¿Tienes resuelta la comida de esta noche? (s/n): ").lower()
    if res == "no":
        ing = data.get("ingredientesResueltos", "null").lower()
        #ing = input("¿Ya tienes los ingredientes? (s/n): ").lower()
        if ing == "no":
            tareas.append(Tarea("Ir al supermercado", urgencia=8, prioridad=7, duracion=30, tipo="necesidad"))
        tareas.append(Tarea("Cocinar", urgencia=6, prioridad=7, duracion=40, tipo="necesidad"))

    examen = data.get("examenEntrevista", "null").lower()
   # examen = input("¿Tienes un examen o entrevista cercana? (s/n): ").lower()
    if examen == "si":
        tareas.append(Tarea("Estudiar / Preparar entrevista", urgencia=9, prioridad=10, duracion=120, tipo="obligación"))
    else:
        duracion_matematicas = 60 if (dia_actual == "sábado" or dia_actual == "domingo") else 45
        tareas.append(Tarea("Estudiar Matematicas / Programacion", urgencia=5, prioridad=6, duracion=duracion_matematicas, tipo="obligación"))
    energia = int(data.get("energiaSlider", 5))  # Valor por defecto 5
    #energia = int(input("¿Cuánta energía tienes ahora mismo? (0 a 10): "))
    if energia < 4:
        tareas.append(Tarea("Descansar / Siesta", urgencia=5, prioridad=8, duracion=30, tipo="personal"))

    
    personal = data.get("tareasPersonales", "null").lower()
    #personal = input("¿Tienes alguna tarea personal pendiente? (Algun curso, aprender algo de programacion nuevo, etc.) (separa por coma): ")
    for personal in personal.split(","):
        personal = personal.strip()
        if personal:
            duracion_personal = 90 if (dia_actual == "sábado" or dia_actual == "domingo") else 45
            # Aumentar duración de tareas personales los sábados y domingos
            tareas.append(Tarea(personal, urgencia=4, prioridad=6, duracion=duracion_personal, tipo="personal"))
    deseos = data.get("deseos", "null").lower()
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
# HELPERS DE BASE DE DATOS
# -------------------------------

def obtener_disponibilidad_usuario(user_id, dia):
    """Obtiene los bloques de disponibilidad del usuario para un día dado."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT start_time, end_time FROM user_availability WHERE user_id = %s AND day_of_week = %s ORDER BY start_time",
        (user_id, dia)
    )
    slots = [[float(row[0]), float(row[1])] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return slots


def obtener_actividades_usuario(user_id):
    """Obtiene las actividades de enfoque del usuario."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT activity_name, priority FROM user_focus_activities WHERE user_id = %s ORDER BY priority DESC",
        (user_id,)
    )
    activities = [{"name": row[0], "priority": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return activities


# -------------------------------
# ENDPOINTS DE AUTENTICACIÓN
# -------------------------------

@app.route('/api/register', methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios."}), 400

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Usuario creado exitosamente."}), 201
    except Exception as e:
        error_msg = str(e)
        if "username" in error_msg:
            return jsonify({"status": "error", "message": "El nombre de usuario ya está en uso."}), 409
        elif "email" in error_msg:
            return jsonify({"status": "error", "message": "El correo electrónico ya está registrado."}), 409
        return jsonify({"status": "error", "message": f"Error al crear el usuario: {error_msg}"}), 500


@app.route('/api/login', methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"status": "error", "message": "Usuario y contraseña son obligatorios."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash, onboarding_complete, username FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404

        user_id, password_hash, onboarding_complete, db_username = user

        if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            return jsonify({"status": "error", "message": "Contraseña incorrecta."}), 401

        token = jwt.encode(
            {
                "user_id": user_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            JWT_SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "status": "success",
            "token": token,
            "onboarding_complete": onboarding_complete,
            "username": db_username
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al iniciar sesión: {str(e)}"}), 500


# -------------------------------
# ENDPOINTS DE ONBOARDING / PERFIL
# -------------------------------

@app.route('/api/onboarding', methods=["POST"])
@token_required
def onboarding(user_id):
    data = request.get_json()
    days = data.get("days", [])
    slots = data.get("slots", {})
    grocery_important = data.get("grocery_important", False)
    activities = data.get("activities", [])

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Eliminar datos existentes del usuario
        cur.execute("DELETE FROM user_availability WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM user_focus_activities WHERE user_id = %s", (user_id,))

        # Insertar nueva disponibilidad
        for day in days:
            day_slots = slots.get(day, [])
            for slot in day_slots:
                cur.execute(
                    "INSERT INTO user_availability (user_id, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s)",
                    (user_id, day, slot["start"], slot["end"])
                )

        # Insertar nuevas actividades de enfoque
        for activity in activities:
            cur.execute(
                "INSERT INTO user_focus_activities (user_id, activity_name, priority) VALUES (%s, %s, %s)",
                (user_id, activity["name"], activity["priority"])
            )

        # Actualizar estado del onboarding y preferencia de compras
        cur.execute(
            "UPDATE users SET onboarding_complete = TRUE, grocery_cooking_important = %s WHERE id = %s",
            (grocery_important, user_id)
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al guardar onboarding: {str(e)}"}), 500


@app.route('/api/me', methods=["GET"])
@token_required
def get_profile(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Obtener datos del usuario
        cur.execute(
            "SELECT username, email, onboarding_complete, grocery_cooking_important FROM users WHERE id = %s",
            (user_id,)
        )
        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404

        username, email, onboarding_complete, grocery_cooking_important = user

        # Obtener disponibilidad
        cur.execute(
            "SELECT day_of_week, start_time, end_time FROM user_availability WHERE user_id = %s ORDER BY day_of_week, start_time",
            (user_id,)
        )
        availability = [
            {"day": row[0], "start": float(row[1]), "end": float(row[2])}
            for row in cur.fetchall()
        ]

        # Obtener actividades
        cur.execute(
            "SELECT activity_name, priority FROM user_focus_activities WHERE user_id = %s ORDER BY priority DESC",
            (user_id,)
        )
        activities = [{"name": row[0], "priority": row[1]} for row in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({
            "status": "success",
            "username": username,
            "email": email,
            "onboarding_complete": onboarding_complete,
            "grocery_cooking_important": grocery_cooking_important,
            "availability": availability,
            "activities": activities
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener perfil: {str(e)}"}), 500


@app.route('/api/me', methods=["PUT"])
@token_required
def update_profile(user_id):
    data = request.get_json()
    days = data.get("days", [])
    slots = data.get("slots", {})
    grocery_important = data.get("grocery_important", False)
    activities = data.get("activities", [])

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Reemplazar disponibilidad
        cur.execute("DELETE FROM user_availability WHERE user_id = %s", (user_id,))
        for day in days:
            day_slots = slots.get(day, [])
            for slot in day_slots:
                cur.execute(
                    "INSERT INTO user_availability (user_id, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s)",
                    (user_id, day, slot["start"], slot["end"])
                )

        # Reemplazar actividades
        cur.execute("DELETE FROM user_focus_activities WHERE user_id = %s", (user_id,))
        for activity in activities:
            cur.execute(
                "INSERT INTO user_focus_activities (user_id, activity_name, priority) VALUES (%s, %s, %s)",
                (user_id, activity["name"], activity["priority"])
            )

        # Actualizar preferencia de compras
        cur.execute(
            "UPDATE users SET grocery_cooking_important = %s WHERE id = %s",
            (grocery_important, user_id)
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al actualizar perfil: {str(e)}"}), 500


# -------------------------------
# ENDPOINTS PRINCIPALES
# -------------------------------

@app.route('/api/home', methods=["GET"])
@token_required
def home(user_id):
    dia_raw, hora_now = hora_actual()
    dia_raw = dia_raw.lower()
    dia = convertir_dia(dia_raw)

    # Obtener disponibilidad del usuario para hoy
    user_slots = obtener_disponibilidad_usuario(user_id, dia)
    bloques = bloques_libres(dia, hora_now, user_slots)

    # Calcular tiempo restante
    tiempo_restante_minutos = 0
    for b in bloques:
        tiempo_restante_minutos += duracion_bloque(b)

    # Calcular porcentaje de tiempo restante
    tiempo_total_minutos = 0
    for b in user_slots:
        tiempo_total_minutos += int((b[1] - b[0]) * 60)
    tiempo_restante_porcentaje = round((tiempo_restante_minutos / tiempo_total_minutos) * 100) if tiempo_total_minutos > 0 else 0

    # Obtener actividades de enfoque
    actividades = obtener_actividades_usuario(user_id)

    # Obtener nombre de usuario
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    username = cur.fetchone()[0]
    cur.close()
    conn.close()

    return jsonify({
        "today": dia,
        "bloques": bloques,
        "tiempo_restante_minutos": tiempo_restante_minutos,
        "tiempo_restante_porcentaje": tiempo_restante_porcentaje,
        "actividades_foco": actividades,
        "username": username
    })


@app.route('/api/respuesta', methods=["POST"])
@token_required
def api_respuesta(user_id):
    dia_raw, hora_now = hora_actual()
    dia_raw = dia_raw.lower()
    dia = convertir_dia(dia_raw)

    # Obtener disponibilidad del usuario para hoy desde la BD
    user_slots = obtener_disponibilidad_usuario(user_id, dia)
    bloques = bloques_libres(dia, hora_now, user_slots)

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