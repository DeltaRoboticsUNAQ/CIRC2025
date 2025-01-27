#!/usr/bin/env python

# Sebastián López Tena 21 de septiembre de 2024
# bastianlopezt@gmail.com  
# 10153@soyunaq.mx


import serial
from serial import SerialException
from serial.tools import list_ports
import hid
import struct

from keyboard import read_key
from keyboard import is_pressed
from random import uniform
from random import randint
from time import sleep

import PySimpleGUI as sg

# NOTA: Es importante revisar estos dos valores antes de ejecutar el código
BAUDRATE = 115200
SERIAL_PORT = "/dev/USB0"

def add_checksum(bytearray_):
    checksum = sum(bytearray_)
    bytearray_.extend((checksum // 256, checksum % 256))
    return checksum


def checksum(bytearray_):
    received_sum = [0, 0]
    received_sum[0] = bytearray_[-2]
    received_sum[1] = bytearray_[-1]
    
    calculated_sum = [sum(bytearray_[:-2]) // 256, sum(bytearray_[:-2]) % 256]
    
    if received_sum == calculated_sum:
        return True
    else:
        return False


def list_to_bytearray(data_list):
    bytearray_list = bytearray()
    try:
        for item in data_list:
            if isinstance(item, int):
                try:
                    bytearray_list.extend(item.to_bytes(1, "big"))
                except OverflowError:
                    bytearray_list.extend(item.to_bytes(1, "big", signed=True))
                except:
                    print("Integer error")
                
            elif isinstance(item, float):
                bytearray_list.extend(struct.pack('f', item))
                
            elif isinstance(item, bool):
                bytearray_list.extend(b'\x01' if item else b'\x00')
                    
            elif isinstance(item, str):
                try:
                    bytearray_list.extend(int(item).to_bytes(1, "big"))
                except ValueError:
                    try:
                        bytearray_list.extend(struct.pack('f', float(item)))
                    except ValueError:
                        pass
                    
        return bytearray_list
    
    except ValueError:
        return 1
    
    except:
        return 2


def pqt_interpret(bytearray_):
    header = bytearray_[0]
    try:
        if int(header) == 10:
            x = bytearray_[1]
            w = bytearray_[2]
            twist = [x, 0, 0, w, 0, 0]
            return twist, 'Twist'
        
        elif int(header) == 51:
            return None, 'A request'
        
        elif int(header) == 52:
            return None, 'B request'
        
        elif int(header) == 101:
            # Mediciones desde RoboClaw del chasis
            chassis_voltage = struct.unpack('f', bytearray_[1:5])[0]
            chassis_current = struct.unpack('f', bytearray_[5:9])[0]
            chassis_error = int(bytearray_[9])
            
            # Mediciones desde RoboClaw para brazo
            arm_voltage = struct.unpack('f', bytearray_[10:14])[0]
            arm_current = struct.unpack('f', bytearray_[14:18])[0]
            arm_error = int(bytearray_[18])
            
            chassis_temp = int(bytearray_[19])
            
            telemetryA = {'VC':chassis_voltage, 'CC':chassis_current, 'EC':chassis_error, 
                        'VA': arm_voltage, 'CA':arm_current, 'EA':arm_error,
                        'TC': chassis_temp}
            return telemetryA, 'A'
        
        elif int(header) == 102:
            # GPS
            gps_latitude = struct.unpack('f', bytearray_[1:5])[0]
            gps_altitude = struct.unpack('f', bytearray_[5:9])[0]
            
            # IMU
            orientation = struct.unpack('>H', bytearray_[9:11])[0]
            
            telemetryB = {'GPS_X': gps_latitude, 'GPS_Y':gps_altitude, 'Orientation': orientation}
            return telemetryB, 'B'
        
        else:
            return None, 1
    
    except IndexError:
        return None, 2
    
    except ValueError:
        return None, 3


def pqt_build(header, data_list):
    try:
        if isinstance(header, int):
            pck = bytearray()
        else:
            return 1
        
        pck.extend(header.to_bytes(1, "big"))
        data_list = list_to_bytearray(data_list)
        pck.extend(data_list)
        add_checksum(pck)
        return pck
    except:
        return 2 


def telemetryA_sim():
    data_list = []
    data_list.append(uniform(11.0, 12.0))
    data_list.append(uniform(5.0, 10.0))
    data_list.append(randint(0, 1))
    data_list.append(uniform(11.0, 12.0))
    data_list.append(uniform(5.0, 10.0))
    data_list.append(randint(0, 1))
    data_list.append(randint(25, 30))
    return data_list


def open_joystick():
    try:
        # Se enlistan los dispositivos conectados disponibles con sus ID
        for device in hid.enumerate():
            print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")  
        
        # Se crea una instancia de hid.device para leer los inputs de los dispositivos
        joystick = hid.device()
        # Se abre comunicación con joystick especificamente usando su ID
        joystick.open(0x12bd, 0xa02f)
        # Si el dispositivo no está listo, solo se regresará None cuando se quiera leer 
        joystick.set_nonblocking(True)
        
        return joystick
    except:
        return None


def open_serial():
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
            return ser
        except SerialException:
            print("Connection failed. Retrying...")
            sleep(1)


def open_serial_window():
    # Configuración de la ventana
    port_column = [
    [
        sg.Text("Select serial port"),
        sg.Listbox(
            values=[], enable_events=True, size=(40,20),
            key="Available ports")
        ]
    ]
    port_layout = [
        [
            sg.Column(port_column)
        ]
    ]
    
    port_window = sg.Window("Ports", port_layout)
    while True:
        print(list_ports.comports())
        event, values = port_window.read()
        print(event)
        if event == sg.WIN_CLOSED:
            return None
        
        try:
            available_ports = list(list_ports.comports())
            port_window["Available ports"].update(available_ports)
        except:
            available_ports = []   
            
        if event == "Available ports":
            try:
                port = values["Available ports"][0].device
                ser = serial.Serial(port, baudrate=BAUDRATE, timeout=1)
                port_window.close()
                return ser
            
            except SerialException:
                print('SerialException error.')
            except IndexError:
                pass


def wasdx_control(ser):
    key = read_key()
    # Se arman paquetes de comandos con el header 10 y dos datos indicando velocidad lineal en x (-128, 127) y velocidad angular en z (-128, 127).
    # Se usan signed int8
    command = None
    # Adelante
    if key == 'W':
        command = pqt_build(10, [100, 0])
    # Giro hacia la izquierda (CW)
    elif key == 'A':
        command = pqt_build(10, [0, 100])
    # Stop
    elif key == 'S':
        command = pqt_build(10, [0, 0])
    # Giro hacia la derecha (CCW)
    elif key == 'D':
        command = pqt_build(10, [0, -100])
    # Atrás
    elif key == 'X':
        command = pqt_build(10, [-100, 0])
        
    if command:
        print(key)
        print(command)
        ser.write(command)


def control_window_1(ser):
    # Desde esta ventana se pueden leer los datos de Telemetría que se reciben del datalink y además se pueden mandar comandos por teclado
    # al mantener presionado SHIFT.
    column_telemetryA = [
        [sg.Button('Telemetry A request')],
        [sg.Text(text='0', size=(40,1), key='VC')],
        [sg.Text(text='0', size=(40,1), key='CC')],
        [sg.Text(text='0', size=(40,1), key='EC')],
        [sg.Text(text='0', size=(40,1), key='VA')],
        [sg.Text(text='0', size=(40,1), key='CA')],
        [sg.Text(text='0', size=(40,1), key='EA')],
        [sg.Text(text='0', size=(40,1), key='TC')]
    ]
    column_telemetryB = [
        [sg.Button('Telemetry B request')],
        [sg.Text(text='0', size=(40,1), key='GPS_X')],
        [sg.Text(text='0', size=(40,1), key='GPS_Y')],
        [sg.Text(text='0', size=(40,1), key='Orientation')],
    ]
    layout = [
        [
            sg.Column(column_telemetryA),
            sg.Column(column_telemetryB)
        ]
    ]
    control_window = sg.Window("Base", layout)
    
    while True:
        event, values = control_window.read(timeout=10)
        
        # Se leen bytes del objeto serial. 
        # Se usa el interpretador para ordenar la información en la interfaz gráfica. 
        if ser.in_waiting > 0:
            bytearray_in = ser.readline()
            print(bytearray_in)
            if True:
                telemetry, packet = pqt_interpret(bytearray_in)
                if telemetry:
                    for key in telemetry.keys():
                        control_window[key].update(telemetry[key])
                elif packet == 1:
                    print(f"Unkown package. Header: {bytearray_in[0]}")
                elif packet == 2:
                    print('IndexError. Interpret fail.')
                elif packet == 3:
                    print('Value error. Interpret fail.')    
            else:
                print("Checksum failed")
                
        if event == 'Telemetry A request':
            request= pqt_build(51, [0])
            ser.write(request)
            
        if event == 'Telemetry B request':
            request = pqt_build(52, [0])
            ser.write(request)
            
        if is_pressed('SHIFT'):
            wasdx_control(ser)
            
        if event == sg.WIN_CLOSED:
            return None