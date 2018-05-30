# ADXL345 
#
# read commands from stdout and dump raw data from accelerometer


import sys
import datetime
import time

import json
import random
from StringIO import StringIO
  
def getFFTDataDummy(gforce = False, durationInSecs = 10, rateInHz = 1, outFile = "test-fft.csv"):
        f = open(outFile, 'w')
        inp = open('adxl345/fft.out', 'r')
        strData=inp.read()
        #strData="%f,%f,%f,%f,%d\n" % (10,20,durationInSecs,rateInHz,1000)
        #f.write(strData)
        numberOfSamples = durationInSecs * rateInHz
        startTime = time.time();
        sampleNumber = 0
        f.write(strData)
        f.close()
        return {"startTime": startTime, "endTime": (startTime + durationInSecs), "durationInSecs":durationInSecs, "rateInHz": rateInHz, "numberOfSamples": numberOfSamples}

if __name__ == "__main__":
    if len (sys.argv) < 3 :
      print "Usage: python adxl345-fft-test.py <number of seconds> <sample rate in Hz> <output file>"
      sys.exit (1)

    # if run directly we'll just create an instance of the class and output 
    # the current readings
    #adxl345 = ADXL345()

    data = getFFTDataDummy(True, int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    strData="%f,%f,%f,%f,%d\n" % (data['startTime'],data['endTime'],data['durationInSecs'],data['rateInHz'],data['numberOfSamples'])
    print strData

    #print "adxl345 fake test done"
