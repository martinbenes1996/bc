#!/usr/bin/env python3

import comm
import cwt
import log









def main():
    client = comm.Client()
    transformer = cwt.Transformer()
    view = log.Viewer()

    while True:
        data = client.get()
        cwtCoefs = transformer.process(data)

        # view cwt coefficients
        view.cwt(cwtCoefs)





if __name__ == '__main__':
    main()

