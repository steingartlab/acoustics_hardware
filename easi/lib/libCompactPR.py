##Author: 
##Date Started: 
##Notes: 

from urllib.request import urlopen as uo
from time import sleep
import pickle
import bisect

class CP():
    def __init__(self,site):
        self.site = site

    def write(self,s):
        out = uo(self.site+"/writecf/%s"%s).read()
        sleep(.05)
        return out

    def read(self):
        return uo(self.site+"/read/").read().split("\r")[-2]

    def getLast(self,ts=300):
        global last
        ticks = 0
        while ticks < ts: 
            ticks +=1
            sleep(.05)
        last = self.aread(split="OK")
        return last

    def convertFreq(self, freq):
        """Takes a frequency(in MHz) and converts it to a CP setting"""
        pw = int(1/(float(freq)*1e-3))
        lut = pickle.load(open('CP_LUT','rb'))
        # print(pw)
        if pw <= 484:
            wide = "X0"
            val = self.returnNearest(list(sorted(lut.values())),pw)
            CPval = "W%i" % val
        else:
            wide = "X1"
            keys = (list(lut.keys())) #keys are ordered in incremental fashion
            val = self.returnNearest(keys,pw)
            CPval = "W%i" % lut[val]
        return [CPval,wide]

    def convertFilt(self,filtmode):
        """Takes a filtermode with the 1st digit as the hp filter and the 2nd digit as the lp filter"""
        hpf = "H0"
        lpf = "L0"
        settings = list(filtmode)
        if len(settings) == 2:
            hpf = "H%i" % int(settings[0])
            lpf = "L%i" % int(settings[1])
        return [hpf,lpf]

    def returnNearest(self,l,pw):
        """Takes an int and a list of ints, and finds the closest list value to the int"""
        ind = (bisect.bisect_left(l, pw))
        if pw >= 2285:
            val = 2285
            print ("Frequency is lower than lowest possible. setting frequency to .437 MHz")
        else:
            val = (min([l[ind],l[ind-1]], key=lambda k: abs(k-pw)))       
        return val


    def commander(self,row):
        """Takes a row of settings and sets params on CompactPulser"""

        #anne's note to self: add some defaults
        [pwidth,widemode] = self.convertFreq(row["freq(mhz)"])
        [hpf, lpf] = self.convertFilt(row["filtermode"])
        settings = {"tr" : "M1", "pe" : "M0"}

        self.write(settings[row['mode(tr/pe)']])
        self.write(hpf)
        self.write(lpf)
        self.write("G%i" % int(row["gain(db)"]*10)) #gain is measured in 10th of dB 34.9 dB =349
        self.write(widemode)
        self.write(pwidth) #wide pulse mode will need a LUT

        ##for now we don't care about Voltage or PRF
        # self.write("V%i" % int(row['voltage'])) 
        # self.write("P%i" % int(row['prf'])) #pulse repitition freq

        data = self.pitaya(row["delay(us)"],row["time(us)"])
        return data

    def pitaya(delay,time):
        pass

if __name__ == "__main__":

    test = CP("yolo")
    print(test.convertFilt("12"))

    # #Write a few settings
    # #Damping
    # print "Adjusting some settings"
    # c.write("D5")
    # #Voltage
    # c.write("V100")
    # #Transducer mode - 1 = TR, 2 = PE
    # c.write("M0")
    # #Gain GXYZ = XY.Z dB
    # c.write("G080")
    # c.write("H0")
    # c.write("L7")
    # c.write("P10")
    # c.write("Q500")
    # c.write("W200")



    # #Show All Settings
    # print "Showing settings:"
    # for i in l: 
    #     c.write("%s?"%i)
    #     print c.read()