#pragma once
#include <opencv2/opencv.hpp>
#include "KeyProcessor.hpp"

class FrameProcessor {
private:
    int frameCount = 0;
    double fps = 0.0;
    int64 t0;
public:
    FrameProcessor();
    void process(cv::Mat& frame, const KeyProcessor& kp);
};