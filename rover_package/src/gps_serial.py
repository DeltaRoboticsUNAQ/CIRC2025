#!/usr/bin/env python3

# Instalación necesaria:
# sudo apt install ros-noetic-sensor-msgs

import rospy

import serial
from serial import SerialException
from time import sleep 
from geometry_msgs.msg import Vector3
import json

def main():
    rospy.inti_node('gps_serial_node')
    port = rospy.get_param('/esp32_port', '/dev/ttyUSB0')
    baudrate = rospy.get_param('/esp32_baudrate', 115200)
    
    pub =  rospy.Publisher('/gps_coords', Vector3, queue_size=10)
    
    try: 
        ser = serial.Serial(port, baudrate, timeout=1)
        rospy.loginfo(f"Conectado a {port}")
    except serial.SerialException as e:
        rospy.logerr(f"No se pudo abrir el puerto serial: {e}")
        return
    
    rate = rospy.Rate(10) # 10 Hz
    
    while not rospy.is_shutdown():
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            
            lat = line[0]
            lon = line[1]
            alt = 0
            
            msg = Vector3()
            msg.x = lat
            msg.y = lon
            msg.z = alt
            
            pub.publish(msg)
            
        except Exception as e:
            rospy.logwarn(f"Error leyendo/parsing: {e}")

        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
