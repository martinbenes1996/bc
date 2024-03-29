
#include "model.h"

void Recog::Features::extract(cv::Mat x, Recog::Wavelet w) {
    unsigned N = x.cols;
    unsigned S = scales_.size();
    features_ = cv::Mat::zeros(S,N, CV_32F);

    // iterate over scales (columns)
    for(unsigned s = 0; s < S; s++) {
        w.setScale(scales_[s]);
        // iterate over shifts (rows)
        for(unsigned n = 0; n < N; n++) {
            w.setShift(n);
            // convolution
            float result = w*x;
            if( scales_[s] > n ) result = 0;
            features_.at<float>(S - (s+1),n) = result;
        }
    }
    extracted_ = true;
    valid_ = true;
}

float Recog::Wavelet::operator*(const cv::Mat& x) {
    unsigned T = x.cols;
    float sum = 0;
    for(unsigned t = 0; t < T; t++) {
        unsigned sigPos = /*T-(t+1)*/t;
        sum += x.at<float>(sigPos) * f_(t/s_ - shift_);
    }
    return sum;
}