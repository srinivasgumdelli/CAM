import collections
import os
import random

seed = "1092384956781341341234656953214543219"
#words = open("lorem.txt", "r").read().replace("\n", '').split()
#
#def fdata():
#    a = collections.deque(words)
#    b = collections.deque(seed)
#    while True:
#        yield ' '.join(list(a)[0:1024])
#        a.rotate(int(b[0]))
#        b.rotate(1)
#
#g = fdata()
size = 262144
for i in range (1,51):
    fname = "test" + str(i)+ ".txt"
    fh = open(fname, 'w')
    while os.path.getsize(fname) < size:
        fh.write(str(random.randrange(0,100000)))
