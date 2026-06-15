#include "movement.h"
#include<Arduino.h>
#include<vector>
void initialize_movement(){
    pinMode(6,OUTPUT);
    pinMode(3,OUTPUT);
    pinMode(8, OUTPUT);
    pinMode(9,OUTPUT);
}

void move(String movement_code){

    digitalWrite(3, movement_code[0]-'0');
    analogWrite(6,movement_code.substring(2,5).toInt() );
    digitalWrite(8, movement_code[1] - '0');
    analogWrite(9, movement_code.substring(5,8).toInt());
}


