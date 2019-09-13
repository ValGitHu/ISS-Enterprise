from math import *#Importation des librairies
import string
import json
with open("document.json") as f:
  spotsJson = json.load(f)

#!/usr/bin/python
# -*- coding: utf-8 -*-



def gps():
    lata = input()
    longitu = input()
    return lata,longitu

def algo(lat,long):
    lat = 47.36
    long = 0.78

    azimuth=0
    elevation=0

    g = (-9+long)
    grad = (g / 57.29578)
    lrad = (lat / 57.29578)

    azi= (pi - (-atan((tan(grad) / sin(lrad)))))
    azimuth = (azi*57.29578)

    a = cos(grad)
    b = cos(lrad)
    ele = atan((a*b-0.1512)/(sqrt(1-pow(a,2)*pow(b,2))))
    elevation = ele*57.29578
    azimuth = str(azimuth)
    elevation = str(elevation)
    print ("valeur d'azimuth a pointer : " + azimuth)
    print ("valeur d'elevation a pointer : "+ elevation)

def zone(latitude, longitude):
    pnt = { 'x': latitude, 'y': longitude }
    test = False
    i=0
    while((i<=len(spotsJson["spots"]) - 1) and (test==False)):
        value = trouveSpot(spotsJson["spots"][i], pnt)
        test = value[0]
        id_spot = value[1]
        i=i+1


    print ("ID spot : "+id_spot)

    if (id_spot=="bleu"):
        num_spot=1

    elif (id_spot=="orange"):
        num_spot=2

    elif (id_spot=="violet"):
        num_spot=3

    elif (id_spot=="vert"):
        num_spot=4
    else:
        num_spot=0

    print ("Numero spot : " + str(num_spot))



def trouveSpot(poly, pt):
    ret=[0,0]
    id="non definit"
    l=len(poly["latitude"])
    c=False
    j=l-1
    for i in range(0, l):
        if(((((poly["longitude"][i] <= pt['y']) and (pt['y'] < poly["longitude"][j])) or ((poly["longitude"][j] <= pt['y']) and (pt['y'] < poly["longitude"][i]))) and (pt['x'] < (((poly["latitude"][j] - poly["latitude"][i]) * (pt['y'] - poly["longitude"][i]) / (poly["longitude"][j] - poly["longitude"][i])) + poly["latitude"][i])))==True):
            c = not c
            id=poly["famille"]
        j=i

    ret[0] = c
    ret[1] = id
    return ret

latitude,longitude = gps()
algo(latitude,longitude)
latitude_float = float(latitude)
longitude_float = float(longitude)
zone(latitude_float,longitude_float)
