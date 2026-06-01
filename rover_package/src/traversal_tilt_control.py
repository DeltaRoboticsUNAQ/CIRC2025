#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Vector3
import serial

class TiltControl:
    def __init__(self, serial_port='/dev/ttyACM1', baudrate=9600):
        self.ser = serial.Serial(serial_port, baudrate, timeout=1)
        rospy.init_node('tilt_control')
        rospy.Subscriber('tilt_cmd', Vector3, self.tilt_callback)
        rospy.loginfo("Tilt Control node started, listening to tilt_cmd.")

    def tilt_callback(self, msg):
        # Extraer velocidades para stand con cámara
        humerus = int(msg.x)
        forearm = int(msg.y)
        base = int(msg.z)
        
        # Comando formateado
        command = f"{humerus},{forearm},{base}\n"
        self.ser.write(command.encode('utf-8'))
        rospy.loginfo(f"\nSent to Arduino2: {command.strip()}")

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        controller = TiltControl()
        controller.run()
    except rospy.ROSInterruptException:
        pass  