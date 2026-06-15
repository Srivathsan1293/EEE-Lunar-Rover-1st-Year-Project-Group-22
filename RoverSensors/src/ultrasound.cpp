#include <Arduino.h>
#include <ultrasound.h>
#include<mqtt.h>
String readUltrasound(){
    if (digitalRead(8)){
      
        return "40kHz";
    }
    else{
  
        return "Not Found";
    }
}
