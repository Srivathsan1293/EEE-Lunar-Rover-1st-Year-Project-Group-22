#include <Arduino.h>
#include<ultrasound.h>
#include<magnet.h>
#include<connect_to_wifi.h>
#include<mqtt.h>
#include<decoderock.h>
#include<radio.h>
#include<ArduinoJson.h>
const int numSensors = 2;
const int sensors[numSensors] = {A0, A1};

StaticJsonDocument<200> message;
String pulseRate = "";

volatile unsigned long pulseCount = 0;
const byte pulsePin = 2;
const unsigned long reportInterval = 500;
unsigned long lastReport = 0;

void pulseISR() {
  pulseCount++;
}

void setup() {
  Serial1.begin(600);
  Serial.begin(9600);
  pinMode(8,INPUT);
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


  unsigned long now = millis();

  if (now - lastReport >= reportInterval) {
    noInterrupts();
    unsigned long count = pulseCount;
    pulseCount = 0;
    interrupts();
    float frequencyHz = count * (1000.0 / reportInterval);
    pulseRate = String(frequencyHz);
    lastReport = now;
    message["s3"] = readUltrasound();
    message["s1"] = pulseRate;
    message["s4"] = getAge();
    message["s2"] = getMagnet(sensors, numSensors, 435,445);
    
    message["rock"] = decodeRock(message);
    SendtoRoverOperator(message);
  }
  
  

}