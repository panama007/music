import numpy as np
from math import *
from random import *
from scipy.io import wavfile

sample_rate = 44100

n = np.arange(sample_rate*5)
data = np.array([])

file = open('music.txt', 'w')


def apply_harmonics(harmonics, freq, dur):
    n = np.arange(sample_rate*dur)
    d = np.sin(freq*2*pi*n/sample_rate)
    for f in range(len(harmonics)): 
        d += harmonics[f]*np.sin(freq*(f+2)*2*pi*n/sample_rate+2*pi*random())
    return d
    
for i in range(10):
    r = randint(200,500)
    #print i,r
    harmonics = [0]*r
    for j in range(r):
        harmonics[j] = 1./(j+2)#random() * 2./(j+2)
    freq = 400#randint(200, 600)
    #print harmonics
    new_data = apply_harmonics(harmonics, freq, 1)  
    #print new_data
        
    data = np.append(data, new_data)
    
    file.write('Freq: %i\tHarmonics: ' % freq + str(harmonics) +'\n')
    

data /= max(data)
data = (data * 2**14).astype(np.int16)
file2 = wavfile.write('test.wav', sample_rate, data)

file.close()


