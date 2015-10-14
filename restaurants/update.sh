#!/bin/sh -x
#xalan -text -in data/allekontrolresultater.xml -out data/r.json -xsl smilres.xslt


wget -O allekontrolresultater.xml http://www.findsmiley.dk/xml/allekontrolresultater.xml
saxon-xslt  data/allekontrolresultater.xml  smilres.xslt > data/r.json
