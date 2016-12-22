#!/usr/bin/python3

# Niels Elgaard Larsen 2016
# for looking up addresses for FVST health reports that do not have a valid position
# TODO look up 20, 20A, 20B
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


api = overpass.API()

limit=500 # for testing
fixedaddrs={'elements':[],'info':'fvst data, fixed by lookup up addresses with voerpass turbo'}
u8o=open(1, 'w', encoding='utf-8', closefd=False)
fixed=open('data/fixed.json',mode="w",encoding='utf-8')

fvsterrfile='data/fvsterror.json';
fvsterr=open(fvsterrfile,mode="r")
alist=json.loads(open(fvsterrfile,'r', encoding='utf-8').read())

def overpass(avej,ano,pno):
    print(" opass: "+avej+", nr="+ ano+" ,pn="+pno)
    r = api.Get('node["addr:country"="DK"]["addr:postcode"="'+pno+'"]["addr:street"="'+avej+'"]["addr:housenumber"="'+anr+'"]',responseformat="json")
    osm=r['elements']
    sleep(1)
    print(json.dumps(osm,indent=2))   
    return osm

def doaddr(fixedaddrs,ac):
        if (ac["type"]=="node"):
            print ("is node")
            adr["lon"]=float(ac["lon"])+0.00003 # not right on top of address node
            adr["lat"]=float(ac["lat"])
            adr["src"]="addrfix"
            fixedaddrs["elements"].append(adr)
ano=0
for adr in alist:
    ano=ano+1
    print("\n")
    a=adr['addr'].split(',')[0].split('-')[0].strip()
    street=adr['addr']
    pno=adr['postnr']
    print("#"+str(ano)+"  vej: "+street)
    ads=re.search("(\D*) ([0-9]+[a-zA-Z]*)",a)
    if ads:
        anr=ads.group(2).replace(" ","").upper()
        avej=ads.group(1).title().replace("Vald ","Valdemar ").split(",")[0]
        print(" vej "+avej+" :: "+anr)
        osm=overpass(avej,anr,pno)
        if (len(osm)==1):
            print ("got exactly one postion")
            ac=osm[0]
            doaddr(fixedaddrs,ac)
        else:
            print("got too many/few sfx= "+street[-1])
            if (street[-1] in "ABCDEFGHIJKabc"):
                anra=anr[:-1]
            else:
                anra=anr+"B"
            print(" anra="+anra)
            osm=overpass(avej,anra,pno)
            if (len(osm)==1):
                print ("NOW got exactly one postion")
                ac=osm[0]
                doaddr(fixedaddrs,ac)
            else:
                avej=avej.replace("Nr ","NÃ¸rre ").replace("gade"," Gade").replace("Henrik Dams Alle","SÃ¸ltofts Plads").replace("vej"," Vej").replace("toft"," Toft").replace("enteret","entret").replace("Skt.","Sankt").replace("Sct.","Sanct").replace("Sdr.","SÃ¸ndre").replace("Gl.","Gammel").replace("Allé","Alle").replace("Sct ","Sanct ")
                osm=overpass(avej,anr,pno)
                if (len(osm)==1):
                    print ("NOW got exactly one postion")
                    ac=osm[0]
                    doaddr(fixedaddrs,ac)
                    
    limit=limit -1
    if limit<0:
        break
    
print(json.dumps(fixedaddrs,indent=2),file=fixed)
print("fixed: "+ str(len(fixedaddrs["elements"])))
