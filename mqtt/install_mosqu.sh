#!/bin/bash

# Add the Mosquitto PPA repository
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa

# Update the package list
sudo apt-get update

# Install Mosquitto
sudo apt-get install mos

#install python / ensure it is installed
sudo apt-get install python3

# run the pip install command for the requirements.txt
python3 -m pip install -r requirements.txt

# start docker compose (Tested on WSL2.0 in Win11), otherwise use docker compose up -d
sudo docker-compose up -d

# Then you may run the two files:
# Subscriber may require sudo priviledge if UAC was configured like mine in WSL2

# python3 publisher.py
# sudo python3 subscriber.py



