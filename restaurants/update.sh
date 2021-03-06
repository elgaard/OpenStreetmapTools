#!/bin/bash
#  area["name"="Denmark"]->.sa;\
# {{geocodeArea:\"Denmark\"}}->.sa;\
q="[timeout:1600] [out:json];\
( \
  area(3600050046)->.sa;\
  nwr["amenity"="restaurant"](area.sa);\
  nwr["amenity"="ice_cream"](area.sa);\
  nwr["amenity"="community_centre"](area.sa);\
  nwr["amenity"="kitchen"](area.sa);\
  nwr["amenity"="hospital"](area.sa);\
  nwr["amenity"="clinic"](area.sa);\
  nwr["amenity"="pharmacy"](area.sa);\
  nwr["amenity"="events_venue"](area.sa);\
  nwr["amenity"="cafe"](area.sa);\
  nwr["amenity"="fast_food"](area.sa);\
  nwr["amenity"="bar"](area.sa);\
  nwr["amenity"="pub"](area.sa);\
  nwr["amenity"="cinema"](area.sa);\
  nwr["amenity"="smokehouse"](area.sa);\
  nwr["shop"="farm"](area.sa);\
  nwr["shop"="craft"]["craft"="catering"](area.sa);\
  nwr["shop"="butcher"](area.sa);\
  nwr["shop"="bakery"](area.sa);\
  nwr["shop"="craft"](area.sa);\
  nwr["shop"="kiosk"](area.sa);\
  nwr["shop"="electronics"](area.sa);\
  nwr["shop"="bicycle"](area.sa);\
  nwr["shop"="clothes"](area.sa);\
  nwr["shop"="alcohol"](area.sa);\
  nwr["shop"="wine"](area.sa);\
  nwr["shop"="supermarket"](area.sa);\
  nwr["shop"="garden_centre"](area.sa);\
  nwr["shop"="party"](area.sa);\
  nwr["shop"="nutrition_supplements"](area.sa);\
  nwr["shop"="convenience"](area.sa);\
  nwr["shop"="confectionery"](area.sa);\
  nwr["shop"="cheese"](area.sa);\
  nwr["shop"="chemist"](area.sa);\
  nwr["department"~\".\"](area.sa);\
  nwr["shop"="doityourself"](area.sa);\
  nwr["amenity"="pub"](area.sa);\
  nwr["amenity"="fuel"](area.sa);\
  nwr["leisure"="golf_course"](area.sa);\
  nwr["leisure"="fitness_centre"](area.sa);\
  nwr["leisure"="water_park"](area.sa);\
  nwr["tourism"="hotel"](area.sa);\
  nwr["tourism"="zoo"](area.sa);\
  nw["tourism"="museum"](area.sa);\
  nwr["tourism"="guest_house"](area.sa);\
  nwr["tourism"="camp_site"](area.sa);\
  nwr["tourism"="hostel"](area.sa);\
  node[\"fvst:navnelbnr\" ~ \".\"]( 54.395, 3.853, 57.8321, 16.9097 );\
  way[\"fvst:navnelbnr\" ~ \".\"]( 54.395, 3.853, 57.8321, 16.9097 );\
  relation[\"fvst:navnelbnr\" ~ \".\"](area.sa);\
);\
out center meta;\
"

#echo "$q"

if [[ x$1 != "xskiposm" && x$2 != "xskiposm" ]] ; then
    echo get osm data
    curl -G --silent --data-urlencode  "data=$q" http://overpass-api.de/api/interpreter > data/osmres.json
fi

echo get kontrolresultater
## http://www.findsmiley.dk/xml/allekontrolresultater.xml
buf=data/allekontrolresultater.xml.bu$(date "+%d")
cp data/allekontrolresultater.xml $buf
gzip -f $buf
if wget -O data/allekontrolresultater.xml --timeout 40 --quiet --timestamping  https://www.foedevarestyrelsen.dk/_layouts/15/sdata/smiley_xml.xml; then
    echo got kontrolresultater
#    xsltproc smilres.xslt data/allekontrolresultater.xml | sed -e "s/\t/ /" | sed -e 's/\\//'> data/r.json
    xsltproc smilresfull.xslt data/allekontrolresultater.xml | sed -e "s/\t/ /" | sed -e 's/\\//' > data/rfull.json
    xsltproc smilresno.xslt data/allekontrolresultater.xml | sed -e "s/\t/ /" | sed -e 's/\\//' > data/rall.json
else
    echo did not get kontrolresultater
fi
echo find matches and misses
python3 missingRest.py

if [[ x$1 != "xskipaddr" && x$2 != "xskipaddr" ]] ; then
  echo look up addrs
  ./addressLookup.py all > addr.log
fi
tail -3 addr.log
