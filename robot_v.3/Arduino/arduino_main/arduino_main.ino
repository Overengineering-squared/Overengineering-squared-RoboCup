#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

Adafruit_BNO055 bno_normal_adr = Adafruit_BNO055(0, 0x28);
Adafruit_BNO055 bno2_diff_adr = Adafruit_BNO055(1, 0x29);

const uint8_t irSensor1 = 9;
const uint8_t irSensor2 = 7;
const uint8_t irSensor3 = 8;
const uint8_t irSensor4 = 6; 
const uint8_t irSensor5 = 5;
const uint8_t irSensor6 = 4;
const uint8_t irSensor7 = 3;

int wait = 100;
long waitTime = millis();

bool gyroBegin = true; 

void setup() {
  Serial.begin(115200);

  if (!bno_normal_adr.begin(OPERATION_MODE_IMUPLUS)) {
    Serial.println("No_BNO055_1_detected.");
    gyroBegin = false;
  }

  if (!bno2_diff_adr.begin(OPERATION_MODE_IMUPLUS)) {
    Serial.println("No_BNO055_2_detected.");
    gyroBegin = false;
  }

  delay(1000);
  bno_normal_adr.setExtCrystalUse(true);
  bno2_diff_adr.setExtCrystalUse(true);
}

void loop() {
  if (millis() - waitTime > wait && Serial.availableForWrite()){
    print_ir_sensor("1", irSensor1, 130);
    print_ir_sensor("2", irSensor2, 130);
    print_ir_sensor("3", irSensor3, 130);
    print_ir_sensor("4", irSensor4, 130);
    print_ir_sensor("5", irSensor5, 130);
    print_ir_sensor("6", irSensor6, 130);
    print_ir_sensor("7", irSensor7, 50);
    print_gyro();
    waitTime = millis();}
}

void print_ir_sensor(String ir_num, int ir_pin, int distance){
  int16_t t = pulseIn(ir_pin, HIGH);
  if (t == 0){Serial.println("S" + ir_num + " No");}
  else if (t > 1850) {Serial.println("S" + ir_num + " -1");}
  else{
    int16_t d = (t - 1000) * 2;
    if (distance == 50) {d = (t - 1000) * 3 / 4;}
    if (d < 0){d = 0;}
    Serial.println("S" + ir_num + " " + String(float(d)));}
  return;}

void print_gyro(){
  if (gyroBegin){
    sensors_event_t event_normal;
    bno_normal_adr.getEvent(&event_normal);
  
    sensors_event_t event_diff;
    bno2_diff_adr.getEvent(&event_diff);
  
    imu::Vector<3> acceleration_normal = bno_normal_adr.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    Serial.println("G1 X: " + String(event_normal.orientation.x) + " Y: " + String(event_normal.orientation.y) + " Z: " + String(event_normal.orientation.z) + " AX: " + String(acceleration_normal.x()) + " AY: " + String(acceleration_normal.y()));
  
    imu::Vector<3> acceleration_diff = bno2_diff_adr.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    Serial.println("G2 X: " + String(event_diff.orientation.x) + " Y: " + String(event_diff.orientation.y) + " Z: " + String(event_diff.orientation.z) + " AX: " + String(acceleration_diff.x()) + " AY: " + String(acceleration_diff.y()));}
  else{
    Serial.println("G1 X: No Y: No Z: No AX: No AY: No");
    Serial.println("G2 X: No Y: No Z: No AX: No AY: No");}}
  