#!/usr/bin/env python3

import roslibpy

import requests

import hid
from keyboard import is_pressed, read_key
import pygame

from time import sleep
from time import time
import logging
import numpy as np

DELAY = 0.5
HUMERUS_POS_URL = 'http://192.168.1.30:5000/move_humerus/'
FOREARM_POS_URL = 'http://192.168.1.30:5000/move_forearm/'

def move_slider(value, url):
    url = f"{url}{value}"
    try:
        response = requests.get(url)
        print(response.text)
    except Exception  as e:
        print("Error sending value:", e)

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

# Update position and move_slider
def update(sticks, last_sticks, s, url):
    if abs(sticks[s]-last_sticks[s])>20:
            try:
                response = requests.get(url)
                last_value = response.json()['value']
                forearm_pos = last_value + sticks[s] - 127
                move_slider(forearm_pos, FOREARM_POS_URL)
                return True
            except:
                return False
        
# Obtener input de joystick y publicarlo/mandarlo al servidor
def handle_joystick_input():
    global t
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
            'laterial': report[0],
            'front': report[1],
            'twist': report[2],
            'throttle': report[4],
        }
        
        humerus_updated = update(sticks, last_sticks, 'front', 'http://192.168.1.30/get_humerus_pos')
        forearm_updated = update(sticks, last_sticks, 'front', 'http://192.168.1.30/get_forearm_pos')
            
        if (humerus_updated and forearm_updated):
            message = {'data' : [humerus_pos, forearm_pos, 0.0]}
            arm_pub.publish(message)
            humerus_updated = False
            forearm_updated = False
    

if __name__ == '__main__':
    # ROS websocket
    ros = roslibpy.Ros(host='192.168.1.30', port=9090)
    ros.run()
    
    # Chassis velocity publisher
    vel_pub = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')
    
    # Arm humerus and forearm publisher
    arm_pub = roslibpy.Topic(ros, '/actuators/command', 'std_msgs/Int16MultiArray')
    
    joystick = open_joystick()
    
    report = joystick.read(64)
    last_sticks = {
        'laterial': report[0],
        'front': report[1],
        'twist': report[2],
        'throttle': report[4],
    }
    last_t = time()

    linear = 0.0
    angular = 0.0

    humerus_pos = 100
    forearm_pos = 100

    wrist_right_pos = 0
    wrist_left_pos = 0

    base_pos = 0
    end_effector_pos = 0
    
    while ros.is_connected:
        handle_joystick_input()