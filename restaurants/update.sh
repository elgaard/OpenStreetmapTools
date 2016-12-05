#!/bin/bash


git pull
#  area["name"="Denmark"]->.sa;\
# {{geocodeArea:\"Denmark\"}}->.sa;\
q="[timeout:600] [out:json];\
( \
  area(3600050046)->.sa;\
  node["amenity"="restaurant"](area.sa);\
  node["amenity"="kitchen"](area.sa);\
  way["amenity"="restaurant"](area.sa);\
  node["amenity"="hospital"](area.sa);\
  node["amenity"="clinic"](area.sa);\
  node["amenity"="events_venue"](area.sa);\
  node["amenity"="cafe"](area.sa);\
  way["amenity"="cafe"](area.sa);\
  node["amenity"="fast_food"](area.sa);\
  way["amenity"="fast_food"](area.sa);\
  node["amenity"="bar"](area.sa);\
  way["amenity"="bar"](area.sa);\
  node["amenity"="pub"](area.sa);\
  node["shop"="farm"](area.sa);\
  node["shop"="butcher"](area.sa);\
  node["shop"="craft"](area.sa);\
  node["shop"="kiosk"](area.sa);\
  node["amenity"="pub"](area.sa);\
  way["tourism"="hotel"](area.sa);\
  node["tourism"="hotel"](area.sa);\
  node["tourism"="museum"](area.sa);\
  way["tourism"="hotel"](area.sa);\
  way["leisure"="golf_course"](area.sa);\
  node["tourism"="guest_house"](area.sa);\
  way["tourism"="guest_house"](area.sa);\
  node["tourism"="hostel"](area.sa);\
  way["tourism"="hostel"](area.sa);\
  node[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
  way[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
  relation[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
);\
(._;>;);\
out center;\
>;"

#printf "$q"

if [[ x$1 != "xskiposm" ]] ; then
    echo get osm data
    curl -G --silent --data-urlencode  "data=$q" http://overpass-api.de/api/interpreter > data/osmres.json
fi

echo get kontrolresultater
## http://www.findsmiley.dk/xml/allekontrolresultater.xml
cp data/allekontrolresultater.xml data/allekontrolresultater.xml.bu$(date "+%d")7
if wget -O data/allekontrolresultater.xml --timeout 40 --quiet --timestamping  https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml; then
    echo got kontrolresultater
    xsltproc smilres.xslt data/allekontrolresultater.xml > data/r.json
    xsltproc smilresfull.xslt data/allekontrolresultater.xml > data/rfull.json
fi
echo find matches and misses
python3 missingRest.py match
python3 missingRest.py

echo misses; grep amenity data/miss.json |wc
echo matches; grep osm:name data/match.json |wc
echo errors; grep tags data/fvsterror.json |wc
