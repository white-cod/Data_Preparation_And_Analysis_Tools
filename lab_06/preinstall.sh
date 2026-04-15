#!/bin/bash
echo "Installing dependencies for OpenCV..."
sudo apt update
sudo apt install -y libopencv-dev cmake g++ make
echo "Dependencies installed successfully!"