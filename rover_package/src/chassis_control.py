#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import serial

from packetSerial import SerialHandler

class ChassisControl:
    def __init__(self, serial_port='/dev/ttyACM0', baudrate=9600):
        self.ser = serial.Serial(serial_port, baudrate, timeout=1)
        rospy.init_node('chassis_control')
        rospy.Subscriber('cmd_vel', Twist, self.cmd_vel_callback, queue_size=1)
        rospy.loginfo("ChassisControl node started, listening to cmd_vel.")

    def cmd_vel_callback(self, msg):
        # Extraer velocidades lineal y angular
        linear = int(msg.linear.x)
        angular = int(msg.angular.z)
        # Comando formateado
        command = f"{linear},{angular}\n"
        self.ser.write(command.encode('utf-8'))
        rospy.loginfo(f"\nSent to Arduino: {command.strip()}")

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        controller = ChassisControl()
        controller.run()
    except rospy.ROSInterruptException:
        pass