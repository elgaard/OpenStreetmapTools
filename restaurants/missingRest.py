import json
from pprint import pprint
import re
import string
import sys

fullmatch=False;
fvstfile='data/r.json';
fvsterrfile='data/fvsterror.txt';
fvsterr=open(fvsterrfile,mode="w")

if (len(sys.argv)>1 and sys.argv[1]=="match"):
      fullmatch=True
#      fvstfile='data/rfull.json'
      print("fullmatch")

blacklist=json.loads(open('blacklist.json').read())['blacklist']

osmres=open('data/osmres.json').read()
osmdata = json.loads(osmres)
osmlbnr=[]


def canonicalname(nm):
      if not nm:
            return nm
      nm0=nm.replace(" AB","").replace(" P/S","").replace("Gl ","Gammel ")

      nm1=nm0.split(" - ")[0].split(" ApS")[0].lower().replace('air group a/s restaurants,','').replace("&","og").replace("å","aa").split(" v. ")[0].split(" v/")[0].split(" /")[0].split(" -")[0].split(" i/s")[0].split(" aps")[0].split(" ved ")[0].split(" c/o")[0].translate(str.maketrans(u'ñèéäöúá–\'-´.,’+&"`|', 'neeæøua            ')) +' '
      nm2=nm1.replace('pizzeria','pizza').replace('pizzaria','pizza').replace('pizzabar','pizza').replace('pizza bar','pizza')
      nm3=re.sub('/v.*',' ',re.sub('den ',' ',re.sub('( og cafe| og bar|cafe | Kro|Café| v/.*| a/s|pizza bar| pizza house|og pizza| og grillbar|pizzeria |restauranten | restaurante|take out|take away| af 20|ristorante|restaurant|spisestedet |bryggeriet| house| and | grill| og cafe|s køkken| pizza|pizza |the |kafe |cafeen |cafe |hotel | spisehus| og grillbar| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| I/S| take away| IVS| aps| ApS)','',nm2))).replace('/','')
      nmc=re.sub(' 2','',nm3)
      return nmc.replace(' ','')

def canonical(res):
  nm='UNDEFINED'
  nm=canonicalname(res['tags']['name'])
  posob=res
  if 'center' in res:
        posob=res['center']
  rv={'id': res['id'],
      'name':nm,
      'orgname':res['tags']['name'],
      'type':res['type'],
      'lat':posob['lat'],
      'lon':posob['lon'],
      'fvst:navnelbnr':res['tags'].get('fvst:navnelbnr','')
  }
  if 'fvst:name' in res['tags']:
        rv['fvstname']=canonicalname(res['tags']['fvst:name'])
  return rv 

smilinfo={}
fvst={} # holds OSM object with a fvst:navnelbnr tag
osminfo={} # holds OSM restaurants, cafes, fast_food, etc
osminfo_by_pos={} # holds OSM restaurants, cafes, fast_food, etc by position
match=[] # holds matches based on name and location, i.e. FVST objects already in OSM, but without fvst:navnelbnr tag

for res in list(osmdata['elements']):
    if res['type'] in ['way','node','relation'] and 'tags' in res and 'name' in res['tags']:
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
            
smilres=open(fvstfile).read()
smildata = json.loads(smilres)['elements']

missingItems={'elements':[],'info':'missing restaurants'}
for smil in smildata:
  osmlbnr.append(str(smil['id']));
#  print(str(smil['id']))

#print(json.dumps(osmlbnr,indent=2))

      
for smil in smildata:
    fvsttags=smil['tags']
    if smil['id'] == 'dummy':
        break
    cn=canonicalname(fvsttags['name'])
    if (cn not in smilinfo):
        smilinfo[cn]=[]
    fvsttags['name']=fvsttags['name'].replace("`","").replace("|","").replace(",","").replace("'","")
    smilinfo[cn].append(smil)
    found=False
    if str(smil['id']) in fvst:
          continue
    if str(smil['id']) in blacklist:
          continue
#    print("cn "+cn)
    if (not smil['lat'] or not smil['lon'] or int(smil['lat']) < 54 or int(smil['lat'])> 57 or int(smil['lon'])<8 or int(smil['lon']) > 15):
          print(json.dumps(smil,indent=2,ensure_ascii=False),file=fvsterr)
    if cn!='':
          if cn in osminfo:
            # print("tze "+cn+" "+str(smil['lat'])+","+str(smil['lon']))
            if (smil['lat']==0.0 or smil['lon']==0.0):
                  # print("ze "+cn)
                  if (len(osminfo[cn])==1): # there is only one global match, so we go with it
                        ores=osminfo[cn][0]
                        olbnr=ores["fvst:navnelbnr"]
                        if (not "fvst:navnelbnr" in ores or ores["fvst:navnelbnr"]==""):
                              # FIXME TODO, also only if ores["fvst:navnelbnr"] still exists in FVST
                              found=True
                              match.append({"fvst:navnelbnr":smil['id'],
                                      "category":"fvst:no_pos",
                                      "type":ores["type"],
                                      "id":ores["id"],
                                      "osm:name":ores["orgname"],
                                      "osm:navnelbnr":olbnr,
                                      "fvst:name":fvsttags['name'],
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
                                  "fvst:name":fvsttags['name'],
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
                          "fvst:name":fvsttags['name'],
                          'lat':ores['lat'],
                          'lon':ores['lon'],
                          'slat':smil['lat'],
                          'slon':smil['lon']
                          })
      else:
        missingItems['elements'].append(smil)

#print(out)
if fullmatch:
      matchfile=open('data/match.json',mode="w")
      print(json.dumps(match,indent=2),file=matchfile)
else:
      missing=open('data/miss.json',mode="w")
      print(json.dumps(missingItems,indent=2),file=missing)
