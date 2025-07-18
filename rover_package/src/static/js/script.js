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

// Crear publisher hacia cmd_vel
const cmdVel = new ROSLIB.Topic({
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

// Enviar comandos de WASD
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
    cmdVel.publish(twist);
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
