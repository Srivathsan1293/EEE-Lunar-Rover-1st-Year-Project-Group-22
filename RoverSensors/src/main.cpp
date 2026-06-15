#include <Arduino.h>
#include<ultrasound.h>
#include<magnet.h>
#include<connect_to_wifi.h>
#include<mqtt.h>
#include<decoderock.h>
#include<radio.h>


String pulseRate = "";

volatile unsigned long pulseCount = 0;
const byte pulsePin = 2;
const unsigned long reportInterval = 500;
unsigned long lastReport = 0;

void pulseISR() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);
  pinMode(pulsePin, INPUT_PULLUP);
  attachInterrupt(
    digitalPinToInterrupt(pulsePin),
    pulseISR,
    RISING
  );
}

void loop() {
  if(!check_connection()){
    connectWIFI();
    connectMQTT();
  }
  client_loop();

  String Ultrasound = readUltrasound();
  String age = getAge();
  String magnet = getMagnet();

  unsigned long now = millis();

  if (now - lastReport >= reportInterval) {
    noInterrupts();
    unsigned long count = pulseCount;
    pulseCount = 0;
    interrupts();
    float frequencyHz = count * (1000.0 / reportInterval);
    pulseRate = String(frequencyHz);
    Serial.println(pulseRate);
    lastReport = now;

  }
  
  String message =  Ultrasound + "///" + age + "///" + pulseRate + "///" + magnet;
  String rock = decodeRock(message);
  message = message + "///" + rock;
  SendtoRoverOperator(message);

}