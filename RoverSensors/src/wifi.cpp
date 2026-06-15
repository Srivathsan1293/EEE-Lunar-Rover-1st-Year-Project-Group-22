#include <SPI.h>
#include <WiFi101.h>
#include "connect_to_wifi.h"


char ssid[] = "Sarthak's iPhone";     //  your network SSID (name)
char pass[] = "Sarthak4627";  // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status

void connectWIFI() {

  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
  }
}

