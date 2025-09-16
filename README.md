<img src="https://github.com/user-attachments/assets/d29a00c3-4102-41a2-afe6-8e1174fef7b9" style="width:100%;"/>

<br/>
<br/>

<div align="center">
  <a href="https://github.com/Tim4022">
    <img src="https://img.shields.io/badge/Contributor-Tim4022-blue" alt="Tim4022">
  </a>
  
  <a href="https://github.com/Skillnoob">
    <img src="https://img.shields.io/badge/Contributor-Skillnoob-blue" alt="Skillnoob">
  </a>
  
  <a href="https://www.youtube.com/@Overengineering2">
    <img src="https://img.shields.io/badge/YouTube-Overengineering2-red?logo=youtube" alt="Overengineering2 YouTube Channel">
  </a>
</div>

<br/>
<br/>

<p align="center">
  This is the repository for the German team Overengineering² (Georg-Büchner-Gymnasium, Seelze), which competed in
the <a href="https://junior.robocup.org/">RoboCup Junior</a> sub-league <a href="https://junior.robocup.org/rcj-rescue-line/">Rescue-Line</a>.
</p>

# About the Competition
<p align="center"><i>
  "The land is too dangerous for humans to reach the victims. Your team has been given a challenging task. The robot must be able to carry out a rescue mission in a fully autonomous mode with no human assistance. The robot must be durable and intelligent enough to navigate treacherous terrain with hills, uneven land, and rubble without getting stuck. When the robot reaches the victims, it has to gently and carefully transport each one to the safe evacuation point where humans can take over the rescue. The robot should exit the evacuation zone after a successful rescue to continue its mission throughout the disaster scene until it leaves the site. Time and technical skills are essential!"
</i></p>

<div align="center">
  <img src="https://github.com/user-attachments/assets/a0c5800d-fcd0-47f1-990c-3d6951691d1c" style="width:70%;"/>
</div>

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

<p align="center">
  In order to achieve all the tasks mentioned above, we decided to take a completely camera-based approach using Raspberry Pi. The development of this design started in March 2022 and has been iterated until now (2024).
</p>

<p align="center">
  With this latest iteration of the robot design, we achieved first place (Individual Team) at the RoboCup Junior World Championship 2024 in Eindhoven. (See the results <a href="documents/scores/Rescue_Line_Overall_Score_World_Championship_Eindhoven.pdf">here</a>.)
</p>

<br/>

<p align="justify">
  As required by the competition <a href="https://junior.robocup.org/wp-content/uploads/2024/04/RCJRescueLine2024-final-1.pdf">rules</a>, in addition to this GitHub, we created a detailed documentation of the robot and our development process in the form of an <a href="documents/documentation/Engineering Journal.pdf">Engineering Journal</a>, a <a href="documents/documentation/Team Description Paper.pdf">Team Description Paper</a>, and a <a href="documents/documentation/Poster.pdf">Poster</a> (all three of which earned us the highest possible score at the 2024 World Championship in Eindhoven).
</p>

## Components

<p align="justify">
  Aside from the custom, 3D-printed robot chassis and customized wheels to fit our mounting hubs, we used mostly off-the-shelf components for their reliability and active support. Our latest iteration used the following parts:
</p>

- 1x [Raspberry Pi 5 8GB](https://www.raspberrypi.com/products/raspberry-pi-5/)
- 1x [Coral USB Accelerator](https://coral.ai/products/accelerator)
- 2x [Arduino Nano](https://store.arduino.cc/en-de/products/arduino-nano)
- 2x [Adafruit BNO055 Gyroscope](https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/overview)
- 6x [Pololu irs17a Infrared Sensor](https://www.pololu.com/product/4071)
- 1x [Pololu irsl16a Infrared Sensor](https://www.pololu.com/product/4067)
- 1m [revoART 12V COB LED-Strip](https://www.leds24.com/12v-cob-led-streifen-neutralweiss-alle-1-cm-teilbar-3mm-breit-)
- 1x [KY-019 Relay](https://sensorkit.joy-it.net/en/sensors/ky-019)
- 5x [Emax ES09MD Servo](https://www.premium-modellbau.de/emax-es09md-digital-metallgetriebe-mini-servo-15g-0-08s-2-6kg-kugellager-es08md)
- 1x [Diymore 35KG Servo](https://www.amazon.de/-/en/diymore-Waterproof-Helicopter-Aeroplane-Suitable/dp/B0BD3XKQSW)
- 4x 12V DC Geared Motor (we don't know the model, our mentor got a recomendation for these in 2017 from a soccer league team, picture is in the [Poster](documents/documentation/Poster.pdf))
- 4x Neoprene Wheels made of neoprene discs and aluminum mounting hubs (we don't know where to buy them anymore because our robotics club bought them a long time ago)
- 1x [L298N Motor Driver](https://projecthub.arduino.cc/lakshyajhalani56/l298n-motor-driver-arduino-motors-motor-driver-l298n-7e1b3b) (controllable from the 3.3V pins of a Raspberry Pi)
- 1x [Conrad 7.4V 3800mAh LiPo](https://www.conrad.com/en/p/conrad-energy-scale-model-battery-pack-lipo-7-4-v-3800-mah-no-of-cells-2-20-c-softcase-xt60-1344142.html)
- 1x [Conrad 11.1V 3800mAh LiPo](https://www.conrad.de/de/p/conrad-energy-modellbau-akkupack-lipo-11-1-v-3800-mah-zellen-zahl-3-20-c-softcase-xt60-1344139.html)
- 1x [XL4015 Step Down Converter](https://www.amazon.de/-/en/XL4015DC-Converter-DC5V-32V-Charging-Constant/dp/B0CC96CN3Q)
- 2x [XL6009 Step Up Converter](https://www.amazon.de/-/en/A0040X5-5-Items/dp/B00HV59922)
- 1x [XL4016E1 Step Down Converter](https://www.az-delivery.de/en/products/xl4016e-yh11060d)
- 1x [Arducam B0268 Wide Angle Camera](https://www.arducam.com/product/arducam-16mp-wide-angle-usb-camera-for-laptop-1-2-8-cmos-imx298-mini-uvc-b0268/)
- 1x [Raspberry Pi Camera Module 3 Wide](https://www.berrybase.de/en/raspberry-pi-camera-module-3-wide-12mp)
- 1x [7,0" IPS Touch-Display](https://www.berrybase.de/universal-7-0-ips-display-mit-hdmi-vga-eingang-und-kapazitivem-touchscreen)

## Software

### Main Program
<p align="justify">
  Our <a href="/robot_v.3/Python/main">main program</a> is written in Python using primarily <a href="https://opencv.org/">OpenCV</a> and <a href="https://numpy.org/doc/1.26/index.html">NumPy</a> for the image processing while following the black line. Different parts of the program like the communication with one of the Arduino Nanos for archiving sensor measurements via USB serial, are split into different files to use <a href="https://docs.python.org/3/library/multiprocessing.html">Python's multiprocessing</a> to execute them simultaneously and to fully use the available resources. Some parts of the image processing are additionally accelerated by the just-in-time compiler <a href="https://numba.pydata.org/">Numba</a>. For more information about our image processing, see our <a href="documents/documentation/Engineering Journal.pdf">Engineering Journal</a>, <a href="documents/documentation/Team Description Paper.pdf">TDP</a>, or <a href="documents/documentation/Poster.pdf">Poster</a>.
</p>

### GUI
<p align="justify">
  We also used <a href="https://customtkinter.tomschimansky.com/">CustomTkinter</a> to create a visually appealing graphical user interface (GUI) for the display on our robot. This GUI (see the image below) shows the feeds from the two cameras with applied image processing, readings from installed sensors, timers that track total run time and time spent in the evacuation zone, and various other debugging information. Furthermore, it contains a detailed, rotating model of our robot, displayed with 5580 images that were previously rendered in <a href="https://www.blender.org/">Blender</a> and assigned to the corresponding real time rotation values obtained from the gyro sensors.
</p>

<div align="center">
  <img src="https://github.com/user-attachments/assets/8f858af3-c65e-4aff-91cc-c88a3b129bd2" style="width:70%;"/>
</div>

### AI

<p align="justify">
  We have chosen to switch to an AI model for the following tasks because we believe it is the most efficient way to solve them. Previous image processing methods had many flaws (such as OpenCV's <a href="https://docs.opencv.org/4.10.0/d4/d70/tutorial_hough_circle.html">Hough Circle Transform</a>), and we believe that AI models can solve these tasks with less effort and better reliability.
</p>

#### Victim Detection
<p align="justify">
  The victim detection inside the evacuation zone relies on a self-trained <a href="https://docs.ultralytics.com/models/yolov8/">YoloV8</a> model. The model was trained on a dataset of 3145 images (available <a href="https://universe.roboflow.com/overengineering-rswji/evacuation-zone">here</a>) using <a href="https://colab.research.google.com/">Google Colab</a>. Together with a wide angle camera and a <a href="https://coral.ai/products/accelerator">Coral USB Accelerator</a>, the model can detect the victims with a high accuracy as well as high FPS. Combining everything, we can reliably complete the evacuation zone in under two minutes or in 52.36 seconds when optimized for speed ;). (See the video <a href="https://youtu.be/VQkRPGvYs4w">here</a>.)
</p>

#### Evacuation Zone Entrance Detection
<p align="justify">
  Just like the victim detection, the detection of the silver reflective strip at the entrance of the evacuation zone is done through a <a href="https://docs.ultralytics.com/models/yolov8/">YoloV8</a> AI model, but instead using the <a href="https://docs.ultralytics.com/tasks/classify/">classification</a> task. After collecting 10998 images for the dataset (available <a href="https://universe.roboflow.com/overengineering-rswji/silver-strip">here</a>) and training the model using <a href="https://colab.research.google.com/">Google Colab</a>, the model can detect the silver strip with an extremely high accuracy and has so far never failed us. The model is exported using the <a href="https://docs.ultralytics.com/modes/export/">Ultralytics export mode</a> to an <a href="https://docs.ultralytics.com/integrations/onnx/">ONNX</a> model for increased performance and runs on the CPU of our Raspberry Pi 5.
</p>

<br/>
<br/>
<br/>

<p align="center">
  Our robot's capabilities are probably best demonstrated in a "perfect run" (without human intervention or error) at the 2024 World Championship in Eindhoven.
  
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
  We decided to open source our code because we think our code can be a great learning resource for teams wanting to try out camera-based robots or current teams who are looking for resources about camera robots. We also think it's important to share knowledge, and we encourage you to do the same! Either by uploading videos of your scoring runs to YouTube, open-sourcing your code, or as simple as chatting with other teams at competitions. However we will not publish or share the CAD models of the robot.
</p>


# About the team
<p align="justify">
  The team originally was founded in 2017 through two former members and began with a Lego Mindstorms NXT robot. The current team (Tim & Marius) switched to a camera-based robot in around March 2022, when Tim joined the robotics club. Besides preparing for our graduation (Abitur) this year, we also iterated on the robot's design until now (2024) and managed to win first place (Individual Team) at the 2024 World Championship in Eindhoven. Our progress can be seen in the many <a href="https://www.youtube.com/@overengineering2">YouTube</a> videos we uploaded over the years. More information about the team can also be found in the <a href="documents/documentation/Engineering Journal.pdf">Engineering Journal</a>, <a href="documents/documentation/Team Description Paper.pdf">TDP</a>, or the <a href="documents/documentation/Poster.pdf">Poster</a>.
</p>

<p align="justify"><b>
We will not participate in any RoboCup Junior competitions in the future, as we will both be university students in 2025.
</b></p>

## Achievements

- 1st @ Local School Qualifying Tournament 2022
- 22nd @ German Open Kassel 2022
- 2nd @ Qualifying Tournament Hanover 2023
- 2nd @ German Open Kassel 2023
- **3rd @ European Championship Varaždin 2023**
- 1st @ Qualifying Tournament Hanover 2024
- 1st @ German Open Kassel 2024
- **1st @ World Championship Eindhoven 2024**

# Links

- [YouTube](https://www.youtube.com/@Overengineering2)
- [Coral TPU Cooler](https://makerworld.com/en/models/233023) by us

# License
This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details. \
Additionally, you can read up one the license [here](https://choosealicense.com/licenses/gpl-3.0/).

##

**We will answer questions whenever we can, but please don't expect active support for this repository**
