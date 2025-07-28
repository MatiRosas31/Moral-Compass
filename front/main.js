const {app, BrowserWindow} = require('electron');

fetch("http://localhost:5000")
  .then(response => response.json())
    .then(data => {
        console.log(data);
    })
  .catch(error => {
    console.error('Error fetching data:', error);
});

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

