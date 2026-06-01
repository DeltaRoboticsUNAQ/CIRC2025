#!/usr/bin/env python3

import rospy
from geomtry msgs.msg import Twist
from roboclaw_3 import RoboClaw

address = 0x80
thresh = 30

class ChassiControl:
    def __init__(self, serial_port='/dev/ttyACM0', baudrate=115200):
        self.rc = RoboClaw(serial_port, baudrate)
        rc.Open()
        
        rospy.init_node('chassis_control')
        rospy.Subscriber('cmd_vel', Twist, self.cmd_vel_callback, queue_size=1)
        rospy.loginfo("ChassiControl node started, listening to cmd_vel.")
        
    def cmd_vel_callback(self, msg):
        # Extraer velocidades lineal y angular
        linear = int(msg.linear.x)
        angular = int(msg.angular.z)
        rospy.loginfo(f"Message received: Linear: {linear}, Angular: {angular}")
        
        # Enviar comando a RoboClaw
        self.rc_command(linear)
        
    def run(self):
        rospy.spin()
        
    def rc_command(self, linear, angular):
        try:
            if abs(angular) > thresh:
                if angular > 0:
                    self.rc.ForwardM1(address,127)
                    self.rc.BackwardM2(address,127)
                elif angular < 0:
                    self.rc.BackwardM1(address,127)
                    self.rc.ForwardM2(address,127)
                
            else:
                if linear > 0:
                    self.rc.ForwardM1(address,linear)
                    self.rc.ForwardM2(address,linear)
                    
                else:
                    self.rc.BackwardM1(address, linear)
                    self.rc.BackwardM2(address, linear)
        
        except:
            rospy.loginfo("RoboClaw command failed.")
            

if __name__ == '__main__':
    try: 
        controller = ChassiControl()
        controller.run()
    except rospy.ROSInterruptException:
        pass