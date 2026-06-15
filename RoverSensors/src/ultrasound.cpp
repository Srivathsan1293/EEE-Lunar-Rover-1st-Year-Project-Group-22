#include <Arduino.h>
#include <ultrasound.h>

String readUltrasound(){
    if (digitalRead(2)){
        return "40kHz";
    }
    else{
        return "Not Found";
    }
}
