
#include "model.h"

void Recog::Features::extract(cv::Mat x, Recog::Wavelet w) {
    unsigned N = x.cols;
    unsigned S = scales_.size();
    cv::Mat features = cv::Mat::zeros(S, N, CV_32F);

    // iterate over shifts (rows)
    for(unsigned n = 0; n < N; n++) {
        // iterate over scales (columns)
        for(auto& s: scales_) {
            w.setScale(s);
            w.setShift(n);
            // convolution
            features.at<float>(s,n) = w*x;
        }
    }
    extracted_ = true;
}

double Recog::Wavelet::operator*(const cv::Mat& x) {
    unsigned T = x.cols;
    double sum = 0;
    for(unsigned t = 0; t < T; t++) {
        unsigned sigPos = T-(t+1);
        // std::cerr << "x[T - t] = " << x.at<float>(sigPos) << "\n";
        // std::cerr << "Psi[t] = " << f_(t) << "\n";
        sum += x.at<float>(sigPos) * f_(t + shift_);
    }
    return sum;
}