#!/usr/bin/env python3

import roslibpy
import requests

import hid
from keyboard import is_pressed, read_key
import pygame

from time import sleep
from time import time

# Commit desde VSCode!
DELAY = 0.5

# ROS
# ROS Websocket
ros = roslibpy.Ros(host='192.168.1.30', port=9090)
ros.run()

# Chassis velocity publisher
vel_pub = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')

# Arm humerus and forearm publisher
arm_pub = roslibpy.Topic(ros, '/actuators/command', 'std_msgs/Int16MultiArray')  

# Wrist publisher
wrist_pub = roslibpy.Topic(ros, '/wrist/command', 'std_msgs/Int16MultiArray')

# Open joystick dev
def open_joystick():
    for device in hid.enumerate():
        print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
        
    joystick = hid.device()
    joystick.open(0x12bd, 0xa02f)
    joystick.set_nonblocking(True)

    print("Initializing joystick...")
    sleep(1.5)
    print("Ready")
    
    return joystick

buttons = {
    'trigger': False,
    'button2': False,
    'button3': False,
    'button4': False,
    'button5': False,
    'button6': False,
    'button7': False,
    'button8': False,
    'button9': False,
    'button10': False,
    'button11': False,
    'button12': False,
}

sticks = {
    'lateral': 127,
    'front': 127,
    'twist': 127,
    'throttle': 255,
}


# Obtener input de joystick y publicarlo/mandarlo al servidor
def handle_joystick_input(joystick):
    global last_t
    t = time()
    
    report = joystick.read(64)
    if report and (last_t - t < DELAY):
        #print(report)
        buttons = {
            'trigger': report[6]==1,
            'button2': report[6]==2,
            'button3': report[6]==4,
            'button4': report[6]==8,
            'button5': report[6]==16,
            'button6': report[6]==32,
            'button7': report[6]==64,
            'button8': report[6]==128,
            'button9': report[7]==1,
            'button10': report[7]==2,
            'button11': report[7]==4,
            'button12': report[7]==8,
        }
        
        for b in buttons:
            if buttons[b]:
                print(b)
    
        sticks = {
            'lateral': report[0],
            'front': report[1],
            'twist': report[2],
            'throttle': report[4],
        }
        
        last_t = time()
        
        return buttons, sticks, True

if __name__ == '__main__':
    print()