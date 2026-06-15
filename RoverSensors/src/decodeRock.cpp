#include <Arduino.h>
#include <decoderock.h>
#include <ArduinoJson.h>

String decodeRock(JsonDocument& message) {
    // Your sensor readings
int infrared = message["s1"].as<int>(); // your IR wavelength reading;
bool ultrasound = (message["s3"] == "40kHz");
String magnetic = message["s3"];

bool ir547 = (450 < infrared and infrared < 650);
bool ir312 = (250 < infrared and infrared < 350);
bool ultra = ultrasound;
bool magDown = (magnetic == "Down");
bool magUp = (magnetic == "Up");

// Check each rock type
int count = 0;

// Basaltoid: IR=547, Ultrasound=40kHz, Magnetic=Down
count = 0;
if (ir547) count++;
if (ultra) count++;
if (magDown) count++;
if (count >= 2) { return "Basaltoid"; }

// Gravion: IR=312, no ultrasound, Magnetic=Down
count = 0;
if (ir312) count++;
if (!ultra) count++;
if (magDown) count++;
if (count >= 2) { return "Gravion"; }

// Regolix: IR=312, Ultrasound=40kHz, Magnetic=Up
count = 0;
if (ir312) count++;
if (ultra) count++;
if (magUp) count++;
if (count >= 2) { return"Regolix";}

// Lunarite: IR=547, no ultrasound, Magnetic=Up
count = 0;
if (ir547) count++;
if (!ultra) count++;
if (magUp) count++;
if (count >= 2) { return "Lunarite";}

return "Not Found";
}
