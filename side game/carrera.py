import time
import sys
import random
import threading

def barra_de_carga(start, total, label):
    for i in range(start, total + 1):
        porcentaje = int((i / total) * 100)
        barra = '█' * (porcentaje // 2) + '-' * (50 - (porcentaje // 2))
        sys.stdout.write(f'\r{label} |{barra}| {porcentaje}%')
        sys.stdout.flush()
        time.sleep(0.1)  # Simula carga
    print(f"\n{label} completa.")

# Crear hilos para las barras de carga
hilos = []
for i in range(1, 4):  # Tres barras de carga
    random_start = random.randint(1, 100)
    hilo = threading.Thread(target=barra_de_carga, args=(random_start, 100, f"Carga {i}"))
    hilos.append(hilo)

# Iniciar los hilos
for hilo in hilos:
    hilo.start()

# Esperar a que todos los hilos terminen
for hilo in hilos:
    hilo.join()


