#!/usr/bin/env python3

import rospy
import serial
from std_msgs.msg import Int16MultiArray, Int16

# Configura el puerto serial con el Arduino
arduino = None

def send_command(cmd):
    """
    Envía un comando al Arduino por serial y agrega salto de línea.
    """
    try:
        arduino.write((cmd + "\n").encode('utf-8'))
        rospy.loginfo(f"Enviado: {cmd}")
    except Exception as e:
        rospy.logerr(f"No se pudo enviar el comando: {e}")

def gripper_callback(msg):
    """
    Callback para controlar el gripper.
    Espera un solo entero: -1 (cerrar), 0 (parar), 1 (abrir).
    """
    val = msg.data
    cmd = f"G{val}"
    send_command(cmd)

def wrist_callback(msg):
    """
    Callback para controlar el wrist.
    Espera 2 enteros: dirección motor1, dirección motor2 (-1, 0, 1).
    """
    if len(msg.data) >= 2:
        cmd = f"W{msg.data[0]},{msg.data[1]}"
        send_command(cmd)
    else:
        rospy.logwarn("Mensaje de wrist inválido (faltan valores)")

def actuators_callback(msg):
    """
    Callback para actuadores lineales y base.
    Espera 3 enteros: target1, target2, dirección base (-1, 0, 1).
    """
    if len(msg.data) >= 3:
        cmd = f"A{msg.data[0]},{msg.data[1]},{msg.data[2]}"
        send_command(cmd)
    else:
        rospy.logwarn("Mensaje de actuadores lineales inválido (faltan valores)")

def base_callback(msg):
    """
    Callback para mover solo la base desde otro tópico.
    Esto manda un comando 'A' con los targets actuales y el nuevo valor de base.
    """
    # Aquí podrías guardar el último target1/target2 y reutilizarlos
    cmd = f"A0,0,{msg.data}"
    send_command(cmd)

def main():
    global arduino
    rospy.init_node("arm_controller_node")

    # Parámetros configurables por ROS param
    port = rospy.get_param("~port", "/dev/ttyACM1")
    baud = rospy.get_param("~baud", 9600)

    try:
        arduino = serial.Serial(port, baud, timeout=1)
        rospy.loginfo(f"Conectado al Arduino en {port} a {baud} bps")
    except Exception as e:
        rospy.logerr(f"No se pudo abrir el puerto serial: {e}")
        return

    # Suscriptores
    rospy.Subscriber("/gripper_cmd", Int16, gripper_callback)
    rospy.Subscriber("/wrist_cmd", Int16MultiArray, wrist_callback)
    rospy.Subscriber("/actuators_cmd", Int16MultiArray, actuators_callback)
    rospy.Subscriber("/base_cmd", Int16, base_callback)

    rospy.loginfo("Nodo de control de brazo iniciado. Esperando comandos...")
    rospy.spin()

    if arduino and arduino.is_open:
        arduino.close()

if __name__ == "__main__":
    main()
