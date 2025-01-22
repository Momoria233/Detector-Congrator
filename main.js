const {app , BrowserWindow } = require('electron')

app.on('ready',()=>{
    const win = new BrowserWindow({
        width: 1120,
        height: 792,
        autoHideMenuBar: true,
        alwaysOnTop: true,
        fullscreen: false,
        resizable: false,
        frame: false
    })
    win.loadFile('./src/index.html')
})
