#!/usr/bin/python3

# Niels Elgaard Larsen 2016
# for looking up addresses for FVST health reports that do not have a valid position
# TODO interpolate if close


import json
from pprint import pprint
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import string
import sys
import re
import overpass
from time import sleep
import os

api = overpass.API()

limit=500 # for testing
fixedaddrs={'elements':[],'info':'fvst data, fixed by lookup up addresses with overpass turbo'}
fixed=open('data/fixed.json',mode="w",encoding='utf-8')

alist=[]
fvsterrfile='data/fvsterror.json'

if os.path.isfile(fvsterrfile):
    fvsterr=open(fvsterrfile,mode="r", encoding='utf-8').read()
    if (len(fvsterr)>0):
        alist=json.loads(fvsterr)

def dooverpass(avej,ano,pno):
    print(" opass:"+avej+", nr="+ano+", pn="+pno+"#")
    sleep(1.5)
    try:
        r = api.Get('node["addr:country"="DK"]["addr:postcode"="'+pno+'"]["addr:street"="'+avej+'"]["addr:housenumber"="'+ano+'"]',responseformat="json")
        osm=r['elements']
        print(json.dumps(osm,indent=2))   
        return osm
    except overpass.errors.MultipleRequestsError:
        print("ignore Multiple Requests Error")
        return []
    except overpass.errors.ServerLoadError:
        print("ignore Server Load Error")
        return []

def doaddr(fixedaddrs,ac):
        if ac["type"]=="node":
            print ("is node")
            adr["lon"]=float(ac["lon"])+0.00003 # not right on top of address node
            adr["lat"]=float(ac["lat"])
            adr["src"]="addrfix"
            fixedaddrs["elements"].append(adr)
ano=0
for adr in alist:
    ano=ano+1
    print("\n")
    altnrs=[];
    at=adr['addr'].replace("Hesseløgade, Drejøgade ","Drejøgade ").split(',')[0].strip().split('-')
    a=at[0].strip()
    if len(at)>1:
        altnrs.append(at[1].strip())
        print("altnrs=",altnrs[0])
    street=adr['addr']
    pno=adr['postnr']
    print("#"+str(ano)+"  vej: "+street)
    ads=re.search("(\D*) ([0-9]+[a-zA-Z]*)",a)
    if ads and "senestekontrol" in adr and adr["senestekontrol"]:
        anr=ads.group(2).replace(" ","").upper()
        avej=ads.group(1).title().replace("Vald ","Valdemar ").split(",")[0]
        print(" vej="+avej+"::"+anr)
        osm=dooverpass(avej,anr,pno)
        if (len(osm)==1):
            print ("got exactly one postion")
            ac=osm[0]
            doaddr(fixedaddrs,ac)
        else:
            print("got "+str(len(osm)) +": anra"+anr)
            #print(json.dumps(osm,indent=2),"\n")
            if (anr[-1] in "ABCDEFGHIJKabcdef"):
                anra=anr[:-1]
            else:
                if len(altnrs)>0:
                    anra=altnrs[0]
                else:
                    anra=anr+"A"
                print(" anra="+anra)
            osm=dooverpass(avej,anra,pno)
            if (len(osm)==1):
                print ("NOW got exactly one postion")
                ac=osm[0]
                doaddr(fixedaddrs,ac)
            else:
                avej=avej.replace("Nr ","NÃ¸rre ").replace("gade"," Gade").replace("Hovedgade","Hovedgaden").replace("Henrik Dams Alle","Sæltofts Plads").replace("vej"," Vej").replace("toft"," Toft").replace("enteret","entret").replace("Skt.","Sankt").replace("Sct.","Sanct").replace("Sdr.","Søndre").replace("Skt.","Sankt ").replace("Ndr.","Nordre ").replace("Gl.","Gammel").replace("Allé","Alle").replace(" Alle","alle").replace("Sct ","Sanct ")
                osm=dooverpass(avej,anr,pno)
                if (len(osm)==1):
                    print ("NOW got exactly one postion")
                    ac=osm[0]
                    doaddr(fixedaddrs,ac)
                    
    limit=limit -1
    if limit<0:
        break
    
print(json.dumps(fixedaddrs,indent=2),file=fixed)
print("fixed: "+ str(len(fixedaddrs["elements"])))
