#!/usr/bin/env python3

from time import sleep
import time
import serial
from serial import SerialException

from flask import Flask, request, Response, jsonify, render_template

from roboclaw_3 import RoboClaw
import rospy 

import cv2

from geometry_msgs.msg import Twist

from packetSerial import SerialHandler
from camera import gen_aruco

header = 'INIT'
voltage = 10.0
currents = 1.0
velocities = {"linear": 0.0, "angular": 0.0}

# //////////////////////////////////////////////////////////////////
# SERIAL
esp32_config = {
        "port": "/dev/ttyUSB0", 
        "baudrate": 115200, 
        "id": 0x40}

esp32Handler = SerialHandler(esp32_config)

# //////////////////////////////////////////////////////////////////
# FLASK SERVER
app = Flask(__name__)

@app.route('/')
def index():
    global voltage
    global currents 
    data = {
        'title': 'T1LIN',
        'voltage': voltage,
        'currents': currents
        }
    return render_template('index.html', data=data)

@app.route('/video_feed')
def video_feed():
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    return Response(gen_aruco(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# TELEMETRÍA 
@app.route('/voltage_stream', methods=['GET'])
def get_voltage():
    return Response(voltage, content_type="text/event-stream")

@app.route('/currents_stream', methods=['GET'])
def get_currents():
    return Response(currents, content_type="text/event-stream")

def gps_event():
    while True:
        try: 
            header, data = esp32Handler.parse_line()
            if header == 'GPS':
                try:
                    gps_x = data['gps_x']
                    gps_y = data['gps_y']
                    
                    yield f"data:{gps_x},{gps_y}\n\n"
                except ValueError:
                    continue
            time.sleep(0.1)
        except SerialException as e:
            yield f"data: ERROR: {e}\n\n"
            
@app.route('/gps_stream')
def gps_stream():
    return Response(gps_event(), mimetype='text/event-stream')       
        

# CONTROL
@app.route('/velocities', methods=['GET', 'POST'])
def receive_velocities():
    global velocities  # Usar la variable global
    data = request.get_json()

    if not data or "linear" not in data or "angular" not in data:
        return jsonify({"error": "Invalid data"}), 400

    velocities["linear"] = data["linear"]
    velocities["angular"] = data["angular"]

    print(f"Received. Linear: {data['linear']}, Angular: {data['angular']}")
    
    publish_velocities(data['linear'], data['angular'])
    
    return jsonify({"status": "ok", "linear": velocities["linear"], "angular": velocities["angular"]})

@app.route('/velocities', methods=['GET'])
def get_velocities():
    global velocities
    return jsonify(velocities), 200


# //////////////////////////////////////////////////////////////////
# ROS

# Nodo de ROS
rospy.init_node('datalink', anonymous=True)

chassisPub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

# Crear mensaje Twist y publicarlo a /cmd_vel
def publish_velocities(linear, angular):
    vel_msg = Twist()
    
    vel_msg.linear.x = linear
    vel_msg.linear.y = 0
    vel_msg.linear.z = 0
    
    vel_msg.angular.z = angular
    vel_msg.angular.y = 0
    vel_msg.angular.z = 0
    
    chassisPub.publish(vel_msg)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    