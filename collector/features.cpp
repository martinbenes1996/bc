
#include "model.h"

void Recog::Features::extract(cv::Mat x, Recog::Wavelet w) {
    unsigned N = x.cols;
    unsigned S = scales_.size();
    cv::Mat features = cv::Mat::zeros(S, N, CV_32S);

    // iterate over shifts (rows)
    for(unsigned n = 0; n < N; n++) {
        // iterate over scales (columns)
        for(unsigned s = 0; s < S; s++) {
            w.setScale(scales_[s]);
            w.setShift(n);
            // convolution
            features.at<int>(s,n) = w*x;
        }
    }
    extracted_ = true;
    valid_ = true;
}

double Recog::Wavelet::operator*(const cv::Mat& x) {
    unsigned T = x.cols;
    double sum = 0;
    for(unsigned t = 0; t < T; t++) {
        unsigned sigPos = T-(t+1);
        sum += x.at<int>(sigPos) * f_(t + shift_);
    }
    return sum;
}