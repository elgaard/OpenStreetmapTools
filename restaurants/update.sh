#!/bin/sh -x
BBOX="(54.54020652089137,8.009033203125,57.76279865944121,12.81005859375)"
#undskyld Bornholm

q="[timeout:120] [out:json];\
( \
  node["amenity"="restaurant"]$BBOX;\
  way["amenity"="restaurant"]$BBOX;\
  node["amenity"="cafe"]$BBOX;\
  way["amenity"="cafe"]$BBOX;\
  node["amenity"="fast_food"]$BBOX;\
  way["amenity"="fast_food"]$BBOX;\
  node["amenity"="bar"]$BBOX;\
  way["amenity"="bar"]$BBOX;\
  node["amenity"="pub"]$BBOX;\
  node["shop"="farm"]$BBOX;\
  node["shop"="butcher"]$BBOX;\
  node["amenity"="pub"]$BBOX;\
  node[\"fvst:navnelbnr\" ~ \".\"]$BBOX;\
);\
(._;>;);\
out center;\
>;"

printf "$q"

cd data
curl -G --data-urlencode  "data=$q" http://overpass-api.de/api/interpreter > osmres.json
wget --timestamping  http://www.findsmiley.dk/xml/allekontrolresultater.xml
xsltproc ../smilres.xslt allekontrolresultater.xml > r.json
cd ..
python3 missingRest.py > data/miss.json

