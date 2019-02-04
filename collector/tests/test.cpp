#define BOOST_TEST_MODULE collector
#include <boost/test/included/unit_test.hpp>

#include <cstring>

#include "model.h"

BOOST_AUTO_TEST_CASE(Recog_Exception) {
    std::string msg = "sample text";
    Recog::Exception e (msg);

    BOOST_TEST( e.what() == msg );

    bool thrown = false;
    try { throw e; }
    catch(Recog::Exception& e) {    
        BOOST_TEST( e.what() == msg );
        thrown = true;
    }
    BOOST_TEST(thrown);
}

BOOST_AUTO_TEST_CASE(Recog_Object) {
    Recog::Object o;
    o.azimuth = 30;
    o.distance = 25;

    BOOST_TEST(o.azimuth == 30);
    BOOST_TEST(o.distance == 25);

    auto cartese = o.toCartesian(1);
    BOOST_TEST( (cartese.x - 21.650635) < 0.00001 );
    BOOST_TEST( (cartese.y - 12.499999) < 0.00001 );

    cartese = o.toCartesian(2);
    BOOST_TEST( (cartese.x - 43.30127) < 0.00001 );
    BOOST_TEST( (cartese.y - 24.999998) < 0.00001 );

    o.azimuth = 90;
    o.distance = 5;
    cartese = o.toCartesian(20);
    BOOST_TEST( (cartese.x - 0) < 0.00001 );
    BOOST_TEST( (cartese.y - 100) < 0.00001 );

    o.azimuth = 180;
    o.distance = 9;
    cartese = o.toCartesian(10);
    BOOST_TEST( (cartese.x - (-90)) < 0.00001 );
    BOOST_TEST( (cartese.y - 0) < 0.00001 );

}

BOOST_AUTO_TEST_CASE(Recog_Wavelet_Convolution) {
    Recog::Wavelet w( [](unsigned s){ return [s](long x){ return x; }; } );
    
    float data[] = {1,2,3,4,5};
    cv::Mat m1 = cv::Mat(1, 5, CV_32F, data);
    BOOST_TEST( (w*m1) == 20 );
}

typedef std::array<int, SEGMENT_SIZE> Segment;
typedef std::vector<Segment> Segments;
Segments readFile(const char * filename) {
    FILE * f;
    f = fopen(filename, "rb");
    if(f == NULL) {
        return Segments(); 
    }
    // count segment count
    fseek(f, 0L, SEEK_END);
        int segN = ftell(f) / (SEGMENT_SIZE*2);
        std::cerr << filename << ": Loaded " << segN << " segments of " << SEGMENT_SIZE*2 << " B.\n";
    fseek(f, 0L, SEEK_SET);

    Segments r;
    char data[2];
    for(int segIt = 0; segIt < segN; segIt++) {
        Segment a;
        for(int i = 0; i < SEGMENT_SIZE*2; i += 2) {
            data[0] = fgetc(f);
            data[1] = fgetc(f);
            unsigned r = (data[0] << 8) | (0xFF & data[1]);
            a.at(i/2) = r;                        
        }
        r.push_back(a);
    }
    return r;
}
BOOST_AUTO_TEST_CASE(Recog_Wavelet) {
    Segments segments = readFile("../../data/calm03.dat");

    int k = 1;
    for(auto& seg: segments) {
        /*
        std::cerr << "Matrix: [";
        for(auto& it: seg) {
            std::cerr << it << ", ";
        }
        std::cerr << "\x08\x08]\n";
        */
        cv::Mat x;
        cv::Mat x_i(1, SEGMENT_SIZE, CV_32S, seg.data());
        x_i.convertTo(x, CV_32F);
        BOOST_TEST((x.type() & CV_MAT_DEPTH_MASK) == CV_32F);
        //std::cerr << "Matrix: " << x << "\n";
        //std::cerr << "Create matrix of samples " << x.rows << "x" << x.cols << ".\n";
        Recog::Wavelet w(Recog::Wavelet::Morlet); 
        Recog::Features r(x, w);

        FILE * f;
        char filename[60];
        sprintf(filename, "calm03_segment%d_cwt.csv", k++);
        f = fopen(filename, "w");
        for(int i = 0; i < r.rows(); i++) {
            for(int j = 0; j < r.cols(); j++) {
                fprintf(f, "%f",r.get().at<float>(i,j));
                if( j+1 < r.cols() ) { fprintf(f, ","); }
            }
            fprintf(f, "\n");
        }
        fclose(f);

        //cv::Mat dst;
        //cv::normalize(r.get(), dst, 0, 1, cv::NORM_MINMAX);
        //std::cerr << "Matrix: " << dst << "\n";
        //cv::imshow("test", dst);
        //cv::waitKey(0);

        //std::cerr << "Matrix: " << r.get() << "\n";


        std::cerr << "Segment processed. Returned feature matrix "
                  << r.rows() << "x" << r.cols() << ".\n";
    }



    

}

BOOST_AUTO_TEST_CASE(Recog_Features) {

}

BOOST_AUTO_TEST_CASE(Recog_Result) {
    Recog::Result r;
    r.data = { Recog::Object(1,2), Recog::Object(3,4), Recog::Object(5,6) };
    r.timestamp = 5;

    int * b = (int *)r.toBuffer();
    unsigned buffsize = r.bufferSize();

    BOOST_TEST( buffsize == 7*sizeof(int) );
    BOOST_TEST( b[0] == 3 );
    for(int i = 1; i < 6; i++) {
        BOOST_TEST( b[i] == i );
    }
}

BOOST_AUTO_TEST_CASE(HW_Exception) {

}

BOOST_AUTO_TEST_CASE(HW_Sensor) {

}

BOOST_AUTO_TEST_CASE(Recog_Fusion) {
    
}