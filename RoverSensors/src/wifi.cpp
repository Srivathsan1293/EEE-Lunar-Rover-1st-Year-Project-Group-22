#include <SPI.h>
#include <WiFi101.h>
#include "connect_to_wifi.h"


char ssid[] = "sarthak";     //  your network SSID (name)
char pass[] = "12345678";  // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status

void connectWIFI() {

  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
  }
}

