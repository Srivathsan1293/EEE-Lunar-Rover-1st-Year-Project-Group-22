#include <PubSubClient.h>
#include "mqtt.h"
#include <WiFi101.h>
#include <vector>
#include <ArduinoJson.h>

const char* broker = "192.168.137.1";
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

void SendtoRoverOperator(JsonDocument& message) {
    char payload[200];
    serializeJson(message, payload, sizeof(payload));
    client.publish("sensor_read", payload);
}