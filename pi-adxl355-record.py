import spidev
import time
import numpy as np
import sys

import adxl355

# default values
outfilename = 'output.csv'
mtime = 1
rate = 62.5

# check for output filename, measurement length and rate
if len(sys.argv) == 3:
    outfilename = sys.argv[1]
    mtime = float(sys.argv[2])
elif len(sys.argv) == 4:
    outfilename = sys.argv[1]
    mtime = float(sys.argv[2])
    rate = float(sys.argv[3])
    if not rate in adxl355.ODR_TO_BIT:
        print("Can only do the following data rates: {:s}".format(sorted(adxl355.ODR_TO_BIT.keys())))
        exit(-1)

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
print("{:b}".format(adxl355.ODR_TO_BIT[rate]))
acc.setfilter(lpf = adxl355.ODR_TO_BIT[rate])
print("{:08b}".format(acc.read(adxl355.REG_FILTER)))

acc.setfilter(lpf = adxl355.SET_ODR_62_5)

datalist = []
t0 = time.time()
tc = time.time()

msamples = mtime * rate
mperiod = 1.0 / rate

datalist = []
acc.emptyfifo()
while (len(datalist) < msamples):
    if acc.fifofull():
        print("Fifo in ADXL355 was found full. Lost data.")
    if acc.hasnewdata():
        datalist += acc.get3Vfifo()

rawdatalist = acc.convertlisttoRaw(datalist)
gdatalist = acc.convertRawtog(acc.convertlisttoRaw(datalist))

alldata = []
for i in range(len(gdatalist)):
    alldata.append([0, i * mperiod] + gdatalist[i])

alldatanp = np.array(alldata)
np.savetxt(outfilename, alldatanp, delimiter=",")


