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
fixcnt=0
limit=500 # for testing
fixedaddrs={'elements':[],'info':'fvst data, fixed by lookup up addresses with overpass turbo'}
notfixedaddrs={'elements':[],'info':'fvst data, not fixed by lookup up addresses with overpass turbo'}

if os.path.isfile("data/fixed.json"):
      try:
            pfixed=json.loads(open("data/fixed.json",'r', encoding='utf-8').read())['elements']
      except json.decoder.JSONDecodeError as e:
            pfixed=[]
else:
     pfixed=[]

alist=[]
fvsterrfile='data/fvsterror.json'

if os.path.isfile(fvsterrfile):
    fvsterr=open(fvsterrfile,mode="r", encoding='utf-8').read()
    if (len(fvsterr)>0):
        alist=json.loads(fvsterr)

def dooverpass(avej,ano,pno):
    print(" opass:"+avej+", nr="+ano+", pn="+pno+"#")
    sleep(2)
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
    global fixcnt
    if ac["type"]=="node":
        fixcnt=fixcnt+1
        print ("is node")
    adr["lon"]=float(ac["lon"])+0.00003 # not right on top of address node
    adr["lat"]=float(ac["lat"])
    adr["src"]="addrfix"
    fixedaddrs["elements"].append(adr)

ano=0
for adr in alist:
    adone=False
    for ca in pfixed:
      #print("cache cmp",ca['id']," == ",adr['id'])
      if ca['id'] == adr['id']:
        print("\ncached ",ca["id"])
        fixedaddrs["elements"].append(ca)
        adone=True
        break
    if adone:
      continue
    ano=ano+1
    print("\n")
    altnrs=[];
    at=adr['addr'].replace("Prof. ","Professor ").replace("(City 2-Staderne)","").replace("Otte Busse","Otto Busse").replace("Chr.","Christian" ).replace("Hesseløgade, Drejøgade ","Drejøgade ").split(',')[0].strip().split('-')
    a=at[0].strip()
    if len(at)>1:
        altnrs.append(at[1].strip())
        print("altnrs=",altnrs[0])
    street=adr['addr']
    pno=str(adr['postnr'])
    print("#"+str(ano)+" "+adr["name"]+":  vej="+street)
    ads=re.search(r"(\D*) ([0-9]+[a-zA-Z]*)",a)
    if ads and ("all" in sys.argv  or "senestekontrol" in adr and adr["senestekontrol"]):
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
                rpls={
                    "  ":" ",
                    "é":"e",
                    ", TV":"",
                    "Center Vej":"Centervej",
                    ", st":"",
                    "Nr ":"Nørre ",
                    "Hovedgade":"Hovedgaden",
                    "desvej":"dsvej",
                    "torv":" Torv",
                    "toft":" Toft",
                    "enteret":"entret",
                    "Skt.":"Sankt",
                    "Sct.":"Sanct",
                    "Sdr.":"Sønder",
                    "Sdr ":"Sønder ",
                    "Ndr.":"Nordre ",
                    "Gl.":"Gammel",
                    "Gl ":"Gammel",
                    "Sct ":"Sanct ",
                    "Dr. ":"Doktor ",
                    "Rafshalevej":"Refshalevej"
                }
                for rpk,rpv in rpls.items():
                    avej=avej.replace(rpk,rpv)
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

fixed=open('data/fixed.json',mode="w",encoding='utf-8')
notfixed=open('data/notfixed.json',mode="w",encoding='utf-8')
print(json.dumps(fixedaddrs,indent=2, ensure_ascii=False),file=fixed)
print(json.dumps(notfixedaddrs,indent=2, ensure_ascii=False),file=notfixed)
print("    fixed: "+ str(fixcnt))
print("    total: "+ str(len(fixedaddrs["elements"])))
print("not fixed: "+ str(len(notfixedaddrs["elements"])))

