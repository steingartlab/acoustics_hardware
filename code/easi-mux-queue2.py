from pithy import *
from libacoustic import *

a = Acoustics(etherurl="http://localhost:9002/acoustic.csv", muxurl="http://localhost:9005", pulser="siui", pulserurl="http://localhost:9001")

a.beginRun()