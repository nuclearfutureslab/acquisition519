import spidev
import time
import numpy as np
import sys

import adxl355
import lis3dhh

# check for output filename
if len(sys.argv) == 3:
    outfilename = sys.argv[1]
    mtime = float(sys.argv[2])
else:
    outfilename = 'output.csv'
    mtime = 5

# init spi interface for adxl355
spi1 = spidev.SpiDev()
bus1 = 0
device1 = 1
spi1.open(bus1, device1)
spi1.max_speed_hz = 5000000
# important - ADXL 355 has mode SPOL=0 SPHA=0
spi1.mode = 0b00

# init spi interface for lis3dhh
spi2 = spidev.SpiDev()
bus2 = 0
device2 = 0
spi2.open(bus2, device2)
spi2.max_speed_hz = 5000000
# important - lis3dhh has mode SPOL=1 SPHA=1
spi2.mode = 0b11

# init adxl355
acc1 = adxl355.ADXL355(spi1.xfer2)
rate = 1000
acc1.setfilter(lpf=adxl355.SET_ODR_1000) # set data rate to 1khz

# init lis3dhh
acc2 = lis3dhh.LIS3DHH(spi2.xfer2)

IDX_ADXL355 = 0
IDX_LIS3DHH = 1

# measure both for mtime seconds
msamples = {}
msamples[IDX_ADXL355] = mtime * rate
msamples[IDX_LIS3DHH] = mtime * 1100
mperiod = {}
mperiod[IDX_ADXL355] = 1.0 / rate
mperiod[IDX_LIS3DHH] = 1.0 / 1100


datalist = {}
datalist[IDX_ADXL355] = []
datalist[IDX_LIS3DHH] = []

acc2.emptyfifo()
acc1.emptyfifo()
discard = acc2.fifovalues()
while (len(datalist[IDX_ADXL355]) < msamples[IDX_ADXL355]) or (len(datalist[IDX_LIS3DHH]) < msamples[IDX_LIS3DHH]):
    if acc2.fifofull():
        print("Fifo in LIS3DHH was found full. Lost data.")
    datalist[IDX_LIS3DHH] += acc2.get3Vfifo()
    if acc1.fifofull():
        print("Fifo in ADXL355 was found full. Lost data.")
    datalist[IDX_ADXL355] += acc1.get3Vfifo()

datalist[IDX_LIS3DHH] = acc2.convertRawtog(acc2.convertlisttoRaw(datalist[IDX_LIS3DHH]))
datalist[IDX_ADXL355] = acc1.convertRawtog(acc1.convertlisttoRaw(datalist[IDX_ADXL355]))

alldata = []
for sensor in [IDX_LIS3DHH, IDX_ADXL355]:
    for i in range(len(datalist[sensor])):
        alldata.append([sensor, i * mperiod[sensor]] + datalist[IDX_LIS3DHH][i])

alldatanp = np.array(alldata)
np.savetxt(outfilename, alldatanp, delimiter=",")
