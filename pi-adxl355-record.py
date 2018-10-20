import spidev
import time
import numpy as np
import sys

import adxl355

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
device = 1
spi.open(bus, device)
spi.max_speed_hz = 5000000
# important - ADXL 355 has mode SPOL=0 SPHA=0
spi.mode = 0b00

# init adxl355
acc = adxl355.ADXL355(spi.xfer2)

acc.start()

acc.setrange(adxl355.SET_RANGE_2G)
acc.setfilter(lpf = adxl355.SET_ODR_1000)

datalist = []
t0 = time.time()
tc = time.time()

while (tc - t0) < mtime:
    if(acc.hasnewdata()):
        datalist.append(acc.get3V())
    tc = time.time()

datalistnp = np.array(datalist)
np.savetxt(outfilename, datalistnp, delimiter=",")


