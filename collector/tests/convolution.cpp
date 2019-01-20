
#include "../model.h"

int main() {
    Recog::Wavelet w ( [](unsigned){
        return [](long t) { return (double)(t+1); };
    } );

    cv::Mat m = cv::Mat::zeros(1, 3, CV_32F);
    m.at<float>(0) = 1;
    m.at<float>(1) = 2;
    m.at<float>(2) = 3;

    double c = w*m;
    assert(c == 10);
}