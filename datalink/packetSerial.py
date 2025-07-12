#!/usr/bin/env python3

from time import sleep
import serial
from serial import SerialException

import yaml

class SerialHandler():
    def __init__(self, port, baudrate, id=0x40):
        self.ser = self.open_serial()
        self.port = port
        self.baurate = baudrate
        self.id = id
        
    # Función sencilla para abrir puerto Serial con infinitos intentos
    def open_serial(self):
        while True:
            try:
                ser = serial.Serial(self.port, self.baudrate, timeout=1)
                return ser
            except SerialException as e:
                print(f"Error {e}. Retrying connection...")
                    
    
    # Función para abrir puerto Serial con comprobación de que se comunica al controlador deseado
    # Intenta hasta lograrlo o hasta llegar a 5 intentos o los que se definan 
    def open_serial_verified(self,tries=5):
        tries = 5
        for i in len(range(0, tries)):
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                self.ser.write(self.id) # Se manda comprobación
                response = self.baurateser.readline() #True/False (1/0)
                
            except SerialException as e:
                print(f"Attempt {tries}. Error: {e}. Retrying connection... ")
                
        if response:
            return self.ser
        else:
            self.ser.close() # Si es el controlador o dispositivo equivocado, cierra la comunicación. 
    
    # Leer linea, decodificar y separa por comas
    def read_serial(self):
        line = self.ser.readline().decode('utf-8').strip()
        if line:
            data = line.split(',')
            return data

    # Cargar configuración y crear parser dinámico
    def load_message_config(self, path='message_config.yaml'):
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            self.config = config
        return config['messages']
    
    def cast_value(self, value, type_str):
        if type_str == 'int':
            return int(value)
        elif type_str == 'float':
            return float(value)
        elif type_str == 'bool':
            return value.lower() in ['1', 'true', 'yes']
        return value  # default: string
        
    # Identificar el tipo de mensaje recibido y crear un diccionario
    def parse_line(self, line):
        
        line = self.ser.readline().decode('utf-8')
        parts = line.strip().split(',')
        
        headers = {
        10 : "TWIST",
        11: "IMU",
        }
        
        # Encontrar header correspondiente
        for key in headers:
            if key == parts[0]:
                header = headers[key]
            
        values = parts[1:]
        
        if header not in self.config:
            raise ValueError(f"Mensaje desconocido: {header}")
        
        msg_def = self.config[header]
        field_names = msg_def['fields']
        field_types = msg_def['types']
        
        if len(values) != len(field_names):
            raise ValueError("Cantidad de datos incorrecta")
        
        data = {
            field: self.cast_value(val, typ)
            for field, val, typ in zip(field_names, values, field_types)
        }
        return header, data
    
    def initialize(self):
        try:
            self.open_serial()
            self.load_message_config()
        except:
            print("Serial Handler initialization failed.")