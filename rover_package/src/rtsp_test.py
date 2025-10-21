#!/usr/bin/env python3

import cv2

# URL RTSP típica para cámaras Dahua:
# rtsp://usuario:contraseña@IP:puerto/cam/realmonitor?channel=1&subtype=0
# Ajusta usuario, contraseña, IP y puerto según tu cámara.
rtsp_url = "rtsp://admin:admin@192.168.1.30:554/cam/realmonitor?channel=1&subtype=0"

# Abrir la transmisión de video RTSP
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo recibir frame (stream terminado?).")
        break

    cv2.imshow('Cámara Dahua RTSP', frame)

    # Presiona 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()