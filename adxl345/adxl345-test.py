# ADXL345 
#
# read commands from stdout and dump raw data from accelerometer


import sys
import datetime
import time

#from adxl345 import ADXL345
import json
import random
from StringIO import StringIO
  
def getAccelDataDummy(gforce = False, durationInSecs = 10, rateInHz = 1, outFile = "test.csv"):
        f = open(outFile, 'w')
        #strData="%f,%f,%f,%f,%d\n" % (10,20,durationInSecs,rateInHz,1000)
        #f.write(strData)
        numberOfSamples = durationInSecs * rateInHz
        startTime = time.time();
        sampleNumber = 0
        while (sampleNumber < numberOfSamples):
          strData="%f,%f,%f\n" % (random.random(), random.random(), random.random())
          f.write(strData)
          sampleNumber += 1
        f.close()
        return {"startTime": startTime, "endTime": (startTime + durationInSecs), "durationInSecs":durationInSecs, "rateInHz": rateInHz, "numberOfSamples": numberOfSamples}

if __name__ == "__main__":
    if len (sys.argv) < 3 :
      print "Usage: python adxl345-gvalues.py <number of seconds> <sample rate in Hz> <output file>"
      sys.exit (1)

    # if run directly we'll just create an instance of the class and output 
    # the current readings
    #adxl345 = ADXL345()

    data = getAccelDataDummy(True, int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    strData="%f,%f,%f,%f,%d\n" % (data['startTime'],data['endTime'],data['durationInSecs'],data['rateInHz'],data['numberOfSamples'])
    print strData

    #print "adxl345 fake test done"
