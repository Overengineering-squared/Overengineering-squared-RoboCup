#!/bin/bash

sudo apt-get update && sudo apt-get upgrade -y

# gpiozero because RPI.GPIO doesn't work with a Pi 5
# onboard because its a great onscreen keyboard
# simple screen recorder because its the most performant screen recorder we found, since we need it to minimally impact the performance of the robot
sudo apt-get install python3-gpiozero onboard simplescreenrecorder -y && sudo apt-get autoremove -y

# Copy over preconfigured file for onboard
cp -fr config/user /home/pi/.config/dconf

# This is to patch the PI for our 1024x600 touchscreen to work
echo " video=HDMI-A-1:1024x600M@59.96D" | sudo tee -a /boot/firmware/cmdline.txt

# Python/Raspi Os is annoying and doesn't allow you to install packages outside of a venv so we just delete the file that limits it
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED

# Install the requirements
pip3 install -U -r requirements.txt

# Install the tflite runtime. Required for the edge TPU to work correctly
pip3 install robot_v.3/Ai/tflite_runtime/tflite_runtime-2.15.0-cp311-cp311-linux_aarch64.whl

read -p "Please unplug the edge TPU and press enter"

# Install a custom Edge TPU library that fixes segmentation faults caused by the 3 year old version of the library
sudo dpkg -i robot_v.3/Ai/libedgetpu/libedgetpu1-max_16.0tf2.15.0-1.bookworm_arm64.deb

read -p "Please plug in the edge TPU and press enter"

# Create the autostart file in case the Pi is rebooted or crashed
./create_autostart.sh