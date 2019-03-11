

import time

import comm_mcast





def main():
    """Main function."""

    # create sensor reader
    s1 = comm_mcast.Reader.getReader("224.0.0.1", 1234)

    while True:
        if s1.indicate(False):
            data = s1.getSegment()
            print("Received", len(data), "B of data")
        else:
            time.sleep(0.3)



# main caller
if __name__ == "__main__":
    main()
