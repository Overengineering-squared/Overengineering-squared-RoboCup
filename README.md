<img src="https://github.com/user-attachments/assets/d29a00c3-4102-41a2-afe6-8e1174fef7b9" style="width:100%;"/>

<br/>
<br/>

<p align="center">
  This is the repository for the German team Overengineering² (Georg-Büchner-Gymnasium, Seelze), which competed in
the <a href="https://junior.robocup.org/">RoboCup Junior</a> sub-league <a href="https://junior.robocup.org/rcj-rescue-line/">Rescue-Line</a>.
</p>

# About the Competition
<p align="center"><i>
  "The land is too dangerous for humans to reach the victims. Your team has been given a difficult task. The robot must be able to carry out a rescue mission in a fully autonomous mode with no human assistance. The robot must be durable and intelligent enough to navigate treacherous terrain with hills, uneven land, and rubble without getting stuck. When the robot reaches the victims, it has to gently and carefully transport each one to the safe evacuation point where humans can take over the rescue. The robot should exit the evacuation zone after a successful rescue to continue its mission throughout the disaster scene until it leaves the site. Time and technical skills are essential!"
</i></p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/a0c5800d-fcd0-47f1-990c-3d6951691d1c" style="width:70%;"/>
</p>

<p align="center"><sub><sup>
  [source: https://junior.robocup.org/wp-content/uploads/2024/04/RCJRescueLine2024-final-1.pdf]
</sup></sub></p>

<p align="justify">
  As mentioned in the short scenario introduction of the official <a href="https://junior.robocup.org/wp-content/uploads/2024/04/RCJRescueLine2024-final-1.pdf">2024 Rescue-Line rules</a>, the goal of this competition is to develop a fully autonomous robot capable of performing various tasks on a series of different obstacle courses. In the competitions, the team whose robot completes the course with the fewest errors or human interventions wins. The tasks the robots have to complete along the courses include following a black line with gaps, intersections (the placement of green intersection markers indicates the direction of the path the robot should follow), speed bumps, large obstacles, debris, ramps, and seesaws. In addition, the robot must recognize the silver reflective strip at the entrance to the so-called evacuation zone (130 cm x 90 cm x at least 10 cm), proceed into it, first pick up two silver balls (alive victims), place them in the green evacuation point (6 cm high), then pick up a black ball (dead victim) and place it in the red evacuation point. The robot should then find the exit of the evacuation zone (marked with a black line), follow the black line from there, and finally stop at a red line and remain stationary.
</p>

<p align="justify">
  There are very few restrictions for the robot. In general, the robot only needs to be able to navigate under tiles that form bridges over other tiles (25 cm high) that are supported by pillars at the corners of the tiles (entry/exit width of 25 cm). Besides that, there are only a few part restrictions on components that have been developed solely for a specific competition task (e.g., ready-to-use line-following cameras).
</p>

# About the project
<img src="https://github.com/user-attachments/assets/8b459bc5-5a42-4c4e-816b-697093f9b683" align="right" style="width:26%;"/>
<img src="https://github.com/user-attachments/assets/a7cf6d5c-9d79-4b35-9c4a-98a944fc0e93" align="left" style="width:25%;"/>

<p align="justify">
  In order to accomplish all of the tasks mentioned above, we decided to take a completely camera-based approach using Raspberry Pi. The development of this design started in March of 2022 and has been iterated until now (2024).
</p>

<p align="center">
  With this latest iteration of the robot design, we achieved 1st place (Individual Team) at the RoboCup Junior World Championship 2024 in Eindhoven.
</p>

## Components

<p align="justify">
  Aside from the custom, 3D-printed robot chassis and customized wheels to fit our mounting hubs, we used mostly off-the-shelf components for their reliability and active support. Our latest iteration used the following parts:
</p>

- [Raspberry Pi 5 8GB](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Coral USB Accelerator](https://coral.ai/products/accelerator)
- 2x [Arduino Nano](https://store.arduino.cc/en-de/products/arduino-nano)
- 2x [Adafruit BNO055 Gyroscope](https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/overview)
- 6x [Pololu irs17a Infrared Sensor](https://www.pololu.com/product/4071)
- [Pololu irsl16a Infrared Sensor](https://www.pololu.com/product/4067)
- [1 m revoART 12 V COB LED-Strip](https://www.leds24.com/12v-cob-led-streifen-neutralweiss-alle-1-cm-teilbar-3mm-breit-)
- [KY-019 Relay](https://sensorkit.joy-it.net/en/sensors/ky-019)
- 5x [Emax ES09MD Servo](https://www.premium-modellbau.de/emax-es09md-digital-metallgetriebe-mini-servo-15g-0-08s-2-6kg-kugellager-es08md)
- [Diymore 35KG Servo](https://www.amazon.de/-/en/diymore-Waterproof-Helicopter-Aeroplane-Suitable/dp/B0BD3XKQSW)
- 4x 12V DC Geared Motor (We don't know the model, our mentor got these in 2017 from a soccer leauge team, picture is in the poster)
- [L298N Motor Driver](https://projecthub.arduino.cc/lakshyajhalani56/l298n-motor-driver-arduino-motors-motor-driver-l298n-7e1b3b) (Can be controlled by the 3.3V of a RPI btw)
- [Conrad 7.4V 3800mAh LiPo](https://www.conrad.com/en/p/conrad-energy-scale-model-battery-pack-lipo-7-4-v-3800-mah-no-of-cells-2-20-c-softcase-xt60-1344142.html)
- [Conrad 11.1V 3800mAh LiPo](https://www.conrad.de/de/p/conrad-energy-modellbau-akkupack-lipo-11-1-v-3800-mah-zellen-zahl-3-20-c-softcase-xt60-1344139.html)
- [XL4015 Step Down Converter](https://www.amazon.de/-/en/XL4015DC-Converter-DC5V-32V-Charging-Constant/dp/B0CC96CN3Q)
- [XL6009 Step Up Converter](https://www.amazon.de/-/en/A0040X5-5-Items/dp/B00HV59922)
- [XL4016E1 Step Down Converter](https://www.az-delivery.de/en/products/xl4016e-yh11060d)
- [Arducam B0268 Wide Angle Camera](https://www.arducam.com/product/arducam-16mp-wide-angle-usb-camera-for-laptop-1-2-8-cmos-imx298-mini-uvc-b0268/)
- [Raspberry Pi Camera Module 3 Wide](https://www.berrybase.de/en/raspberry-pi-camera-module-3-wide-12mp)

## Software
<p align="justify">
  Our <a href="/robot_v.3/Python/main">main program</a> is written in Python using primarily <a href="https://opencv.org/">OpenCV</a> and <a href="https://numpy.org/doc/1.26/index.html">NumPy</a> for image processing while following the black line. Different parts of the program like the communication with one of the Arduino Nanos for archiving sensor measurements via USB serial, are split into different files in order to use <a href="https://docs.python.org/3/library/multiprocessing.html">Python's multiprocessing</a> to execute them simultaneously and to fully utilize the available resources.
</p>

<p align="justify">
  We also utilized <a href="https://customtkinter.tomschimansky.com/">CustomTkinter</a> to create a visually appealing graphical user interface (GUI) for the display on our robot. This GUI (see the image below) shows the feeds from the two cameras with applied image processing, readings from installed sensors, timers that track total run time and time spent in the evacuation zone, and various other debugging information. Furthermore, it contains a detailed, rotating model of our robot, displayed with 5580 images that were previously rendered in <a href="https://www.blender.org/">Blender</a> and assigned to the corresponding real time rotation values obtained from the gyro sensors.
</p>

<div align="center">
  <img src="https://github.com/user-attachments/assets/8f858af3-c65e-4aff-91cc-c88a3b129bd2" style="width:70%;"/>
</div>

<br/>
<br/>

<p align="center">
  Our robot's capabilities are best showcased in a "perfect run" (with no human interventions or errors) at the 2024 World Championship in Eindhoven.
  
  <br/>
  
  <sub>
    (See the video below.) 
  </sub>
</p>

<div align="center">
  <a href="https://www.youtube.com/watch?v=x7Rn8mP2tpE">
     <img src="https://github.com/user-attachments/assets/f0cb298c-e418-4ef0-88bf-e6768288a34f" style="width:70%;">
  </a>
</div>

<br/>

## Why open source?

<p align="justify">
  We chose to open source our code because we think our code can be a great learning resource for teams wanting to try out camera based robots or current teams who are looking for resources about camera robots. Furthermore we think it's important to share knowledge and we encourage you to do the same! Either by uploading videos of your scoring runs on YouTube, open sourcing your code or as simple as chatting with other teams at competitions.
</p>


# About the team
<p align="justify">
  The team originally was founded in 2017 through 2 former members and began with a Lego Mindstorms NXT robot. The current team (Tim & Marius) switched to a camera based robot at around March 2022, when Tim joined the robotics club. We iterated on the design until now (2024) and achieved to finish as the 1st Place (Individual Team) at the world championship 2024 in Eindhoven. Our progress can be seen in the many YouTube videos we uploaded over the years. More information about the team can be found in the poster and TDP (documentation).
</p>

<p align="justify">
We will not participate in any RoboCup Junior competitions in the future, as we will both be university students in 2025.
</p>

## Achievements

- 1st @ Local School Qualifying Tournament 2022
- 22nd @ German Open Kassel 2022
- 2nd @ Qualifying Tournament Hanover 2023
- 2nd @ German Open Kassel 2023
- 3rd @ European Championship Varaždin 2023
- 1st @ Qualifying Tournament Hanover 2024
- 1st @ German Open Kassel 2024
- 1st @ World Championship Eindhoven 2024

# Contributors

- https://github.com/Tim4022
- https://github.com/Skillnoob

# Links

- [YouTube](https://www.youtube.com/@Overengineering2)
- [Coral TPU Cooler](https://makerworld.com/en/models/233023) by us

##

**We will answer questions whenever we can, but please don't expect active support for this repository**
