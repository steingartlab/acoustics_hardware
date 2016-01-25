###################################################
###################################################
##      import this library, not libepoch or     ##
##      whatever else                            ##
###################################################
###################################################

from pithy import *
from urllib import urlopen as uo
import json
import libSIUI as siui
import libEpoch
import libethercalc as ether

class Acoustics():
    def __init__(self,muxurl=None,etherurl=None,pulser=None,pulserurl=None):
        self.pre = "/home/lab/EASI/data/"
        
        self.muxurl = muxurl #check+add trailing /
        self.pulserurl = pulserurl
        #self.pulserurl = 'http://localhost:9002/EPOCHmux.csv' #cuz.
        #self.initurl = 'http://localhost:9002/EPOCHmux-init.csv'
        if etherurl is not None:
            self.ether = ether.Ether(etherurl)
        else:
            print "-----------------------------------------"
            print "WARNING: No ethercalc. Stuff might break."
            print "-----------------------------------------"
        if muxurl is None:
            print "------------------------------------------------"
            print "WARNING: No mux given. Ignoring channel numbers."
            print "------------------------------------------------"
            
        if pulser.lower()=="epoch":
            self.pulser="epoch"
            print "connecting to Epoch..."
            self.p = libepoch.epoch(pulserurl)
            print "... done!"
        elif pulser.lower()=="siui":
            self.pulser="siui"
            print "connecting to SIUI..."
            self.p = siui.SIUI(pulserurl)
            print "... done!"
        else:
            raise AttributeError("no valid pulser type given!")
        
    def switchMux(self,chan,chan2=None):
        try:
            if chan2 is None:
                u = self.muxurl+"/write/%i" % int(chan)
            else:
                u = self.muxurl+"/write/%i,%i" % (int(chan),int(chan2))
            uo(u).read()
        except: #don't think this is correct anymore
            print "problem with mux"

    def mark_time(self):
        print time.time() - self.start_time
    
    def getSingleData(self,row):
        self.start_time = time.time()
        
        q = row
        fn = self.pre+"%s_%s_%s_%i.json" % (q['Name'],q['Channel'],q['Mode (tr/pe)'].upper(),int(time.time()))
            
        if self.muxurl is not None:
            if q['Channel 2']!="":
                self.switchMux(q['Channel'],q['Channel 2'])
            else:
                self.switchMux(q['Channel'])
        if self.pulser=="epoch":
            try:
                data = self.p.commander(
                    isTR=q['Mode (tr/pe)'].lower(),
                    gain=float(q['Gain (dB)']),
                    tus_scale=int(q['Time (us)']),
                    freq=float(q['Freq (MHz)']),
                    delay=int(q['Delay (us)']))
                json.dump({'time (us)':data[0],'amp':list(data[1])}, open(fn,'w'))
            except:
                print '***ERROR***'
                import traceback
                print traceback.format_exc()
        elif self.pulser=="siui":
            vel = 4000 #m/s
            pw = 1/(float(q['Freq (MHz)'])*1E6)*1E9
            rng = (float(q['Time (us)'])/1E6)*vel*1000.0
            self.p.params['range'] = int(rng)
            self.p.params['vset'] = 400 #pulse voltage
            self.p.params['pw'] = int(floor(pw/10)*10)
            self.p.params['vel'] = int(vel)
            #s.params['rect'] = 'rf'#rectification
            #s.params['prf'] = 100  #repitition frequency
            self.p.params['gain'] = q['Gain (dB)']
            self.p.params['mode'] = q['Mode (tr/pe)'].upper()
            data = self.p.setGetCheck()
            rtime = [round(float(x),3) for x in list(data['x'])]
            out = {'time (us)':rtime,'amp':[int(x) for x in list(data['wave'])]}
            #print out
            json.dump(out, open(fn,'w'))
            
            print "execution time: ",
            self.mark_time()
            
            return data
    
    def beginRun(self):
        while True: 
            self.ether.refresh()
            for i in range(len(self.ether.rows)-1):
                r = self.ether.rows[i]
                if r['Run (y/n)'].lower() == 'y':
                    print "Executing row "+str(i+1)
                    self.getSingleData(r)
                else:
                    pass

if __name__=="__main__":
    a = Acoustics(pulser="siui",pulserurl="http://localhost:9000",muxurl="http://localhost:8001")
    
    d1 = a.getSingleData({'Name':"fakefakefake",'Channel':1,'Channel 2':7,'Gain (dB)':60,'Freq (MHz)':2.25,'Mode (tr/pe)':"TR",'Time (us)':20})
    d2 = a.getSingleData({'Name':"fakefakefake",'Channel':2,'Channel 2':8,'Gain (dB)':60,'Freq (MHz)':2.25,'Mode (tr/pe)':"TR",'Time (us)':20})
    plot(d1['wave'])
    plot(d2['wave'])
    showme()

"""
init = False
while True:
    if init:
        queue = parsecsv(initurl)
        init = False
    else:
        queue = parsecsv(csvurl)
    for q in queue:
        #print q
        if q['Mode tr/pe/both'].lower() in ['tr','both']:
            switchmux(mm[int(q['Channel'])])
            getSingleData(q,True)
        if q['Mode tr/pe/both'].lower() in ['pe','both']:
            switchmux(mm[int(q['Channel'])]-1)
            getSingleData(q,False)
"""




























