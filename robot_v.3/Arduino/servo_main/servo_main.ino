#include <Servo.h>

Servo G1;
Servo K1;
Servo K2;
Servo S1;
Servo S2;
Servo C1;

const int controlPin = 5;
const int inputPin1 = 6;
const int inputPin2 = 7;
const int inputPin3 = 8;

const int servoPinG1 = 9; //Lift Arm
const int servoPinK1 = 11; //Rotate Gripper
const int servoPinK2 = 12; //Open/Close Gripper
const int servoPinS1 = 2; //Main Barrier
const int servoPinS2 = 3; //Dead Barrier
const int servoPinC1 = 0; //Camera

float lastServoPosG1 = 13.0;
float lastServoPosK1 = 180.0;
float lastServoPosK2 = 49.0;
float lastServoPosS1 = 120.0;
float lastServoPosS2 = 0.0;   //Barrier closed
float lastServoPosC1 = 0.0;

void setup() {
  Serial.begin(9600);
  pinMode(controlPin, INPUT);
  pinMode(inputPin1, INPUT);
  pinMode(inputPin2, INPUT);
  pinMode(inputPin3, INPUT);

  G1.write(lastServoPosG1);
  K1.write(lastServoPosK1);
  K2.write(lastServoPosK2);
  S1.write(lastServoPosS1);
  S2.write(lastServoPosS2);
  C1.write(lastServoPosC1);

  G1.attach(servoPinG1);
  K1.attach(servoPinK1);
  K2.attach(servoPinK2);
  S1.attach(servoPinS1);
  S2.attach(servoPinS2);
  C1.attach(servoPinC1);
}

void lower_arm(){
  float EndPosG1 = 153;
  float EndPosK1 = 91;
  float EndPosK2 = 80;

  float MoveK1_Start = 60;
  float MoveK1_End = 130;
  float MoveK2_Start = 60;
  float MoveK2_End = 120;


  for(int servoPos = lastServoPosG1; servoPos <= EndPosG1; servoPos++){
    G1.write(servoPos);
    //Serial.println("G1: " + String(servoPos));
    
    if ((servoPos >= MoveK1_Start) && (servoPos <= MoveK1_End)) 
      {K1.write(lastServoPosK1 - ((lastServoPosK1 - EndPosK1) * ((servoPos - MoveK1_Start) / (MoveK1_End - MoveK1_Start))));
       //Serial.println("K1: " + String(lastServoPosK1 - ((lastServoPosK1 - EndPosK1) * ((servoPos - MoveK1_Start) / (MoveK1_End - MoveK1_Start)))));
       }
       
    if ((servoPos >= MoveK2_Start) && (servoPos <= MoveK2_End)) 
      {K2.write(lastServoPosK2 + ((EndPosK2 - lastServoPosK2) * ((servoPos - MoveK2_Start) / (MoveK2_End - MoveK2_Start))));
      //Serial.println("K2: " + String(lastServoPosK2 + ((EndPosK2 - lastServoPosK2) * ((servoPos - MoveK2_Start) / (MoveK2_End - MoveK2_Start)))));
      }
    
    delay(5);}
    
  lastServoPosG1 = EndPosG1;
  lastServoPosK1 = EndPosK1;
  lastServoPosK2 = EndPosK2;
  }


void raise_arm_left(){
  float StopPosG1_1 = 40;
  float StopPosG1_2 = 70;
  float StopPosK1 = 0;
  float StopPosK2 = 60;

  float MoveK1_Start_1 = 140;
  float MoveK1_End_1 = 100;
  
  float EndPosG1 = 15;
  float EndPosK1 = 180;
  float EndPosK2 = 49;

  float MoveK1_Start_2 = 50;
  float MoveK1_End_2 = 40;


  K2.write(EndPosK2);
  delay(500);
  
  for(int servoPos = lastServoPosG1; servoPos >= StopPosG1_1; servoPos--){
    G1.write(servoPos);
    //Serial.println("G1: " + String(servoPos));
    
    if ((servoPos <= MoveK1_Start_1) && (servoPos >= MoveK1_End_1)) 
    {K1.write(lastServoPosK1 + ((lastServoPosK1 - StopPosK1) * ((servoPos - MoveK1_Start_1) / (MoveK1_Start_1 - MoveK1_End_1))));
    //Serial.println("K1: " + String(lastServoPosK1 + ((lastServoPosK1 - StopPosK1) * ((servoPos - MoveK1_Start_1) / (MoveK1_Start_1 - MoveK1_End_1)))));
    }
    
    delay(5);}
  lastServoPosK1 = StopPosK1;

  delay(500);
  K2.write(StopPosK2);
  delay(500);
  K2.write(EndPosK2);

  G1.write(StopPosG1_2);
  delay(300);
  lastServoPosG1 = StopPosG1_2;
  
  for(int servoPos = lastServoPosG1; servoPos >= EndPosG1; servoPos--){
    G1.write(servoPos);
    //Serial.println("G1: " + String(servoPos));
    
    if ((servoPos <= MoveK1_Start_2) && (servoPos >= MoveK1_End_2)) 
    {K1.write(lastServoPosK1 + ((lastServoPosK1 - EndPosK1) * ((servoPos - MoveK1_Start_2) / (MoveK1_Start_2 - MoveK1_End_2))));
    //Serial.println("K1: " + String(lastServoPosK1 + ((lastServoPosK1 - EndPosK1) * ((servoPos - MoveK1_Start_2) / (MoveK1_Start_2 - MoveK1_End_2)))));
    }
    
    delay(2);}

  lastServoPosG1 = EndPosG1;
  lastServoPosK1 = EndPosK1;
  lastServoPosK2 = EndPosK2;
  }


void raise_arm_right(){
  float StopPosG1_1 = 40;
  float StopPosG1_2 = 55;
  float StopPosK1 = 180;
  float StopPosK2 = 70;

  float MoveK1_Start_1 = 140;
  float MoveK1_End_1 = 100;
  
  float EndPosG1 = 15;
  float EndPosK1 = 180;
  float EndPosK2 = 49;

  K2.write(EndPosK2);
  delay(500);
  
  for(int servoPos = lastServoPosG1; servoPos >= StopPosG1_1; servoPos--){
    G1.write(servoPos);
    //Serial.println("G1: " + String(servoPos));
    
    if ((servoPos <= MoveK1_Start_1) && (servoPos >= MoveK1_End_1)) 
    {K1.write(lastServoPosK1 + ((lastServoPosK1 - StopPosK1) * ((servoPos - MoveK1_Start_1) / (MoveK1_Start_1 - MoveK1_End_1))));
    //Serial.println("K1: " + String(lastServoPosK1 + ((lastServoPosK1 - StopPosK1) * ((servoPos - MoveK1_Start_1) / (MoveK1_Start_1 - MoveK1_End_1)))));
    }
    
    delay(5);}

  delay(500);
  K2.write(StopPosK2);
  delay(500);
  K2.write(EndPosK2);

  G1.write(StopPosG1_2);
  K1.write(EndPosK1);
  delay(300);
  G1.write(EndPosG1);

  lastServoPosG1 = EndPosG1;
  lastServoPosK1 = EndPosK1;
  lastServoPosK2 = EndPosK2;
  }

void openGate(int gateNum){
  float EndPosS1 = 0;
  float EndPosS2 = 120;

  if(gateNum == 1)
    {S1.write(EndPosS1);
    lastServoPosS1 = EndPosS1;}
  else if(gateNum == 2)
    {S2.write(EndPosS2);
    lastServoPosS2 = EndPosS2;}}

void closeGate(int gateNum){
  float EndPosS1 = 120;
  float EndPosS2 = 0;

  if(gateNum == 1)
    {S1.write(EndPosS1);
    lastServoPosS1 = EndPosS1;}
  else if(gateNum == 2){S2.write(EndPosS2);
    lastServoPosS2 = EndPosS2;}}


void loop() {
  bool isControlPin = digitalRead(controlPin);
  bool isPin1 = digitalRead(inputPin1);
  bool isPin2 = digitalRead(inputPin2);
  bool isPin3 = digitalRead(inputPin3);

  if(isControlPin == false){
    delay(100);
    if(isPin1 == false and isPin2 == true and isPin3 == false){
      Serial.println("lower arm");
      delay(300);
      lower_arm();}
    else if(isPin1 == true and isPin2 == false and isPin3 == false){
      Serial.println("raise arm left");
      delay(300);
      raise_arm_left();}
    else if(isPin1 == true and isPin2 == true and isPin3 == false){
      Serial.println("raise arm right");
      delay(300);
      raise_arm_right();}
    else if(isPin1 == true and isPin2 == true and isPin3 == true){
      Serial.println("open gate 1");
      delay(300);
      openGate(1);}
    else if(isPin1 == false and isPin2 == true and isPin3 == true){
      Serial.println("close gate 1");
      delay(300);
      closeGate(1);}
    else if(isPin1 == false and isPin2 == false and isPin3 == true){
      Serial.println("open gate 2");
      delay(300);
      openGate(2);}
    else if(isPin1 == true and isPin2 == false and isPin3 == true){
      Serial.println("close gate 2");
      delay(300);
      closeGate(2);}
    }
                       
  G1.write(lastServoPosG1);
  K1.write(lastServoPosK1);
  K2.write(lastServoPosK2);
  S1.write(lastServoPosS1);
  S2.write(lastServoPosS2);
  }
