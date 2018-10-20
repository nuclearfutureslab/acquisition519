import spidev
import time
import lis3dhh
import numpy as np
import sys

# check for output filename
if len(sys.argv) == 2:
    outfilename = sys.argv[1]
else:
    outfilename = 'output.csv'

# init spi interface
spi = spidev.SpiDev()
bus = 0
device = 0
spi.open(bus, device)
spi.max_speed_hz = 5000000
spi.mode = 0b11

# init lis3dhh
acc = lis3dhh.LIS3DHH(spi.xfer2)
print(acc.whoami())

# collecting 500 samples
t0 = time.time()
sampleno = 500
data = acc.getsamples(sampleno)
t1 = time.time()
print("No Fifo: Collected {:d} samples in {:f} seconds, {:f} samples/s".format(sampleno, t1 - t0, sampleno / (t1 - t0)))

# collecting 500 samples
acc.setfifo(mode = lis3dhh.SET_FIFO_CONTINUOUS)
print("fifo set")
sampleno = 500
acc.emptyfifo()
t0 = time.time()
data = acc.fastgetsamples(sampleno)
t1 = time.time()
print("Fifo: Collected {:d} samples in {:f} seconds, {:f} samples/s".format(sampleno, t1 - t0, sampleno / (t1 - t0)))



