import spidev
import time
import lis3dhh
import numpy as np
import sys

# check for output filename
if len(sys.argv) == 3:
    outfilename = sys.argv[1]
    mtime = float(sys.argv[2])
else:
    outfilename = 'output.csv'
    mtime = 1

# init spi interface
spi = spidev.SpiDev()
bus = 0
device = 0
spi.open(bus, device)
spi.max_speed_hz = 5000000
spi.mode = 0b11

# init lis3dhh
acc = lis3dhh.LIS3DHH(spi.xfer2)

datalist = []
t0 = time.time()
tc = time.time()

while (tc - t0) < mtime:
    if(acc.hasnewdata()):
        datalist.append(acc.get3V())
    tc = time.time()

datalistnp = np.array(datalist)
np.savetxt(outfilename, datalistnp, delimiter=",")

