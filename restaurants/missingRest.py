import json
from pprint import pprint
import re
import string
osmres=open('data/osmres.json').read()
data = json.loads(osmres)

def canonicalname(nm):
      nm1=nm.lower().translate(str.maketrans(u'éäö–\'-´.,’+&"', 'eæø          ')) +' '
      nm2=nm1.replace('pizzaria','pizza')
      nmc=re.sub('/v.*',' ',re.sub('den ',' ',re.sub('(cafe |i/s|v/.*| a/s|pizzeria |restaurant| pizza |the |kafe |cafe |hotel| spisehus| og |steakhouse | kaffebar| vinbar| conditori|produktionskøkken|traktørstedet| takeaway| aps)','',nm2))).replace('/','')
#      print('xx  '+nmc)
      return nmc.replace(' ','')
def canonical(res):
  nm='UNDEFINED'
  if 'name' in res['properties']:
      nm=canonicalname(res['properties']['name'])
  if (res['geometry']['type']=='Point'):
    cn=res['geometry']['coordinates']
  else:
    cn=res['geometry']['coordinates'][0][0]
  return {'id': res['id'],
          'name':nm,
          'lat':cn[1],
          'lon':cn[0],
  }

smilinfo={}
osminfo={}
for res in list(data['features']):
    cn=canonical(res)
    if (cn['name'] not in osminfo):
        osminfo[cn['name']]=[]
    osminfo[cn['name']].append(cn)

smilres=open('data/r.json').read()
smildata = json.loads(smilres)['elements']
out={'elements':[]}

for smil in smildata:
    tags=smil['tags']
    cn=canonicalname(tags['name'])
    if smil['id'] == 'dummy':
        break
    if (cn not in smilinfo):
        smilinfo[cn]=[]
    smilinfo[cn].append(smil)
    found=False
    if cn!='':
        if cn in osminfo:
            for ores in osminfo[cn]:
                d = (smil['lat']-ores['lat'])*(smil['lat']-ores['lat'])+(smil['lon']-ores['lon'])*(smil['lon']-ores['lon'])
                # print('diff= (%7f,%7f)-(%7f,%7f)' %(smil['lat'],smil['lon'],ores['lat'],ores['lon']))
                # print('XXmatch '+tags['name']+' d=%5f cn=%s' % (d,cn))
                # print('d== %6f' %(d))
                if (d<0.000001):
                    found=True
    if not found:
        out['elements'].append(smil)

print(json.dumps(out))
