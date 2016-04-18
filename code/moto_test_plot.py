from pithy import *
import json 

path = '/Users/j125mini/EASI/data/'

pat = '''20160331-MotoATL-50cyc-CellF1'''

# pat = "poooooooop"

pat = pat.split('\n')

for pul in ['TR','PE']:
    for nm in pat:
        top = glob(path + "%s*top*%s*.json" % (nm,pul))
        top.sort()
        mid = glob(path + "%s*mid*%s*.json" % (nm,pul))
        mid.sort()
        bot = glob(path + "%s*bot*%s*.json" % (nm,pul))
        bot.sort()
        
        print len(top)
        print len(mid)
        print len(bot)
        
        bigdextop = []
        bigdexmid = []
        bigdexbot = []
        
        for i in top:
            ts = i.split("_")[-1].replace(".json","")
            f = json.load(open(i))
            bigdextop.append(abs(array(f['amp'])-127))
        for i in mid:
            ts = i.split("_")[-1].replace(".json","")
            f = json.load(open(i))
            bigdexmid.append(abs(array(f['amp'])-127))
        for i in bot:
            ts = i.split("_")[-1].replace(".json","")
            f = json.load(open(i))
            bigdexbot.append(abs(array(f['amp'])-127))
        
        subplot(311)
        bigdextop = array(bigdextop).transpose()
        plot(bigdextop)
        ylabel('Top Position')
        title(nm)
        
        subplot(312)
        bigdexmid = array(bigdexmid).transpose()
        plot(bigdexmid)
        ylabel('Middle Position')
        
        
        subplot(313)
        bigdexbot = array(bigdexbot).transpose()
        plot(bigdexbot)
        ylabel('Bottom Position')
        xlabel('index')
        
        showme()
        clf()