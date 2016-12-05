#!/usr/bin/python3

import json
from pprint import pprint
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import string
import sys
from time import sleep

limit=10 # for testing
fixedaddrs=[]
u8o=open(1, 'w', encoding='utf-8', closefd=False)
fixed=open('data/fixed.json',mode="w",encoding='utf-8')

fvsterrfile='data/fvsterror.json';
fvsterr=open(fvsterrfile,mode="r")
alist=json.loads(open(fvsterrfile,'r', encoding='utf-8').read())

for adr in alist:
    print("\n\n\n")
    print(adr, file=u8o)
    alu="http://nominatim.openstreetmap.org/search?"+urlencode({"country":"Denmark","format":"json","street":adr['addr'],"postalcode":adr['postnr'],"email":"osm@agol.dk","addressdetails":0})
    print("alu= "+alu, file=u8o)
    oar=urlopen(Request(alu, headers={'User-Agent': 'Elgaard OSM Restaurant health inspection report synchronizer'}))
    oa=oar.read().decode("utf8")
    osm=json.loads(oa)
    print(json.dumps(osm,indent=2))
    print("#addr= "+str(len(osm)))
    if (len(osm)==1):
        print ("got exactly one postion")
        ac=osm[0]
        if (ac["osm_type"]=="node"):
            print ("is node")
            adr["lon"]=float(ac["lon"])
            adr["lat"]=float(ac["lat"])
            fixedaddrs.append(adr)
    print(" do " + alu)
    sleep(1)
    limit=limit -1
    if limit<0:
        break
    
print(json.dumps(fixedaddrs,indent=2),file=fixed)
