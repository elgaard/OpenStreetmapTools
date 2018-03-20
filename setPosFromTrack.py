#!/usr/bin/env python2
import sys
import argparse
import glob
import gzip
import time
from pexif import JpegFile
from datetime import datetime

trackf = gzip.open("track.txt.gz", 'rt')
trackf.readline()

def ipol(tr1,tr2,t,l):
    return tr1[l]+(tr2[l]-tr1[l])*(t-tr1['t'])/(tr2['t']-tr1['t'])
    
tracks=[]
for line in trackf.readlines():
    ls=line.split(";")
    if (line!="DONE" and ls[1] and ls[2]):
        t=ls[0]
        lon=ls[1]
        lat=ls[2]
        d=ls[3]
        tracks.append({'t':float(t),'lat':float(lat),'lon':float(lon),'heading':float(ls[3])})

print("start\n")
for fn in glob.glob("*.jpg"):
#    print("do",fn,"\n")

    ef = JpegFile.fromFile(fn)
    primary = ef.get_exif().get_primary()

    print(primary.DateTime)
    dt=datetime.strptime(primary.DateTime,"%Y:%m:%d %H:%M:%S")
#python 3 .timestamp()

    t=time.mktime(dt.timetuple())

    trp=None
    for tr in tracks:
        if trp is not None and t>=trp['t'] and t<=tr['t'] and tr['t']-trp['t']<20:
            lat=ipol(trp,tr,t,'lat')
            lon=ipol(trp,tr,t,'lon')
            h=ipol(trp,tr,t,'heading')
            print("tdiff=",tr['t']-trp['t'], " pos=",lat,",",lon, " h=",h)
            ef.set_geo(lat, lon)
#            sign, deg, min, sec = JpegFile._parse(h)
#            primary.GPS.GPSImgDirection=[]
            ef.writeFile(fn)
        trp=tr
