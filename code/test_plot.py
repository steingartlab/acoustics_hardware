from pithy import *
import json 

path = '/Users/j125mini/EASI/data/'

pat = '''2016-CurrDistData-Exp1/20160331-Exp1-1500mAh-cellB4-p1-mid
2016-CurrDistData-Exp1/20160401-Exp1-1500mAh-cellB4-p1-mid'''

# btslist = '''2-2-443
# 2-3-440
# 2-4-440
# 2-5-440
# 2-6-440
# 2-7-440
# 2-9-446
# 2-10-441
# 2-11-441
# 2-12-441
# 2-16-440'''

# btslist = btslist.split('\n')
# btscsv = []

# for j in btslist:
#     tmp = j.split('-')
#     unit = int(tmp[0])
#     chl = int(tmp[1])
#     test = int(tmp[2])
#     btscsv.append("data_%i_%i_%i.csv" % (unit,chl,test))


pat = pat.split('\n')

for nm in pat:
    # tr = glob(path + "%s*TR*.json" % nm)
    # tr.sort()
    pe = glob(path + "%s*TR*.json" % nm)
    pe.sort()
    
    # print len(tr)
    print len(pe)
    
    # bigdextr = []
    bigdexpe = []
    
    # for i in tr:
    #     ts = i.split("_")[-1].replace(".json","")
    #     f = json.load(open(i))
    #     bigdextr.append(abs(array(f['amp'])-32639))
    for i in pe:
        ts = i.split("_")[-1].replace(".json","")
        f = json.load(open(i))
        bigdexpe.append(abs(array(f['amp'])-127))
    
    # subplot(211)
    # bigdextr = array(bigdextr).transpose()
    # pod = imshow(bigdextr,aspect="auto")
    # ylabel('TR')
    # title(nm)
    
    subplot(212)
    bigdexpe = array(bigdexpe).transpose()
    imshow(bigdexpe,aspect="auto")
    ylabel('PE')
    xlabel('index')
    
    showme()
    clf()