#include "Display.hpp"

Display::Display(const std::string& name, KeyProcessor* kp) : windowName(name) {
    cv::namedWindow(windowName, cv::WINDOW_AUTOSIZE);
    cv::createTrackbar("Brightness", windowName, &kp->brightness, 100);
}

void Display::show(const cv::Mat& frame) {
    cv::imshow(windowName, frame);
}