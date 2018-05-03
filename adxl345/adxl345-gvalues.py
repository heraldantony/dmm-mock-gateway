# ADXL345 
#
# read commands from stdout and dump raw data from accelerometer


import sys
import datetime

from adxl345 import ADXL345
import json
from StringIO import StringIO
  

if __name__ == "__main__":
    if len (sys.argv) < 3 :
      print "Usage: python adxl345-gvalues.py <number of seconds> <sample rate in Hz> <output file>"
      sys.exit (1)

    # if run directly we'll just create an instance of the class and output 
    # the current readings
    adxl345 = ADXL345()
    
    data = adxl345.getAccelData(True, int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    strData="%f,%f,%f,%f,%d\n" % (data['startTime'],data['endTime'],data['durationInSecs'],data['rateInHz'],data['numberOfSamples'])
    print strData
