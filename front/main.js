const {app, BrowserWindow} = require('electron');


//Falta probar esto
//Para correr es npm start

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
  });

    win.loadFile('index.html')
}


app.whenReady().then(createWindow);

