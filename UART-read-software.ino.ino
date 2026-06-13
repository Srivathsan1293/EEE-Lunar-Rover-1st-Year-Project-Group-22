void setup() {
  Serial.begin(600);
}

void loop() {
  while (Serial.available()) {
    byte b = Serial.read();
    Serial.print((char)b);
  }
}