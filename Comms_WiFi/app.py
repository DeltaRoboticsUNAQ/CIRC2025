#!/usr/bin/env python3

from time import sleep
import time
import serial
from serial import SerialException
from flask import Flask, request, Response, jsonify, render_template 
from roboclaw_3 import Roboclaw
import cv2
import json

app = Flask(__name__)

# Variable global para almacenar las velocidades
velocities = {"linear": 0.0, "angular": 0.0}

# Roboclaw adress
address = 0x80

# Página principal. Regresa plantilla index.html
@app.route('/')
def index():
    voltage = roboclaw.ReadMainBatteryVoltage(address)[1] # Obtiene el voltaje actual
    currents = roboclaw.ReadCurrents(address)
    data = {
            'title': 'T1LIN',
            'voltage': voltage,
            'currents': currents
            }
    return render_template('index.html', data=data)


### CAMARA ###
def gen(cam):
    while True:
        ret, frame = cam.read()

        if not ret:
            continue

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        jpeg_bytes = jpeg.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
### FIN CAMARA ###

### CONTROL ###
# Función para recibir velocidades con joystick. Se requiere programa de control desde laptop para postearlas en /velocities
@app.route('/velocities', methods=['GET', 'POST'])
def receive_velocities():
    global velocities  # Usar la variable global
    data = request.get_json()

    if not data or "linear" not in data or "angular" not in data:
        return jsonify({"error": "Invalid data"}), 400

    velocities["linear"] = data["linear"]
    velocities["angular"] = data["angular"]

    print(f"Received. Linear: {velocities['linear']}, Angular: {velocities['angular']}")
    
    PWM(velocities["linear"], velocities["angular"])

    return jsonify({"status": "ok", "linear": velocities["linear"], "angular": velocities["angular"]})

@app.route('/velocities', methods=['GET'])
def get_velocities():
    return jsonify(velocities), 200

def PWM(vel_linear, vel_angular_der):
    if abs(vel_angular_der) > 20:
        if vel_angular_der > 0:
            roboclaw.ForwardM1(address, vel_angular_der)
            roboclaw.BackwardM2(address, vel_angular_der)
            print("derecha")
            print(vel_angular_der)
        elif vel_angular_der < 0:
            roboclaw.BackwardM1(address, abs(vel_angular_der))
            roboclaw.ForwardM2(address, abs(vel_angular_der))
            print("izquierda")
            print(vel_angular_der)

    elif vel_linear < 0:
        roboclaw.ForwardM1(address, abs(vel_linear))
        roboclaw.ForwardM2(address, abs(vel_linear))
    elif vel_linear > 0:
        roboclaw.BackwardM1(address, abs(vel_linear))
        roboclaw.BackwardM2(address, abs(vel_linear))
    else:
        roboclaw.ForwardM1(address, 0)
        roboclaw.ForwardM2(address, 0)
### FIN CONTROL ###

### TELEMETRÍA ###
def gen_voltage():
    while True:
        voltage = roboclaw.ReadMainBatteryVoltage(address)[1]
        time.sleep(0.1)  # Simula un nuevo dato cada 1/10 s
        data = {"voltage": voltage}
        # yield jsonify({"currents":  roboclaw.ReadMainBatteryVoltage(address)[1]})
        yield f"data: {json.dumps(data)}\n\n" 
    
def gen_currents():
    while True:
        currents = currents = roboclaw.ReadCurrents(address)
        time.sleep(0.1)  # Simula un nuevo dato cada 1/10 s
        data = {"currents": currents}
        # yield jsonify({"currents":  roboclaw.ReadMainBatteryVoltage(address)[1]})
        yield f"data: {json.dumps(data)}\n\n" 

@app.route('/voltage_stream', methods=['GET'])
def get_voltage():
    return Response(gen_voltage(), content_type="text/event-stream")

@app.route('/currents_stream', methods=['GET'])
def get_currents():
    return Response(gen_currents(), content_type="text/event-stream")
### FIN TELEMETRÍA ###

def open_serial_(baudrate, port):
    while True:
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            return ser
        except SerialException:
            print("Connection failed. Retrying...")
            sleep(1) 

if __name__ == '__main__':
    roboclaw = Roboclaw("/dev/ttyACM0", 38400)
    roboclaw.Open()
    print("Roboclaw open\n")
    app.run(host='0.0.0.0', port=5000, debug=True)