import roslibpy

import hid
from keyboard import is_pressed, read_key
import pygame

from time import sleep
from time import time
import numpy as np

# Open joystick dev
for device in hid.enumerate():
    print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
    
joystick = hid.device()
joystick.open(0x12bd, 0xa02f)
joystick.set_nonblocking(True)

ros = roslibpy.Ros(host='localhost', port=9090)
ros.run()

vel_pub = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')

while ros.is_connected:
    
    t = time()
    linear = 0.0
    angular = 0.0
    
    last_linear = linear # Update last linear
    last_angular = angular # Update last angular
    
    report = joystick.read(64)
    if report:
        print(report)
        linear = report[]
        
        vel_pub.publish(roslibpy.Message({
        'linear': {'x':linear, 'y':0.0, 'z':0.0},
        'angular': {'x': 0.0, 'y':0.0, 'z':angular}
        }))
    
    sleep(0.1)
    