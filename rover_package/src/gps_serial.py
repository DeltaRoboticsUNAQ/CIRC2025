#!/usr/bin/env python3

# Instalación necesaria:
# sudo apt install ros-noetic-sensor-msgs

import rospy

import serial
from serial import SerialException
from time import sleep 
#from sensor_msgs.msg import NavSatFix, NavSatStatus
import json

def parse_gps_line(line):
    """
    Espera una línea tipo: {"gps_x": lat, "gps_y": lon, "alt": alt}
    """
    try:
        if line.startswith('{'):
            data = json.loads(line)
            return float(data['gps_x']), float(data['gps_y']), float(data.get('alt', 0.0))
    except Exception as e:
        rospy.logwarn(f"No se pudo parsear línea: {line} → {e}")
    return None, None, None

def main():
    rospy.inti_node('gps_serial_node')
    port = rospy.get_param('/esp32_port', '/dev/ttyUSB0')
    baudrate = rospy.get_param('/esp32_baudrate', 115200)
    
    pub =  rospy.Publisher('/gps/fix', NavSatFix, queue_size=10)
    
    try: 
        ser = serial.Serial(port, baudrate, timeout=1)
        rospy.loginfo(f"Conectado a {port}")
    except serial.SerialException as e:
        rospy.logerr(f"No se pudo abrir el puerto serial: {e}")
        return
    
    rate = rospy.Rate(10) # 10 Hz
    
    while not rospy.is_shutdown():
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            
            lat, lon, alt = parse_gps_line(line)
            
            msg = NavSatFix()
            msg.header.stamp = rospy.Time.now()
            msg.header.frame_id = "gps_link"
            msg.status.status = NavSatStatus.STATUS_FIX
            msg.status.service = NavSatStatus.SERVICE_GPS

            msg.latitude = lat
            msg.longitude = lon
            msg.altitude = alt

            msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_UNKNOWN

            pub.publish(msg)

        except Exception as e:
            rospy.logwarn(f"Error leyendo/parsing: {e}")

        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
