// Este archivo se ejecuta en el renderer process (como si fuera un navegador)
const { ipcRenderer } = require("electron");

document.addEventListener('DOMContentLoaded', () => {
    fetch('https://moral-compass-production.up.railway.app')
      .then(response => response.json())
      .then(data => {
        console.log('✅ Data recibida del backend:', data);
        const today = document.querySelector(".today");
        today.innerHTML = data.today;
        const youhave = document.querySelector(".youhave");
        youhave.innerHTML = data.message_time;
        const detalatalhora = document.querySelector(".detalatalhora");
        detalatalhora.innerHTML = data.message_time2;
        const tiemporestante = document.querySelector(".tiemporestante");
        tiemporestante.innerHTML = data.tiempo_restante;
        barrita = document.querySelector(".barrita");
        barrita.style.width =
        data.tiempo_restante_porcentaje + '%';
        console.log(barrita);
        const percentage = document.querySelector("#percentage");
        percentage.innerHTML = data.tiempo_restante_porcentaje + '%';
      })
      .catch(error => {
        console.error('❌ Error en fetch:', error);
        document.getElementById('resultado').textContent = 'Error al obtener datos del backend';
      });
  });
  
document.getElementById('ir-a-preguntas').addEventListener('click', () => {
    ipcRenderer.send('abrir-preguntas');
  });