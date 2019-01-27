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

BOOST_AUTO_TEST_CASE(Recog_Wavelet) {

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