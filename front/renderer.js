const { ipcRenderer } = require("electron");

document.getElementById('button-ir-a-preguntas').addEventListener('click', () => {
  document.getElementById('super-container').innerHTML = ''; // Limpiar el contenedor principal

  // 1. Crear contenedor principal y formulario
  let preguntasContainer = document.createElement('div');
  preguntasContainer.className = "max-w-xl mx-auto";

  const formulario = document.createElement('form');
  formulario.id = 'formulario';
  formulario.className = 'space-y-6';

  preguntasContainer.appendChild(formulario);

  // 2. Pregunta: comida resuelta
  const pregunta1 = document.createElement('div');
  pregunta1.innerHTML = ` 
    <label class="block mb-2 font-medium">¿Tienes resuelta la comida de esta noche?</label>
    <select id="comidaResuelta" class="w-full rounded p-2 text-black">
      <option value="">Selecciona una opción</option>
      <option value="si">Si</option>
      <option value="no">No</option>
    </select>
  `;
  formulario.appendChild(pregunta1);

  // 3. Preguntas condicionales (ingredientes)
  const condicional = document.createElement('div');
  condicional.className = 'space-y-6';
  condicional.id = 'preguntasCondicionales';
  condicional.innerHTML = ` 
    <div>
      <label class="block mb-2 font-medium">¿Ya tienes los ingredientes?</label>
      <select id="ingredientesResueltos" class="w-full rounded p-2 text-black">
        <option value="">Selecciona una opción</option>
        <option value="si">Si</option>
        <option value="no">No</option>
      </select>
    </div>
  `;
  formulario.appendChild(condicional);

  // 4. Pregunta: examen o entrevista
  const pregunta_examen = document.createElement('div');
  pregunta_examen.innerHTML = `
    <label class="block mb-2 font-medium">¿Tienes un examen o entrevista cercana?</label>
    <select id="examenEntrevista" class="w-full rounded p-2 text-black">
      <option value="">Selecciona una opción</option>
      <option value="si">Si</option>
      <option value="no">No</option>
    </select>
  `;
  formulario.appendChild(pregunta_examen);

  // 5. Pregunta: nivel de energía
  const pregunta_energia = document.createElement('div');
  pregunta_energia.innerHTML = ` 
    <label class="block mb-2 font-medium">¿Cuánta energía tienes ahora mismo? (1 a 10)</label>
    <input type="range" min="1" max="10" value="5" class="w-full" id="energiaSlider">
    <p class="mt-1 text-sm text-gray-300">Nivel: <span id="valorEnergia">5</span></p>
  `;
  formulario.appendChild(pregunta_energia);

  // 6. Pregunta: tareas personales
  const pregunta_tareas = document.createElement('div');
  pregunta_tareas.innerHTML = ` 
    <label class="block mb-2 font-medium">¿Tienes alguna tarea personal pendiente? (Curso, programación, etc.)</label>
    <input id="tarea_personal" type="text" class="w-full rounded p-2 text-black" placeholder="Separar por coma">
  `;
  formulario.appendChild(pregunta_tareas);

  // 7. Pregunta: placer
  const pregunta_placer = document.createElement('div');
  pregunta_placer.innerHTML = ` 
    <label class="block mb-2 font-medium">¿Qué te gustaría hacer hoy por placer?</label>
    <input id="placer" type="text" class="w-full rounded p-2 text-black" placeholder="Separar por coma">
  `;
  formulario.appendChild(pregunta_placer);

  // 8. Botón submit
  const submitButton = document.createElement('button');
  submitButton.type = 'submit';
  submitButton.className = 'w-full bg-green-500 hover:bg-green-400 text-white my-4 py-2 rounded';
  submitButton.textContent = 'Guardar respuestas';
  formulario.appendChild(submitButton);

  // Agregar todo al contenedor principal
  document.getElementById('super-container').appendChild(preguntasContainer);

  // 9. Interacciones dinámicas
  const comidaSelect = document.getElementById('comidaResuelta');
  const preguntasCondicionales = document.getElementById('preguntasCondicionales');
  const energiaSlider = document.getElementById('energiaSlider');
  const valorEnergia = document.getElementById('valorEnergia');
  const ingredientesSelect = document.getElementById('ingredientesResueltos');
  const examenEntrevistaSelect = document.getElementById('examenEntrevista');
  const tareaPersonalInput = document.getElementById('tarea_personal');
  const placerInput = document.getElementById('placer');

  preguntasCondicionales.classList.add('hidden'); // Ocultar condicional al inicio

  comidaSelect.addEventListener('change', () => {
    preguntasCondicionales.classList.toggle('hidden', comidaSelect.value !== 'no');
  });

  energiaSlider.addEventListener('input', () => {
    valorEnergia.textContent = energiaSlider.value;
  });

  // 10. Envío del formulario
  formulario.addEventListener('submit', (event) => {
    event.preventDefault();

    const respuestas = {
      comidaResuelta: comidaSelect.value,
      ingredientesResueltos: comidaSelect.value === 'no' ? ingredientesSelect.value : null,
      examenEntrevista: examenEntrevistaSelect.value,
      energiaSlider: energiaSlider.value,
      tareasPersonales: tareaPersonalInput.value,
      deseos: placerInput.value
    };

    console.log('Respuestas del formulario:', respuestas);

    const local_url = "http://127.0.0.1:5000/api/respuesta";
    const token = localStorage.getItem('token');

    fetch(local_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(respuestas)
    })
      .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        preguntasContainer.innerHTML = '';

        const contenedor = document.createElement('div');
        contenedor.className = "max-w-xl mx-auto mt-10 p-6 bg-gray-800 rounded text-white space-y-4";

        const titulo = document.createElement('h2');
        titulo.textContent = data.message_plan_4_today;
        titulo.className = "text-2xl font-bold";
        contenedor.appendChild(titulo);

        if (data.message_tareas) {
          const tareasMensaje = document.createElement('p');
          tareasMensaje.textContent = data.message_tareas;
          tareasMensaje.className = "text-gray-300";
          contenedor.appendChild(tareasMensaje);
        }

        const lista = document.createElement('ul');
        lista.className = "list-disc pl-5 space-y-1";
        data.plan_today.forEach(item => {
          const li = document.createElement('li');
          li.textContent = item;
          lista.appendChild(li);
        });
        contenedor.appendChild(lista);

        const volverBtn = document.createElement('button');
        volverBtn.textContent = "Volver";
        volverBtn.className = "mt-6 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded";
        volverBtn.onclick = () => location.reload();
        contenedor.appendChild(volverBtn);

        preguntasContainer.appendChild(contenedor);
      })
      .catch(error => {
        console.error('Error during fetch:', error);
        preguntasContainer.innerHTML = '';
        const errorMessage = document.createElement('p');
        errorMessage.textContent = 'Error al obtener datos del backend';
        errorMessage.className = 'text-red-500';
        preguntasContainer.appendChild(errorMessage);
      });
  });
});
