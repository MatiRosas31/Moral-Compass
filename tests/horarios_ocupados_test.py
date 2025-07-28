def horarios_ocupados(dias: list[str], horas: list[int]):
    """
    Esta función recibe el nombre de la actividad, los días de la semana y las horas ocupadas.
    Devuelve un diccionario con los horarios ocupados.
    """
    horarios = {}
    for dia, hora in zip(dias, horas):
        horarios[dia] = hora
    return horarios


print(horarios_ocupados(["lunes", "martes", "miércoles"], [[8, 12], [14, 18], [9, 11]]))