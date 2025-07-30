#include <SoftwareSerial.h>
#include "RoboClaw.h"

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

#define ROBOCLAW_ADDRESS_ARM 0x81    
#define ROBOCLAW_ADDRESS_WRIST 0x80  
#define ROBOCLAW_BAUDRATE 9600
#define ROBOCLAW_ARM_RX 10
#define ROBOCLAW_ARM_TX 11
#define ROBOCLAW_WRIST_RX 12
#define ROBOCLAW_WRIST_TX 13

SoftwareSerial roboclawSerial_arm(ROBOCLAW_ARM_RX, ROBOCLAW_ARM_TX);
SoftwareSerial roboclawSerial_wrist(ROBOCLAW_WRIST_RX, ROBOCLAW_WRIST_TX);
RoboClaw roboclaw_arm(&roboclawSerial_arm, ROBOCLAW_BAUDRATE);
RoboClaw roboclaw_wrist(&roboclawSerial_wrist, ROBOCLAW_BAUDRATE);

#define ENCODER_MIN 0
#define ENCODER_MAX 1023
#define PWM_MAX 255
#define TOLERANCE 30
#define MAX_SPEED 200
#define MIN_SPEED 50
#define TIMEOUT_MS 10000
#define DEBUG_INTERVAL 500

struct LinearActuator {
  int pwmPin;
  int inaPin;
  int inbPin;
  int enablePin;
  int encoderPin;
  int targetPosition;
  int currentPosition;
  bool isMoving;
  unsigned long startTime;
  unsigned long lastDebugTime;
};

LinearActuator actuator1 = {MOTOR1_PWM, MOTOR1_INA, MOTOR1_INB, MOTOR1_EN, ENCODER1_PIN, 0, 0, false, 0, 0};
LinearActuator actuator2 = {MOTOR2_PWM, MOTOR2_INA, MOTOR2_INB, MOTOR2_EN, ENCODER2_PIN, 0, 0, false, 0, 0};

unsigned long lastLoopTime = 0;
const unsigned long LOOP_INTERVAL = 20;

void setup() {
  Serial.begin(9600);
  roboclawSerial_arm.begin(ROBOCLAW_BAUDRATE);
  delay(100);
  roboclawSerial_wrist.begin(ROBOCLAW_BAUDRATE);
  delay(100);
  
  pinMode(MOTOR1_INA, OUTPUT);
  pinMode(MOTOR1_INB, OUTPUT);
  pinMode(MOTOR1_PWM, OUTPUT);
  pinMode(MOTOR1_EN, OUTPUT);
  
  pinMode(MOTOR2_INA, OUTPUT);
  pinMode(MOTOR2_INB, OUTPUT);
  pinMode(MOTOR2_PWM, OUTPUT);
  pinMode(MOTOR2_EN, OUTPUT);
  
  digitalWrite(MOTOR1_EN, LOW);
  digitalWrite(MOTOR2_EN, LOW);

  Serial.println("Arduino Deltabot Controller iniciado");
  Serial.println("Comandos: A<pos1>,<pos2>,<pos3> o W<pos1>,<pos2>");
}

void loop() {
  if (Serial.available()) {
    String receivedCommand = Serial.readStringUntil('\n');
    receivedCommand.trim();
    if (receivedCommand.length() > 0) {
      processCommand(receivedCommand);
    }
  }

  unsigned long currentTime = millis();
  if (currentTime - lastLoopTime >= LOOP_INTERVAL) {
    updateLinearActuators();
    lastLoopTime = currentTime;
  }
}

void processCommand(String command) {
  command.trim();
  if (command.length() < 2) {
    Serial.println("ERROR: Comando demasiado corto");
    return;
  }

  char commandType = command.charAt(0);
  String parameters = command.substring(1);

  switch (commandType) {
    case 'A':
      processArmCommand(parameters);
      break;
    case 'W':
      processWristCommand(parameters);
      break;
    default:
      Serial.println("ERROR: Comando no reconocido");
      break;
  }
}

void processArmCommand(String params) {
  int positions[3];
  if (!parsePositions(params, positions, 3)) {
    Serial.println("ERROR: Formato inválido para comando ARM");
    return;
  }

  for (int i = 0; i < 3; i++) {
    if (positions[i] < 0 || positions[i] > 1023) {
      Serial.println("ERROR: Posición fuera de rango (0-1023)");
      return;
    }
  }

  actuator1.targetPosition = positions[0];
  actuator2.targetPosition = positions[1];
  int basePosition = positions[2];

  startActuatorMovement(&actuator1);
  startActuatorMovement(&actuator2);

  moveBaseMotor(basePosition);

  Serial.print("ARM - Objetivo: [");
  Serial.print(positions[0]); Serial.print(",");
  Serial.print(positions[1]); Serial.print(",");
  Serial.print(positions[2]); Serial.println("]");
}

void processWristCommand(String params) {
  int positions[2];
  if (!parsePositions(params, positions, 2)) {
    Serial.println("ERROR: Formato inválido para comando WRIST");
    return;
  }

  for (int i = 0; i < 2; i++) {
    if (positions[i] < 0 || positions[i] > 1023) {
      Serial.println("ERROR: Posición fuera de rango (0-1023)");
      return;
    }
  }

  moveWristMotors(positions[0], positions[1]);

}

bool parsePositions(String params, int* positions, int expectedCount) {
  int count = 0;
  int startIndex = 0;
  
  for (int i = 0; i <= params.length(); i++) {
    if (i == params.length() || params.charAt(i) == ',') {
      if (count >= expectedCount) return false;
      String numberStr = params.substring(startIndex, i);
      positions[count] = numberStr.toInt();
      count++;
      startIndex = i + 1;
    }
  }
  return count == expectedCount;
}

void startActuatorMovement(LinearActuator* actuator) {
  actuator->isMoving = true;
  actuator->startTime = millis();
  actuator->lastDebugTime = 0;
  digitalWrite(actuator->enablePin, HIGH);
}

void updateLinearActuators() {
  updateActuator(&actuator1);
  updateActuator(&actuator2);
}

void updateActuator(LinearActuator* actuator) {
  if (!actuator->isMoving) {
    digitalWrite(actuator->enablePin, LOW);
    return;
  }

  actuator->currentPosition = analogRead(actuator->encoderPin);
  int error = actuator->targetPosition - actuator->currentPosition;
  unsigned long currentTime = millis();

  if (currentTime - actuator->lastDebugTime >= DEBUG_INTERVAL) {
    actuator->lastDebugTime = currentTime;
  }

  if (abs(error) <= TOLERANCE) {
    stopMotor(actuator);
    digitalWrite(actuator->enablePin, LOW);
    actuator->isMoving = false;
    return;
  }

  if (currentTime - actuator->startTime > TIMEOUT_MS) {
    stopMotor(actuator);
    digitalWrite(actuator->enablePin, LOW);
    actuator->isMoving = false;
    Serial.print("Timeout actuador ");
    Serial.println((actuator == &actuator1) ? "1" : "2");
    return;
  }

  int speed = constrain(map(abs(error), 0, 1023, MIN_SPEED, MAX_SPEED), MIN_SPEED, MAX_SPEED);

  if (error > 0) {
    moveMotorForward(actuator, speed);
  } else {
    moveMotorBackward(actuator, speed);
  }
}

void moveMotorForward(LinearActuator* actuator, int speed) {
  digitalWrite(actuator->inaPin, HIGH);
  digitalWrite(actuator->inbPin, LOW);
  analogWrite(actuator->pwmPin, speed);
}

void moveMotorBackward(LinearActuator* actuator, int speed) {
  digitalWrite(actuator->inaPin, LOW);
  digitalWrite(actuator->inbPin, HIGH);
  analogWrite(actuator->pwmPin, speed);
}

void stopMotor(LinearActuator* actuator) {
  digitalWrite(actuator->inaPin, LOW);
  digitalWrite(actuator->inbPin, LOW);
  analogWrite(actuator->pwmPin, 0);
}

void moveBaseMotor(int position) {
  long targetPulses = map(position, 0, 1023, 0, 4096);
  roboclaw_arm.SpeedAccelDeccelPositionM1(ROBOCLAW_ADDRESS_ARM, 1000, 500, 500, targetPulses, 1);
}

void moveWristMotors(int pos1, int pos2) {
  long targetPulses1 = map(pos1, 0, 1023, 0, 4096);
  long targetPulses2 = map(pos2, 0, 1023, 0, 4096);

  roboclaw_wrist.SpeedAccelDeccelPositionM1(ROBOCLAW_ADDRESS_WRIST, 800, 400, 400, targetPulses1, 1);
  delay(10);
  roboclaw_wrist.SpeedAccelDeccelPositionM2(ROBOCLAW_ADDRESS_WRIST, 800, 400, 400, targetPulses2, 1);
  
}
