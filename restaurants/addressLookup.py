#!/usr/bin/python3

# Niels Elgaard Larsen 2018
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
notfixedaddrs={'elements':[],'info':'fvst data, not fixed by lookup up addresses with overpass turbo'}

fixed=open('data/fixed.json',mode="w",encoding='utf-8')
notfixed=open('data/notfixed.json',mode="w",encoding='utf-8')

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
    at=adr['addr'].replace("Prof. ","Professor ").replace("Otte Busse","Otto Busse").replace("Hesseløgade, Drejøgade ","Drejøgade ").split(',')[0].strip().split('-')
    a=at[0].strip()
    if len(at)>1:
        altnrs.append(at[1].strip())
        print("altnrs=",altnrs[0])
    street=adr['addr']
    pno=str(adr['postnr'])
    print("#"+str(ano)+" "+adr["name"]+":  vej="+street)
    ads=re.search("(\D*) ([0-9]+[a-zA-Z]*)",a)
    if ads and "senestekontrol" in adr and adr["senestekontrol"]:
        anr=ads.group(2).replace(" ","").upper()
        anrn=int(re.split("[a-zA-Z ]",anr)[0])
        avej=ads.group(1).title().replace("Vald ","Valdemar ").replace(" Pl."," Plads").split(",")[0]
        if avej=="Bernstorffsgade" and anrn==3 and pno=="1557":
            pno="1577"
        if avej=="Refshalevej" and pno=="1422":
            pno="1432"
        if avej=="Onkel Dannys plads" and pno=="1700":
            pno="1711"
        if avej=="Rødovre Centrum" and anrn==82:
            anr="1P"
        if avej=="Kampmannsgade" and pno=="1603":
            pno="1604"
        if avej=="Slagelsevej" and anrn==2 and pno=="4460":
            anr="4"
        if avej=="Bygaden" and pno=="4295":
            avej="Hovedgaden"
        if avej=="Kongens Nytorv" and anrn==13 and pno=="1095":
            pno="1050"
        if avej=="Sønder Boulevard" and anrn==136 and pno=="1718":
            pno="1720"
        if avej=="Over Bølgen" and anrn==15 and pno=="2670":
            anr="11A"
        if avej=="Christian Xs Vej":
            avej="Christian X's Vej"
        if avej=="Smedebjergvej":
            avej="Smedebjergevej"
        if avej=="Baron Boltens Gaard":
            avej="Boltens Gård"
        if avej=="Århusgade" and anrn>120 and pno=="2100":
            pno="2150"
        if avej=="Dronningens Tværgade" and anrn==22 and pno=="1322":
            pno="1302"
        print(" vej="+avej+"::"+anr+"~"+str(anrn)+" p="+pno)
        osm=dooverpass(avej,anr,pno)
        if (len(osm)==1):
            print ("got exactly one postion")
            ac=osm[0]
            doaddr(fixedaddrs,ac)
        else:
            print("got "+str(len(osm)) +": anra="+anr)
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
                avej=avej.replace("  "," ").replace(", TV","").replace("Center Vej","Centervej").replace(", st","").replace("Nr ","Nørre ").replace("xxxgade"," Gade").replace("Hovedgade","Hovedgaden").replace("Henrik Dams Alle","Sæltofts Plads").replace("desvej","dsvej").replace("xxvej"," Vej").replace("torv"," Torv").replace("toft"," Toft").replace("enteret","entret").replace("Skt.","Sankt").replace("Sct.","Sanct").replace("Sdr.","Sønder").replace("Sdr ","Sønder ").replace("Skt.","Sankt ").replace("Ndr.","Nordre ").replace("Gl.","Gammel").replace("Allé","Alle").replace(" Alle","alle").replace("Sct ","Sanct ").replace("Dr. ","Doktor ").replace("Rafshalevej","Refshalevej")
                osm=dooverpass(avej,anr,pno)
                if (len(osm)==1):
                    print ("FINALLY got exactly one postion")
                    ac=osm[0]
                    doaddr(fixedaddrs,ac)
                else:
                    notfixedaddrs["elements"].append(adr)
                    
    limit=limit -1
    if limit<0:
        break
    
print(json.dumps(fixedaddrs,indent=2, ensure_ascii=False),file=fixed)
print(json.dumps(notfixedaddrs,indent=2, ensure_ascii=False),file=notfixed)
print("    fixed: "+ str(len(fixedaddrs["elements"])))
print("not fixed: "+ str(len(notfixedaddrs["elements"])))

