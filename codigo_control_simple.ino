#include <SoftwareSerial.h>

// Pines motores lineales
#define MOTOR1_INA 7
#define MOTOR1_INB 8
#define MOTOR1_PWM 5
#define MOTOR1_EN A0

#define MOTOR2_INA 4
#define MOTOR2_INB 9
#define MOTOR2_PWM 6
#define MOTOR2_EN A1

#define ENCODER1_PIN A2
#define ENCODER2_PIN A3

#define TOLERANCE 15          
#define MIN_SPEED 50
#define MAX_SPEED 250
#define KP 0.25              

SoftwareSerial serial(12, 13);  // RX, TX

int target1 = -1;
int target2 = -1;

void setup() {
  Serial.begin(9600);
  serial.begin(9600);

  // Configurar pines motores
  pinMode(MOTOR1_INA, OUTPUT);
  pinMode(MOTOR1_INB, OUTPUT);
  pinMode(MOTOR1_PWM, OUTPUT);
  pinMode(MOTOR1_EN, OUTPUT);

  pinMode(MOTOR2_INA, OUTPUT);
  pinMode(MOTOR2_INB, OUTPUT);
  pinMode(MOTOR2_PWM, OUTPUT);
  pinMode(MOTOR2_EN, OUTPUT);

  pinMode(ENCODER1_PIN, INPUT);
  pinMode(ENCODER2_PIN, INPUT);

  digitalWrite(MOTOR1_EN, LOW);
  digitalWrite(MOTOR2_EN, LOW);

  Serial.println("Actuadores listos");
}

void loop() {
  // Procesamiento de comandos por serial
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.length() > 0) {
      char type = cmd.charAt(0);
      String args = cmd.substring(1);

      int sep1 = args.indexOf(',');
      int sep2 = args.indexOf(',', sep1 + 1);
      int sep3 = args.indexOf(',', sep1 + 2);

      int val1 = 0, val2 = 0, val=3 ;

      if (sep1 != -1 && sep2 != -1) {
        val1 = args.substring(0, sep1).toInt();
        val2 = args.substring(sep1 + 1, sep2).toInt();
      } else if (sep1 != -1) {
        val1 = args.substring(0, sep1).toInt();
        val2 = args.substring(sep1 + 1).toInt();
      } else {
        val1 = args.toInt();
      }

      switch (type) {
        case 'A':
          target1 = val1;
          target2 = val2;

          if (sep1 != -1 && sep2 != -1) {
            int val3 = args.substring(sep2 + 1).toInt();
            if (val3 == 1) {
              Serial.println("Base gira a la derecha");
              serial.write(96);  // Reemplaza con el valor que corresponda a tu motor base
            } else if (val3 == -1) {
              Serial.println("Base gira a la izquierda");
              serial.write(32);  // Reemplaza con el valor que necesites
            } else {
              Serial.println("Base stop");
              serial.write(64);  // Detener motor base
            }
          }

          Serial.print("Nuevos objetivos -> T1: ");
          Serial.print(target1);
          Serial.print(" | T2: ");
          Serial.println(target2);
          break;

        case 'W':
          
          if (val1 == 1 && val2 == 1) {
            serial.write(72); serial.write(200);
          } else if (val1 == -1 && val2 == -1) {
            serial.write(56); serial.write(184);
          } else if (val1 == 1 && val2 == -1) {
            serial.write(72); serial.write(184);
          } else if (val1 == -1 && val2 == 1) {
            serial.write(56); serial.write(200);
          } else {
            serial.write(64); serial.write(192);
          }
          break;

        case 'G':
          // Gripper
          if (val1 == 0) serial.write(64);
          else if (val1 == 1) serial.write(70);
          else if (val1 == -1) serial.write(58);
          break;

        default:
          Serial.println("Comando no reconocido");
          break;
      }
    }
  }

  // Control de posición si hay objetivo válido
  if (target1 >= 0 && target2 >= 0) {
    controlActuador(MOTOR1_INA, MOTOR1_INB, MOTOR1_PWM, MOTOR1_EN, ENCODER1_PIN, target1, "M1");
    controlActuador(MOTOR2_INA, MOTOR2_INB, MOTOR2_PWM, MOTOR2_EN, ENCODER2_PIN, target2, "M2");
  }
}

// Función modular de control para cada actuador
void controlActuador(int pinA, int pinB, int pwmPin, int enPin, int sensorPin, int target, const char* label) {
  int current = analogRead(sensorPin);
  int error = target - current;

  if (abs(error) > TOLERANCE) {
    int speed = abs(error) * KP;
    speed = constrain(speed, MIN_SPEED, MAX_SPEED);

    digitalWrite(enPin, HIGH);
    if (error > 0) {
      digitalWrite(pinA, HIGH);
      digitalWrite(pinB, LOW);
    } else {
      digitalWrite(pinA, LOW);
      digitalWrite(pinB, HIGH);
    }
    analogWrite(pwmPin, speed);
  } else {
    analogWrite(pwmPin, 0);
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
    digitalWrite(enPin, LOW);
  }

}
