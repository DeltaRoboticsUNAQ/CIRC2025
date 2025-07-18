#!/usr/bin/env python3

# Servidor de Flask que se usa principalmente para:
# - Servir el HTML de la interfaz
# - Facilitar la visualización del marcado del Aruco en la página principal. 

from time import sleep
import time

from flask import Flask, request, Response, jsonify, render_template
import json

import rospy 

import cv2
from geometry_msgs.msg import Twist

# FLASK SERVER
app = Flask(__name__)

@app.route('/')
def index():
    data = {
        'title': 'T1LIN',
        }
    return render_template('index.html', data=data)

# Diccionario de aruco usado
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
# ROS

# Nodo de ROS
rospy.init_node('server_aruco', anonymous=True)
aruco_publisher = rospy.Publisher('/aruco', Twist, queue_size=10)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    