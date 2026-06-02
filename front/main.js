const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createMainWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
    },
    autoHideMenuBar: true,
  });
  mainWindow.loadFile('login.html');
  mainWindow.webContents.openDevTools({ mode: 'detach' })
}

app.whenReady().then(createMainWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
