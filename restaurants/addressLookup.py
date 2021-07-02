#!/usr/bin/python3

# Niels Elgaard Larsen 2018
# for looking up addresses for FVST health reports that do not have a valid position
# TODO interpolate if close


import json
from pprint import pprint
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import string
import urllib3
import sys
import re
import overpass
from time import sleep
from collections import defaultdict
import os
api = overpass.API()
fixcnt=0
limit=900 # for testing
fixedaddrs={'elements':{},'info':'fvst data, fixed by lookup up addresses with overpass turbo'}
notfixedaddrs={'elements':[],'info':'fvst data, not fixed by lookup up addresses with overpass turbo'}

if os.path.isfile("data/addrcache.json"):
      addrcache=defaultdict(dict,json.loads(open("data/addrcache.json",'r', encoding='utf-8').read()))
else:
      addrcache=defaultdict(dict)

alist=[]
fvsterrfile='data/fvsterror.json'

if os.path.isfile(fvsterrfile):
    fvsterr=open(fvsterrfile,mode="r", encoding='utf-8').read()
    if (len(fvsterr)>0):
        alist=json.loads(fvsterr)

def dooverpass(avej,ano,pno):
    print(" opass:"+avej+", nr="+ano+", pn="+pno+"#")
    sleep(4)
    try:
        r = api.Get('node["addr:country"="DK"]["addr:postcode"="'+pno+'"]["addr:street"="'+avej+'"]["addr:housenumber"="'+ano+'"]',responseformat="json")
        osm=r['elements']
        print(json.dumps(osm,indent=2))
        return osm
    except overpass.errors.MultipleRequestsError:
        print("ignore Multiple Requests Error")
        return []
    except urllib3.exceptions.ProtocolError:
        print("ignore proto err")
        return []
    except:
        print("ignore API Error")
        return []

def doaddr(fixedaddrs,ac,adr):
    global fixcnt
    global addrcache
    if ac["type"]=="node":
        fixcnt=fixcnt+1
        print ("is node")
        adr["lon"]=float(ac["lon"])+0.00003 # not right on top of address node
        adr["lat"]=float(ac["lat"])
        adr["src"]="addrfix"
        addrcache[adr["postnr"]][adr['addr']]={"lat":ac["lat"],"lon":ac["lon"]}
        fixedaddrs["elements"][str(adr["id"])]=adr

ano=0
for adr in alist:
    #print("check cache for ", adr["id"])
    cachedadr=addrcache[adr["postnr"]].get(adr['addr'],'')
    if cachedadr:
        #print("\n  CACHED ",adr["id"])
        adr["lat"]=cachedadr["lat"]
        adr["lon"]=cachedadr["lon"]
        fixedaddrs["elements"][str(adr['id'])]=adr
        continue
    if limit<0:
        continue
    ano=ano+1
    altnrs=[];
    at=adr['addr'].replace("Prof. ","Professor ").replace("Albertlnelund","Albertinelund").replace("(City 2-Staderne)","").replace("Peter Fjelstrupvej","Peter Fjelstrups Vej").replace("Otte Busse","Otto Busse").replace("Hesseløgade, Drejøgade ","Drejøgade ").replace("Gammelskolevej19 3210 vejby 19","Gammel Skolevej 19 3210 vejby").replace("HC ","H. C. ").replace("Frederik 7,","Frederik 7 Vej,").replace("Tordensskjoldgade","Tordenskjoldsgade").replace("Estruplundevej","Estruplundvej").replace("Tømregade","Tømrergade").replace(" Kvt "," Kvarter ").split(',')[0].strip().split('-')
    a=at[0].strip()
    street=adr['addr']
    pno=str(adr['postnr'])
    if pno=="1659":
          pno="1658"
    ads=re.search(r"(\D*) ([0-9]+ ?[a-zA-Z]*)",a)
    if ads and ("all" in sys.argv  or "senestekontrol" in adr and adr["senestekontrol"]):
        if len(at)>1:
           altnrs.append(at[1].strip())
           print("altnrs=",altnrs[0])
        print("\n")
        print("#"+str(ano)+" l="+str(limit)+" "+adr["name"]+":  VEJ="+street)
        limit=limit -1
        anr=ads.group(2).replace(" ","").upper()
        if (len(anr)>1  and anr[0] == "0" ):
              anr=anr[1:]
        anrn=int(re.split("[a-zA-Z ]",anr)[0])
        avej=ads.group(1).title()
        avej=avej.replace("Vald ","Valdemar ").replace(" Pl."," Plads").split(",")[0]
        avej=avej.replace("  "," ").replace(", TV","")
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
        if avej=="Vimmelskaftet" and anrn==47 and pno=="1162":
            pno="1161"
        if avej=="Christian Xs Vej":
            avej="Christian X's Vej"
        if avej=="Alsgde":
            avej="Alsgade"
        if avej=="Smedebjergvej":
            avej="Smedebjergevej"
        if avej=="Baron Boltens Gaard":
            avej="Boltens Gård"
        if avej=="Århusgade" and anrn>120 and pno=="2100":
            pno="2150"
        if avej=="Dronningens Tværgade" and anrn==22 and pno=="1322":
            pno="1302"
        print(" Vej="+avej+"::"+anr+"~"+str(anrn)+" p="+pno)
        osm=dooverpass(avej,anr,pno)
        if (len(osm)==1):
            print ("got exactly one postion")
            ac=osm[0]
            doaddr(fixedaddrs,ac,adr)
        else:
            #print("got "+str(len(osm)) +": anra="+anr)
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
                doaddr(fixedaddrs,ac,adr)
            else:
                rpls={
                      r"Agerup":"Ågerup",
                      r" Og ":" & ",
                      r" +vej$":r"vej",
                      r"(\w)vej$":r"\1svej",
                      r"(\w)vej\b":r"\1 Vej",
                      r"evej\b":"vej",
                      r"bakke\b":" Bakke",
                      r"centeret\b":"centret",
                      r"centeret$":" Centret",
                      r"bjergvej\b":"bjerg",
                      r"Bentzosvej":"Bentzonsvej",
                      r"(^s)vej\b":r"\1s Vej",
                      r", st":"",
                      r"Aalborg":"Ålborg",
                      r"Alekistevej$":"Ålekistevej",
                      r"Alholm":"Ålholm",
                      r"Allee$":"Alle",
                      r"alle$":" Alle",
                      r"Bogbinder":"Bogbinderi",
                      r"Bjerggade$":"Bjergegade",
                      r"Blomsyerlunden":"Blomsterlunden",
                      r"Center Vej":"Centervej",
                      r"City 2$":"Cityringen",
                      r"Dosseringen":"Dossering",
                      r"Dronning Margrethevej":"Dronning Margrethes Vej",
                      r"Eli ":"E. ",
                      r"Eddison":"Edison",
                      r"^(\w+) Havekoloni":r"Havekolonien \1",
                      r"\bGd\b":"Gade",
                      r"Estruplundevej\b":"Estruplundvej",
                      r"Frederik 7":"Frederik 7 Vej",
                      r"Frederiks ":"Frederik ",
                      r"Fuglsang":"Fuglesang",
                      r"Karen Blixens Vej":"Karen Blixens Plads",
                      r"Gravervenget$":"Gravervænget",
                      r"Gunslevmaglevej\b":"Gundslevmaglevej",
                      r"\bGertrude Stenin":"Gertrude Stein",
                      r"Hovedgade$":"Hovedgaden",
                      r"Holmstrupgårdsvej":"Holmstrupgårdvej",
                      r"Holmstrupgård\b":"Holmstrupgårdvej",
                      r"Holmgaardvej\b":"Holmegårdvej",
                      r"Islevgård Allé":"Islevgård Alle",
                      r"J(F|f) ":"John F. ",
                      r"JF Kennedys ":"John F. Kennedys",
                      r"Jf ":"J. F. ",
                      r"J Chr Juliussens Vej":"Jens Christian Juliussens Vej",
                      r"Kaj Lindbergsgade":"Kai Lindbergs Gade",
                      r"Lerso Parkalle":"Lersø Parkallé",
                      r"Langeløbet":"Langløbet",
                      r"Sct. Laurantii Vej":"Sankt Laurentii Vej",
                      r"terrasserna$":"terrasserne",
                      r"Skt. Knuds Allé":"Sanct Knuds Alle",
                      r"Listved":"Listedvej",
                      r"Møldrupvej":"Mørdrupvej",
                      r"Sofiemindes Allé":"Sofiesminde Alle",
                      r"Nr\. ":"Nr ",
                      r"Nøreng\b":"Nør-Eng",
                      r"Nr\.? ":"Nørre ",
                      r"Ny ":"Nye ",
                      r"Rafshalevej":"Refshalevej",
                      r"Søndergågade$":"Søndergade",
                      r"Taastrup":"Tåstrup",
                      r"Tønsbjerg":"Tønsberg",
                      r"Volk Møllevej$":"Volkmøllevej",
                      r"\bAlle\b":"Allé",
                      r"\bAllé\b":"Alle",
                      r"\bFennevej\b":"Fennvej",
                      r"\bKaj\b":"Kai",
                      r"\bLerso\b":"Lersø",
                      r"\bLykkeholmsvej":"Lykkesholms Allé",
                      r"\bMarkmansgade":"Markmandsgade",
                      r"\bSdr\.? ?":"Søndre ",
                      r"\bStadion Alle":"Stadionalle",
                      r"\bTordensskjoldgade\b":"Tordenskjoldsgade",
                      r"\bTove Ditlevsen Vej\b":"Tove Ditlevsens Vej",
                      r"Tvillum":"Tvilum",
                      r"\bVilh\. ?\b":"Vilhelm ",
                      r"\bWildensskovsvej":"Wildenskovsvej",
                      r"\bmøllevej":" Møllevej",
                      r"^Vinbyholtvej\b":"Vindbyholtvej",
                      r"^(\w) ":r"\1. ",
                      r"^(\w)\.? ?(.)\.? (\w+)":r"\1. \2. \3",
                      r"^(\w)\.(\w)\.":r"\1. \2.",
                      r"^Alholm":"Ålholm",
                      r"^Chr. d. IXs":"Christian IX's",
                      r"^Chr. d. Xs":"Christian X's",
                      r"^Chr\. Kold":"Christen Kold",
                      r"^Chr\.? ":"Christian ",
                      r"^Chr\b":"Chr.",
                      r"Dokkedalsvej":"Dokkedalvej",
                      r"^D B U ":"DBU ",
                      r"Jensden":"Jensen",
                      r"Listvej":"Listedvej",
                      r"Erikhusfeldstvej":"Erik Husfeldts Vej",
                      r"Faurgaardsvej":"Favrgaardsvej",
                      r"^Dr\. ?":"Doktor ",
                      r"^Gl\.? ":"Gammel ",
                      r"^Gl\.? ":"Gammel ",
                      r"^Gl Skolevej\b":"Gl. Skolevej",
                      r"Hampelandsvej":"Hampelandvej",
                      r"^H P ":"H.P. ",
                      r"^H P \b":"H. P. ",
                      r"Indius Jensensvej":"Indius J. Vej",
                      r"^Hf\. ?":"Haveforeningen ",
                      r"Kridthøjtorvet":"Kridthøjvej",
                      r"Kroppendal":"Kroppedal",
                      r"Linnesgade":"Linnésgade",
                      r"L.A.Ringsvej":"L.A. Rings Vej",
                      r"^Mylius Erichsens Vej\b":"Mylius-Erichsensvej",
                      r"^Magrethe":"Margrethe",
                      r"^Markedstræde\b":"Markedsstræde",
                      r"^Ndr\.? ":"Neder ",
                      r"^Ndr\.? ?":"Nordre ",
                      r"^Neder ":"Ndr ",
                      r"^Niels Borh":"Niels Bohr",
                      r"Niels W ":"Niels W. ",
                      r"^Nørreboulevard":"Nørre Boulevard",
                      r"^Nørre(\w)":r"Nørre \1",
                      r"^Osvald Helmutsvej":"Osvald Helmuths Vej",
                      r"^Paludan Müller":"Paludan-Müller",
                      r"^Saddelmagerporten\b":"Sadelmagerporten",
                      r"^Soborg Hodvegade":"Søborg Hovedgade",
                      r"Staegers":"Stægers",
                      r"^Sct\.? ?":"Sanct ",
                      r"^Sct\. ":"Sankt ",
                      r"^Sdr\.? ?":"Sønder ",
                      r"^Skt ":"Sankt ",
                      r"^Skt\. ?":"Sankt ",
                      r"^Skt\. ":"Sanct ",
                      r"^St\. ?":"Store ",
                      r"aa":"å",
                      r"([^s])toften":r"\1stoften",
                      r"Stavnsager":"Stavnager",
                      r"å":"aa",
                      r"ae":"æ",
                      r"\bÅ":"Aa",
                      r"allen$":"alleen",
                      r"centeret\b":"centret",
                      r"centret\b":" Centret",
                      r"desvej$":"dsvej",
                      r"enteret$":"entret",
                      r"gade$":"sgade",
                      r"gade\b":" Gade",
                      r"gård ":"gårds ",
                      r"gård ":"gårds ",
                      r"gården$":"gård",
                      r"husfeldst":"husfeldts",
                      r"skov\b":" Skov",
                      r"Provesten":"Prøvesten",
                      r"strædet$":"stræde",
                      r"Sigurdesgade$":"Sigurdsgade",
                      r"Stjerneholmsgade$":"Stjernholmsgade",
                      r"Stynø":"Strynø",
                      r"toft$":" Toft",
                      r"Tvaervej$":"Tværvej",
                      r"torv$":" Torv",
                      r"vej$":" Vejen",
                      r"Vaenge":"Vænge",
                      r"Slangrup":"Slangerup",
                      r" vej$":"vej",
                      r" Vej$":"vej",
                      r" V$":" Vej",
                      r"\bVarebro":"Værebro",
                      r" Plads$":" Vej",
                      r"vej\b":"vejen",
                      r"Ålborg":"Aalborg",
                      r"Ålsgårdecenteret":"Ålsgårdecentret",
                      r"é":"e",
                      r"Øster ":"Østre ",
                      r"Østre\b":"Øster",
                      r"I C\b":"I.C.",
                      r"Ålhomvej":"Ålholmvej",
                      r"\bVenstrupparken":"Ventrupparken"
                }
                for rpk,rpv in rpls.items():
                    tavej=re.sub(rpk,rpv,avej)
                    if tavej != avej:
                          osm=dooverpass(tavej,anr,pno)
                          if (len(osm)==1):
                                print ("FINALLY got exactly one postion")
                                ac=osm[0]
                                doaddr(fixedaddrs,ac,adr)
                                break
                else:
                    notfixedaddrs["elements"].append(adr)

adc=open('data/addrcache.json',mode="w",encoding='utf-8')
print(json.dumps(addrcache,indent=2, ensure_ascii=False),file=adc)

fixed=open('data/fixed.json',mode="w",encoding='utf-8')
notfixed=open('data/notfixed.json',mode="w",encoding='utf-8')
print(json.dumps(fixedaddrs,indent=2, ensure_ascii=False),file=fixed)
print(json.dumps(notfixedaddrs,indent=2, ensure_ascii=False),file=notfixed)
print("    fixed: "+ str(fixcnt))
print("    total: "+ str(len(fixedaddrs["elements"])))
print("not fixed: "+ str(len(notfixedaddrs["elements"])))

