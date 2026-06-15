#include <SPI.h>
#include <WiFi101.h>
#include "connect_to_wifi.h"


char ssid[] = "EEERover";     //  your network SSID (name)
char pass[] = "exhibition";  // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status

void connectWIFI() {

  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
  }
}

