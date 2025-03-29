window.addEventListener("keydown", (event) => {
    const keyMap = {
        "w": { linear: 150, angular: 0 },   // Adelante
        "s": { linear: -150, angular: 0 },  // Atrás
        "a": { linear: 0, angular: -150 },  // Girar izquierda
        "d": { linear: 0, angular: 150 },   // Girar derecha
        "x": { linear: 0, angular: 0 }      // Detenerse
    };
    
    if (keyMap[event.key]) {
        sendVelocities(keyMap[event.key].linear, keyMap[event.key].angular);
    }
});

function sendVelocities(linear, angular) {
    fetch('/velocities', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ linear: linear, angular: angular })
    })
    .then(response => response.json())
    .then(data => console.log("Respuesta del servidor:", data))
    .catch(error => console.error("Error enviando comando:", error));
}

function startVoltageStream() {
    const output = document.getElementById('voltage');
    const eventSource = new EventSource('/voltage_stream');

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            output.textContent = JSON.stringify(data.voltage, null, 2);
        } catch (error) {
            console.error("Error parsing voltage stream data", error);
        }
    };

    eventSource.onerror = function() {
        console.error("Error connecting to voltage stream");
        eventSource.close();
    };
}

function startCurrentsStream() {
    const output = document.getElementById('currents');
    const eventSource = new EventSource('/currents_stream');

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            output.textContent = JSON.stringify(data.currents, null, 2);
        } catch (error) {
            console.error("Error parsing currents stream data", error);
        }
    };

    eventSource.onerror = function() {
        console.error("Error connecting to currents stream");
        eventSource.close();
    };
}

startCurrentsStream()
startVoltageStream()