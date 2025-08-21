# Programa para recibir inputs de un control de PS4 para controlar rover a través de roslibpy. 
# Para Windows 11

# Actualizado desde GitHub!

import pygame
import sys

import roslibpy

from time import sleep
from time import time

# Constantes
DELAY = 0.05
DRIFT = 0.1
THRESHOLD = 0.05
ARM_SENSITIVITY = 1
WRIST_SENSITIVITY = 1
SATURN_MOTOR_ENCODER_PULSES = 2500

# /////////////////////////////////////////////////////////////////
# ROS Websocket con roslibpy
ros  = roslibpy.Ros(host='192.168.1.30', port=9090)
ros.run() # Inicializar Websocket

# Chassis velocity publisher
chassis_pub = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')

# Arm humerus and forearm publisher
arm_pub = roslibpy.Topic(ros, '/actuators/command', 'std_msgs/Int16MultiArray')

# Wrist publisher
wrist_pub = roslibpy.Topic(ros, '/wrist/command', 'std_msgs/Int16MultiArray')

# Arm humerus and forearm position subscriber

# ///////////////////////////////////////////////////////////////
# Joystick
# Listar joysticks
def list_joysticks():
    
    count = pygame.joystick.get_count()
    if count == 0:
        print("No joysticks detected. Conect a controller and run again.")
        sys.exit()
        return False
    
    print(f"{count} detected joystick(s): ")
    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        print(f" {i}: {js.get_name()}")
    return True

# Se enlistan joysticks. Si se regresa False, se termina el código con error.
if not list_joysticks():
    sys.exit(1)
    
# Use first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"\nUsing joystick: {joystick.get_name()}")
print("Press buttons or move sticks. Ctrl+C to exit.\n")

# Map buttons
button_names = {
    0: 'X',
    1: 'O',
    2: 'Square',
    3: 'Triangle',
    4: 'L1',
    5: 'R1',
    6: 'Share',
    7: 'Options',
    8: 'L3',
    9: 'R3',
    11: 'Up',
    12: 'Down',
    13: 'Left',
    14: 'Right'
}

# Revisar estado previo para detectar cambios y evitar inputs repetidos
buttons_prev_states = [False] * joystick.get_numbuttons()
axis_prev = [0.0] * joystick.get_numaxes()
hat_prev = (0, 0)

modes = ["Chassis", "Arm", "End Effector"]
mode_idx = 0

# ///////////////////////////////////////////////////////////////
# Funciones de movimiento con control

def change_mode():
    global mode_idx
    global modes
    mode_idx = (mode_idx + 1) % len(modes)
    print(f"Switched to {modes[mode_idx]} mode.")

def chassis_command(event):
    if event == 'Up':
        linear_x = 255.0
        angular_z = 0.0
    elif event == 'Down':
        linear_x = -255.0
        angular_z = 0.0
    elif event == 'Right':
        linear_x = 0.0
        angular_z = 255.0
    elif event == 'Up':
        linear_x = 0.0
        angular_z = -255.0
    elif event == 'Stop':
        linear_x = 0.0
        angular_z = 0.0
    try:
        twist_msg = {
        'linear': {'x': linear_x, 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': angular_z}
        }
        chassis_pub.publish(twist_msg)
        return True
    except:
        print(f"Chassis command not recognized: {event}")
        return False

right_motor_last_pos = 0
left_motor_last_pos = 0

def ef_command(event):
    global right_motor_last_pos
    global left_motor_last_pos
    '''try:
        right_motor_last_pos = 
        left_motor_last_pos =
    except:
        pass'''
    # Levantar 20 grados
    if event == 'Up':
        right_motor_pos = right_motor_last_pos + SATURN_MOTOR_ENCODER_PULSES/360*20
        left_motor_pos = left_motor_last_pos + SATURN_MOTOR_ENCODER_PULSES/360*20
    # Bajar 20 grados
    elif event == 'Down':
        right_motor_pos = right_motor_last_pos - SATURN_MOTOR_ENCODER_PULSES/360*20
        left_motor_pos = left_motor_last_pos - SATURN_MOTOR_ENCODER_PULSES/360*20
    elif event == 'Right':
        right_motor_pos = right_motor_last_pos + SATURN_MOTOR_ENCODER_PULSES/360*45
        left_motor_pos = left_motor_last_pos - SATURN_MOTOR_ENCODER_PULSES/360*45
    elif event == 'Left':
        right_motor_pos = right_motor_last_pos - SATURN_MOTOR_ENCODER_PULSES/360*45
        left_motor_pos = left_motor_last_pos + SATURN_MOTOR_ENCODER_PULSES/360*45
    
    try:
        wrist_message = {'data' : [right_motor_pos, left_motor_pos, 0.0]}
        wrist_pub.publish(wrist_pub)
        
        right_motor_last_pos = right_motor_pos
        left_motor_last_pos = left_motor_pos
        return True
    except:
        print(f"Wrist command failed: {wrist_message}")
        return False
    
def arm_command(event):
    # Retraer por completo
    if event == 'Up':
        humerus_pos = 0.0
        forearm_pos = 0.0
    # Extender por completo
    elif event == 'Down':
        humerus_pos = 1000
        forearm_pos = 1000
    try:
        wrist_message = {'data' : [humerus_pos, forearm_pos, 0.0]}
        arm_pub.publish(wrist_pub)
        
        return True
    except:
        print(f"Wrist command failed: {wrist_message}")
        return False
    
def handle_event(event):
    global modes
    global mode_idx
    if event == 'O':
        full_stop()
        return
    if event == 'R3':
        change_mode()
        return True
    if modes[mode_idx] == "Chassis":
        chassis_command(event)
    elif modes[mode_idx] == "Arm":
        arm_command(event)
    elif modes[mode_idx] == "End Effector":
        ef_command(event)
    elif event == 'default':
        print(event)


def chassis_axis_command(axis_values):
    try:
        linear_x = ((-axis_values[1]-axis_values[3])/2.0)*255.0
        angular_z = ((-axis_values[1]+axis_values[3])/2.0)*255.0
        twist_msg = {
        'linear': {'x': linear_x, 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': angular_z}
        }
        chassis_pub.publish(twist_msg)
        return True
    except:
        print(f"Chassis axis failed: {axis_values}")
        return False

humerus_last_pos = 0.0
forearm_last_pos = 0.0

def arm_axis_command(axis_values):
    # Obtener valores de los publicados por ROS si es posible
    global humerus_last_pos
    global forearm_last_pos
    try: 
        humerus_pos = humerus_last_pos + axis_values[1]*ARM_SENSITIVITY
        forearm_pos = forearm_last_pos + axis_values[3]*ARM_SENSITIVITY
    # De lo contrario, usar los valores del programa
    except:
        humerus_pos = humerus_last_pos + axis_values[1]*ARM_SENSITIVITY
        forearm_pos = forearm_last_pos + axis_values[3]*ARM_SENSITIVITY
    
    try:
        arm_message = {'data' : [humerus_pos, forearm_pos, 0.0]}
        arm_pub.publish(arm_message)
        
        humerus_last_pos = humerus_pos
        forearm_last_pos = forearm_pos
        return True
    except:
        print(f"Arm command failed: {arm_message}")
        return False

def ef_axis_command(axis_values):
    global right_motor_last_pos
    global left_motor_last_pos
    # Obtener valores de los publicados por ROS si es posible
    '''try:
        right_motor_last_pos = 
        left_motor_last_pos =
    except:
        pass'''
    if abs(axis_values[2])>abs(axis_values[3]):
        right_motor_pos = right_motor_last_pos + axis_values[2]*WRIST_SENSITIVITY
        left_motor_pos = left_motor_last_pos + axis_values[2]*WRIST_SENSITIVITY
    else:
        right_motor_pos = right_motor_last_pos + axis_values[2]*WRIST_SENSITIVITY
        left_motor_pos = left_motor_last_pos - axis_values[2]*WRIST_SENSITIVITY
    
    try:
        wrist_message = {'data' : [right_motor_pos, left_motor_pos, 0.0]}
        wrist_pub.publish(wrist_pub)
        
        right_motor_last_pos = right_motor_pos
        left_motor_last_pos = left_motor_pos
        return True
    except:
        print(f"Wrist command failed: {wrist_message}")
        return False

def handle_axis(axis_values):
    if modes[mode_idx] == "Chassis":
        chassis_axis_command(axis_values)
    elif modes[mode_idx] == "Arm":
        arm_axis_command(axis_values)
    elif modes[mode_idx] == "End Effector":
        ef_axis_command(axis_values)

def full_stop():
    print("Full stop")
    sleep(5)
    axis_stop_values = [0.0] * joystick.get_numaxes()
    
    chassis_command('Stop')
    arm_axis_command(axis_stop_values)
    ef_axis_command(axis_stop_values)

try:
    while True:
        # Procesar eventos para mantener acutalizado el sistema interno
        for event in pygame.event.get():
            # Eventos 
            if event.type == pygame.JOYBUTTONDOWN:
                name = button_names.get(event.button, f"Button {event.button}")
                print(f"[EVENT] {name} pressed")
                handle_event(button_names.get(event.button, 'default'))
            elif event.type == pygame.JOYBUTTONUP:
                name = button_names.get(event.button, f"Button {event.button}")
                print(f"[EVENT] {name} released")
            elif event.type == pygame.JOYHATMOTION:
                if event.value != (0, 0):
                    print(f"[EVENT] D-Pad: {event.value}")
            elif event.type == pygame.JOYAXISMOTION:
                val = event.value
                if abs(val) > DRIFT:
                    print(f"[EVENT] Axis {event.axis} moved: {val:.2f}")
                    
        # Botones (solo si cambian)
        for i in range(joystick.get_numbuttons()):
            actual = bool(joystick.get_button(i))
            if actual != buttons_prev_states[i]:
                name = button_names.get(i, f"Botón {i}")
                state = "pressed" if actual else "released"
                print(f"[POLL] {name} {state}")
                buttons_prev_states[i] = actual

        # Ejes (con deadzone y cambio significativo)
        axis_nums = joystick.get_numaxes()
        for i in range(axis_nums):
            val = joystick.get_axis(i)
            if abs(val) < DRIFT:
                val = 0.0  # estabilizar en zona muerta
            # Solo reportar si cambio mayor a umbral pequeño para evitar ruido
            if abs(val - axis_prev[i]) > THRESHOLD:
                print(f"[POLL] Eje {i} movido: {val:.2f}")
                axis_prev[i] = val
                handle_axis(axis_prev)

        # Hat / D-Pad
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            if hat != hat_prev:
                if hat != (0, 0):
                    print(f"[POLL] D-Pad: {hat}")
                else:
                    print("[POLL] D-Pad centrado")
                hat_prev = hat

        # Pequeña pausa para no saturar CPU
        sleep(DELAY)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pygame.quit()
