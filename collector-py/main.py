#!/usr/bin/env python3

import comm
import cwt









def main():
    client = comm.Client()
    transformer = cwt.Transformer()

    while True:
        data = client.get()
        cwtCoefs = transformer.process(data, show=True)





if __name__ == '__main__':
    main()

