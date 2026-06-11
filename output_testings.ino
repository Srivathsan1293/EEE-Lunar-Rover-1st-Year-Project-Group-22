const int numSensors = 2;
const int sensors[numSensors] = {A0, A1};

void setup() {
  Serial.begin(9600);
  Serial.println("This works");
}

void loop() {

  // int reading[2] = {0,0};
  // int sensorPins[2] = {A0, A1};
  // for (int i = 0; i < 10; i++) {
  //   for (int j = 0; j < 2; j++) {
  //     reading[j] += analogRead(sensorPins[j]);
  //   }
  //   delay(10);
  // }
  // for (int i = 0; i < 2; i++) {
  //   reading[i] = reading[i] / 10;
  // }

  // Serial.print(reading[0]);
  // Serial.print(" ");
  // Serial.println(reading[1]);

  

  
  
  // Example of how to call the function:
  getMagenticStateV2(sensors, numSensors, 430, 445);
}

// Added 'num_sensors' parameter
void getMagenticStateV2(const int sensorPins[], int num_sensors, int up_threshold, int down_threshold) {
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
    delay(10);
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
  } else if (reading[index] > down_threshold) {
    Serial.println("Down");
  } else {
    Serial.println("no magnet");
  }
}