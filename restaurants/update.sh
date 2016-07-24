#!/bin/bash 



#  area["name"="Denmark"]->.sa;\
# {{geocodeArea:\"Denmark\"}}->.sa;\
q="[timeout:600] [out:json];\
( \
  area(3600050046)->.sa;\
  node["amenity"="restaurant"](area.sa);\
  node["amenity"="events_venue"](area.sa);\
  way["amenity"="restaurant"](area.sa);\
  node["amenity"="cafe"](area.sa);\
  way["amenity"="cafe"](area.sa);\
  node["amenity"="fast_food"](area.sa);\
  way["amenity"="fast_food"](area.sa);\
  node["amenity"="bar"](area.sa);\
  way["amenity"="bar"](area.sa);\
  node["amenity"="pub"](area.sa);\
  node["shop"="farm"](area.sa);\
  node["shop"="butcher"](area.sa);\
  node["amenity"="pub"](area.sa);\
  node[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
  way[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
  relation[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
);\
(._;>;);\
out center;\
>;"

#printf "$q"

cd data
curl -G --silent --data-urlencode  "data=$q" http://overpass-api.de/api/interpreter > osmres.json
if wget --quiet --timestamping  http://www.findsmiley.dk/xml/allekontrolresultater.xml; then
    xsltproc ../smilres.xslt allekontrolresultater.xml > r.json
    xsltproc ../smilresfull.xslt allekontrolresultater.xml > rfull.json
fi
cd ..
python3 missingRest.py
python3 missingRest.py match

echo misses
grep amenity data/miss.json |wc
echo matches
grep osm:name data/match.json |wc
