import random
HORARIO_ESTUDIO_TRABAJO = {"lunes": [8, 19], "martes": [8, 19], "miércoles": [8, 19], "jueves": [8, 19], "viernes": [8, 19]}
HORARIO_FIN_DE_SEMANA = {"sábado": [19, 23], "domingo": [19, 23]}
HORARIO_TENIS = {"martes": [19.5, 23], "jueves": [19.5, 23]}



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

# dia = "sabado"  # Ejemplo de día
# hora_random = random.randint(7, 22) + random.randint(0, 59) / 60 
# bloques = bloques_libres(dia, hora_random)  # Ejemplo de uso


dia = "sábado"  # Ejemplo de día
hora_random = 10.39
bloques = bloques_libres(dia, hora_random)  # Ejemplo de uso

print(f"Los bloques libres para el dia {dia} siendo la hora {hora_random} son: {bloques}")