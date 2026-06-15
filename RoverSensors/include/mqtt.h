#ifndef MQTT_H
#define MQTT_H

void connectMQTT();
void client_loop();
bool check_connection();
void client_publish(const char* topic, const char* payload);
void SendtoRoverOperator(String message);

#endif