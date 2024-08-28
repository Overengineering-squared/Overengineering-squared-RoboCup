#include <Servo.h>
 
Servo servoG1;
Servo servoG2;
Servo servoK1;
Servo servoK2;

int controlPin = 2;
int inputPin1 = 3;
int inputPin2 = 4;
int inputPin3 = 5;

int servoPinG1 = 7;
int servoPinG2 = 8;
int servoPinK1= 9;
int servoPinK2 = 10;

float lastServoPosG1 = 255.0;
float lastServoPosK1 = 0.0;
float lastServoPosK2 = 180.0;

void setup()
{
  Serial.begin(9600);
  pinMode(controlPin, INPUT);
  pinMode(inputPin1, INPUT);
  pinMode(inputPin2, INPUT);
  pinMode(inputPin3, INPUT);
    
  servoG1.attach(servoPinG1);
  servoG2.attach(servoPinG2);
  servoK1.attach(servoPinK1);
  servoK2.attach(servoPinK2);
  
  servoG1.write(round(lastServoPosG1 * (2.0/3.0)));
  servoG2.write(round((270 - lastServoPosG1) * (2.0/3.0)));
  servoK1.write(lastServoPosK1);
  servoK2.write(lastServoPosK2);
}

void loop(){
  bool isControlPin = digitalRead(controlPin);
  bool isPin1 = digitalRead(inputPin1);
  bool isPin2 = digitalRead(inputPin2);
  bool isPin3 = digitalRead(inputPin3);

  if(isControlPin == true)
  {
    // 1
    Serial.println("1");
    if(isPin1 == true and isPin2 == false and isPin3 == false)
    {
      float endPosG1 = 255.0;
      float endPosK1 = 0.0;
      for(int servoPos = lastServoPosG1; servoPos < endPosG1; servoPos++)
      {
        servoG1.write(round(servoPos * (2.0/3.0)));
        servoG2.write(round((270 - servoPos) * (2.0/3.0)));
        servoK1.write(round(lastServoPosK1 - ((lastServoPosK1 - endPosK1) * (abs(servoPos - lastServoPosG1) / abs(endPosG1 - lastServoPosG1)))));
        delay(10);
      }
      lastServoPosG1 = endPosG1;
      lastServoPosK1 = endPosK1;
    }
    
    // 2
    else if(isPin1 == true and isPin2 == true and isPin3 == false)
    {
      Serial.println("2");
      float endPosG2 = 35.0;
      float endPosK2 = 145.0;
      for(int servoPos = lastServoPosG1; servoPos > endPosG2; servoPos--)
      {
        servoG1.write(round(servoPos * (2.0/3.0)));
        servoG2.write(round((270 - servoPos) * (2.0/3.0)));
        servoK1.write(round(lastServoPosK1 + ((endPosK2 - lastServoPosK1) * ((abs(servoPos - lastServoPosG1) / abs(endPosG2 - lastServoPosG1))))));
        delay(10);
      }
      lastServoPosG1 = endPosG2;
      lastServoPosK1 = endPosK2;
    }

    // 3
    else if(isPin1 == true and isPin2 == true and isPin3 == true)
    {
      Serial.println("3");
      float endPosG3 = 100.0;
      float endPosK3 = 0.0;
      
      if(lastServoPosG1 > endPosG3)
      {
        for(int servoPos = lastServoPosG1; servoPos > endPosG3; servoPos--)
        {
          servoG1.write(round(servoPos * (2.0/3.0)));
          servoG2.write(round((270 - servoPos) * (2.0/3.0)));
          delay(10);
        }
      }
      else
      {
        for(int servoPos = lastServoPosG1; servoPos < endPosG3; servoPos++)
        {
          servoG1.write(round(servoPos * (2.0/3.0)));
          servoG2.write(round((270 - servoPos) * (2.0/3.0)));
          delay(10);
        }
      }

      if(lastServoPosK1 > endPosK3)
      {
        for(int servoPos = lastServoPosK1; servoPos > endPosK3; servoPos--)
        {
          servoK1.write(servoPos);
          delay(10);
        }
      }
      else
      {
        for(int servoPos = lastServoPosK1; servoPos < endPosK3; servoPos++)
        {
          servoK1.write(servoPos);
          delay(10);
          
        }
      }

      delay(500);
      
      for(int servoPos = 180; servoPos > 0; servoPos--)
      {
        servoK2.write(servoPos);
        delay(10);
      }

      delay(1500);

      for(int servoPos = 0; servoPos < 180; servoPos++)
      {
        servoK2.write(servoPos);
        delay(10);
      }
      
      lastServoPosG1 = endPosG3;
      lastServoPosK1 = endPosK3;
    }

    // 4
    else if (isPin1 == false and isPin2 == true and isPin3 == true)
    {
      Serial.println("4");
      float endPosG4 = 35.0;
      float endPosK4 = 145.0;
      for(int servoPos = lastServoPosG1; servoPos > endPosG4; servoPos--)
      {
        servoG1.write(round(servoPos * (2.0/3.0)));
        servoG2.write(round((270 - servoPos) * (2.0/3.0)));
        servoK1.write(round(lastServoPosK1 + ((endPosK4 - lastServoPosK1) * ((abs(servoPos - lastServoPosG1) / abs(endPosG4 - lastServoPosG1))))));

        if (servoPos == 85) 
        {
          delay(1500);
        }

        if (servoPos == 65)
        {
          for(int servoPosK = 180; servoPosK > 0; servoPosK--)
          {
            servoK2.write(servoPosK);
            delay(10);
          }
          delay(500);
        }
        
        delay(10);
      }
      
      delay(500);
      
      for(int servoPos = 0; servoPos < 180; servoPos++)
      {
        servoK2.write(servoPos);
        delay(10);
      }

      lastServoPosG1 = endPosG4;
      lastServoPosK1 = endPosK4;
    }

    // 5
    else if (isPin1 == false and isPin2 == false and isPin3 == true)
    {
      Serial.println("5");
      float endPosG5 = 115.0;
      float endPosK5 = 110.0;
      
      if(lastServoPosG1 > endPosG5)
      {
        for(int servoPos = lastServoPosG1; servoPos > endPosG5; servoPos--)
        {
          servoG1.write(round(servoPos * (2.0/3.0)));
          servoG2.write(round((270 - servoPos) * (2.0/3.0)));
          delay(10);
        }
      }
      else
      {
        for(int servoPos = lastServoPosG1; servoPos < endPosG5; servoPos++)
        {
          servoG1.write(round(servoPos * (2.0/3.0)));
          servoG2.write(round((270 - servoPos) * (2.0/3.0)));
          delay(10);
        }
      }

      if(lastServoPosK1 > endPosK5)
      {
        for(int servoPos = lastServoPosK1; servoPos > endPosK5; servoPos--)
        {
          servoK1.write(servoPos);
          delay(10);
        }
      }
      else
      {
        for(int servoPos = lastServoPosK1; servoPos < endPosK5; servoPos++)
        {
          servoK1.write(servoPos);
          delay(10);
          
        }
      }

      for(int servoPos = 180; servoPos > 0; servoPos--)
      {
        servoK2.write(servoPos);
        delay(10);
      }

      delay(2000);

      for(int servoPos = 0; servoPos < 180; servoPos++)
      {
        servoK2.write(servoPos);
        delay(10);
      }
      
      lastServoPosG1 = endPosG5;
      lastServoPosK1 = endPosK5;
    }
  }
}
