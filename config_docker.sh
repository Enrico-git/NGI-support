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

echo "Downloading Mystique Image"
sudo docker pull enrico2docker/ubuntu-mystique:1.4

echo "Creating Mystique Container"
sudo docker run --name mystique -p 6633:6633 -d -t enrico2docker/ubuntu-mystique:1.4

echo "Waiting for Docker container"
while ( ! sudo docker ps | grep mystique); do
  echo "Waiting for Docker container"
  sleep 3
done
