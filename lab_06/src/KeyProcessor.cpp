#include "KeyProcessor.hpp"

bool KeyProcessor::processKey(int key) {
    if (key == 27) return false;
    
    switch (key) {
        case 'n': case 'N': currentMode = ProcessMode::NORMAL; break;
        case 'i': case 'I': currentMode = ProcessMode::INVERT; break;
        case 'b': case 'B': currentMode = ProcessMode::BLUR; break;
        case 'c': case 'C': currentMode = ProcessMode::CANNY; break;
    }
    return true;
}