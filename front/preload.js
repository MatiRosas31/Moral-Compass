// Este archivo se ejecuta en el renderer process (como si fuera un navegador)
const { ipcRenderer } = require("electron");

document.addEventListener('DOMContentLoaded', () => {
    // Solo ejecutar en la pantalla principal para evitar loops de redirección
    if (!window.location.pathname.endsWith('index.html')) {
        return;
    }

    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const local_url = "http://127.0.0.1:5000/api/home";

    fetch(local_url, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
      .then(response => {
          if (response.status === 401) {
              localStorage.removeItem('token');
              window.location.href = 'login.html';
              throw new Error('No autorizado');
          }
          return response.json();
      })
      .then(data => {
        console.log('✅ Data recibida del backend:', data);
        const headerUsername = document.querySelector(".header-username");
        if (headerUsername) headerUsername.innerHTML = `Bienvenido, ${username || data.username}`;

        const today = document.querySelector(".today");
        if (today) today.innerHTML = data.today;

        const youhave = document.querySelector(".youhave");
        if (youhave) {
            if (data.tiempo_restante_minutos > 0) {
                const horas = Math.floor(data.tiempo_restante_minutos / 60);
                const minutos = data.tiempo_restante_minutos % 60;
                let text = `Tienes `;
                if (horas > 0) text += `${horas} horas `;
                if (minutos > 0) text += `${minutos} minutos `;
                text += `de tiempo libre hoy`;
                youhave.innerHTML = text;
            } else {
                youhave.innerHTML = "No tienes tiempo libre hoy 💤";
            }
        }

        const detalatalhora = document.querySelector(".detalatalhora");
        if (detalatalhora) {
            let bloquesStr = "";
            data.bloques.forEach(b => {
                bloquesStr += `- De ${b[0].toFixed(2)} a ${b[1].toFixed(2)} hs<br>`;
            });
            detalatalhora.innerHTML = bloquesStr;
        }

        const tiemporestante = document.querySelector(".tiemporestante");
        if (tiemporestante) tiemporestante.innerHTML = data.tiempo_restante_minutos + " min";
        
        const barrita = document.querySelector(".barrita");
        if (barrita) barrita.style.width = data.tiempo_restante_porcentaje + '%';
        
        const percentage = document.querySelector("#percentage");
        if (percentage) percentage.innerHTML = data.tiempo_restante_porcentaje + '%';

        // Update focus activities
        const focusContainer = document.querySelector("#focus-activities-container");
        if (focusContainer && data.actividades_foco) {
            focusContainer.innerHTML = '';
            data.actividades_foco.forEach(act => {
                focusContainer.innerHTML += `
                    <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 flex justify-between items-center">
                        <span class="text-white font-medium">${act.activity_name}</span>
                        <span class="bg-green-900/50 text-green-400 px-2 py-1 rounded text-xs border border-green-800">Prioridad: ${act.priority}</span>
                    </div>
                `;
            });
        }
      })
      .catch(error => {
        console.error('❌ Error en fetch:', error);
      });
  });
