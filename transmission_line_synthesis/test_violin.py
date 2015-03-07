from __future__ import division

import math
import cmath

import sys

import fice

gnd = fice.Net('gnd')
v0 = fice.Net('v0')
v1 = fice.Net('v1')
v2 = fice.Net('v2')

l = .5/(440*2**(int(sys.argv[1])/12))

att = lambda f: .0001*abs(f)+.001+.1*max(0, abs(f)-2*math.pi*20000)

objs = [
    fice.Ground(gnd),
    
    #fice.TransmissionLine(100, att, 0.35*l, gnd, gnd, v1),
    fice.TransmissionLine(50, att, 0.2*l, gnd, gnd, v1),
    fice.CurrentSource(
        lambda f: 1/(1j*f)*cmath.exp(-1j*f*.25) if f else 0, gnd, v1),
    fice.TransmissionLine(50, att, 0.3*l, v1, gnd, v2),
    fice.TransmissionLine(100, att, 0.5*l, v2, gnd, gnd),
    fice.TransmissionLine(100, att, 0.75*l, v2, gnd, gnd),
    #fice.TransmissionLine(150, att, 1*l, v2, gnd, gnd),
    
    #fice.TransmissionLine(50, lambda f: 2, 0.1, v2, gnd, gnd),
]

RATE = 24000
LENGTH = 3

res = []
for i in xrange(int(RATE*LENGTH//2)):
    if i % 1000 == 0: print i / (RATE*LENGTH//2)
    r = fice.do_nodal(objs, w=i*2*math.pi/LENGTH)
    res.append(r[v2.voltage])
    #print '%i,%f,%f' % (i,res[v2.voltage].real, res[v2.voltage].imag)

res[0] = 0

import numpy
x = numpy.fft.irfft(res)
print numpy.mean(x)
x = x - numpy.mean(x)
x = x / numpy.max(numpy.abs(x))
print x

#x = numpy.array((list(x)+list(x)[::-1]*0)*30)

import scipy.io.wavfile
scipy.io.wavfile.write(sys.argv[2], RATE, (2**14*x).astype(numpy.int16))
