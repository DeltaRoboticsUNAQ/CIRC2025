import cv2

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)

def gen_aruco(cam):
    while True:
        ret, frame = cam.read()

        if not ret:
            continue
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar marcadores
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)

        if ids is not None:
            # Dibujar los marcadores detectados
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            # También puedes procesar los IDs aquí si lo necesitas
            print("Marcadores detectados:", ids.flatten())
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        jpeg_bytes = jpeg.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')

def test_aruco(cam):
    while True:
        ret, frame = cam.read()

        if not ret:
            continue
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar marcadores
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)

        if ids is not None:
            # Dibujar los marcadores detectados
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            # También puedes procesar los IDs aquí si lo necesitas
            print("Marcadores detectados:", ids.flatten())
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        
        cv2.imshow('Cámara', frame)

        # Presionar 'q' para salir del bucle
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
if __name__ == '__main__':
    camera = cap = cv2.VideoCapture(0)
    test_aruco(camera)