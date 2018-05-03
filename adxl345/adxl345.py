# ADXL345 Python library for Raspberry Pi 
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
# 
# This is a Raspberry Pi Python implementation to help you get started with
# the Adafruit Triple Axis ADXL345 breakout board:
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer

import smbus
import time
from time import sleep
from array import *
import datetime
import numpy as np
from numpy import mean, sqrt, square
from scipy.fftpack import fft

# select the correct i2c bus for this revision of Raspberry Pi
revision = ([l[12:-1] for l in open('/proc/cpuinfo','r').readlines() if l[:8]=="Revision"]+['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

# ADXL345 constants
EARTH_GRAVITY_MS2   = 9.80665
SCALE_MULTIPLIER    = 0.004

DATA_FORMAT         = 0x31
BW_RATE             = 0x2C
POWER_CTL           = 0x2D

BW_RATE_1600HZ      = 0x0F
BW_RATE_800HZ       = 0x0E
BW_RATE_400HZ       = 0x0D
BW_RATE_200HZ       = 0x0C
BW_RATE_100HZ       = 0x0B
BW_RATE_50HZ        = 0x0A
BW_RATE_25HZ        = 0x09

RANGE_2G            = 0x00
RANGE_4G            = 0x01
RANGE_8G            = 0x02
RANGE_16G           = 0x03

MEASURE             = 0x08
AXES_DATA           = 0x32

class ADXL345:

    address = None

    def __init__(self, address = 0x53):        
        self.address = address
        self.setBandwidthRate(BW_RATE_100HZ)
        self.setRange(RANGE_2G)
        self.enableMeasurement()

    def enableMeasurement(self):
        bus.write_byte_data(self.address, POWER_CTL, MEASURE)

    def setBandwidthRate(self, rate_flag):
        bus.write_byte_data(self.address, BW_RATE, rate_flag)

    def setBandwidthRateInHz(self, rateInHz):
        rateUsed = 1600
        if(rateInHz >= 1600):
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_1600HZ)
            rateUsed = 1600
        elif(rateInHz >= 800):
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_800HZ)
            rateUsed = 800
        elif(rateInHz >= 400):
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_400HZ)
            rateUsed = 400
        elif(rateInHz >= 200):
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_200HZ)
            rateUsed = 200
        elif(rateInHz >= 100):
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_100HZ)
            rateUsed = 100
        elif(rateInHz >= 50):
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_50HZ)
            rateUsed = 50
        else:
            bus.write_byte_data(self.address, BW_RATE, BW_RATE_25HZ)
            rateUsed = 25
        return rateUsed

    # set the measurement range for 10-bit readings
    def setRange(self, range_flag):
        value = bus.read_byte_data(self.address, DATA_FORMAT)

        value &= ~0x0F;
        value |= range_flag;  
        value |= 0x08;
        value |= 0x80;  #enable self test

        bus.write_byte_data(self.address, DATA_FORMAT, value)
    
    # returns the current reading from the sensor for each axis
    #
    # parameter gforce:
    #    False (default): result is returned in m/s^2
    #    True           : result is returned in gs
    def getAxes(self, gforce = False):
        bytes = bus.read_i2c_block_data(self.address, AXES_DATA, 6)
        return self.convertBytes(bytes, gforce)

    def convertBytes(self, bytes,  gforce = False):        
        x = bytes[0] | (bytes[1] << 8)
        if(x & (1 << 16 - 1)):
            x = x - (1<<16)

        y = bytes[2] | (bytes[3] << 8)
        if(y & (1 << 16 - 1)):
            y = y - (1<<16)

        z = bytes[4] | (bytes[5] << 8)
        if(z & (1 << 16 - 1)):
            z = z - (1<<16)

        x = x * SCALE_MULTIPLIER 
        y = y * SCALE_MULTIPLIER
        z = z * SCALE_MULTIPLIER

        if gforce == False:
            x = x * EARTH_GRAVITY_MS2
            y = y * EARTH_GRAVITY_MS2
            z = z * EARTH_GRAVITY_MS2

        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)

        return {"x": x, "y": y, "z": z}

    def getRawBytes(self, gforce = False):
        bytes = bus.read_i2c_block_data(self.address, AXES_DATA, 6)
        return bytes

    def getAccelData(self, gforce = False, durationInSecs = 10, rateInHz = 1, outFile = "test.csv"):
        numberOfSamples = durationInSecs * rateInHz
        sleepTime = 1.0 / rateInHz   #not very accurate, needs to be adjusted
        rateUsed = self.setBandwidthRateInHz(rateInHz)
        rawDataArray = array('B')
        sampleNumber = 0
        s1 = time.time()
        while (sampleNumber < numberOfSamples):
            rawDataArray.fromlist(bus.read_i2c_block_data(self.address, AXES_DATA, 6))
            sampleNumber += 1
            sleep(sleepTime)
        s2 = time.time()
        accelDataArray = []
        accelDataArrayNumeric = []
        sampleNumber = 0
        while (sampleNumber < numberOfSamples):
            sn6 = sampleNumber*6
            rdArr = array('B', [rawDataArray[sn6],rawDataArray[sn6+1],rawDataArray[sn6+2],rawDataArray[sn6+3],rawDataArray[sn6+4],rawDataArray[sn6+5]]) 
            data = self.convertBytes(rdArr.tolist(), gforce)
            strData="%f,%f,%f\n" % (data['x'], data['y'], data['z'])
            accelDataArray.append(strData)
            accelDataArrayNumeric.append([data['x'], data['y'], data['z']])
            sampleNumber += 1

        f = open(outFile, 'w')
        #strData="%f,%f,%f,%f,%d\n" % (s1,s2,durationInSecs,rateInHz,numberOfSamples)
        #f.write(strData)
        for ad in accelDataArray:
            f.write(ad)
        f.close() 
        rms = sqrt(mean(square(accelDataArrayNumeric)))

        return {"startTime": s1, "endTime": s2, "durationInSecs":durationInSecs, "rateInHz": rateInHz, "numberOfSamples": numberOfSamples, "rms": rms}

    def getFFT(self, gforce = False, durationInSecs = 10, rateInHz = 1, outFile = "test.csv"):
        numberOfSamples = durationInSecs * rateInHz
        sleepTime = 1.0 / rateInHz   #not very accurate, needs to be adjusted
        rateUsed = self.setBandwidthRateInHz(rateInHz)
        rawDataArray = array('B')
        sampleNumber = 0
        s1 = time.time()
        while (sampleNumber < numberOfSamples):
            rawDataArray.fromlist(bus.read_i2c_block_data(self.address, AXES_DATA, 6))
            sampleNumber += 1
            sleep(sleepTime)
        s2 = time.time()
        accelDataXArray = []
        accelDataYArray = []
        accelDataZArray = []
        sampleNumber = 0
        actualSampleSpacing = (s2 - s1)/numberOfSamples
        xf = np.linspace(0.0, 1.0/(2.0*actualSampleSpacing), numberOfSamples/2)
        
        while (sampleNumber < numberOfSamples):
            sn6 = sampleNumber*6
            rdArr = array('B', [rawDataArray[sn6],rawDataArray[sn6+1],rawDataArray[sn6+2],rawDataArray[sn6+3],rawDataArray[sn6+4],rawDataArray[sn6+5]]) 
            data = self.convertBytes(rdArr.tolist(), gforce)
            #strData="%f,%f,%f\n" % (data['x'], data['y'], data['z'])
            accelDataXArray.append(data['x'])
            accelDataYArray.append(data['y'])
            accelDataZArray.append(data['z'])
            sampleNumber += 1

        

        xFFTArray = 2.0/numberOfSamples * np.abs(fft(accelDataXArray)[0:numberOfSamples/2])
        yFFTArray = 2.0/numberOfSamples * np.abs(fft(accelDataYArray)[0:numberOfSamples/2])
        zFFTArray = 2.0/numberOfSamples * np.abs(fft(accelDataZArray)[0:numberOfSamples/2])
        f = open(outFile, 'w')
        #strData="%f,%f,%f,%f,%d\n" % (s1,s2,durationInSecs,rateInHz,numberOfSamples)
        #f.write(strData)
        fftIdx = 0
        while fftIdx < xf.size:
          strData="%f,%f,%f,%f\n" % (xf[fftIdx], xFFTArray[fftIdx], yFFTArray[fftIdx], zFFTArray[fftIdx])
          f.write(strData)
          fftIdx += 1
        f.close() 
        return {"startTime": s1, "endTime": s2, "durationInSecs":durationInSecs, "rateInHz": rateInHz, "numberOfSamples": numberOfSamples}

    def getAccelDataDummy(self, gforce = False, durationInSecs = 10, rateInHz = 1, outFile = "test.csv"):
          f = open(outFile, 'w')
          strData="%f,%f,%f,%f,%d\n" % (10,20,durationInSecs,rateInHz,1000)
          f.write(strData)
          f.write("dummy test done")
          f.close()
          return {"startTime": 10, "endTime": 20, "durationInSecs":durationInSecs, "rateInHz": rateInHz, "numberOfSamples": numberOfSamples}

if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output 
    # the current readings
    adxl345 = ADXL345()
    
    axes = adxl345.getAxes(True)
    print "ADXL345 on address 0x%x:" % (adxl345.address)
    print "   x = %.3fG" % ( axes['x'] )
    print "   y = %.3fG" % ( axes['y'] )
    print "   z = %.3fG" % ( axes['z'] )
