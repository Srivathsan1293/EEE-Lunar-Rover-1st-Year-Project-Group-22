#include<Arduino.h>
#include <radio.h>
String getAge(){
String result = "";
  while (Serial1.available()) {
    // Read from Serial1, not Serial!
    char b = (char)Serial1.read(); 

    if (b == '#') {
      // We found the delimiter, print the result and reset
      return result;
    } else {
      // Still reading the message, add the character to the string
      result += b;
    }
  }
  return "Not Detected";
}