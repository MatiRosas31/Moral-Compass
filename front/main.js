const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createMainWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,     // Permite usar require en renderer.js
      contextIsolation: false,   // Para que ipcRenderer funcione
    },
  });

  mainWindow.loadFile('index.html');
}

function openPreguntasWindow() {
  const preguntasWindow = new BrowserWindow({
    width: 500,
    height: 500,
    title: 'Gestionar Preguntas',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  preguntasWindow.loadFile('preguntas.html');
}

// Escuchar evento desde renderer.js
ipcMain.on('abrir-preguntas', () => {
  openPreguntasWindow();
});

app.whenReady().then(createMainWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
