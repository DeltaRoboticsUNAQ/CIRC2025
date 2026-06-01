# Control de chasis con WASD -> roslibpy (Windows)
# Requisitos: pip install keyboard roslibpy
# En Windows suele ser necesario ejecutar el script como Administrador para que keyboard funcione.

from keyboard import is_pressed
import roslibpy
from time import sleep, time
import traceback

# Constantes
DELAY = 0.05  # intervalo de lectura (s)
STOP_TIMEOUT = 0.2  # tiempo máximo sin tecla para mandar 0 (s)

# Conexión ROS WebSocket
ros = roslibpy.Ros(host='192.168.1.30', port=9090)
ros.run()
print('Intentando conectar a ROS...')

# esperar conexión (timeout simple)
t0 = time()
while not ros.is_connected and time() - t0 < 5:
    sleep(0.1)

if not ros.is_connected:
    print('No se pudo conectar al servidor roscore/rosbridge en 192.168.1.30:9090')
    # puedes decidir hacer sys.exit(1) aquí
else:
    print('Conectado a ROS.')

# Publisher para /cmd_vel
chassis_pub = roslibpy.Topic(ros, '/cmd_vel', 'geometry_msgs/Twist')

def publish_twist(linear_x, angular_z):
    msg = {
        'linear': {'x': float(linear_x), 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': float(angular_z)}
    }
    chassis_pub.publish(msg)

def chasis_wasd_control():
    print("Control con WASD activado. Presiona ESC o Ctrl-C para salir.")
    last_input_time = 0.0
    try:
        while True:
            try:
                new_input = False
                linear_x = 0.0
                angular_z = 0.0

                if is_pressed('w'):
                    linear_x = 250.0
                    angular_z = 0.0
                    new_input = True
                    print('w')

                elif is_pressed('a'):
                    linear_x = 0.0
                    angular_z = 250.0
                    new_input = True
                    print('a')

                elif is_pressed('s'):
                    linear_x = -150.0
                    angular_z = 0.0
                    new_input = True
                    print('s')

                elif is_pressed('d'):
                    linear_x = 0.0
                    angular_z = -250.0
                    new_input = True
                    print('d')

                elif is_pressed('x'):
                    linear_x = 0.0
                    angular_z = 0.0
                    new_input = True
                    print('x (stop)')

                elif is_pressed('esc'):
                    print('ESC pulsado. Saliendo.')
                    break

                if new_input:
                    publish_twist(linear_x, angular_z)
                    last_input_time = time()
                else:
                    # si hace más de STOP_TIMEOUT s que no hay input, enviar stop para evitar deriva
                    if time() - last_input_time > STOP_TIMEOUT:
                        publish_twist(0.0, 0.0)
                        last_input_time = time()  # evita publicar continuamente exactamente aquí

                sleep(DELAY)

            except Exception as e_inner:
                # Mostrar trace completo para depuración
                print('Excepción en el bucle de lectura de teclado:')
                traceback.print_exc()
                # si falla keyboard.is_pressed por privilegios, por ejemplo, se capturará aquí
                # intentar seguir (o romper según prefieras)
                sleep(0.5)

    except KeyboardInterrupt:
        print('Interrupción por teclado (Ctrl-C).')

    finally:
        # mandar stop por seguridad y limpiar
        try:
            publish_twist(0.0, 0.0)
        except Exception:
            pass
        try:
            chassis_pub.unadvertise()
        except Exception:
            pass
        # terminar conexión ros si procede
        if hasattr(ros, 'terminate'):
            try:
                ros.terminate()
            except Exception:
                pass
        print('Programa terminado.')

if __name__ == '__main__':
    chasis_wasd_control()
