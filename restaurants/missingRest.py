import json
from pprint import pprint
import re
import string
import sys
import os
from datetime import datetime
import urllib.request
from time import sleep


now=datetime.now()

def fvstage(s):
      d=s.split(" ")[0].split("-")
      return (now-datetime(int(d[2]),int(d[1]),int(d[0]))).days


def osmage(s):
      d=s.split("T")[0].split("-")
      return (now-datetime(int(d[0]),int(d[1]),int(d[2]))).days

fullmatch=False;
fvstfile='data/r.json';
fvsterrfile='data/fvsterror.json'
fvsterr=open(fvsterrfile,mode="w")
mlog=open("missing.log",encoding='utf-8',mode="w")

fvstall=open("data/rall.json",mode="r").read()

fvsterrlist=[]
gone=[]
merge_candidates=[];

if (len(sys.argv)>1 and sys.argv[1]=="match"):
      fullmatch=True
      fvstfile='data/rfull.json'
      print("fullmatch")

blacklist=json.loads(open('blacklist.json','r', encoding='utf-8').read())['blacklist']

osmres=open('data/osmres.json',"r",encoding='utf-8').read()
osmdata = json.loads(osmres)
osmlbnr=[]

def getfvst(o):
      if 'fvst:navnelbnr' in o:
            return o['fvst:navnelbnr']
      elif 'tags' in o and  'fvst:navnelbnr' in o['tags']:
            return o['tags']['fvst:navnelbnr']
      return None
      
def getname(o):
      if ('name' in o):
            return o['name']
      elif ('tags' in o and 'name' in o['tags']):
            return o['tags']['name']
      else:
            return ""

def getamenity(o):
      if 'amenity' in o:
            return o['amenity']
      if 'tags' in o and 'amenity' in o['tags']:
            return o['tags']['amenity']
      return None


def canonicalname(nm):
      if not nm:
            return nm
      nm0=nm.replace(" AB","").replace(" P/S","").replace("Gl ","Gammel ")

      nm1=nm0.split(" - ")[0].split(" ApS")[0].lower().replace('air group a/s restaurants,','').replace("&","og").replace("å","aa").split(" i/s")[0].split(" v. ")[0].split(" v/")[0].split(" /")[0].split(" -")[0].split(" i/s")[0].split(" aps")[0].split(" ved ")[0].split(" c/o")[0].translate(str.maketrans(u'ñèéäöúá–\'-´.,’+&"`|', 'neeæøua            ')) +' '
      nm2=nm1.replace('pizzeria','pizza').replace('pizzaria','pizza').replace('pizzabar','pizza').replace('pizza bar','pizza')
      nm3=re.sub('/v.*',' ',re.sub('den ',' ',re.sub('( og cafe| og bar|cafe | Kro|Café| v/.*| a/s|pizza bar| pizza house|og pizza| og grillbar|pizzeria |restauranten | restaurante|take out|take away| af 20|ristorante|restaurant|spisestedet |bryggeriet| house| and | grill| og cafe|s køkken| pizza|pizza |the |kafe |cafeen |cafe |hotel | spisehus| og grillbar| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| I/S| take away| IVS| aps| ApS)','',nm2))).replace('/','')
      nmc=re.sub(' 2','',nm3)
      return nmc.replace(' ','')

def canonical(res):
  nm='UNDEFINED'
  nm=canonicalname(getname(res))
  posob=res
  if 'center' in res:
        posob=res['center']
  rv={'id': res['id'],
      'name':nm,
      'orgname':getname(res),
      'type':res['type'],
      'lat':posob['lat'],
      'lon':posob['lon'],
      'fvst:navnelbnr':res['tags'].get('fvst:navnelbnr','')
  }
  if 'tags' in res and 'fvst:name' in res['tags']:
        rv['fvstname']=canonicalname(res['tags']['fvst:name'])
  return rv 

smilinfo={}
fvst={} # holds OSM object with a fvst:navnelbnr tag
osminfo={} # holds OSM restaurants, cafes, fast_food, etc
osminfo_by_pos={} # holds OSM restaurants, cafes, fast_food, etc by position
match=[] # holds matches based on name and location, i.e. FVST objects already in OSM, but without fvst:navnelbnr tag

for res in list(osmdata['elements']):
    if res['type'] in ['way','node','relation'] and getname(res):
      cn=canonical(res)
      if (cn['name'] not in osminfo):
        osminfo[cn['name']]=[]
      osminfo[cn['name']].append(cn)
      osminfo_by_pos["p"+str(cn['lat'])+","+str(cn['lon'])]=cn
      if 'fvstname' in cn:
            if (cn['fvstname'] not in osminfo):
                  osminfo[cn['fvstname']]=[]
            osminfo[cn['fvstname']].append(cn)
            
      if 'tags' in res and 'fvst:navnelbnr' in res['tags']:
          fvst[res['tags']['fvst:navnelbnr']]=res
            
smilres=open(fvstfile,"r",encoding='utf-8').read()
smf = json.loads(smilres)['elements']
fixed='data/fixed.json'
if os.path.isfile(fixed):
      fixeddata=json.loads(open(fixed,'r', encoding='utf-8').read())['elements']
else:
     fixeddata=[] 

smildata=fixeddata+smf
print(str(len(fixeddata))+" fixed "+str(len(smf))+" from fvst, now in smildata: "+ str(len(smildata)))

missingItems={'elements':[],'info':'missing restaurants'}
for smil in smildata:
  osmlbnr.append(str(smil['id']));
      
for smil in smildata:
    if smil['id'] == 'dummy':
        break
    cn=canonicalname(getname(smil))
    if (cn not in smilinfo):
        smilinfo[cn]=[]
    smil['name']=getname(smil).replace("`","").replace("|","").replace(",","").replace("'","")
    smilinfo[cn].append(smil)
    print("do smil ", cn,smil['id'], file=mlog )
    found=False
    if str(smil['id']) in fvst:
          print(" in fvst ", cn,smil['id'], " osmid",fvst[str(smil['id'])]['id'], file=mlog )
          continue
    if str(smil['id']) in blacklist:
          print(" in blacklist ", cn,smil['id'], file=mlog )
          continue
    if (not smil['lat'] or not smil['lon'] or int(smil['lat']) < 54 or int(smil['lat'])> 57 or int(smil['lon'])<8 or int(smil['lon']) > 15):
          print(" missing pos: ", cn,smil['id'], file=mlog )
          fvsterrlist.append(smil)
    if cn=='':
      print("  no name:",smil['id'], file=mlog )          
    else:
          if cn in osminfo:
            # print("tze "+cn+" "+str(smil['lat'])+","+str(smil['lon']))
            if (smil['lat']==0.0 or smil['lon']==0.0):
                  print(" zero pos: ", cn,smil['id'], file=mlog )
                  # print("ze "+cn)
                  if (len(osminfo[cn])==1): # there is only one global match, so we go with it
                        ores=osminfo[cn][0]
                        olbnr=ores["fvst:navnelbnr"]
                        if (not "fvst:navnelbnr" in ores or ores["fvst:navnelbnr"]=="" or not ores["fvst:navnelbnr"] in osmlbnr):
                              # FIXME TODO, also only if ores["fvst:navnelbnr"] still exists in FVST
                              found=True
                              merge_candidates.append(olbnr);
                              match.append({"fvst:navnelbnr":smil['id'],
                                      "category":"fvst:no_pos",
                                      "type":ores["type"],
                                      "id":ores["id"],
                                      "osm:name":ores["orgname"],
                                      "osm:navnelbnr":olbnr,
                                      "fvst:name":smil['name'],
                                      'lat':ores['lat'],
                                      'lon':ores['lon']
                        })
            else:
              print(" try pos match: ", cn,smil['id'], file=mlog)
              for ores in osminfo[cn]:
                d = (smil['lat']-ores['lat'])*(smil['lat']-ores['lat'])+(smil['lon']-ores['lon'])*(smil['lon']-ores['lon'])
#                print("d=",d,"for ",smil['id']," ", smil['name'])
                if (d<0.000005 or 'fvst:fixme' in ores):
                    found=True
                    olbnr=ores["fvst:navnelbnr"]
                    if (olbnr and not (olbnr in osmlbnr)):
                          olbnr=""
                    print("   is found: ", cn,smil['id']," olbnr=",olbnr, file=mlog)
                    merge_candidates.append(olbnr)
                    print("     append: ", cn,smil['id']," olbnr=",olbnr, file=mlog)
                    match.append({"fvst:navnelbnr":smil['id'],
                                  "type":ores["type"],
                                  "id":ores["id"],
                                  "osm:name":ores["orgname"],
                                  "osm:navnelbnr":olbnr,
                                  "fvst:name":smil['name'],
                                  'lat':ores['lat'],
                                  'lon':ores['lon'],
                                  'slat':smil['lat'],
                                  'slon':smil['lon']
                    })
    if not found and smil['lat']>0 and smil['lon']>0:
      print(" not found: ", cn,smil['id'], file=mlog)
      pos="p"+str(smil['lat'])+","+str(smil['lon'])
      if (pos in osminfo_by_pos):
            ores=osminfo_by_pos[pos]
            olbnr=ores["fvst:navnelbnr"]
            if (olbnr and not (olbnr in osmlbnr)):
                  olbnr=""
            match.append({"fvst:navnelbnr":smil['id'],
                          "type":ores["type"],
                          "category":"exact",
                          "exact":1,
                          "id":ores["id"],
                          "osm:name":ores["orgname"],
                          "osm:navnelbnr":olbnr,
                          "fvst:name":smil['name'],
                          'lat':ores['lat'],
                          'lon':ores['lon'],
                          'slat':smil['lat'],
                          'slon':smil['lon']
                          })
      else:
        missingItems['elements'].append(smil)

print("now osm not in fvst")
print("merge_candidates: ",json.dumps(merge_candidates,indent=2),file=mlog)

for osmelm in list(osmdata['elements']):
      if "tags" in osmelm and "amenity" in osmelm["tags"] and osmelm["tags"]["amenity"] in ["restaurant","cafe","fast_food"]:
            if not "fvst:navnelbnr" in osmelm["tags"] or not osmelm["tags"]["fvst:navnelbnr"] in fvstall:
                  age=osmage(osmelm["timestamp"])
                  if "name" in osmelm["tags"]:
                        osmelm["osm:name"]=osmelm["tags"]["name"]
                  else:
                        osmelm["osm:name"]="unnamed"
                  if (not "lat" in osmelm) and "center" in osmelm:
                        osmelm["lat"]=osmelm["center"]["lat"]
                        osmelm["lon"]=osmelm["center"]["lon"]
                  if "fvst:navnelbnr" in osmelm["tags"] and not osmelm["tags"]["fvst:navnelbnr"] in merge_candidates and osmelm["osm:name"].find('Pølsevogn')<0:
                        osmelm["stalefvst"]=True
                        match.append(osmelm)                 
                  elif age>120 and osmelm["osm:name"].find('Pølsevogn')<0:
                        osmelm["notinfvst"]=True
                        match.append(osmelm)
                        gone.append(osmelm)                  
                  #else:
                      #  print("keep",osmelm["osm:name"], "ts=",osmelm["timestamp"], "age: ",age,"days")
                        
print("there was ",len(gone),"not in fvst")        
            
print(json.dumps(fvsterrlist,indent=2,ensure_ascii=True),file=fvsterr)

nids=[]
nidslot={}
for osmelm in match:
  if 'stalefvst' in osmelm or "notinfvst" in osmelm:
    nid= osmelm["type"][0].upper()+ str(osmelm["id"])
    nids.append(nid)
    nidslot[nid]= osmelm

staleaddresses=[]
maxids=50
nid=0

while nid < len(nids):
      nidargs=",".join(nids[nid:nid+maxids])
#      print("args=",nidargs)
      nourl="https://nominatim.openstreetmap.org/lookup/?format=json&osm_ids="+nidargs
      stalef = urllib.request.urlopen(nourl)
      staleaddresses+=json.loads(stalef.read().decode('utf8'))
      nid+=maxids
      sleep(1)

for staleaddress in staleaddresses:
      id=staleaddress["osm_type"][0].upper()+staleaddress["osm_id"]
      addr=nidslot[id]
      addr['stale_address']=staleaddress["address"]

if fullmatch:
      matchfile=open('data/match.json',mode="w")
      print(json.dumps(match,indent=2),file=matchfile)
else:
      missing=open('data/miss.json',mode="w")
      print(json.dumps(missingItems,indent=2),file=missing)
      gonefd=open('data/gone.json',mode="w")
      print(json.dumps(gone,indent=2),file=gonefd)
