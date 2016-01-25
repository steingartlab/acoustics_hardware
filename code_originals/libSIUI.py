from numpy import *
import time
from urllib import urlopen as uo
from struct import pack
import requests
import json

class SIUI():
    def __init__(self,site):
        self.site = site
        self.dec = {}
        self.dec['range'] = {'start': 28,'bytes': 4,'type':float32}
        self.dec['gain']  = {'start': 48,'bytes': 4,'type':int32}
        self.dec['prf']   = {'start':184,'bytes': 2,'type':int16} #SIUI was wrong here
        self.dec['delay'] = {'start': 44,'bytes': 4,'type':float32}
        self.dec['vel']   = {'start':168,'bytes': 4,'type':float32}
        self.dec['vel2']  = {'start': 56,'bytes': 2,'type':uint16 }
        self.dec['wave']  = {'start':400,'bytes':800,'type':uint16}
        self.base = self.getBaseline() #necessary every time?
        self.gbase = self.getGainBaseline()
        self.rects = ['pos','neg','full','filter','rf']
        self.volts = range(50,550,50)
        self.freqs = ['1_4MHz','0.5_10MHz','2_20MHz','1MHz','2.5MHz','4MHz','5MHz','10MHz','13MHz','15MHz','20MHz']
        
        self.params = {}
        self.resetDefaultParams()
        
    def resetDefaultParams(self): 
        params = {}
        params['vset'] = 400        #pulse voltage
        params['range'] = 30
        params['mode'] = 'TR'       #echo vs transmission
        params['vel'] = 2450        #stupid scaling factor
        params['pw'] = 440          #1/(frequency)
        params['prf'] = 100        #repitition frequency (Hz)
        params['damp'] = 0
        params['rect'] = 'rf'       #rectifier
        params['power'] = 0         # this breaks stuff if not 0
        params['freq'] = '1MHz'   #Bandwidth/filtering
        params['gain'] = 30       #gain
        self.params = params
        return params
    
    def getBaseline(self):
        a = uo(self.site+"/getBaseline").read()
        base =  json.loads(a)
        return [item for sublist in base for item in sublist] 

    def getGainBaseline(self):
        a = uo(self.site+"/getGainBaseline").read()
        base =  json.loads(a)
        return [item for sublist in base for item in sublist] 

    
    def rawData(self):
        site = self.site
        data = uo(site+"/data/").read()
        ata = []
        for d in data.split(","):
            try:
                ata.append(int(d))
            except Exception as err:
                off = "on"

        return array(ata).T
    
    
    def setGain(self):
        a = self.gbase
        gains = []
        for i in pack('i',int(self.params['gain'])*10): gains.append(ord(i))
        a[48:52] = gains
        cc = 0
        aout = []
        while cc < len(a):
            aout.append(a[cc:cc+1460])
            cc+=1460
        return self.sendMass({'data':aout})   


    def setParams(self):
        a = self.base
        #unpack sets and set things like TR,Voltage, etc
        rsets = a[80:84]
        foo = []
        for j in rsets:
            for i in range(8): 
                foo.append((j >> i) & 1)
                
        #set driving potential    
        sets = range(50,550,50)
        try: food = sets.index(self.params['vset'])
        except: food = 0
        d = bin(food).replace("0b","").rjust(4,"0")
        volts = []
        for b in d: volts.append(int(b))
        volts.reverse()
        foo[25:29] = volts
        
        #set pulse width    
        food = self.params['pw']/10
        d = bin(food).replace("0b","").rjust(7,"0")
        pws = []
        for b in d: pws.append(int(b))
        pws.reverse()
        foo[18:25] = pws

        #set rect    
        food = self.rects.index(self.params['rect'])
        d = bin(food).replace("0b","").rjust(4,"0")
        pws = []
        for b in d: pws.append(int(b))
        pws.reverse()
        foo[8:12] = pws

        #set Bandwidth
        food = self.freqs.index(self.params['freq'])
        d = bin(food).replace("0b","").rjust(4,"0")
        pws = []
        for b in d: pws.append(int(b))
        pws.reverse()
        foo[4:8] = pws

        #set power
        food = self.params['power']
        d = bin(food).replace("0b","").rjust(4,"0")
        pws = []
        for b in d: pws.append(int(b))
        pws.reverse()
        foo[0:4] = pws


        #set PE/TR Mode
        if self.params['mode'] == 'TR': foo[16] = 1
        else: foo[16] = 0

        #set damping
        foo[17] = self.params['damp']

        #repack bits to bytes for settings
        count = 0
        sets = []
        while count < len(foo):
            temp = ""
            for f in foo[count:count+8]: temp+=str(f)
            count += 8
            temp = temp[::-1]
            sets.append(int(temp,2))
        a[80:84] = sets
    
        #set range
        rngs = []
        for i in pack('f',self.params['range']): rngs.append(ord(i))
        a[28:32] = rngs

        #vel
        vels = []
        for i in pack('f',self.params['vel']): vels.append(ord(i))
        #print self.params['vel']
        #print vels
        a[168:168+4] = vels
        

        vels = []
        for i in pack('h',self.params['vel']): vels.append(ord(i))
        #print self.params['vel']
        #print vels
        a[56:56+2] = vels


        #prf
        prfs = []
        for i in pack('h',self.params['prf']): prfs.append(ord(i))
        a[184:184+2] = prfs

        #send bundle off
        cc = 0
        aout = []
        while cc < len(a):
            aout.append(a[cc:cc+1460])
            cc+=1460
        return self.sendMass({'data':aout})    
    
    
    
    def processData(self,d):
        out = {}

        #do what we can automagically
        for k in self.dec.keys():
            out[k] = self.convert(k,d)
            if len(out[k]) == 1: out[k] = out[k][0]
        out['x'] = linspace(0,out['range'],len(out['wave']))
        
        #bit manip
        rsets = d[80:84]
        out['sets'] =[]
        for s in rsets:
            for i in range(8): 
                out['sets'].append((s >> i) & 1)
        
        out['gain'] = out['gain']/10.
        #get mode
        #print rsets
        if out['sets'][16] == 0: out['mode'] = 'PE'
        else: out['mode'] = 'TR'

        #get damping
        out['damp'] = out['sets'][17]

        #get power
        temp = out['sets'][0:4]
        b = ""
        for t in temp:  b+=str(t)
        b = b[::-1]
        out['power'] = int(b,2)

        #get driving potential
        sets = range(50,550,50)
        temp = out['sets'][25:29]
        b = ""
        for t in temp: b+=str(t)
        b = b[::-1]
        out['vset'] = sets[int(b,2)]
        
        #get rectification
        temp = out['sets'][8:12]
        b = ""
        for t in temp: b+=str(t)
        b = b[::-1]
        #print b
        out['rect'] = self.rects[int(b,2)]
        
        #get freqs
        temp = out['sets'][4:8]
        b = ""
        for t in temp: b+=str(t)
        b = b[::-1]
        out['freq'] = self.freqs[int(b,2)]

        #get pulse width
        temp = out['sets'][18:25]
        b = ""
        for t in temp: b+=str(t)
        b = b[::-1]
        out['pw'] = int(b,2)*10
        
        return out
    
    def sendCommand(self,c):
        return uo(site+"/sendCmd/%s" % c).read()


    def sendMass(self,s):
        payload = s
        r = requests.post(self.site+"/toSIUI", json=payload)
        return r.text
        
    #thanks stack http://stackoverflow.com/a/2577487/565514
    def getData(self):
        d = self.rawData()
        return self.processData(d)

    def convert(self,k,arr):
        temp = ""
        s = self.dec[k]['start']
        l = self.dec[k]['bytes']
        for i in arr[s:s+l]:
            temp += chr(int(i))
            #if k == "vel": print int(i),
        return fromstring(temp,dtype=self.dec[k]['type'])

    
    def setGetCheck(self,gain=True,params=True):
        #self.setGain()
        #time.sleep(.2)
        set1 = [1]
        set2 = [2]
        while set1 != set2:        
            if gain:
                self.setGain()
                time.sleep(.2)
            if params:
                self.setParams()
                time.sleep(.5)
            a = self.getData()
            ps = ['gain','range','mode','freq','vset','rect']
            if params and gain:
                set1 = [self.params[x] for x in ps[:]]
                set1[0] = int(set1[0])
                set2 = [a[x] for x in ps[:]]
                set2=[int(x) for x in set2[0:2]]+set2[2:]
            elif params:
                set1 = [self.params[x] for x in ps[1:]]
                set2 = [a[x] for x in ps[:]]
                set2=[int(x) for x in set2[1:2]]+set2[2:]
            elif gain:
                set1 = [self.params['gain']]
                set2 = [int(a['gain'])]
            else:
                set1 = []
                set2 = []
            #print "set 1: ",
            #print set1
            #print "set 2: ",
            #print set2
        return a

if __name__ == "__main__":# and False:
    from pithy import *
    site = 'http://localhost:9000'
    s = SIUI(site)
    
    #specify parameters
    s.params['vset'] = 200
    s.params['gain'] = 25
    s.params['range'] = 100
    s.params['pw'] = 444 
    s.params['rect'] = 'rf'
    s.params['freq'] = '1MHz'
    s.params['prf'] = 100
    s.params['mode'] = 'TR'
    s.params['vel'] = 4000
    start = time.time()
    for i in range(10):
        data = s.setGetCheck(gain=True,params=True)
        end = time.time()
        print end-start
        start = end
        

























    
 
    
