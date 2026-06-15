#include<Arduino.h>
#include <radio.h>
String getAge(){
    byte b;
    while(Serial.available()){
        byte b = Serial.read();
        Serial.print(char(b));

    }
    return "";
}