#include "CameraProvider.hpp"
#include "KeyProcessor.hpp"
#include "FrameProcessor.hpp"
#include "Display.hpp"
#include <iostream>

int main() {
    CameraProvider camera(0);
    if (!camera.isOpened()) {
        return -1;
    }

    KeyProcessor keyProcessor;
    FrameProcessor frameProcessor;
    Display display("Lab 6 - C++ OpenCV", &keyProcessor);

    while (true) {
        cv::Mat frame = camera.getFrame();
        if (frame.empty()) {
            std::cerr << "Error: Empty frame!" << std::endl;
            break;
        }

        frameProcessor.process(frame, keyProcessor);

        display.show(frame);

        int key = cv::waitKey(30);
        if (!keyProcessor.processKey(key)) {
            break;
        }
    }

    return 0;
}