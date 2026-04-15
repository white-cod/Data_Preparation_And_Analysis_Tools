#pragma once
#include <opencv2/opencv.hpp>
#include <string>
#include "KeyProcessor.hpp"

class Display {
private:
    std::string windowName;
public:
    Display(const std::string& name, KeyProcessor* kp);
    void show(const cv::Mat& frame);
};