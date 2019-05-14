
import sys
import time
import threading

sys.path.insert(0, '.')
import comm_replay
import conf




def main():
    conf.Config.setDebug(False)

    r = comm_replay.Reader.getReader("../data/c4m_LR_1/c4m_LR_1_1.csv")
    time.sleep(2)
    r.readThrd.join()


if __name__ == '__main__':
    main()