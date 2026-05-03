#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <thread>
#include <mutex>
#include <atomic>
#include <condition_variable>
#include <vector>
#include <chrono>

class FaceDetector {
private:
    std::thread worker;
    std::mutex mtx;
    std::condition_variable condVar;
    std::atomic<bool> running;
    
    cv::dnn::Net net;
    cv::Mat currentFrame;
    bool newFrameReady;
    
    std::vector<cv::Rect> latestFaces;

    void process() {
        while (running) {
            cv::Mat frameToProcess;
            {
                std::unique_lock<std::mutex> lock(mtx);
                condVar.wait(lock, [this]() { return newFrameReady || !running; });
                
                if (!running) break;
                
                frameToProcess = currentFrame.clone();
                newFrameReady = false;
            }
            
            if (frameToProcess.empty()) continue;

            cv::Mat blob = cv::dnn::blobFromImage(frameToProcess, 1.0, cv::Size(300, 300), cv::Scalar(104.0, 177.0, 123.0));
            net.setInput(blob);
            
            auto detections = net.forward();
            
            std::vector<cv::Rect> detectedFaces;
            cv::Mat detectionMat(detections.size[2], detections.size[3], CV_32F, detections.ptr<float>());
            
            for (int i = 0; i < detectionMat.rows; i++) {
                float confidence = detectionMat.at<float>(i, 2);
                if (confidence > 0.5) {
                    int x1 = static_cast<int>(detectionMat.at<float>(i, 3) * frameToProcess.cols);
                    int y1 = static_cast<int>(detectionMat.at<float>(i, 4) * frameToProcess.rows);
                    int x2 = static_cast<int>(detectionMat.at<float>(i, 5) * frameToProcess.cols);
                    int y2 = static_cast<int>(detectionMat.at<float>(i, 6) * frameToProcess.rows);
                    
                    detectedFaces.push_back(cv::Rect(cv::Point(x1, y1), cv::Point(x2, y2)));
                }
            }
            
            {
                std::lock_guard<std::mutex> lock(mtx);
                latestFaces = detectedFaces;
            }
        }
    }

public:
    FaceDetector(const std::string& prototxt, const std::string& model) {
        try {
            net = cv::dnn::readNetFromCaffe(prototxt, model);
        } catch (const cv::Exception& e) {
            std::cerr << "Помилка завантаження моделі: " << e.what() << std::endl;
            exit(1);
        }
        
        running = true;
        newFrameReady = false;
        worker = std::thread(&FaceDetector::process, this);
    }
    
    ~FaceDetector() {
        running = false;
        condVar.notify_all();
        if (worker.joinable()) {
            worker.join();
        }
    }
    
    void updateFrame(const cv::Mat& frame) {
        std::lock_guard<std::mutex> lock(mtx);
        currentFrame = frame.clone();
        newFrameReady = true;
        condVar.notify_one();
    }
    
    std::vector<cv::Rect> getFaces() {
        std::lock_guard<std::mutex> lock(mtx);
        return latestFaces;
    }
    
    void clearFaces() {
        std::lock_guard<std::mutex> lock(mtx);
        latestFaces.clear();
    }
};

int main() {
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Не вдалося відкрити камеру" << std::endl;
        return -1;
    }
    
    FaceDetector detector("deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel");
    
    bool faceDetectionEnabled = false;
    std::cout << "Натисніть 'F' для увімкнення/вимкнення детекції облич." << std::endl;
    std::cout << "Натисніть 'ESC' або 'Q' для виходу." << std::endl;
    
    auto timeStart = std::chrono::steady_clock::now();
    int framesCount = 0;
    double fps = 0.0;
    
    while (true) {
        cv::Mat frame;
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Кадр порожній Завершення роботи." << std::endl;
            break;
        }
        
        if (faceDetectionEnabled) {
            detector.updateFrame(frame);
            
            auto faces = detector.getFaces();
            
            for (const auto& face : faces) {
                cv::rectangle(frame, face, cv::Scalar(0, 255, 0), 2);
            }
            
            cv::putText(frame, "Face Detection: ON", cv::Point(10, 30), 
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 255, 0), 2);
        } else {
            detector.clearFaces();
            cv::putText(frame, "Face Detection: OFF (Press 'F' to turn ON)", cv::Point(10, 30), 
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 0, 255), 2);
        }
        
        framesCount++;
        auto timeNow = std::chrono::steady_clock::now();
        std::chrono::duration<double> timeDiff = timeNow - timeStart;
        if (timeDiff.count() >= 1.0) {
            fps = framesCount / timeDiff.count();
            framesCount = 0;
            timeStart = timeNow;
        }
        
        cv::putText(frame, "FPS: " + std::to_string((int)fps), cv::Point(10, 60), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(255, 0, 0), 2);
        
        cv::imshow("Camera", frame);
        
        char key = (char)cv::waitKey(1);
        if (key == 27 || key == 'q' || key == 'Q') {
            break;
        } else if (key == 'f' || key == 'F') {
            faceDetectionEnabled = !faceDetectionEnabled;
        }
    }
    
    cap.release();
    cv::destroyAllWindows();
    return 0;
}