#include<PubSubClient.h>
#include "mqtt.h"
#include <WiFi101.h>
#include<vector>
#include "movement.h"
const char* broker = "192.168.137.1";
const int brokerPort = 1883;

WiFiClient wificlient;
PubSubClient client(wificlient);


void callback(char* topic, byte* payload, unsigned int length) {
    String new_payload = "";
    for(int i = 0; i < length; i++){
        new_payload += (char)payload[i];
    }
    // Serial.println(new_payload);
    move(new_payload);
}

void connectMQTT(){
    client.setServer(broker, brokerPort);
    client.setCallback(callback);
    while(!client.connected()){
        if(client.connect("Laptop")){
            Serial.println("connected");
            client.subscribe("movement_controls");
            Serial.println("Subscribed");
        }
    }
}

bool check_connection(){
    return client.connected();
}

void client_loop(){
    client.loop();
}