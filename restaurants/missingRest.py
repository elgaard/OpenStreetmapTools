import json
from pprint import pprint
import re
import string
import sys
import os
from datetime import datetime,date
import urllib.request
import urllib.error
from time import sleep
import gpxpy
import gpxpy.gpx
from collections import defaultdict
import pprint
now=datetime.now()
mlog=open("missing.log",encoding='utf-8',mode="w")
pp = pprint.PrettyPrinter(indent=2)
foodshops=["butcher","bakery","wine","alcohol","cheese"]

gpx = gpxpy.gpx.GPX()
#gpx_miss = gpxpy.gpx.GPXTrack()
#gpx.tracks.append(gpx_miss)

if os.path.isfile("data/addrcache.json"):
      addrcache=defaultdict(dict,json.loads(open("data/addrcache.json",'r', encoding='utf-8').read()))
else:
      addrcache=defaultdict(dict)


brancher={
      'servering':'DD.56.30.99',
      'restaurant':'DD.56.10.99',
      'vin':'DD.47.25.00',
      'dagligvarer':'DD.47.10.99',
      'bager':'DD.10.71.20',
      'hospital':'DD.56.10.00',
      'slagter':'DD.47.22.00',
      'slagterE':'EB.10.10.99',
      'kødE':'EB.10.10.13',
      'fiskehandel':'47.23.00',
      'ost':'47.29.00',
      'drikE':'EB.11.00.00',
      'chokolade': '47.24.00',
      'deli':"DD.47.20.99",
      'nyRest':'00.00.02.L',
      'ikketildelt':'00.00.02.E',
      'ny':'00.00.02.H',
      'dtransport':'DD.49.41.00',
      'etransport':'EE.49.41.00',
      'emballage':'EE.46.40.99',
      'emb':'EB.20.16.99',
      'hospk':'DD.56.29.00',
      'lager':'DE.46.39.99',
      'lageru':'EE.46.30.99',
      'lagerg':'EE.46.30.88',
      'lagergu':'EB.52.10.99',
      'kontor':'EE.46.17.00',
      'kæde':'EE.70.10.10',
      'animE':'EB.20.59.99',
      'keramik':'DD.47.50.99'
}

def selected(smil):
      if not (smil["branchekode"] in [brancher["restaurant"],brancher["servering"],brancher["dagligvarer"],brancher["slagter"],brancher["bager"],brancher["deli"],brancher["nyRest"],brancher["ost"]] and smil.get("vt",'ingen')=='Detail') and smil["name"].find('Sushi')<0 and smil["name"].find('Brasserie')<0:
            return False
      if  not smil.get("senestekontrol","") or (datetime.today()-datetime.strptime(smil["senestekontrol"].split(" ")[0],'%d-%m-%Y')).days>365*4:
            print("  very old senestekontrol",smil["name"],file=mlog)
            return False
      if not smil["cvr"] and (not smil.get("senestekontrol","") or (datetime.today()-datetime.strptime(smil["senestekontrol"].split(" ")[0],'%d-%m-%Y')).days>365*2):
            print("  no cvr and old senestekontrol",smil["name"],file=mlog)
            return False
      if re.search(r"\bpop[ -]?(up|op)\b",smil["name"],re.IGNORECASE):
            print("  nosel popup",smil["name"],file=mlog)
            return False
      nm=re.search(r'\bEUC\b|\bm/s\b|^bM/F\b|\bturistbåd|færgen\b|båden\b|^m\/f\b|Ophørt|Pølsevogn|julebod|ejerskifte|Festvogn|mobilvogn|Street Food|\bMobil\b|udlejning\b|Seaways|mobile| Detaillager|\bgarage\b|\bcykel|Mobile|Brugsen|Psykia|Truck|Foodtruck|foodtruck|Salgsvogn|grillvogn|pølsevogn|\btruck|\bcykel|Texaco|Kommune|\bafsnit|Kursus|\bvogn|grillvogn|personalekantine|kantine\b|kantinen|fjernlager|shell|\blager|pølsevogn|Catering|hjemmet|klubben|MENY|Statoil\b|Circle K|Vogn |vognen|Produktionskøkken|Q8|køkkenet|\bOK\b|Anretterkøkken|Vaffelvogn|\bcandy|7-Eleven|\bAfd.|\bkantine|medicinsk|Sygehus|Afdeling|hospital|afdeling|Aktivitet|Bofælles|institution|plejehjem|skole\b|skolen\b|Fazer|Onkologisk|Driftsenhed|Danhostel|styrelsen|Psykiatrisk|\bselskabslokale|kirurg',smil["name"],re.IGNORECASE)
      #print("SELECTED",smil.get("vt",'ingen'),str(not nm),json.dumps(smil,indent=2))
      if nm==None:
            return True
      else:
            print("deselect ",smil["name"],"  ::",  nm.group(0),file=mlog)
            return False

def sanes(s):
      sn=s.replace("xxx&","og").replace("|","").replace("'","").replace("`","").replace("´","").replace('´',"").replace(",","")
      sn=re.sub(r"\b(butik|Butik) \d\d\d\b","",sn)
      sn=re.sub(r"\b(Aldi B\d\d\b)","Aldi",sn)
      sn=re.sub(r"\b(Aldi B\d\d\b)","Aldi",sn)
      sn=re.sub(r"\b(Fakta \d\d\d\b)","Bilka",sn)
      sn=re.sub(r"\b(ALDI B\d\d\b)","Aldi",sn)
      sn=re.sub(r"([^aA]) \d\d\d\d\b",r"\1",sn)
      sn=re.sub(r"\d\d\d\d\d\b",r"",sn)
      return sn

def checked(elm):
      if "tags" in elm:
         if "check:date" in elm["tags"]:
               elm["tags"]["check_date"]=elm["tags"]["check:date"]
         if "check_date" in elm["tags"]:
            print("CHECKDATE",elm.get("osm:name","nn"),elm["tags"]["check_date"],file=mlog)
            sd=elm["tags"]["check_date"].split("-")
            if len(sd)==3:
                  d=date(int(sd[0]),int(sd[1]),int(sd[2]))
                  cdiff=datetime.today().date()-d
                  print("  checkdate diff ",elm.get("osm:name","NN"), elm['id'], str(cdiff.days), file=mlog)
                  return cdiff.days<180
      return False

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
      if "tags" in elm:
            if elm["tags"].get("access:covid19","yes") in ["private","no"]:
                  return True
            if month <9 and month >4:
                  return False
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


with open("data/rall.json", 'r') as f:
  fvstall = json.load(f)

fvsterrlist=[]
merge_candidates=[];
blacklist=json.loads(open('blacklist.json','r', encoding='utf-8').read())['blacklist']
osmres=open('data/osmres.json',"r",encoding='utf-8').read()
osmdata = json.loads(osmres)
osmlbnr=[]
handled=[]

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
            "pizza bar":"pizza",
            "sct.":"sankt",
            "é":"e"
      }
      for rpk,rpv in rpls.items():
            nm=nm.replace(rpk,rpv)
      for spl in splits:
            nm=nm.split(spl)[0]
      for rpk,rpv in rpls1.items():
            nm=nm.replace(rpk,rpv)
      nm=nm + ' '
      nm=re.sub('den ',' ',re.sub(r'(\bog cafe| og bar|\bB\d\d\b|\bsupermarked\b|\b(\d\d\d\d )?dagligvarer\b|butik \d\d\d|\bcafe\b|\bkro|\bS/I\b|\bv/.*|\ba/s\b|\bs/i\b| pizza house|\bog pizza|\bog grillbar|\bpizzeria\b|forretning\b|\brestauranten\b|\brestaurante\b|\btake out\b|\btake away\b|\bristorante\b|\brestaurant\b|\bspisestedet\b|\bbryggeriet\b|\bhouse|\band\b|\bdetail\b|\bgrill\b|\bog cafe\b|s køkken|\bkøbmand$|\bpizza\b|\bthe\b|\bkafe\b|\bcafeen\b|\bhotel\b|\bspisehus\b|\bog grillbar\b|\bog\b|\bsteakhouse\b|\bkaffebar\b|\bvinbar\b|\bconditori\b|\bproduktionskøkken|\btraktørstedet|\btakeaway|\bi/s\b|\bivs\b|\baps\b)','',nm)).replace('/','')
      nm=re.sub('apoteket\b','apotek',nm)
      nmc=re.sub(' 2','',nm)
      if nmc=='':
            nmc=nm
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
      'check_date':posob.get('check_date',""),
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
#print("\n\nOSMINFO ", json.dumps(osminfo,indent=2), file=mlog )
fvstfullfile='data/rfull.json';
smilresfull=open(fvstfullfile,"r",encoding='utf-8').read()
smildatafull = json.loads(smilresfull)['elements']

for smil in smildatafull:
      if smil.get('lat',0)<1 or smil.get('lon',0) < 1:
          cachedadr=addrcache[smil["postnr"]].get(smil['addr'],'')
          if cachedadr:
             smil["lat"]=cachedadr["lat"]
             smil["lon"]=cachedadr["lon"]

#print("\n\nSMILDATAFULL ", pp.pprint(smildatafull), file=mlog )

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
          if (not smil['id'] in fvst and smil["vt"] == 'Detail' and smil["branchekode"] not in [brancher['dtransport'],brancher['ikketildelt'],brancher['ny'],brancher['etransport'],brancher['emballage'],brancher['emb'],brancher['hospk'],brancher['lager'],brancher['lageru'],brancher['lagerg'],brancher['lagergu'],brancher['kontor'],brancher['kæde'],brancher['animE'],brancher['slagterE'],brancher['kødE'],brancher['keramik']]) or selected(smil):
                fvsterrlist.append(smil)
    if cn=='':
      print("  no name:",smil['id'], file=mlog )
    else:
          if cn in osminfo:
            # print("tze "+cn+" "+str(smil['lat'])+","+str(smil['lon']))
            if smil['lat']==0.0 or smil['lon']==0.0:
              if selected(smil):
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
                                    "category":"guess_noaddr",
                                    "cvr":smil.get('cvr','cvrmiss'),
                                    "pnr":smil.get('pnr',''),
                                    "fa":smil.get('addr',''),
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
                if (d<0.000005):
                    found=True
                    olbnr=ores["fvst:navnelbnr"]
                    if (olbnr and not (olbnr in osmlbnr)):
                          olbnr=""
                    else:
                          merge_candidates.append(olbnr)
                    print("   is found: ", cn,smil['id']," olbnr=",olbnr, file=mlog)
                    print("     append: ", cn,smil['id']," olbnr=",olbnr, file=mlog)
                    if smil["senestekontrol"] and smil["vt"]=="Detail":
                          wp=gpxpy.gpx.GPXWaypoint(smil['lat'],smil['lon'],None,None,smil['name']+"<=>"+ores["orgname"],smil['addr'] if 'addr' in smil else 'no addr','Restaurant','merge')
                          gpx.waypoints.append(wp)
                          allfix["match"].append({"fvst:navnelbnr":smil['id'],
                                  "type":ores["type"],
                                  "cvr":smil.get('cvr','CVRMISS'),
                                  "pnr":smil.get('pnr',''),
                                  "fa":smil.get('addr',''),
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
                    osminfo[cn].remove(ores)
                    handled.append(ores["id"])
                    break
    if not found and smil['lat']>0 and smil['lon']>0 and selected(smil):
      print(" not found: ", cn,smil['id'], file=mlog)
      pos="p"+str(smil['lat'])+","+str(smil['lon'])
      if (pos in osminfo_by_pos) and smil["senestekontrol"]:
            print("  DBL",smil['name'],smil["senestekontrol"],file=mlog)
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
      else:
        if "operator" in smil:
           smil["operator"]=sanes(smil["operator"])
        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(smil['lat'],smil['lon'],None,None,smil['name'],smil['addr'] if 'addr' in smil else 'no addr','Restaurant','new'))
        allfix['miss'].append(smil)

print("now osm not in fvst")
#print("merge_candidates: ",json.dumps(merge_candidates,indent=2),file=mlog)

for osmelm in list(osmdata['elements']):
      if "tags" in osmelm and ("amenity" in osmelm["tags"] or "shop" in osmelm["tags"]) and not osmelm["id"] in handled:
#            print("   mck ", json.dumps(osmelm),file=mlog )
            if not "fvst:navnelbnr" in osmelm["tags"] or osmelm["tags"]["fvst:navnelbnr"]=="undefined" or not (osmelm["tags"]["fvst:navnelbnr"].isnumeric() and int(osmelm["tags"]["fvst:navnelbnr"]) in fvstall):
                  age=osmage(osmelm["timestamp"])
                  if "name" in osmelm["tags"]:
                        osmelm["osm:name"]=osmelm["tags"]["name"]
                  else:
                        osmelm["osm:name"]="unnamed"
                  if (not "lat" in osmelm) and "center" in osmelm:
                        osmelm["lat"]=osmelm["center"]["lat"]
                        osmelm["lon"]=osmelm["center"]["lon"]
                  if "fvst:navnelbnr" in osmelm["tags"] and not osmelm["tags"]["fvst:navnelbnr"] in merge_candidates and not outofseason(osmelm) and not future(osmelm) and not checked(osmelm):
                        print("     MCK STALE ", osmelm["tags"]["fvst:navnelbnr"],file=mlog)
                        osmelm["stalefvst"]=True
                        allfix["match"].append(osmelm)
                        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(osmelm['lat'],osmelm['lon'],None,None,osmelm['osm:name'],osmelm["tags"].get("amenity","")+osmelm["tags"].get("shop",""),'Bell','stale'))
                  elif age>-120 and not checked(osmelm) and not future(osmelm) and osmelm["osm:name"].find('Pølsevogn')<0 and not outofseason(osmelm) and not osmelm["tags"].get('amenity','xxx') in ['events_venue','xpharmacy','community_centre','social_facility','clinic','hospital','marketplace','arts_centre','fuel','cinema'] and not osmelm["tags"].get('shop','x') in ['outpost'] and  ("shop" in osmelm["tags"] and osmelm["tags"].get("shop") in foodshops):
                        osmelm["notinfvst"]=True
                        allfix["gone"].append(osmelm)
                        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(osmelm['lat'],osmelm['lon'],None,None,osmelm['osm:name'],osmelm["tags"].get("amenity","")+osmelm["tags"].get("shop","") ,'Bell','notinFvst'))
                  #else:
                      #  print("keep",osmelm["osm:name"], "ts=",osmelm["timestamp"], "age: ",age,"days")
print("there was ",len(allfix["gone"]),"not in fvst")
fvsterrfile='data/fvsterror.json'
fvsterr=open(fvsterrfile,mode="w",encoding='utf8')
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
