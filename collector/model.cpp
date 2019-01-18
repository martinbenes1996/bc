
#include <vector>

#include "model.h"

class Wavelet {
    public:
        enum Type {
            Morlet,
            Coiflet,
            Daubechies,
            Biorthogonal,
            MexicanHat,
            Symlet,
        };

        Wavelet(Type t, int scale): s_(scale) {
            switch(t) {
                case Morlet:
                    f_ = [](double x){return x;};
                    break;
                default:
                    break;
            }
        }

        double operator*(const cv::Mat& x) {
            std::cerr << "Operator * called!\n";
            return 0.;
        }

    private:
        std::function<double(double)> f_ = [](double){return 0.;};
        unsigned s_;

};

void CWT(cv::Mat x, Wavelet wavelet, std::vector<unsigned> scales, cv::Mat& y) {
    unsigned N = x.cols;
    unsigned S = scales.size();
    cv::Mat features = cv::Mat::zeros(S, N, CV_32F);



    // iterate over shifts (rows)
    for(unsigned n = 0; n < N; n++) {
        // iterate over scales (columns)
        for(auto& s: scales) {

            // iterate over signal (convolution)
            for(unsigned t = 0; t < N; t++) {
                
                features.at<float>(n,s);
            }

        }
    }
}


