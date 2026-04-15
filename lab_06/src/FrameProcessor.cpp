#include "FrameProcessor.hpp"

FrameProcessor::FrameProcessor() {
    t0 = cv::getTickCount();
}

void FrameProcessor::process(cv::Mat& frame, const KeyProcessor& kp) {
    int beta = (kp.brightness - 50) * 2;
    frame.convertTo(frame, -1, 1, beta);

    switch (kp.currentMode) {
        case ProcessMode::INVERT:
            cv::bitwise_not(frame, frame);
            break;
        case ProcessMode::BLUR:
            cv::GaussianBlur(frame, frame, cv::Size(15, 15), 0);
            break;
        case ProcessMode::CANNY: {
            cv::Mat gray, edges;
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            cv::Canny(gray, edges, 50, 150);
            cv::cvtColor(edges, frame, cv::COLOR_GRAY2BGR);
            break;
        }
        case ProcessMode::NORMAL:
        default:
            break;
    }

    frameCount++;
    int64 t1 = cv::getTickCount();
    double timePassed = (t1 - t0) / cv::getTickFrequency();
    if (timePassed >= 1.0) {
        fps = frameCount / timePassed;
        frameCount = 0;
        t0 = t1;
    }

    std::string fpsText = "FPS: " + std::to_string((int)fps);
    cv::putText(frame, fpsText, cv::Point(10, 30), 
                cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(0, 255, 0), 2);
}