# -*- coding: utf-8 -*-
import math 
import serial
import pynmea2
import string

gps = serial.Serial('/dev/ttyUSB0', 4800)
print(gps.name)

while True:
	nmea = gps.readline()

	if nmea[0:6] == "$GPGGA":
		print nmea
		gpsData = pynmea2.parse(nmea)
		print("Lattitude : " + "%02d°%02d'%07.4f''" % (gpsData.latitude, gpsData.latitude_minutes, gpsData.latitude_seconds))
		print("Longitude : " + "%02d°%02d'%07.4f''" % (gpsData.longitude, gpsData.longitude_minutes, gpsData.longitude_seconds))
		print("Lattitude = ", float(gpsData.latitude))
		print("Longitude = ", float(gpsData.longitude))
		print("Fix" if gpsData.gps_qual else "No fix")
		print("Sats : " + gpsData.num_sats)

		print("")

		alng= [18.04,20.1,29.69,11.09,24.5,-4.64,6.17,-6.57,15.05,11.61,
		18.5,35.18,-0.18,28.67,21.07,7.27,14.65,-8.1,4.1,30.7,
		37.82,23.66,-2.87,10.98,17.61,1.21,40.96,7.56,14.06,26.21,
		20.22,32.59,-1.74,4.41,10.75,28.41,16.61,22.78,34.78,1.7,
		7.65,13.35,-7.36,19.25,25.17,-8.94,-0.99,16.06,21.65,27.14,
		4.94,-3.86,10.39,34.21,29.9,37.68,2.31,12.9,24.09,47.37,
		7.98,40.573,18.66,-6.09,-0.24,26.35,15.6,20.72,-8.5,32.46,
		-2.75,28.88,23.47,13.03,-5.2,34.61,2.44,25.24,10.03,-6.61,
		21.13,31.05,53.8]

		alat= [65.81,62.91,62.79,62.07,60.3,59.39,59.81,56.33,58.92,55.95,
		55.74,53.4,53.92,53.61,53.14,53.28,53.07,52.71,51.58,50.98,
		50.25,50.42,51.34,50.76,50.57,49.27,48.85,48.58,48.36,47.98,
		48.02,48.15,47.24,46.6,46.51,46,46.32,46.25,45.97,44.6,
		44.65,44.27,43.85,44.09,44.06,42.18,43.09,42.57,42.42,42.25,
		42.44,41.94,42.39,40.9,40.33,40.06,40.9,40.57,40.39,38.90,
		40.53,39.247,40.47,40.27,39.35,38.65,38.29,38.64,38.91,37.6,
		37.64,36.54,36.79,36.28,36.44,35.77,35.12,34.83,34.3,32.3,
		30.83,29.77,25.59]

		anum= [71,70,75,65,76,45,56,35,64,55,
		63,74,34,69,62,44,54,24,33,68,
		73,61,23,43,53,22,72,32,42,60,
		52,67,16,21,31,59,41,51,66,15,
		20,30,9,40,50,6,11,29,39,49,
		14,8,19,58,48,57,10,18,38,83,
		13,77,28,5,7,37,17,27,2,47,
		4,36,26,12,1,46,3,25,79,78,
		80,81,82]

		atyp= [2,1,4,4,2,3,2,1,3,1,
		4,3,2,2,3,3,2,3,1,1,
		4,4,4,4,1,3,3,2,3,3,
		2,2,1,4,1,4,4,1,1,2,
		3,2,1,3,2,3,4,1,4,1,
		1,2,4,4,2,3,3,3,3,4,
		2,1,2,4,1,4,4,1,2,1,
		3,3,2,1,1,2,4,1,3,4,
		3,1,2]

		position=9       ## constante en fonction de la technologie de satellite (correspond à la longitude 9)

		a=2.5     # diamètre moyen x de l'ellipse
		b=2.7     # diamètre moyen y de l'ellipse
		boussole = 250 	# à remplacer par la valeur du capteur

		# Entrée des coordonnées actuelles
		cy=float(input("Entrer la lattitude : "))
		cx=float(input("Entrer la longitude : "))

		# application de la formule des ellipses droites
		resultat=0     # stocke le résultat de la formule
		affichage=0    # autorise l'affichage si un satellite est détecté
		i_mem=0        # garde en mémoire le numéro du satellite détecté dans la boucle
		res_mem=1      # garde en mémoire le résultat de la formule quand un satellite a été détecté

		for i in range(83):
			resultat=((cx-alng[i])/a)**2+((cy-alat[i])/b)**2
			if resultat<1:
				affichage=1             # si un satellite est détecté, on affiche les  résultats à la fin
			if resultat<res_mem:    # car plus le résultat est petit, plus on est proche du centre de l'ellipse
				res_mem=resultat      # si résultat plus proche
				i_mem=i               # si résultat plus proche
		 
		if (affichage==1): # teste s'il y a quelquechose à afficher ou pas
			latitude=alat[i_mem]
			longitude=alng[i_mem]
				## calculs avec précision au degré près
			azimuth=180+180*math.atan(-1*math.tan(math.pi*(position-longitude)/180)/math.sin(math.pi*latitude/180))/math.pi
			elevation1=math.acos(math.cos(math.pi/180*(longitude-position))*math.cos(math.pi/180*abs(latitude)));
			elevation=180*math.atan((math.cos(elevation1)-(6378000/(6378000+35786000)))/math.sin(elevation1))/math.pi;
		  
			## affichages

			print("i: " + str (i_mem))
			print("type : "+  str (atyp[i_mem]))
			print("Lattitude du centre de l'ellipse : " + str(latitude)) # affiche lattitude
			print("Longitude du centre de l'ellipse : " + str(longitude)) # affiche longitude
			print("Azimuth : " + str(azimuth)) # affiche l'azimuth
			boussole=int(input("\nAngle indiqué par la boussole : "))
			if boussole>180:
				azimuth=azimuth-360+boussole
			else:
				azimuth=azimuth+boussole
			print("Azimuth corrigé : " + str(int(azimuth)))  # affiche l'azimuth corrigée
			#print("Elévation : " + str(elevation))  # affiche l'élévation
			#print(int(azimuth))  # convertit l'angle en entier pour le rotor
		  
		else :
			print("Aucun satellite détecté")



gps.close()
