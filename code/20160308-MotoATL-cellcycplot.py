from pithy import *
import json 
from urllib import urlopen as uo
import time
import matplotlib.gridspec as gridspec

path = '/Users/j125mini/EASI/data/'

pat = '''20160308-MotoATL-cells/20160308-MotoATL-cellA1-p2
20160308-MotoATL-cells/20160308-MotoATL-cellA2-p2
20160308-MotoATL-cells/20160308-MotoATL-cellB1-p2
20160308-MotoATL-cells/20160308-MotoATL-cellB2-p2
20160308-MotoATL-cells/20160308-MotoATL-cellC1-p2
20160308-MotoATL-cells/20160308-MotoATL-cellC2-p2
20160308-MotoATL-cells/20160308-MotoATL-cellD2-p2
20160308-MotoATL-cells/20160308-MotoATL-cellE1-p2
20160308-MotoATL-cells/20160308-MotoATL-cellE2-p2
20160308-MotoATL-cells/20160308-MotoATL-cellF1-p2
20160308-MotoATL-cells/20160308-MotoATL-cellF2-p2'''

btslist = '''2-2-443
2-3-440
2-4-440
2-5-440
2-6-440
2-7-440
2-9-446
2-10-441
2-11-441
2-12-441
2-16-440'''

btslist = btslist.split('\n')
btscsv = []

for j in btslist:
    tmp = j.split('-')
    unit = int(tmp[0])
    chl = int(tmp[1])
    test = int(tmp[2])
    btscsv.append("data_%i_%i_%i.csv" % (unit,chl,test))

pat = pat.split('\n')

for nm in range(len(pat)):
    
    figure(figsize=(10,6))
    gs = gridspec.GridSpec(24, 1)
    ax_pe = plt.subplot(gs[0:12,0])
    ax_pot = plt.subplot(gs[12:15,0])
    ax_cur = plt.subplot(gs[15:18,0])
    ax_cap = plt.subplot(gs[18:21,0])
    
    pe = glob(path + "%s*PE*.json" % pat[nm])
    pe.sort()
    
    # print len(pe)
    
    bigdexpe = []
    tus = []
    
    for i in pe:
        tus.append(int(i.split("_")[-1].replace(".json","")))
        f = json.load(open(i))
        bigdexpe.append(abs(array(f['amp'])-32639))
    
    tofs = array(f['time (us)'])
    tickpt  = [0,50,100,150,200,250,300,350,399]
    ticktof = [0,2,4,6,8,10,12,14,16]
    
    bigdexpe = array(bigdexpe).transpose()
    boom = ax_pe.imshow(bigdexpe,aspect="auto")
    ax_pe.set_ylabel("Reflection ToF ($\mu$s)")
    ax_pe.set_xticks([])
    ax_pe.set_yticks(tickpt)
    ax_pe.set_yticklabels(ticktof)
    ax_pe.set_ylim([210,30])
    boom.set_clim([0,20000])
    ax_pe.set_title(pat[nm].split('-')[-2])
    
    tus = array(tus)
    tus = tus - min(tus)
    
    tim = []
    pot = []
    cur = []
    dcap = []
    ccap = []
    ttime = []
    b1 = path + btscsv[nm]
    splits = uo(b1).read().split("\n")
    header = splits.pop(0)
    cols = header.split(",")
    for k in splits:
        try:
            p = k.split(",")
            tim.append(float(p[26]))
            pot.append(float(p[11]))
            cur.append(float(p[12]))
            ttime.append(float(p[10]))
        except:
            pass
    b = {}
    b['time'] = tim
    b['potential'] = pot
    b['current'] = cur
    
    chs = []
    char_q = []
    dis_q = []
    char_t = []
    dis_t = []
    for p in range(1,len(b['time'])):
        bnow = b['current'][p] 
        bthen = b['current'][p-1]
        if abs(bnow-bthen) > .05:
            chs.append(b['time'][p])
            if bthen > .01:
                char_q.append(abs(bthen)*(chs[-1]-chs[-2]))
                char_t.append(b['time'][p-1])
            elif bthen < -.01:
                dis_q.append(abs(bthen)*(chs[-1]-chs[-2]))
                dis_t.append(b['time'][p-1])
    chs.append(max(b['time']))
    
    ax_pot.plot(array(tim),pot)
    ax_pot.set_ylabel('Volts')
    ax_pot.set_xticks([])
    ax_cur.plot(array(tim),cur)
    ax_cur.set_ylabel('Amps')
    ax_cur.set_xticks([])
    ax_cap.plot(dis_t,dis_q,linestyle = 'None',marker = '.')
    ax_cap.set_xlabel('Cycling Time (hr)')
    ax_pot.set_ylim(3,4.4)
    ax_pot.set_yticks([3,3.4,3.8,4.2])
    ax_cur.set_ylim(min(cur)*1.1,max(cur)*(1.1))
    ax_cur.set_xlim(min(tus),max(tus)/3600)
    ax_pot.set_xlim(min(tus),max(tus)/3600)
    ax_cap.set_xlim(min(tus),max(tus)/3600)
    ax_cap.set_ylabel('Disch.\nCap (Ah)')
    ax_cap.set_yticks([2,2.1,2.2,2.3])
    # ax_cap.set_ylim(min(dis_q)-.1,max(dis_q)+.1)
    
    showme(dpi=150)
    clf()
    plt.close("all")