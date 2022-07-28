#!/bin/bash

echo "Installing Docker..."
sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

echo "Waiting for Docker to launch..."
while [ ! "$(command -v docker)" ]; do
  # Docker takes a few seconds to initialize
  echo "Waiting for Docker to launch..."
  sleep 1
done

while (! sudo docker stats --no-stream ); do
  # Docker takes a few seconds to initialize
  echo "Waiting for Docker to launch..."
  sleep 1
done

sudo touch happy2.txt

echo "Downloading Mystique Image"
sudo docker pull enrico2docker/ubuntu-mystique:1.1

echo "Creating Mystique Container"
sudo docker run --name mystique -p 6633:6633 -d -t enrico2docker/ubuntu-mystique:1.1

echo "Waiting for Docker container"
while ( ! sudo docker ps | grep mystique); do
  echo "Waiting for Docker container"
  sleep 3
done

sudo touch happy.txt

# config Ryu
# data_frequency= ' 1'
# support_switches=' s0'
# cmd_config_ryu = '/bin/bash /mystique/ryu_controller/config_ryu.sh'+data_frequency+support_switches #config.ini - ryu_controller
# cmd_docker_ryu = 'sudo docker exec -d mystique ' + cmd_config_ryu


# config Model

#run ryu

#run train
