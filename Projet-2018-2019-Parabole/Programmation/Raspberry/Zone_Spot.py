import json


with open("document.json") as f:
  spotsJson = json.load(f)


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

zone(47.36834,0.77810)
