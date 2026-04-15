#!/bin/bash
echo "Building project..."
mkdir -p build
cd build
cmake ..
make
echo "Project built successfully"