#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

Adafruit_BNO055 bno = Adafruit_BNO055(55);

const uint8_t irSensor1 = 3;
const uint8_t irSensor2 = 4;
const uint8_t irSensor3 = 5;
const uint8_t irSensor4 = 6;
const uint8_t irSensor5 = 7;

int t = 100; //250
long waitTime = millis();
bool bnoBegin = false;

void setup(void) {
  Serial.begin(9600);

  if(bno.begin(OPERATION_MODE_IMUPLUS)) // THIS HAS TO BE OPERATION_MODE_IMUPLUS OTHERWISE THE GYRO WILL BE INACCURATE
    bnoBegin = true;
  
  delay(1000);
  bno.setExtCrystalUse(true);
}

void loop(void) {
  if (millis() - waitTime > t && Serial.availableForWrite())
  {
    // InfraRot-Sensor 1
    int16_t ts1 = pulseIn(irSensor1, HIGH);
    String serial_s1 = "-1";
    if (ts1 == 0 || ts1 > 1850)
    {
      serial_s1 = "S1 -1";
    }
    else
    {
      int16_t ds1 = (ts1 - 1000) * 2;
      if (ds1 < 0) { ds1 = 0; } 
      serial_s1 = ("S1 " + String(float(ds1)));
    }
    Serial.println(serial_s1);
    
    // InfraRot-Sensor 2
    int16_t ts2 = pulseIn(irSensor2, HIGH);
    String serial_s2 = "-1";
    if (ts2 == 0 || ts2 > 1850)
    {
      serial_s2 = "S2 -1";
    }
    else
    {
      int16_t ds2 = (ts2 - 1000) * 2;
      if (ds2 < 0) { ds2 = 0; } 
      serial_s2 = ("S2 " + String(float(ds2)));
    }
    Serial.println(serial_s2);
    
    // InfraRot-Sensor 3
    int16_t ts3 = pulseIn(irSensor3, HIGH);
    String serial_s3 = "-1";
    if (ts3 == 0 || ts3 > 1850)
    {
      serial_s3 = "S3 -1";
    }
    else
    {
      int16_t ds3 = (ts3 - 1000) * 2;
      if (ds3 < 0) { ds3 = 0; } 
      serial_s3 = ("S3 " + String(float(ds3)));
    }
    Serial.println(serial_s3);

    // InfraRot-Sensor 4
    int16_t ts4 = pulseIn(irSensor4, HIGH);
    String serial_s4 = "-1";
    if (ts4 == 0 || ts4 > 1850)
    {
      serial_s4 = "S4 -1";
    }
    else
    {
      int16_t ds4 = (ts4 - 1000) * 3 / 4;
      if (ds4 < 0) { ds4 = 0; } 
      serial_s4 = ("S4 " + String(float(ds4)));
    }
    Serial.println(serial_s4);

    // InfraRot-Sensor 5
    int16_t ts5 = pulseIn(irSensor5, HIGH);
    String serial_s5 = "-1";
    if (ts5 == 0 || ts5 > 1850)
    {
      serial_s5 = "S5 -1";
    }
    else
    {
      int16_t ds5 = (ts5 - 1000) * 2;
      if (ds5 < 0) { ds5 = 0; } 
      serial_s5 = ("S5 " + String(float(ds5)));
    }
    Serial.println(serial_s5);
    
    String serial_gx = ("GX 361.00");
    String serial_gy = ("GY 361.00");
    String serial_ax = ("AX 255.00");
    String serial_ay = ("AY 255.00");
    
    sensors_event_t event;
    bno.getEvent(&event);
    
    if(bnoBegin)
    {
       serial_gx = ("GX " + String(float(event.orientation.x)));
       serial_gy = ("GY " + String(float(event.orientation.y)));

       imu::Vector<3> acceleration = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER );
       serial_ax = ("AX " + String(float(acceleration.x())));
       serial_ay = ("AY " + String(float(acceleration.y())));
    }
    else 
    {
      if(bno.begin(OPERATION_MODE_IMUPLUS))
         bnoBegin = true;
    }
    Serial.println(serial_gx);
    Serial.println(serial_gy);
    Serial.println(serial_ax);
    Serial.println(serial_ay);

    waitTime = millis();
  }
}
  
