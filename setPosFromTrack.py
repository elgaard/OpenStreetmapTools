#!/usr/bin/env python2
import sys
import argparse
import glob
import gzip
import time
from pexif import JpegFile
from pexif import Rational
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

for fn in glob.glob("*.jpg"):
    ef = JpegFile.fromFile(fn,mode="rw")
    primary = ef.get_exif(create=True).get_primary()

    print(primary.DateTime)
    dt=datetime.strptime(primary.DateTime,"%Y:%m:%d %H:%M:%S") #python 3 .timestamp()
    t=time.mktime(dt.timetuple())

    trp=None
    for tr in tracks:
        if trp is not None and t>=trp['t'] and t<=tr['t'] and tr['t']-trp['t']<20:
            gps = primary.GPS

            lat=ipol(trp,tr,t,'lat')
            lon=ipol(trp,tr,t,'lon')
            h=ipol(trp,tr,t,'heading')
            print("tdiff=",tr['t']-trp['t'], " pos=",lat,",",lon, " h=",h)
            ef.set_geo(lat, lon)
            hr=Rational(int(round(h*60)), 60)
#            gps.GPSImgDirection=[hr] # requires patched pexif.py:     0x11: ("Image Direction", "GPSImgDirection", RATIONAL, 1),

            ef.writeFile(fn)
        trp=tr
