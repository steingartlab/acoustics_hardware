from pithy import *
from libbigfig import BigFig as bf
from glob import glob

drop_pre = "/Users/j125mini/EASI/data/"

#print glob(drop_pre+"20160322-NCA18650-relaytest-1*")

b = bf(acoustic="20160322-NCA18650-relaytest-1")

b.genBigFig(skips=['pe'])