import sys

import numpy

import scipy.io.wavfile


r = None
res = []
for a in sys.argv[2:]:
    r1, x = scipy.io.wavfile.read(a)
    if r is None:
        r = r1
    if r1 != r:
        assert False
    res.append(x)

res2 = numpy.zeros(sum(len(x) for x in res))
for i, a in enumerate(res):
    res2[i*r//5:i*r//5+len(a)] += a
res2 = res2 / numpy.max(numpy.abs(res2))
scipy.io.wavfile.write(sys.argv[1], r, (2**14*res2).astype(numpy.int16))
