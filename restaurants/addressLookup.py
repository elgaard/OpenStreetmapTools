#!/usr/bin/python3

import json
from pprint import pprint
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import string
import sys
from time import sleep

fixedaddrs=[]
u8o=open(1, 'w', encoding='utf-8', closefd=False)
fixed=open('data/fixed.jason',mode="w",encoding='utf-8')


fvsterrfile='data/fvsterror.json';
fvsterr=open(fvsterrfile,mode="r")
alist=json.loads(open(fvsterrfile,'r', encoding='utf-8').read())

for adr in alist:
    print("\n\n\n")
    print(adr, file=u8o)
    alu="http://nominatim.openstreetmap.org/search?"+urlencode({"country":"Denmark","format":"json","street":adr['addr'],"postalcode":adr['postnr'],"email":"osm@agol.dk","addressdetails":0})
    print("alu= "+alu, file=u8o)
    oar=urlopen(Request(alu, headers={'User-Agent': 'Elgaard OSM Restaurant health inspection report synchronizer'}))
    os=oar.read().decode("utf8")
    osm=json.loads(oa)
    print(json.dumps(osm,indent=2))
    print("#addr= "+str(len(osm)))
    if (len(osm)==1):
        ac=osm[0]
        if (ac.address):
                adr.lon=ac.lon
                adr.lat=ac.lat
                fixedaddrs.append(adr)
    print(" do " + alu)
    sleep(1)
print(json.dumps(fixedaddrs,indent=2),file=fixed)
