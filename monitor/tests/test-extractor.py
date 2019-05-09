
import sys
import time

sys.path.insert(0, '.')
import model
import comm_serial
import comm
import conf

i = 0
status = True
def test(s1, s2, acc = 0.0001):
    global status
    global i
    i += 1
    d = abs(s1 - s2)
    
    if d > acc:
        if status:
            print("")
        print(str(i)+": "+str(s1)+" != "+str(s2)+".", file=sys.stderr)
        status = False

def generalTest():
    try:
        devicename = '/dev/ttyS1'
        src = comm.Reader()
        extractor = model.Extractor.getExtractor(devicename, src)
        for i in range(0,10):
            time.sleep(conf.Config.period()/1000)
            src.indicate(True)
    except Exception as e:
        print("Extractor failed when simulating serial line!")
        status = False
        raise e
    finally:
        extractor.stop()

def main():
    global status
    conf.Config.init()
    try:
        generalTest()
    except Exception as e:
        print(e)
        status = False
        raise e

    assert(status)





if __name__ == '__main__':
    main()
