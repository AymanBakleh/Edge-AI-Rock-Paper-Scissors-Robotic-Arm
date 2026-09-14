#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Define the PWM driver using the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

// Define the frequency for the servos
#define SERVOMIN  150  // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600  // This is the 'maximum' pulse length count (out of 4096)
#define FREQUENCY 60   // Analog servos run at ~50 Hz updates

// Define the servo channels for each finger
#define THUMB_CHANNEL     3
#define INDEX_CHANNEL     5
#define MIDDLE_CHANNEL    9
#define RING_CHANNEL      11
#define PINKY_CHANNEL     14


void setup() {
  Serial.begin(2000000);  // Initialize serial communication at 9600 baud
  Serial.println("Rock-Paper-Scissors Bionic Hand");

  // Initialize the PWM driver
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);  // Analog servos run at ~50 Hz updates
}

void setServoAngle(uint8_t channel, uint16_t angle) {
  uint16_t pulse = map(angle, 0, 180, SERVOMIN, SERVOMAX);
  pwm.setPWM(channel, 0, pulse);
}

void loop() {
  if (Serial.available()) {
 String gesture = Serial.readStringUntil('\n');   // Read a single character from the serial buffer
     gesture.trim();
    if (gesture == "scissors") {
      // Make rock gesture
      setServoAngle(THUMB_CHANNEL, 180);
      setServoAngle(INDEX_CHANNEL, 180);
      setServoAngle(MIDDLE_CHANNEL, 180);
      setServoAngle(RING_CHANNEL, 180);
      setServoAngle(PINKY_CHANNEL, 180);
    } else if (gesture == "rock") {
      // Make paper gesture
      setServoAngle(THUMB_CHANNEL, 0);
      setServoAngle(INDEX_CHANNEL, 0);
      setServoAngle(MIDDLE_CHANNEL, 0);
      setServoAngle(RING_CHANNEL, 0);
      setServoAngle(PINKY_CHANNEL, 0);
    } else if (gesture == "paper") {
      // Make scissors gesture
      setServoAngle(THUMB_CHANNEL, 180);
      setServoAngle(INDEX_CHANNEL, 0);
      setServoAngle(MIDDLE_CHANNEL, 0);
      setServoAngle(RING_CHANNEL, 180);
      setServoAngle(PINKY_CHANNEL, 180);
    } else {
      // Invalid gesture
      Serial.println("Invalid gesture!");
    }
  }
}
