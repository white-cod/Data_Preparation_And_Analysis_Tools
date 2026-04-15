#pragma once

enum class ProcessMode {
    NORMAL,
    INVERT,
    BLUR,
    CANNY
};

class KeyProcessor {
public:
    ProcessMode currentMode = ProcessMode::NORMAL;
    int brightness = 50;

    bool processKey(int key);
};