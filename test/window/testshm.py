
import sys
sys.path.insert(0, '../../src/window/')

import shm


def main():
    mem = shm.ShmWrapper()
    print('nazdar')

if __name__ == '__main__':
    main()