const { ipcRenderer } = require("electron");

// Obtener referencias a los elementos del DOM
const formulario = document.getElementById('formulario');
const ingredientesSelect = document.getElementById('ingredientesResueltos'); // Asegúrate de tener un ID para este select
const examenEntrevistaSelect = document.getElementById('examenEntrevista');
const tareaPersonalInput = document.getElementById('tarea_personal');
const placerInput = document.getElementById('placer');


// Event listener para el envío del formulario
formulario.addEventListener('submit', (event) => {
  event.preventDefault(); // Evita el envío del formulario por defecto

  // Recopilar todas las respuestas en el momento del envío
  const respuestas = {
    comidaResuelta: comidaSelect.value,
    // Solo incluir ingredientesResueltos si es visible (comidaResuelta es 'no')
    ingredientesResueltos: comidaSelect.value === 'no' ? ingredientesSelect.value : null,
    examenEntrevista: examenEntrevistaSelect.value,
    energiaSlider: energiaSlider.value,
    tareasPersonales: tareaPersonalInput.value,
    deseos: placerInput.value
  }
  ;

  console.log('Respuestas del formulario:', respuestas);

  // Enviar las respuestas al proceso principal de Electron
  ipcRenderer.send('guardar-respuestas', respuestas);

  const url = 'https://moral-compass-production.up.railway.app/respuesta';
  
  fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(respuestas)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json(); // Or response.text() if expecting plain text
    })
    .then(data => {
      console.log('Success:', data);
      document.getElementById('max_container').innerHTML  = '';  ; // Eliminar el formulario del DOM // formulario.remove()
      // 2. Crear contenedor de respuesta
    const contenedor = document.createElement('div');
    contenedor.className = "max-w-xl mx-auto mt-10 p-6 bg-gray-800 rounded text-white space-y-4";

  // 3. Agregar mensaje principal
  const titulo = document.createElement('h2');
  titulo.textContent = data.message_plan_4_today;
  titulo.className = "text-2xl font-bold";
  contenedor.appendChild(titulo);

  // 4. Agregar tareas (si hay)
  if (data.message_tareas) {
    const tareasMensaje = document.createElement('p');
    tareasMensaje.textContent = data.message_tareas;
    tareasMensaje.className = "text-gray-300";
    contenedor.appendChild(tareasMensaje);
  }

  // 5. Agregar lista de plan sugerido
  const lista = document.createElement('ul');
  lista.className = "list-disc pl-5 space-y-1";
  data.plan_today.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    lista.appendChild(li);
  });
  contenedor.appendChild(lista);

  // 6. Agregar botón para volver
  const volverBtn = document.createElement('button');
  volverBtn.textContent = "Volver";
  volverBtn.className = "mt-6 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded";
  volverBtn.onclick = () => location.reload(); // recarga la página original
  contenedor.appendChild(volverBtn);

  // 7. Agregar al body
  document.body.appendChild(contenedor);


    })
    .catch(error => {
      console.error('Error during fetch:', error);
    })
});