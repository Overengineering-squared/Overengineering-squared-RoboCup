#!/bin/bash

# Update system packages
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove -y

# delete the EXTERNALLY-MANAGED file because apt LOVES to create it, see reason in install.sh
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED

# Update python packages
pip3 install -U -r requirements.txt
