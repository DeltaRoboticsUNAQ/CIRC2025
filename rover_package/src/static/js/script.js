////// SLIDER BARS //////////
const humerus_slider = document.getElementById('humerus_pos');
const forearm_slider = document.getElementById('forearm_pos');

const humerus_output = document.getElementById('humerus_demo');
const forearm_output = document.getElementById('forearm_demo');

const humerus_input = document.getElementById('humerus_pos_input');
const forearm_input = document.getElementById('forearm_pos_input');

var socket = io();

// Mostrar el valor inicial
humerus_output.innerHTML = humerus_slider.value;

// Actualizar el valor mostrado cuando el slider cambia
humerus_slider.oninput = function() {
    humerus_output.textContent = this.value;
    humerus_input.value = this.value;
}

// Actualizar el slider cuando el input cambia
humerus_input.oninput = function() {
    let val = Number(this.value);
    if (val >= 1 && val <= 1000) {
        humerus_slider.value = val;
        humerus_output.textContent = val;
    }
}

socket.on('update_humerus_slider', function(data) {
    let val = Number(data.value);
    if (val >= 1 && val <= 1000) {
        humerus_slider.value = val;
        humerus_output.textContent = val;
        humerus_input.value = val;
    }
});

// Mostrar el valor inicial
forearm_output.innerHTML = forearm_slider.value;

// Actualizar el valor mostrado cuando el slider cambia
forearm_slider.oninput = function() {
    forearm_output.textContent = this.value;
    forearm_input.value = this.value;
}

// Actualizar el slider cuando el input cambia
forearm_input.oninput = function() {
    let val = Number(this.value);
    if (val >= 1 && val <= 1000) {
        forearm_slider.value = val;
        forearm_output.textContent = val;
    }
}

socket.on('update_humerus_slider', function(data) {
    let val = Number(data.value);
    if (val >= 1 && val <= 1000) {
        forearm_slider.value = val;
        forearm_output.textContent = val;
        forearm_input.value = val;
    }
});



/////////// ROS /////////////

// Añadir nodo de ROS
const ros = new ROSLIB.Ros({
    url: 'ws://localhost:9090'
})

ros.on('connection', function () {
    console.log('Conectado a rosbridge');
});

ros.on('error', function () {
    console.log('Error de conexión:', error);
});

ros.on('close', function () {
    console.log('Conexión a rosbridge cerrada');
});

// Chasis
// Crear publisher hacia cmd_vel
const velPub = new ROSLIB.Topic({
    ros: ros,
    name : '/cmd_vel',
    messageType : 'geometry_msgs/Twist'
})

var vel = 150;
window.addEventListener("keydown", (event) => {
    const keyMap = {
        "w": {linear: vel, angular:0},
        "a": {linear: 0, angular:-vel},
        "s": {linear:-vel, angular:0},
        "d": {linear: 0, angular:vel},
        "x": {linear: 0, angular:0},
    };

    if (keyMap[event.key]) {
        sendVelocities(keyMap[event.key].linear, keyMap[event.key].angular)
    }
});

// Enviar comandos
function sendVelocities(linearV, angularV) {
    // Crear mensaje tipo Twist
    var twist = new ROSLIB.Message({
        linear: {
            x : linearV,
            y : 0,
            z : 0
        },
        angular : {
            x : 0,
            y : 0,
            z : angularV
        }
    });

    // Enviar mensaje a tópico /cmd_vel
    velPub.publish(twist);
}

// Escuchar el tópico a donde se publicann los mensajes GPS
const gpsListener = new ROSLIB.Topic({
    ros : ros,
    name : '/gps_coords',
    messageType : 'geometry_msgs/Vector3'
});

gpsListener.subscribe(function (message) {
    document.getElementById('latitude').textContent = message.latitude.toFixed(6);
    document.getElementById('longitude').textContent = message.longitude.toFixed(6);
    document.getElementById('altitude').textContent = message.altitude.toFixed(2);
});

const armListener = new ROSLIB.Topic({
    ros : ros,
    name : '/actuators/command',
    messageType : 'std_msgs/Int16MultiArray'
});

armListener.subscribe(function (message) {
    document.getElementById('humerus_pos_input').textContent = message[0];
    document.getElementById('humerus_pos_input').textContent = message[1];
});