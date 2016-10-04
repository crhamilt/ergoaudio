#!c:\Anaconda\python.exe
#
# gen_timing:
#    generate timing CSV file for waveforms for ergometer exercise prompting
#
# CAHamilton
#
# Version   Date     Description
#   1.0     9/12/16  Initial coding
#   


import argparse
import sys
import os
import csv
import numpy as np

def torange(x):
    # this function converts a string representing an index range, to a set of indices
    #       for example,  "2-5,9-12" as a string becomes indices [2,3,4,9,10,11] 
    result = []

    try:
        for part in x.split(','):
            if '-' in part:
                a, b = part.split('-')
                a, b = int(a), int(b)
                result.extend(range(a, b + 1))
            else:
                a = int(part)
                result.append(a)
                return result

    except Error:
        print "error parsing silence range"
        sys.exit()

def gen_timing(args):
    
    # ~~~~~~~~~~~~~~   parse command line   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    parser = argparse.ArgumentParser(description=
       "gen_timing: generate CSV file of audio timing for input to ergo_wavegen.py")
    parser.add_argument("duration",type=str,
                        help="duration of exercise in minutes")
    parser.add_argument("rpm",type=str,
                        help="period of exercise repetition in reps-per-minute")
    parser.add_argument("alert",type=str,
                        help="alert time for weight change in seconds")
    parser.add_argument("-s","--silencerange",type=str,
                        help="range(s) of silence in seconds (ex: 10-20,40-50)")
    args=parser.parse_args()
    
    if args.silencerange:
        silenceRangeStr = args.silencerange    # of the form:   1-12, 8-30, 50-54
        silenceRange = np.r_[torange(silenceRangeStr)]  
    else:
        silenceRangeStr = "[]"
        
    
    durationMins = float(args.duration)
    rpm  = float(args.rpm)
    alertSecs = float(args.alert)

    print("Creating timing file of duration: %3.0f minutes, reps/min: %2d, alert every %3d seconds,\
            silence range: %s seconds" % (durationMins, rpm, alertSecs, silenceRangeStr))
    
    # ~~~~~~~~~~~~~~  setup some variables  ~~~~~~~~~~~~~~~~~~~~~
    
    periodS = 60.0/rpm
    durationS = durationMins*60.0
    hibeep = 1000.0
    lobeep = 2000.0
    alertbeep = 2000.0
    silencearray = np.ones(durationS)
    if silenceRangeStr != "[]":
        silencearray[silenceRange]=0

    # print("silencearray[0:11] = ",silencearray[0:11])
    
    
    outfilename = "ergo_%02dmin_%2drpm_%2dA_%sS.csv" % (durationMins,rpm,alertSecs,silenceRangeStr)
    
    with open(outfilename,'w') as tfile:
        try:
            print >> tfile,"onset(sec), duration(sec), freq(hz)"
    
            timeptS = 0.0
            cnt = 0
            
            while (timeptS < durationS):

                # print("  At timeptS %4.1f\n" % (timeptS))
                
                if silencearray[cnt] != 0:
                    if (timeptS % alertSecs < 0.1):
                        print >> tfile,timeptS,", 0.2,",alertbeep
                        timeptS += periodS
                    else:
                        print >> tfile,timeptS,", 0.2,",hibeep
                    
                        timeptS += periodS/2.0
                        print >> tfile,timeptS,", 0.2,",lobeep
                        timeptS += periodS/2.0
                else:
                    timeptS += periodS   # no sound for one full period

                if cnt<119:
                    cnt += 1   # this counts half periods
                
            else:
                print("wrote file to: %s\n" % (outfilename) )
    
            tfile.close()
    
        except IOError:
            print "Could not open file: ",outfilename
            sys.exit()

if __name__ == "__main__":
    sys.exit(gen_timing(sys.argv[1:]))
