#include "connect_to_wifi.h"
#include "mqtt.h"
#include <Arduino.h>
#include "movement.h"


void setup(){
  initialize_movement();
  Serial.begin(9600);
  connectWIFI();
}

void loop(){
  if(!check_connection()){
    connectWIFI();
    connectMQTT();
  }
  client_loop();
}
