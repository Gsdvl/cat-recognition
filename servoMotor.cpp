#include <Servo.h>

Servo servoMotor;

void setup() {
  servoMotor.attach(9);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'o') {        
      servoMotor.write(90);   
      delay(2000);                      
      servoMotor.write(0);           
    }
  }
}
