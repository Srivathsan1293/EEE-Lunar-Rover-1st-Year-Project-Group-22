#include<Arduino.h>
#include<magnet.h>

String getMagnet(const int sensorPins[], int num_sensors, int up_threshold, int down_threshold) {
  int index = 0;
  int reading[num_sensors];
  for (int k = 0; k < num_sensors; k++) {
    reading[k] = 0;
  }

  // Taking average
  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < num_sensors; j++) {
      reading[j] += analogRead(sensorPins[j]);
    }
  }
  for (int i = 0; i < num_sensors; i++) {
    reading[i] = reading[i] / 10;
  }

  // Find max value
  int max_value = abs(reading[index] - 301); 
  int current_value = 0;
  for (int i = 0; i < num_sensors; i++) {
    current_value = abs(reading[i] - 301); 
    if (current_value > max_value) {
      max_value = current_value;
      index = i;
    }
  }

  // Determine final value
  if (reading[index] < up_threshold) {
   
    Serial.println("Up");
     return "Up";
  } else if (reading[index] > down_threshold) {
     Serial.println("d");
     return "Down";
  } else {
    return "No Magnet";
  }
}