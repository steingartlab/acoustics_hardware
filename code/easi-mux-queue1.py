from pithy import *
from libacoustic import *

a = Acoustics(etherurl="http://localhost:9002/acoustic.csv", muxurl="http://localhost:9003", pulser="epoch", pulserurl="http://localhost:9008")

a.beginRun(loop=True)