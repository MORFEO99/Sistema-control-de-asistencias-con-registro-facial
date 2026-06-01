#include <Servo.h>

Servo myservo;

char data;

void setup() {

  Serial.begin(9600);

  myservo.attach(9);

  myservo.write(0);

  Serial.println("Arduino listo");
}

void loop() {

  if (Serial.available() > 0) {

    data = Serial.read();

    Serial.println(data);

    if (data == '1') {

      Serial.println("Abriendo puerta");

      myservo.write(90);

      delay(5000);

      myservo.write(0);
    }
  }
}