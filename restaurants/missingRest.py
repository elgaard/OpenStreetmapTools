import json
from pprint import pprint
import re
import string
import sys

fullmatch=False;
fvstfile='data/r.json';
if (len(sys.argv)>1 and sys.argv[1]=="match"):
      fullmatch=True
      fvstfile='data/rfull.json'
      print("fullmatch")

blacklist=json.loads(open('blacklist.json').read())['blacklist']

osmres=open('data/osmres.json').read()
osmdata = json.loads(osmres)
osmlbnr=[]


def canonicalname(nm):
      if not nm:
            return nm
      nm1=nm.lower().translate(str.maketrans(u'éäö–\'-´.,’+&"`|', 'eæø            ')) +' '
      nm2=nm1.replace('pizzaria','pizza')
      nm3=re.sub('/v.*',' ',re.sub('den ',' ',re.sub('(cafe | Kro|Café|i/s| v/.*| v\. .*| a/s|pizzeria |ristorante|restaurant|bryggeriet| house| and | pizza |the |kafe |cafe |hotel| spisehus| og grillbar| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| I/S| take away| IVS| aps| ApS)','',nm2))).replace('/','')
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
  if 'fvst:name' in res:
        rv['fvstname']=canonicalname(res['tags']['fvst:name'])
  return rv 

smilinfo={}
fvst={} # holds OSM object with a fvst:navnelbnr tag
osminfo={} # holds OSM restaurants, cafes, fast_food, etc
match=[] # holds matches based on name and location, i.e. FVST objects already in OSM, but without fvst:navnelbnr tag

for res in list(osmdata['elements']):
    if res['type'] in ['way','node','relation'] and 'tags' in res and 'name' in res['tags']:
      cn=canonical(res)
      if (cn['name'] not in osminfo):
        osminfo[cn['name']]=[]
      osminfo[cn['name']].append(cn)
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
    if cn!='':
        if cn in osminfo:
            for ores in osminfo[cn]:
                d = (smil['lat']-ores['lat'])*(smil['lat']-ores['lat'])+(smil['lon']-ores['lon'])*(smil['lon']-ores['lon'])
                if (d<0.000001):
                    found=True
                    olbnr=ores["fvst:navnelbnr"]
                    if (olbnr and not (olbnr in osmlbnr)):
                          olbnr=""
                    match.append({"fvst:navnelbnr":smil['id'],
                                  "type":ores["type"],"id":ores["id"],
                                  "osm:name":ores["orgname"],
                                  "osm:navnelbnr":olbnr,
                                  "fvst:name":fvsttags['name'],
                                  'lat':ores['lat'],
                                  'lon':ores['lon'],
                                  'slat':smil['lat'],
                                  'slon':smil['lon']
                    })
    if not found:
        missingItems['elements'].append(smil)

#print(out)
if fullmatch:
      matchfile=open('data/match.json',mode="w")
      print(json.dumps(match,indent=2),file=matchfile)
else:
      missing=open('data/miss.json',mode="w")
      print(json.dumps(missingItems,indent=2),file=missing)
