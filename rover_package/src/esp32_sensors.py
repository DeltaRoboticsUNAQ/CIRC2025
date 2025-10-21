#/usr/bin/env python3

import rospy

import serial
from serial import SerialException
from time import sleep 
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64
import json

def main():
    # Declarar nodo de ROS
    rospy.init_node('gps_serial_node')
    
    # Configurar puerto Serial a partir de datos en archivo launch. '/dev/ttyUSB0' y 115200 por defecto respectivamente. 
    port = rospy.get_param('/esp32_port', '/dev/ttyUSB0')
    baudrate = rospy.get_param('/esp32_baudrate', 115200)
    
    # ROS GPS publisher
    gps_pub =  rospy.Publisher('/gps_coords', Vector3, queue_size=10)
    
    # ROS Geiger publisher
    geiger_pub = rospy.Publisher('/geiger', Float64, queue_size=10)
    
    # Intentar conectar a puerto serial con timeout de 5 segundos. 
    try: 
        ser = serial.Serial(port, baudrate, timeout=5)
        rospy.loginfo(f"Conectado a {port}")
    except serial.SerialException as e:
        rospy.logerr(f"No se pudo abrir el puerto serial: {e}")
        return
    
    rate = rospy.Rate(10) # 10 Hz
    
    while not rospy.is_shutdown():
        try:
            # Recibir linea 
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            
            # Separar linea por comas y guardar array de strings en coords. 
            data = line.split(',')
            
            if data[0] == 'GPS':
            
                lat = data[1]
                lon = data[2]
                alt = 0 # coords[2]
                
                msg = Vector3()
                msg.x = lat
                msg.y = lon
                msg.z = alt
                
                gps_pub.publish(msg)
                rospy.loginfo(f"Publishing GPS: {msg.x}, {msg.y}")
            
            elif data[0] ==  'Geiger':
                
                msg = Float64
                msg = data[1]
                
                geiger_pub.publish(msg)
                rospy.loginfo(f"Publishing Gieger Data: {msg}")
            
        except Exception as e:
            rospy.logwarn(f"Error leyendo/parsing: {e}")

        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass