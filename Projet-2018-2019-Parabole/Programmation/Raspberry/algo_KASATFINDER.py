from math import *
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

    print (azimuth)
    print (elevation)
