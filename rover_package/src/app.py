#!/usr/bin/env python3

# Servidor de Flask que se usa principalmente para:
# - Servir el HTML de la interfaz
# - Facilitar la visualización del marcado del Aruco en la página principal. 
# - Asistir funciones para actualizar sliders.

from time import sleep
import time

from flask import Flask, request, Response, jsonify, render_template
from flask_socketio import SocketIO, emit

import json
import response

import rospy 
from std_msgs import Int8, Int16MultiArray

import cv2
from geometry_msgs.msg import Twist

# FLASK SERVER
app = Flask(__name__)
socketio = SocketIO(app)

# Nodo de ROS
rospy.init_node('web_server', anonymous=True)
aruco_publisher = rospy.Publisher('/aruco', Int8, queue_size=10)

humerus_pos = 0
forearm_pos = 0

def arm_callback(data):
    global humerus_pos 
    global forearm_pos
    
    humerus_pos = data[0]
    forearm_pos = data[1]
    
    move_humerus_slider(humerus_pos)
    move_forearm_slider(forearm_pos)
    
arm_subscriber = rospy.Subscriber('/actuators/command', Int16MultiArray, arm_callback)

@app.route('/')
def index():
    data = {
        'title': 'T1LIN',
        }
    return render_template('index.html', data=data)

# Diccionario de aruco usado
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)

def gen_aruco(cam):
    while True:
        ret, frame = cam.read()

        if not ret:
            continue
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar marcadores
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)

        if ids is not None:
            # Dibujar los marcadores detectados
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            # También puedes procesar los IDs aquí si lo necesitas
            print("Marcadores detectados:", ids.flatten())
            # Publish aruco id
            aruco_publisher.publish(ids[0])
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        jpeg_bytes = jpeg.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    return Response(gen_aruco(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
@socketio.on('set_slider')
def handle_set_slider(data):
    global current_value
    current_value = data['value']
    emit('update_slider', data, broadcast=True)

@app.route('/move_humerus/<int:value>')
def move_humerus_slider(value):
    global humerus_pos
    humerus_pos = value
    socketio.emit('update_slider', {'value': value})
    return f"Forearm slider moved to {value}"

@app.route('/move_forearm/<int:value>')
def move_forearm_slider(value):
    global forearm_pos
    forearm_pos = value
    socketio.emit('update_slider', {'value': value})
    return f"Forearm slider moved to {value}"
    
@app.route('/get_humerus_pos')
def get_humerus_pos():
    return jsonify({'value' : humerus_pos})

@app.route('/get_forearm_pos')
def get_forearm_pos():
    return jsonify({'value': forearm_pos})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
    