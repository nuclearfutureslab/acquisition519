# Copyright (c) 2018 Moritz Kuett
#
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import time

# register addresses
REG_WHO_AM_I   = 0x0F
REG_CTRL_01    = 0x20
REG_INT1_CTRL  = 0x21
REG_INT2_CTRL  = 0x22
REG_CTRL_04    = 0x23
REG_CTRL_05    = 0x24
REG_TEMP_L     = 0x25
REG_TEMP_H     = 0x26
REG_STATUS     = 0x27
REG_X_L        = 0x28
REG_X_H        = 0x29
REG_Y_L        = 0x2A
REG_Y_H        = 0x2B
REG_Z_L        = 0x2C
REG_Z_H        = 0x2D
REG_FIFO_CTRL  = 0x2E
REG_FIFO_SRC   = 0x2F

# settings
SET_DSP_FIR    = 0
SET_DSP_IIR    = 1
SET_BW_440     = 0
SET_BW_235     = 1

SET_FIFO_BYPASS     = 0b000
SET_FIFO_STOPFULL   = 0b001
SET_FIFO_CONT_TRIG  = 0b011
SET_FIFO_BY_TRIG    = 0b100
SET_FIFO_CONTINUOUS = 0b110

# factor for adjusting bit to g value
# +/- 2.5g on 16 bit
FACTOR_2G     = 2 * 2.5 / (2 ** 16)

class LIS3DHH():
    def __init__(self, transfer_function, factor = FACTOR_2G):
        self.transfer = transfer_function
        self.factor = factor
        self.fifo = False
        
        # turn device on
        self.write(REG_CTRL_01, 0xC0)

        # read to check
        t = self.read(REG_CTRL_01)
        if t != 0xC0:
            print("LIS3DHH: There seems to be a problem with initialization")

    def read(self, register):
        result = self.transfer([register | 0b10000000, 0x00])
        return result[1]

    def write(self, register, value):
        result = self.transfer([register & 0b00111111, value])

    def fifovalues(self):
        return self.read(REG_FIFO_SRC) & 0b00111111

    def fifofull(self):
        return self.read(REG_FIFO_SRC) & 0b01000000

    def dumpinfo(self):
        print("LIS3DHH SPI Info Dump")
        print("========================================")
        wai = self.read(REG_WHO_AM_I)
        print("Who am I register (should be 17): {:d}".format(wai))
        
    def whoami(self):
        t = self.read(REG_WHO_AM_I)
        return t

    def setdsp(self, dsp):
        current = self.read(REG_CTRL_04)
        if dsp == SET_DSP_FIR:
            current = current & 0b01111111
        if dsp == SET_DSP_IIR:
            current = current | 0b10000000

    def setbw(self, bw):
        current = self.read(REG_CTRL_04)
        if bw == SET_BW_440:
            current = current & 0b10111111
        if dsp == SET_BW_235:
            current = current | 0b01000000

    def setfifo(self, mode = None, threshold = None):
        tmp = self.read(REG_FIFO_CTRL)
        if not mode is None:
            if mode == 0b000:
                self.fifo = False
                tmp2 = self.read(REG_CTRL_04)
                self.write(REG_CTRL_04, tmp2 & 0b11111101)
            else:
                self.fifo = True
                tmp2 = self.read(REG_CTRL_04)
                self.write(REG_CTRL_04, tmp2 | 0b00000010)
            tmp = tmp & 0b00011111
            tmp = tmp | (mode << 5)
            self.write(REG_FIFO_CTRL, tmp)
        if not threshold is None:
            tmp = tmp & 0b11100000
            tmp = tmp | threshold
            self.write(REG_FIFO_CTRL, tmp)
            
    def temperature(self):
        low = self.read(REG_TEMP_L)
        high = self.read(REG_TEMP_H)
        res = (low >> 4) | (high << 4)
        return res

    def getXList(self):
        return([self.read(REG_X_L), self.read(REG_X_H)])

    def getXRaw(self):
        t = self.getXList()
        low = t[0]
        high = t[1]
        res = low | (high << 8)
        res = self.twocomp(res)
        return res

    def getX(self):
        return float(self.getXRaw()) * self.factor

    def getYList(self):
        return([self.read(REG_Y_L), self.read(REG_Y_H)])

    def getYRaw(self):
        t = self.getYList()
        low = t[0]
        high = t[1]
        res = low | (high << 8)
        res = self.twocomp(res)
        return res

    def getY(self):
        return float(self.getYRaw()) * self.factor
    
    def getZList(self):
        return([self.read(REG_Z_L), self.read(REG_Z_H)])

    def getZRaw(self):
        t = self.getZList()
        low = t[0]
        high = t[1]
        res = low | (high << 8)
        res = self.twocomp(res)
        return res

    def getZ(self):
        return float(self.getZRaw()) * self.factor

    def get3VList(self):
        return [self.getXList(), self.getYList(), self.getZList()]

    def get3VRaw(self):
        return [self.getXRaw(), self.getYRaw(), self.getZRaw()]

    def get3V(self):
        return [self.getX(), self.getY(), self.getZ()]

    def get3Vfifo(self):
        res = []
        while(self.read(REG_FIFO_SRC & 0b111111)):
            res.append(self.get3VList())
        return res

    def emptyfifo(self):
        res = []
        while(self.read(REG_FIFO_SRC & 0b111111)):
            no = self.get3VList()
    
    def hasnewdata(self):
        res = self.read(REG_STATUS)
        if res & 0b1000:
            return True
        return False

    def fastgetsamples(self, sampleno = 1000):
        """Get specified numbers of samples from FIFO, without any processing (when FIFO active)

        This function is needed for fast sampling, without loosing samples. While FIFO should be enough for many situations, there is no check for FIFO overflow implemented (yet).
        """
        if(self.fifo):
            res = []
            while(len(res) < sampleno):
                res += self.get3Vfifo()
            return res[0:sampleno]
        else:
            data = [0] * sampleno
            for i in range(sampleno):
                while(not self.hasnewdata()):
                    continue
                data[i] = self.get3VList()
            return data

    def getsamplesRaw(self, sampleno = 1000):
        """Get specified numbers of samples from FIFO, and process them into signed integers"""
        data = self.fastgetsamples(sampleno)
        return self.convertlisttoRaw(data)

    def getsamples(self, sampleno = 1000):
        """Get specified numbers of samples from FIFO, process and convert to g values"""
        data = self.getsamplesRaw(sampleno)
        return self.convertRawtog(data)

    def convertlisttoRaw(self, data):
        """Convert a list of 'list' style samples into signed integers"""
        res = [[0, 0, 0]] * len(data)
        for i in range(len(data)):
            for j in range(3):
                low = (data[i][j][0])
                high = (data[i][j][1])
                res[i][j] = self.twocomp(low | (high << 8))
        return res

    def convertRawtog(self, data):
        """Convert a list of raw style samples into g values"""
        res = [[d[0] * self.factor, d[1] * self.factor, d[2] * self.factor] for d in data]
        return res
    
    def twocomp(self, value):
        if (0x8000 & value):
            value = - (0x010000 - value)
        return value
    
    
