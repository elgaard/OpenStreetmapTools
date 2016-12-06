import json
from pprint import pprint
import re
import string
import sys

fullmatch=False;
fvstfile='data/r.json';
fvsterrfile='data/fvsterror.json';
fvsterr=open(fvsterrfile,mode="w")
fvsterrlist=[]

if (len(sys.argv)>1 and sys.argv[1]=="match"):
      fullmatch=True
      fvstfile='data/rfull.json'
      print("fullmatch")

blacklist=json.loads(open('blacklist.json','r', encoding='utf-8').read())['blacklist']

osmres=open('data/osmres.json',"r",encoding='utf-8').read()
osmdata = json.loads(osmres)
osmlbnr=[]

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
fixeddata=json.loads(open(fixed,'r', encoding='utf-8').read())['elements']

smildata=fixeddata+smf
#smildata=fixeddata
print(str(len(fixeddata))+" fixed "+str(len(smf))+" from fvst, now in smildata: "+ str(len(smildata)))

missingItems={'elements':[],'info':'missing restaurants'}
for smil in smildata:
  osmlbnr.append(str(smil['id']));
#  print(str(smil['id']))

# print(json.dumps(osmlbnr,indent=2))

      
for smil in smildata:
    if smil['id'] == 'dummy':
        break
    cn=canonicalname(getname(smil))
    if (cn not in smilinfo):
        smilinfo[cn]=[]
    smil['name']=getname(smil).replace("`","").replace("|","").replace(",","").replace("'","")
    smilinfo[cn].append(smil)
    found=False
    if str(smil['id']) in fvst:
          continue
    if str(smil['id']) in blacklist:
          continue
#    print("cn "+cn)
    if (not smil['lat'] or not smil['lon'] or int(smil['lat']) < 54 or int(smil['lat'])> 57 or int(smil['lon'])<8 or int(smil['lon']) > 15):
          fvsterrlist.append(smil)
    if cn!='':
          if cn in osminfo:
            # print("tze "+cn+" "+str(smil['lat'])+","+str(smil['lon']))
            if (smil['lat']==0.0 or smil['lon']==0.0):
                  # print("ze "+cn)
                  if (len(osminfo[cn])==1): # there is only one global match, so we go with it
                        ores=osminfo[cn][0]
                        olbnr=ores["fvst:navnelbnr"]
                        if (not "fvst:navnelbnr" in ores or ores["fvst:navnelbnr"]=="" or not ores["fvst:navnelbnr"] in osmlbnr):
                              # FIXME TODO, also only if ores["fvst:navnelbnr"] still exists in FVST
                              found=True
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
              for ores in osminfo[cn]:
                d = (smil['lat']-ores['lat'])*(smil['lat']-ores['lat'])+(smil['lon']-ores['lon'])*(smil['lon']-ores['lon'])
                if (d<0.000005 or 'fvst:fixme' in ores):
                    found=True
                    olbnr=ores["fvst:navnelbnr"]
                    if (olbnr and not (olbnr in osmlbnr)):
                          olbnr=""
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
print(json.dumps(fvsterrlist,indent=2,ensure_ascii=True),file=fvsterr)

#print(out)
if fullmatch:
      matchfile=open('data/match.json',mode="w")
      print(json.dumps(match,indent=2),file=matchfile)
else:
      missing=open('data/miss.json',mode="w")
      print(json.dumps(missingItems,indent=2),file=missing)
