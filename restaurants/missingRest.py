import json
from pprint import pprint
import re
import string
blacklist=json.loads(open('blacklist.json').read())['blacklist']

osmres=open('data/osmres.json').read()
osmdata = json.loads(osmres)
missing=open('data/miss.json',mode="w")
matchfile=open('data/match.json',mode="w")


def canonicalname(nm):
      nm1=nm.lower().translate(str.maketrans(u'éäö–\'-´.,’+&"`', 'eæø           ')) +' '
      nm2=nm1.replace('pizzaria','pizza')
      nm3=re.sub('/v.*',' ',re.sub('den ',' ',re.sub('(cafe |i/s|v/.*| a/s|pizzeria |ristorante|restaurant|bryggeriet| house| and | pizza |the |kafe |cafe |hotel| spisehus| og grillbar| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| take away| aps|ApS)','',nm2))).replace('/','')
      nmc=re.sub(' 2','',nm3)
#      print('xx  '+nmc)
      return nmc.replace(' ','')

def canonical(res):
  nm='UNDEFINED'
  nm=canonicalname(res['tags']['name'])
  posob=res
  if 'center' in res:
        posob=res['center']
  return {'id': res['id'],
          'name':nm,
          'orgname':res['tags']['name'],
          'lat':posob['lat'],
          'lon':posob['lon'],
          'fvst:navnelbnr':res['tags'].get('fvst:navnelbnr','')
  }

smilinfo={} #holds all FVST objects, not used yet
fvst={} # holds OSM object with a fvst:navnelbnr tag
osminfo={} # holds OSM restaurants, cafes, fast_food, etc
match=[] # holds matches based on name and location, i.e. FVST objects already in OSM, but without fvst:navnelbnr tag

for res in list(osmdata['elements']):
    if res['type'] in ['way','node','relation'] and 'tags' in res and 'name' in res['tags']:
      cn=canonical(res)
      if (cn['name'] not in osminfo):
        osminfo[cn['name']]=[]
      osminfo[cn['name']].append(cn)
    if 'tags' in res and 'fvst:navnelbnr' in res['tags']:
          fvst[res['tags']['fvst:navnelbnr']]=res
            
smilres=open('data/r.json').read()
smildata = json.loads(smilres)['elements']
out={'elements':[],'info':'missing restaurants'}

for smil in smildata:
    fvsttags=smil['tags']
    if smil['id'] == 'dummy':
        break
    cn=canonicalname(fvsttags['name'])
    if (cn not in smilinfo):
        smilinfo[cn]=[]
    fvsttags['name']=fvsttags['name'].replace("`","")
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
                    match.append({"fvst:navnelbnr":smil['id'], "id":ores["id"], "osm:name":ores["orgname"],"fvst:name":fvsttags['name']})
    if not found:
        out['elements'].append(smil)

#print(out)
print(json.dumps(out,indent=2),file=missing)
print(json.dumps(match,indent=2),file=matchfile)
