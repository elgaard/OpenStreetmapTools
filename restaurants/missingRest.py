import json
from pprint import pprint
import re
import string
import sys
import os
from datetime import datetime
import urllib.request
import urllib.error
from time import sleep
import gpxpy
import gpxpy.gpx
from datetime import date

now=datetime.now()
mlog=open("missing.log",encoding='utf-8',mode="w")

gpx = gpxpy.gpx.GPX()
#gpx_miss = gpxpy.gpx.GPXTrack()
#gpx.tracks.append(gpx_miss)

def selected(smil):
      if smil["branchekode"] in ["56.29.00.A","99.99.99.H","xDD.56.30.99"] or smil.get("vt",'ingen')!='Detail' or smil.get("pixi","u")!='Restauranter, pizzeriaer, kantiner m.m.' and smil["branchekode"] not in ['56.10.00.A','56.10.00.B','56.10.00.C','DD.56.10.99','00.00.02.H'] and smil["name"].find('Sushi')<0 and smil["name"].find('Brasserie')<0:
            return False
      if smil["name"].find("Pop Up")>-1:
            return False
      nm=re.search(r'\bEUC\b|\bm/s\b|båden\b|\bm/f\b|Ophørt|Pølsevogn|julebod|ejerskifte|Festvogn|mobilvogn|Street Food|\bMobil\b|udlejning\b|Seaways|mobile| Detaillager|\bgarage\b|\bcykel|Mobile|Brugsen|Psykia|Truck|Foodtruck|foodtruck|Salgsvogn|grillvogn|pølsevogn|\btruck|\bcykel|Texaco|Kommune|\bafsnit|Kursus|\bvogn|grillvogn|personalekantine|kantine\b|kantinen|fjernlager|shell|\blager|pølsevogn|Catering|hjemmet|klubben|MENY|Statoil\b|Circle K|Vogn |vognen|Produktionskøkken|Q8|køkkenet|\bOK\b|Anretterkøkken|Vaffelvogn|\bcandy|7-Eleven|\bAfd.|\bkantine|medicinsk|Sygehus|Afdeling|hospital|afdeling|Aktivitet|Bofælles|institution|plejehjem|skole\b|skolen\b|Fazer|Onkologisk|Driftsenhed|Danhostel|styrelsen|Psykiatrisk|\bselskabslokale|kirurg',smil["name"],re.IGNORECASE)
      #print("SELECTED",smil.get("vt",'ingen'),str(not nm),json.dumps(smil,indent=2))
      if nm==None:
            return True
      else:
            print("deselect ",smil["name"],"  ::",  nm.group(0),file=mlog)
            return False

def sanes(s):
      return s.replace("xxx&","og").replace("|","").replace("'","").replace("`","").replace("´","").replace('´',"").replace(",","")

def future(elm):
      if "tags" in elm and "start_date" in elm["tags"]:
            sd=elm["tags"]["start_date"].split("-")
            print("  c future ", elm['id'],json.dumps(sd,indent=2),file=mlog )
            if len(sd)==3:
                  d=date(int(sd[0]),int(sd[1]),int(sd[2]))
                  rv=datetime.today().date()<d
                  print("  r future ", smil['id'],rv, file=mlog)
                  return rv
            elif len(sd)==1:
                  if (sd[0].isdigit()):
                        d=date(int(sd[0]),6,1) # just guess on mid year
                        return (datetime.today().date()<d)
                  else:
                     print("Invalid year: ",sd[0], " for:", json.dumps(elm))
      return False

def outofseason(elm):
      month=datetime.now().month
      if month <9 and month >4:
            return False
      if "tags" in elm:
            if elm["tags"].get("access:covid19","yes")=="no":
                  return True
            if "opening_hours" in elm["tags"]:
                  hours=elm["tags"]["opening_hours"].split(" ")
                  if len(hours)>0:
                        if hours[0].lower() in ["summer","apr-oct"]:
                              print("  out of season: ", json.dumps(elm),file=mlog )
                              return hours
            if "summer" in elm["tags"].get("seasonal","").split(';'):
                  return "outofseason"
      return False

def fvstage(s):
      d=s.split(" ")[0].split("-")
      return (now-datetime(int(d[2]),int(d[1]),int(d[0]))).days


def osmage(s):
      d=s.split("T")[0].split("-")
      return (now-datetime(int(d[0]),int(d[1]),int(d[2]))).days

fvsterrfile='data/fvsterror.json'
fvsterr=open(fvsterrfile,mode="w",encoding='utf8')

with open("data/rall.json", 'r') as f:
  fvstall = json.load(f)

fvsterrlist=[]
merge_candidates=[];


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
            return sanes(o['name'])
      elif ('tags' in o and 'name' in o['tags']):
            return sanes(o['tags']['name'])
      else:
            return ""

def getamenity(o):
      if 'amenity' in o:
            return o['amenity']
      if 'tags' in o and 'amenity' in o['tags']:
            return o['tags']['amenity']
      return None


def canonicalname(nmi):
      if not nmi:
            return nmi
      nm=nmi.lower()
      nm=nm.translate(str.maketrans(u'ñèéäöúá–\'-´.,’+&"`|', 'neeæøua            '))
      splits=[ " i/s"," aps"," APS"," I/S"," Aps"," - ", " c/o", " ved", " v/"," /"]
      rpls={
            "AB":"",
            " P/S":"",
            "Gl. ":"Gammel",
            "Gl ":"Gammel",
            "&":"og",
            "å":"aa",
            ",":""
      }
      rpls1={
            "air group a/s restaurants":"",
            "pizzaria":"pizza",
            "pizzeria":"pizza",
            "pizzabar":"pizza",
            "é":"e"
      }
      for rpk,rpv in rpls.items():
            nm=nm.replace(rpk,rpv)
      for spl in splits:
            nm=nm.split(spl)[0]
      for rpk,rpv in rpls1.items():
            nm=nm.replace(rpk,rpv)
      nm=nm + ' '
      nm=re.sub('den ',' ',re.sub('( og cafe| og bar| cafe| Kro|cafe | S/I\b| v/.*| a/s|pizza bar| pizza house|og pizza| og grillbar|pizzeria |restauranten | restaurante|take out|take away| af 20|ristorante|restaurant|spisestedet |bryggeriet| house| and | grill| og cafe|s køkken| pizza|pizza |the |kafe |cafeen |cafe |hotel | spisehus| og grillbar| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| i/s| take away| ivs| aps)','',nm)).replace('/','')
      nmc=re.sub(' 2','',nm)
#      print("CANON  ",nmi, nmc.replace(' ','') , file=mlog )
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
      'cvr':res.get('cvr','miss'),
      'vt':res.get('vt','uu'),
      'lat':posob['lat'],
      'lon':posob['lon'],
      'fvst:navnelbnr':res['tags'].get('fvst:navnelbnr','')
  }
  if 'tags' in res:
      rv['alt_names']=[]
      if 'fvst:name' in res['tags']:
            rv['alt_names'].append(canonicalname(res['tags']['fvst:name']))
      for ex in ["brand","branch"]:
            if ex in res['tags']:
                  rv['alt_names'].append(canonicalname(nm+res['tags'][ex]))

  return rv

smilinfo={}
fvst={} # holds OSM object with a fvst:navnelbnr tag
osminfo={} # holds OSM restaurants, cafes, fast_food, etc, by name
osminfo_by_pos={} # holds OSM restaurants, cafes, fast_food, etc by position
allfix={"match":[],"miss":[],"gone":[],"info":"missing and matching restaurants"}
# holds matches based on name and location, i.e. FVST objects already in OSM, but without fvst:navnelbnr tag

for res in list(osmdata['elements']):
    if res['type'] in ['way','node','relation'] and getname(res):
      cn=canonical(res)
      if (cn['name'] not in osminfo):
            osminfo[cn['name']]=[]
      osminfo[cn['name']].append(cn)
      osminfo_by_pos["p"+str(cn['lat'])+","+str(cn['lon'])]=cn
      if 'alt_names' in cn:
            for an in cn['alt_names']:
                  if (an not in osminfo):
                        osminfo[an]=[]
                        osminfo[an].append(cn)
      if 'tags' in res and 'fvst:navnelbnr' in res['tags']:
          fvst[res['tags']['fvst:navnelbnr']]=res
print("\n\nOSMINFO ", json.dumps(osminfo,indent=2), file=mlog )
fvstfullfile='data/rfull.json';
smilresfull=open(fvstfullfile,"r",encoding='utf-8').read()
smf = json.loads(smilresfull)['elements']
fixed='data/fixed.json'
if os.path.isfile(fixed):
      try:
            fixeddata=json.loads(open(fixed,'r', encoding='utf-8').read())['elements']
      except json.decoder.JSONDecodeError as e:
            fixeddata=[]
else:
     fixeddata=[]

smildatafull=fixeddata+smf
print(str(len(fixeddata))+" fixed "+str(len(smf))+" from fvst, now in smildata: "+ str(len(smildatafull)))
for smil in smildatafull:
  osmlbnr.append(str(smil['id']))
for smil in smildatafull:
    if smil['id'] == 'dummy':
        break
    cn=canonicalname(getname(smil))
    if (cn not in smilinfo):
        smilinfo[cn]=[]
    smil['name']=getname(smil)
    smil['tags']['name']=smil['name']
    smilinfo[cn].append(smil)
    print("do smil ", cn,smil['id'],smil.get('cvr','NOCVR'), file=mlog )
    found=False
    if str(smil['id']) in fvst:
          print(" in fvst ", cn,smil['id'], " osmid0",fvst[str(smil['id'])]['id'], file=mlog )
          continue
    if str(smil['id']) in blacklist:
          print(" in blacklist ", cn,smil['id'], file=mlog )
          continue
    if (not smil['lat'] or not smil['lon'] or int(smil['lat']) < 54 or int(smil['lat'])> 57 or int(smil['lon'])<8 or int(smil['lon']) > 15):
          print(" missing pos: ", cn,smil['id'], file=mlog )
          isFixed=False;
          for fx in fixeddata:
                if 'fvst:navnelbnr' in smil['tags'] and fx['id']==smil['tags']['fvst:navnelbnr']:
                      isFixed=True
                      break
          if not isFixed and selected(smil):
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
                              allfix["match"].append({
                                    "fvst:navnelbnr":smil['id'],
                                    "cvr":smil.get('cvr','cvrmiss'),
                                    "category":"fvst:no_pos",
                                    "type":ores["type"],
                                    "id":ores["id"],
                                    "osm:name":sanes(ores["orgname"]),
                                    "osm:navnelbnr":olbnr,
                                    "fvst:name":smil['name'],
                                    "fvst:city":smil['city'],
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
                    else:
                          merge_candidates.append(olbnr)
                    print("   is found: ", cn,smil['id']," olbnr=",olbnr, file=mlog)
                    print("     append: ", cn,smil['id']," olbnr=",olbnr, file=mlog)
                    wp=gpxpy.gpx.GPXWaypoint(smil['lat'],smil['lon'],None,None,smil['name']+"<=>"+ores["orgname"],smil['addr'] if 'addr' in smil else 'no addr','Restaurant','join')
                    wp.extension={"color":"#ff0000"}
                    gpx.waypoints.append(wp)
                    allfix["match"].append({"fvst:navnelbnr":smil['id'],
                                  "type":ores["type"],
                                  "cvr":smil.get('cvr','CVRMISS'),
                                  "id":ores["id"],
                                  "osm:name":ores["orgname"],
                                  "osm:navnelbnr":olbnr,
                                  "fvst:name":smil['name'],
                                  "fvst:city":smil['city'],
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
            gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(smil['lat'],smil['lon'],None,None,smil['name'],smil['addr'] if 'addr' in smil else 'no addr','Restaurant','double'))
            allfix["match"].append({"fvst:navnelbnr":smil['id'],
                          "type":ores["type"],
                          "category":"exact",
                          "exact":1,
                          "id":ores["id"],
                          "osm:name":ores["orgname"],
                          "osm:navnelbnr":olbnr,
                          "fvst:name":smil['name'],
                          "fvst:city":smil['city'],
                          'lat':ores['lat'],
                          'lon':ores['lon'],
                          'osm:cvr':ores.get('cvr',''),
                          'scvr':smil.get('cvr',''),
                          'slat':smil['lat'],
                          'slon':smil['lon']
                          })
      elif selected(smil) :
        if "operator" in smil:
           smil["operator"]=sanes(smil["operator"])
        allfix['miss'].append(smil)

print("now osm not in fvst")
print("merge_candidates: ",json.dumps(merge_candidates,indent=2),file=mlog)

for osmelm in list(osmdata['elements']):
      if "tags" in osmelm and "amenity" in osmelm["tags"]:
            print("   mck ", json.dumps(osmelm),file=mlog )
            if not "fvst:navnelbnr" in osmelm["tags"] or osmelm["tags"]["fvst:navnelbnr"]=="undefined" or not (osmelm["tags"]["fvst:navnelbnr"].isnumeric() and int(osmelm["tags"]["fvst:navnelbnr"]) in fvstall):
                  age=osmage(osmelm["timestamp"])
                  if "name" in osmelm["tags"]:
                        osmelm["osm:name"]=osmelm["tags"]["name"]
                  else:
                        osmelm["osm:name"]="unnamed"
                  if (not "lat" in osmelm) and "center" in osmelm:
                        osmelm["lat"]=osmelm["center"]["lat"]
                        osmelm["lon"]=osmelm["center"]["lon"]
                  if "fvst:navnelbnr" in osmelm["tags"] and not osmelm["tags"]["fvst:navnelbnr"] in merge_candidates and not outofseason(osmelm) and not future(osmelm):
                        print("     MCK STALE ", osmelm["tags"]["fvst:navnelbnr"],file=mlog )
                        osmelm["stalefvst"]=True
                        allfix["match"].append(osmelm)
                        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(osmelm['lat'],osmelm['lon'],None,None,osmelm['osm:name'],osmelm["tags"]["amenity"],'Bell','merge'))
                  elif age>120 and not future(osmelm) and osmelm["osm:name"].find('Pølsevogn')<0 and not outofseason(osmelm) and not osmelm["tags"].get('amenity','xxx') in ['events_venue','community_centre','social_facility','clinic','hospital','marketplace']:
                        osmelm["notinfvst"]=True
                        allfix["gone"].append(osmelm)
                        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(osmelm['lat'],osmelm['lon'],None,None,osmelm['osm:name'],osmelm["tags"]["amenity"],'Bell','notinFvst'))
                  #else:
                      #  print("keep",osmelm["osm:name"], "ts=",osmelm["timestamp"], "age: ",age,"days")
print("there was ",len(allfix["gone"]),"not in fvst")
print(json.dumps(fvsterrlist,indent=2,ensure_ascii=False),file=fvsterr)

nids=[]
nidslot={}
for osmelm in allfix["match"]:
  if 'stalefvst' in osmelm or "notinfvst" in osmelm:
    nid= osmelm["type"][0].upper()+ str(osmelm["id"])
    nids.append(nid)
    nidslot[nid]= osmelm
staleaddresses=[]
maxids=30
nid=0

while nid < len(nids):
      nidargs=",".join(nids[nid:nid+maxids])
#      print("args=",nidargs)
      nourl="https://nominatim.openstreetmap.org/lookup/?format=json&osm_ids="+nidargs
      try:
            stalef = urllib.request.urlopen(nourl)
            staleaddresses+=json.loads(stalef.read().decode('utf8'))
      except urllib.error.HTTPError as e:
            print(e,nourl)
      nid+=maxids
      sleep(1)

for staleaddress in staleaddresses:
      id=staleaddress["osm_type"][0].upper()+str(staleaddress["osm_id"])
      addr=nidslot[id]
      addr['stale_address']=staleaddress["address"]

fixfile=open('data/all.json',mode="w",encoding='utf-8')
print(json.dumps(allfix,indent=2),file=fixfile)
gpxfile=open('data/all.gpx',mode="w",encoding='utf-8')
print(gpx.to_xml("1.1"),file=gpxfile)

print('misses: ',str(len(allfix["miss"])))
print('matches: ',str(len(allfix["match"])))
print('gone: ',str(len(allfix["gone"])))
