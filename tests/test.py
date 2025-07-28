# python
import unittest
from moral_compass import bloques_libres, duracion_bloque, Tarea, planificar_tareas

class TestMoralCompass(unittest.TestCase):
    def test_bloques_libres(self):
        dia = "lunes"
        hora_now = 9.10
        result = bloques_libres(dia, hora_now)
        expected = [[19, 23.0]]  # Ajusta según tu lógica
        self.assertEqual(result, expected)

    def test_duracion_bloque(self):
        bloque = [10.0, 12.0]
        result = duracion_bloque(bloque)
        expected = 120  # 2 horas en minutos
        self.assertEqual(result, expected)

    def test_tarea_puntaje(self):
        tarea = Tarea("Estudiar", urgencia=5, prioridad=7, duracion=60, tipo="obligación")
        result = tarea.puntaje()
        expected = 14.5  # 5 * 1.5 + 7
        self.assertEqual(result, expected)

    def test_planificar_tareas(self):
        tareas = [
            Tarea("Tarea 1", urgencia=5, prioridad=7, duracion=60, tipo="obligación"),
            Tarea("Tarea 2", urgencia=8, prioridad=6, duracion=30, tipo="personal"),
        ]
        bloques = [[10.0, 12.0]]
        result = planificar_tareas(tareas, bloques)
        self.assertEqual(len(result), 2)  # Ambas tareas deben caber en el bloque

if __name__ == "__main__":
    unittest.main()