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
directions=[]
for line in trackf.readlines():
    ls=line.split(";")
    if line!="DONE" and ls[1] and ls[2]:
        t=ls[0]
        lon=ls[1]
        lat=ls[2]
        d=ls[3]
        tracks.append({'t':float(t),'lat':float(lat),'lon':float(lon)})
    elif line!="DONE" and ls[13]:
        t=ls[0]
        directions.append({'t':float(t),'direction':float(ls[13])})
for fn in glob.glob("*.jpg"):
    print("do "+fn)
    ef = JpegFile.fromFile(fn,mode="rw")
    primary = ef.get_exif(create=True).get_primary()

    dt=datetime.strptime(primary.DateTime,"%Y:%m:%d %H:%M:%S") #python 3 .timestamp()
    t=time.mktime(dt.timetuple())
    dirty=False
    trp=None
    drp=None
    for tr in tracks:
        if trp is not None and t>=trp['t'] and t<=tr['t'] and tr['t']-trp['t']<20:
            gps = primary.GPS
            lat=ipol(trp,tr,t,'lat')
            lon=ipol(trp,tr,t,'lon')
            ef.set_geo(lat, lon)
            dirty=True
        trp=tr
    for dr in directions:
        if drp is not None and t>=drp['t'] and t<=dr['t'] and dr['t']-drp['t']<20:
            gps = primary.GPS
            h=ipol(drp,dr,t,'direction')
            hr=Rational(int(round(h)), 1)
            
            gps.GPSImgDirection=[hr] # requires patched pexif.py: https://github.com/elgaard/pexif , with  0x11: ("Image Direction", "GPSImgDirection", RATIONAL, 1),
            #comment out if you are using the standard pexif
            
            dirty=True
        drp=dr
    if dirty:
        ef.writeFile(fn)
