
import sys
import time
import threading

sys.path.insert(0, '.')
#sys.path.insert(0, '..')
import comm_replay




def main():
    r = comm_replay.Reader.getReader("../data/3m_LR/3m_LR_1.csv")
    time.sleep(2)
    r.readThrd.join()


if __name__ == '__main__':
    main()