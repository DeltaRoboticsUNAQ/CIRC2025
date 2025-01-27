#!/usr/bin/env python

from datalink import *
import hid
import serial
from serial import SerialException
from serial.tools import list_ports
from keyboard import is_pressed, read_key
from time import sleep
from time import time

# Constante que representa la posición neutra del joystick
standard = 127.0

# Función que mapea los valores del joystick a velocidades lineales
def map_val_lin(lineal):
    if lineal == standard:
        return 0.0
    elif lineal < standard:
        return (standard - lineal)
    else:
        return (standard + 1) - lineal

# Función que mapea los valores del joystick a velocidades angulares
def map_val_ang(angular):
    if angular == standard:
        return 0.0, 0.0
    elif angular < standard:
        # Girando a la izquierda
        left_motor = -(standard - angular)
        right_motor = standard - angular
    else:
        # Girando a la derecha
        left_motor = angular - (standard + 1)
        right_motor = -(angular - (standard + 1))
    return left_motor, right_motor

# Función para abrir el puerto serial
def open_serial(dev_):
    while True:
        try:
            print('Puertos disponibles: ')
            port = list(list_ports.comports())
            for p in port:
                print(p.device)
            
            puerto = input(f'Escriba el puerto para {dev_}: ')
            dev = serial.Serial(puerto, 9600, timeout=1)
            break
        
        except SerialException:
            print('No se pudo abrir el puerto serial')
            print("\n")
            sleep(2)
    return dev

if __name__ == '__main__':
    try:
        ser = open_serial_window()
        joystick = open_joystick()
        last_lineal = 127
        last_angular = 127  
        threshold = 1  # Umbral de cambio
        while True:
            if ser:
                try:
                    report = joystick.read(8)
                    if report:
                        lineal = report[1]
                        angular = report[2]
                            
                        # Solo enviar si hay un cambio significativo
                        if abs(lineal - last_lineal) > threshold or abs(angular - last_angular) > threshold:
                            vel_lineal = map_val_lin(lineal)
                            vel_left_motor, vel_right_motor = map_val_ang(angular)
                            
                            # Topamos el valor de la velocidad de giro para giros mas suaves
                            max_angular = 90
                            if vel_right_motor > max_angular:
                                cmd = pqt_build(11, [int(vel_lineal), int(max_angular)])
                            else:
                                cmd = pqt_build(11, [int(vel_lineal), int(vel_right_motor)])
                            
                            ser.writelines(cmd)
                            print(int(vel_lineal))
                            print(int(vel_right_motor))
                            print(cmd)
                            
                            last_lineal = lineal
                            last_angular = angular
                            
                    if is_pressed('SHIFT') and read_key() == 'S':
                        cmd = pqt_build(11, [0, 0])
                        print("S")
                        print(cmd)
                        ser.write(cmd)
                        
                    if is_pressed('SHIFT') and read_key() == 'W':
                        cmd = pqt_build(11, [1, 0])
                        print("W")
                        print(cmd)
                        ser.write(cmd)
                    
                    if is_pressed('SHIFT') and read_key() == 'Q':
                        ser.close()
                        break
                    
                    
                        
                except SerialException as e:
                        print(f'Error: {e}')
                        
                
                
            else:
                break 
    except KeyboardInterrupt:
        print('\n   --- Programa interrumpido por el usuario. ---')
        
