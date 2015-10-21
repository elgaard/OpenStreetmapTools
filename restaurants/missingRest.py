import json
from pprint import pprint
import re
import string
blacklist=json.loads(open('blacklist.json').read())['blacklist']

osmres=open('data/osmres.json').read()
osmdata = json.loads(osmres)


def canonicalname(nm):
      nm1=nm.lower().translate(str.maketrans(u'éäö–\'-´.,’+&"', 'eæø          ')) +' '
      nm2=nm1.replace('pizzaria','pizza')
      nm3=re.sub('/v.*',' ',re.sub('den ',' ',re.sub('(cafe |i/s|v/.*| a/s|pizzeria |restaurant|bryggeriet| house| and | pizza |the |kafe |cafe |hotel| spisehus| og grillbar| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| take away| aps)','',nm2))).replace('/','')
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
          'lat':posob['lat'],
          'lon':posob['lon'],
          'fvst:navnelbnr':res['tags'].get('fvst:navnelbnr','')
  }

smilinfo={}
fvst={}
osminfo={}
for res in list(osmdata['elements']):
    if res['type'] in ['way','node','relation'] and 'tags' in res and 'name' in res['tags']:
      cn=canonical(res)
      if (cn['name'] not in osminfo):
        osminfo[cn['name']]=[]
      osminfo[cn['name']].append(cn)
      if 'fvst:navnelbnr' in res['tags']:
            fvst[res['tags']['fvst:navnelbnr']]=res
            
smilres=open('data/r.json').read()
smildata = json.loads(smilres)['elements']
out={'elements':[],'info':'missing restaurants'}

for smil in smildata:
    tags=smil['tags']
    if smil['id'] == 'dummy':
        break
    cn=canonicalname(tags['name'])
    if (cn not in smilinfo):
        smilinfo[cn]=[]
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
    if not found:
        out['elements'].append(smil)

#print(out)
print(json.dumps(out,indent=2))
