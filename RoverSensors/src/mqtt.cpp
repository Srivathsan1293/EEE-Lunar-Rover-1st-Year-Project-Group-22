#include<PubSubClient.h>
#include "mqtt.h"
#include <WiFi101.h>
#include<vector>

const char* broker = "192.168.0.142";
const int brokerPort = 1883;

WiFiClient wificlient;
PubSubClient client(wificlient);


void callback(char* topic, byte* payload, unsigned int length) {
    
}

void connectMQTT(){
    client.setServer(broker, brokerPort);
    client.setCallback(callback);
    while(!client.connected()){
        if(client.connect("SensorMetroM0")){
            client.subscribe("Hi");
        }
    }
}

bool check_connection(){
    return client.connected();
}

void client_loop(){
    client.loop();
}

void SendtoRoverOperator(String message){
    char payloadbuf[200];
    message.toCharArray(payloadbuf, sizeof(payloadbuf));
    client.publish("sensor_read",payloadbuf);
}