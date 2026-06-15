#include "connect_to_wifi.h"
#include "mqtt.h"
#include <Arduino.h>
#include "movement.h"


void setup(){
  initialize_movement();

}

void loop(){
  if(!check_connection()){
    connectWIFI();
    connectMQTT();
  }
  client_loop();
}