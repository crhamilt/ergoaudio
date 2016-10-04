#!c:\Anaconda\python.exe
#
# ergo_wavegen:  generate waveforms for ergometer exercise prompting
# CAHamilton
#
# Version   Date     Description
#   1.0     8/30/16  Initial coding


#  based on http://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array

# TODO:
#  * apodize the audio "pulses" or make integer multiple of period
#  * 
#  *

import argparse
import sys
import os
import csv
import scipy.io.wavfile
import matplotlib.rcsetup
# print(matplotlib.rcsetup.all_backends)

import matplotlib
matplotlib.use('TkAgg')  # identify by using matplotlib.get_backend()
import numpy as np
# import sounddevice as sd
import pylab as pl
import wave


# ~~~~~~~~~~~~~~   parse command line   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser()
parser.add_argument("timingfilename",type=str,help="timing file name. File is CSV with top row header: onset, duration, freq")
args=parser.parse_args()

timingfilename = args.timingfilename

# ~~~~~~~~~~~~~~   read in the timing CSV file  ~~~~~~~~~~~~~~~~~~~~~

rownum=0
# use lists, because they can grow in-place.  arrays can't
list0 = []
list1 = []
list2 = []

if os.path.exists(timingfilename):
    with open(timingfilename,'r') as tfile:
        try:
            reader = csv.reader(tfile)
            for row in reader:
                if rownum == 0:
                    header = row
                else:
                    list0.append(row[0])
                    list1.append(row[1])
                    list2.append(row[2])
                rownum += 1

            tfile.close()
        except IOError:
            print "Could not read file: ",timingfilename
            sys.exit()
else:
    print "File not found: ", timingfilename
    sys.exit()

# ~~~~~~~~~~~~~   create numpy arrays from lists ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
onset = np.array([float(i) for i in list0])
duration = np.array([float(i) for i in list1])
freq = np.array([float(i) for i in list2])

# ~~~~~~~~~~~~~  compute some values  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
totalduration = onset[-1]+duration[-1]   # duration of entire waveform in seconds
srate = 44100
# sd.default.samplerate = srate

# ~~~~~~~~~~~~~   create empty array to hold the entire waveform  ~~~~~~~~~~~~~
fulltime = np.arange(srate * totalduration )/(1.0*srate)
fullwave = np.zeros(int(np.ceil(srate*totalduration)))     # may leave a few zeros at the end

# ~~~~~~~~~~~~~   insert the beeps into the full array  ~~~~~~~~~~~~~~~~~~~~~~
pt=0
for tim in onset:
    # create the beep
    beeptime = np.arange(srate * duration[pt])/srate
    thebeep  = 10000 * np.sin(2 * np.pi * freq[pt] * beeptime)

    if (pt < 0):
        print("pt = %d thebeep.size = %d tim = %5.1f freq = %d" % (pt,thebeep.size,tim,int(freq[pt])))

    # insert it into the full waveform at the proper onset
    fullwave[(int(tim*srate)):((int(tim*srate))+int(thebeep.size))] = thebeep
    pt=pt+1

# ~~~~~~~~~~~~~~   convert to int16 array  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
wav_wave = np.array(fullwave, dtype=np.int16)


# ~~~~~~~~~~~~~~~~  save the file  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#wavfile = wave.open('test.wav','w')
# setup for 1 channel, 2 bytes per sample (int16)
#wavfile.setparams((1,2,int(srate),0,'NONE','not compressed'))
#packed_wav = struct.pack('h',wav_wave)
#wavfile.writeframes(packed_wav)
#wavfile.close() 

(wavname,ext) = os.path.splitext(timingfilename);
wavname += ".wav"

scipy.io.wavfile.write(wavname,44100,wav_wave)

print("wrote file to: %s\n" % (wavname))

# play the file
# sd.play(wav_wave)

# plot first 10 seconds in the waveform, subsampled at x100
# fig=pl.figure()
# pl.plot(fulltime[1:srate*10:100],fullwave[1:srate*10:100])
# pl.show()

