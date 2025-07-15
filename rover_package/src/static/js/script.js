window.addEventListener("keydown", (event) => {
    const keyMap = {
        "w": {linear: 150, angular:0},
        "a": {linear: 0, angular:-150},
        "s": {linear: -150, angular:0},
        "d": {linear: 0, angular:150},
        "x": {linear: 0, angular:0},
    };

    if (keyMap[event.key]) {
        sendVelocities(keyMap[event.key].linear, keyMap[event.key].angular)
    }
});

// Actualiza el voltage cada 1 segundos
setInterval(fetchCurrents, 1000);

function sendVelocities(linear, angular) {
    fetch('/velocities' , {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ linear : linear, angular : angular})
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
    }
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
        console.error("Error connecting to current stream");
        eventSource.close();
    }
}

function startGPSStream() {
    const eventSource = new EventSource('/gps_stream');

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            document.getElementById("gps_x").textContent = data.gps_x;
            document.getElementById("gps_y").textContent = data.gps_y;
        } catch (error) {
            console.error("Error parsing gps stream data", error);
        }
    };

    eventSource.onerror = function() {
        console.error("Error connecting to gps stream");
        eventSource.close();
    }
}

startVoltageStream()
startCurrentsStream()
startGPSStream()
