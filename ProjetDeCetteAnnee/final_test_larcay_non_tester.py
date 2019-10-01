#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# server_gui.py

import serial  # acquisition des trames
#from helpers import *  # import de toutes les variables de la librairie helpers est les associe au current name space deconseillé(libraire pour dev des applis externe)
from RPi import GPIO  # gestion des gpio# server_gui.py
GPIO.setwarnings(False)  # supprime les warnings sur les gpio
GPIO.setmode(GPIO.BOARD)  # utilisation de la numérotation de serigraphie et pas celle electronique

import pygame
import sys
from time import sleep
import requests
import json
pygame.init()
clock = pygame.time.Clock()
with open("document.json") as f:
spotsJson = json.load(f)

BLACK = 0, 0, 0
WHITE = 255, 255, 255
CIEL = 0, 200, 255
RED = 255, 0, 0
ORANGE = 255,220, 0
GREEN = 0, 255, 0
GREY = 23,23,23
ORANGETEST= 204,21,21
class Rotor:
	def __init__(self, chemin):
		try:
			self.ser = serial.Serial(chemin)
			self.config()
		except serial.SerialException: # L'ERC n'est pas connecté
			self.ser = None

	def tourner(self, angle):
		if self.ser is not None:
			angle = int(angle)
			if (angle<100):
                            commande = "M0" + repr(angle) + "\r\n"

                        else:
                            commande = "M" + repr(angle) + "\r\n"
			print(commande)
			self.ser.write(commande.encode('latin-1'))

	def angle(self):
		if self.ser is not None:
			self.ser.write(b'C\r')
			return int(self.ser.readline())

	def tournerHoraire(self):
		if self.ser is not None:
			self.ser.write(b'R\r\n')

	def tournerAntiHoraire(self):
		if self.ser is not None:
			self.ser.write(b'L\r\n')

	def stop(self):
		if self.ser is not None:
			self.ser.write(b'S\r\n')

	def calibrationDroite(self):
		if self.ser is not None:
			self.ser.write(b'sCAR0360\r\n')

	def calibrationGauche(self):
		if self.ser is not None:
			self.ser.write(b'sCAL0000\r\n')

	def config(self):
		if self.ser is not None:
			self.ser.write(b'sSPA0000\r')
			self.ser.write(b'sSPL0003\r')
			self.ser.write(b'sSPH0003\r')

rotor=Rotor("/dev/ttyUSB1")

# ----- Vérin ----- #
class Verin:
    def __init__(self, pinPush, pinPull, pinInterrupt):
        self.pinPush = pinPush
        self.pinPull = pinPull
        self.pinInterrupt = pinInterrupt
        GPIO.setup(pinPush, GPIO.OUT)
        GPIO.setup(pinPull, GPIO.OUT)
        GPIO.setup(pinInterrupt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(pinPush, GPIO.LOW)
        GPIO.output(pinPull, GPIO.LOW)
        self.compteur = 100
        GPIO.add_event_detect(pinInterrupt, GPIO.FALLING, callback=self.impulsion, bouncetime=50)

    def impulsion(self, channel):
        self.compteur += self.increment
        print("Impulsion {}".format(self.compteur))

    def monter(self):
        self.increment = 1
        GPIO.output(self.pinPush, GPIO.HIGH)
        GPIO.output(self.pinPull, GPIO.LOW)

    def descendre(self):
        self.increment = -1
        GPIO.output(self.pinPush, GPIO.LOW)
        GPIO.output(self.pinPull, GPIO.HIGH)

    def arreter(self):
        GPIO.output(self.pinPush, GPIO.LOW)
        GPIO.output(self.pinPull, GPIO.LOW)

verin = Verin(10, 8, 12)

class Button:
    def __init__(self, fond, text, color, font, dx, dy):
        self.fond = fond
        self.text = text
        self.color = color
        self.font = font
        self.dec = dx, dy
        self.state = False  # enable or not
        self.title = self.font.render(self.text, True, BLACK)
        textpos = self.title.get_rect()
        textpos.centerx = self.fond.get_rect().centerx + self.dec[0]
        textpos.centery = self.dec[1]
        self.textpos = [textpos[0], textpos[1], textpos[2], textpos[3]]
        self.rect = pygame.draw.rect(self.fond, self.color, self.textpos)
        self.fond.blit(self.title, self.textpos)

    def update_button(self, fond, action=None):
        self.fond = fond
        mouse_xy = pygame.mouse.get_pos()
        over = self.rect.collidepoint(mouse_xy)
        if over:
            action()
            if self.color == RED:
                self.color = GREEN
                self.state = True
            elif self.color == GREEN:
                # sauf les + et -, pour que ce soit toujours vert
                if len(self.text) > 5:  # 5 char avec les espaces
                    self.color = RED
                self.state = False
        # à la bonne couleur
        self.rect = pygame.draw.rect(self.fond, self.color, self.textpos)
        self.fond.blit(self.title, self.textpos)

    def display_button(self, fond):
        self.fond = fond
        self.rect = pygame.draw.rect(self.fond, self.color, self.textpos)
        self.fond.blit(self.title, self.textpos)


class IHM:

    def __init__(self):
        self.screen = pygame.display.set_mode((480,320))
        self.loop = True

        # Définition de la police
        self.big = pygame.font.SysFont('Helvetica',25)
        self.small = pygame.font.SysFont('Helvetica',15)

        self.create_fond()
        self.create_button()

    def update_textes(self):
        self.textes = [["Positionnement de l'Antenne",WHITE, self.big,0,10],
                        ["Azimuth de la parabole : ",WHITE, self.small,-170,50],
                        ["Elevation de la parabole : ",WHITE, self.small,-165,80],
                        ["Angle du satellite :", WHITE, self.small,-185,110],
                        ["Elevation du satellite :",WHITE, self.small,-180,140]]

    def create_fond(self):
        # Image de la taille de la fenêtre
        self.fond = pygame.Surface(self.screen.get_size())
        self.fond.fill(ORANGETEST)
    def image(self):
        strategic = pygame.image.load("StrategicTelecom.png").convert_alpha()
        strategic = self.fond.blit(strategic, (200,200))
    def rect(self):
        paraelev = pygame.draw.rect(self.fond,WHITE, [0,70,200,20],2)
        paraazi  = pygame.draw.rect(self.fond,WHITE, [0,40,200,20],2)
        satangle = pygame.draw.rect(self.fond,WHITE, [0,100,200,20],2)
        satelev = pygame.draw.rect(self.fond,WHITE, [0,130,200,20],2)

    def create_button(self):
        self.verin_baisse = Button(self.fond, " Monter ", ORANGE, self.small, 100, 50)
        self.verin_hausse = Button(self.fond, " Baisser", ORANGE, self.small,100 , 150)
        self.rotor_horaire  = Button(self.fond, "   Droite ", ORANGE, self.small,20,100 )
        self.rotor_antihoraire = Button(self.fond, " Gauche ",ORANGE, self.small,185,100)
        self.numero0 = Button(self.fond, " 0 ", ORANGE, self.small, 70 , 250)
        self.numero1 = Button(self.fond, " 1 ", ORANGE, self.small, 90 , 250)
        self.numero2 = Button(self.fond, " 2 ", ORANGE, self.small, 110 , 250)
        self.numero3 = Button(self.fond, " 3 ", ORANGE, self.small, 130 , 250)
        self.numero4 = Button(self.fond, " 4 ", ORANGE, self.small, 150 , 250)
        self.numero5 = Button(self.fond, " 5 ", ORANGE, self.small, 170 , 250)
        self.numero6 = Button(self.fond, " 6 ", ORANGE, self.small, 190 , 250)
        self.numero7 = Button(self.fond, " 7 ", ORANGE, self.small, 210 ,  250)
        self.numero8 = Button(self.fond, " 8 ", ORANGE, self.small, 230 , 250)
        self.numero9 = Button(self.fond, " 9 ", ORANGE, self.small, 70 , 270)
        self.valider = Button(self.fond, " VALIDER ", ORANGE, self.small, 110 , 270)
        self.nouveau = Button(self.fond, " NOUVEAU  ", ORANGE, self.small, 190, 270)
        self.quitter = Button(self.fond, " QUITTER  ", RED, self.small, 200, 300)
        #self.auto = Button(self.fond, " AUTO  ", RED, self.small, 100,100)
        self.stop = Button(self.fond, " STOP  ", RED, self.small, 200,200)
        #self.auto_verin = Button(self.fond, " AUTO VERIN  ", RED, self.small,100,200)


    def display_text(self, text, color, font, dx, dy):
        '''Ajout d'un texte sur fond. Décalage dx, dy par rapport au centre.
        '''
        mytext = font.render(text, True, color)  # True pour antialiasing
        textpos = mytext.get_rect()
        textpos.centerx = self.fond.get_rect().centerx + dx
        textpos.centery = dy
        self.fond.blit(mytext, textpos)

   def variable(self,parametre):
	   	myfont = pygame.font.SysFont(None, 70)
		variable_display = myfont.render(str(parametre),1,(255,255,255))
		return variable_display

    def infinite_loop(self):
        while self.loop:
            self.create_fond()

            # Boutons
            self.verin_baisse.display_button(self.fond)
            self.verin_hausse.display_button(self.fond)
            self.rotor_horaire.display_button(self.fond)
            self.rotor_antihoraire.display_button(self.fond)
            self.numero0.display_button(self.fond)
            self.numero1.display_button(self.fond)
            self.numero2.display_button(self.fond)
            self.numero3.display_button(self.fond)
            self.numero4.display_button(self.fond)
            self.numero5.display_button(self.fond)
            self.numero6.display_button(self.fond)
            self.numero7.display_button(self.fond)
            self.numero8.display_button(self.fond)
            self.numero9.display_button(self.fond)
            self.valider.display_button(self.fond)
            self.quitter.display_button(self.fond)
            self.nouveau.display_button(self.fond)
            self.stop.display_button(self.fond)
            self.auto.display_button(self.fond)
            self.auto_verin.display_button(self.fond)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.rotor_horaire.update_button(self.fond, action=rotorhor)
                    self.rotor_antihoraire.update_button(self.fond, action=rotorant)
                    self.verin_baisse.update_button(self.fond, action=monterverin)
                    self.verin_hausse.update_button(self.fond, action=baisserverin)
                    self.quitter.update_button(self.fond, action=Quitter)
                    self.valider.update_button(self.fond,action=afficher)
                    self.nouveau.update_button(self.fond, action=nouveau)
                    self.numero0.update_button(self.fond, action=numero0)
                    self.numero1.update_button(self.fond, action=numero1)
                    self.numero2.update_button(self.fond, action=numero2)
                    self.numero3.update_button(self.fond, action=numero3)
                    self.numero4.update_button(self.fond, action=numero4)
                    self.numero5.update_button(self.fond, action=numero5)
                    self.numero6.update_button(self.fond, action=numero6)
                    self.numero7.update_button(self.fond, action=numero7)
                    self.numero8.update_button(self.fond, action=numero8)
                    self.numero9.update_button(self.fond, action=numero9)
                    self.auto.update_button(self.fond, action=pilotage_rotor)
                    self.stop.update_button(self.fond, action=stop)
                    self.auto_verin.update_button(self.fond, action=pilotage_verin)


            self.update_textes()
            self.rect()
            self.image()
			b = angle()
            test = self.variable(b)

            for text in self.textes:
                self.display_text(text[0], text[1], text[2],text[3],text[4])

            # Ajout du fond dans la fenêtre
            self.screen.blit(self.fond, (0, 0))
			self.screen.blit(test,(100,100))
            # Actualisation de l'affichage
            pygame.display.update()
            # 10 fps
            clock.tick(10)

def rotorhor():
    print("rotor horaire")
    rotor.tournerHoraire()

def rotorant():
    print("rotor antihoraire")
    rotor.tournerAntiHoraire()

def baisserverin():
    print("baisser verin")
    verin.descendre()

def monterverin():
    print("monter verin")
    verin.monter()
	verin.impulsion()


garder =  []

def nouveau():
    del garder[0:100]
    return garder

def saisie(para):
    garder.append(para)
    print (garder)
    return garder

def numero0():
    a = "0"
    saisie(a)
    #numer00()
def numero1():
    b = "1"
    saisie(b)
def numero2():
    c = "2"
    saisie(c)

def numero3():
    d = "3"
    saisie(d)

def numero4():
     e = "4"
     saisie(e)

def numero5():
     f = "5"
     saisie(f)
def numero6():
    g = "6"
    saisie(g)
def numero7():
    h = "7"
    saisie(h)
def numero8():
    i = "8"
    saisie(i)
def numero9():
    j = "9"
    saisie(j)

def stop():
    rotor.stop()
    verin.arreter()

def resultat():
     total = []
     total = saisie("")
     total.append("")
     total.append("")
     total.append("")
     premier_chiffre = total[0]
     second_chiffre = total[1]
     troisieme_chiffre= total[2]
     Angle_saisie = premier_chiffre+second_chiffre+troisieme_chiffre
     print(Angle_saisie)
     return Angle_saisie

def pilotage_rotor():
    auto_angle = resultat()
    rotor.tourner(auto_angle)

def pilotage_verin():
    valeur_pilotage_verin = int(resultat())
    angle_verin = valeur_pilotage_verin*1.5
    verin.descendre()
    sleep(90)
    verin.monter()
    sleep(angle_verin)
    verin.arreter()

def GPS()
    gps = serial.Serial("/dev/ttyUSB0", 4800)
	nmea = gps.readline()
	if nmea[0:6] == "$GPGGA": #On compare la trame GPGGA
	    print nmea
	    gpsData = pynmea2.parse(nmea) #On parcoure la trame qu'on affecte a une variable gpsDATA
	    #global lata #Variable global utilisé pour l'algo suivant
	    #global longitu #Variable longitude  utilise pour l'algo suivant
	    lata = float(gpsData.latitude) #permet de retrouver  dans notre trame la latitude et la traduire
	    longitu = float(gpsData.longitude)#permet de retrover dans notre trame la latitude et la traduire
	    print 'latitude = ' , lata
	    print 'longitude = ' , longitu
	    print("Fix" if gpsData.gps_qual else "No fix")
	    print("Sats : " + gpsData.num_sats)
        gps.close()
		lat = lata
		longi = longitu
		algoazimuth = 0
		algoelevation = 0
		g = (-9+longi)
		grad = (g / 57.29578)
		lrad = (lat / 57.29578)
		azi= (pi - (-atan((tan(grad) / sin(lrad)))))# calcul azimuth en radian
		algoazimuth = (azi*57.29578)#calcul en degré
		a = cos(grad)
		b = cos(lrad)
		ele = atan((a*b-0.1512)/(sqrt(1-pow(a,2)*pow(b,2))))# calcul en radion de l'elevation
		algoelevation = ele*57.29578#calcul de l'elevation en degré
		print lat
		print longi
		print "valeur azimuth pointer ",algoazimuth
		print "valeur  elevation ou pointer ",algoelevation
		return algoazimuth,algoelevation,lat,longi

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
	return num_spot



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

def request():
	r = requests.get('https://www.google.com/search?q=url+google')
	a = r.status_code
	print(type(a))
	if(a == 200):
	  print "connexion reussis"
	  puissance,bruit = getData()
	if(a == 404):
	  print "page non trouvée"
	return puissance,bruit

def getData():
	data = []
    r = requests.get("http://192.168.100.1/index.cgi?page=modemStatusData")
    data = r.text.split("##")
	rxPower = data[14]
	rxSNR =data[11]
	return rxPower,rxSNR

def auto():
	rotor_angle,verin_angle,latitude_auto,longitude_auto= GPS()
    rotor.tourner(rotor_angle)
	numero_spot = zone(latitude_auto,longitude_auto)

def affichage_valeurs():
	affichage_rotor = rotor.angle()
	affichage_azimuth,affichage_elevation,affichage_latitude,affichage_longitude = GPS()
	angle_utilisateur = resultat()
	affichage_puissance,affichage_bruit  = request()
	affichage_numspot = zone()

	return affichage_rotor,affichage_elevation,affichage_azimuth,angle_utilisateur,affichage_latitude,affichage_longitude,affichage_numspot


def Quitter():
    print("Quit")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    Larcay = IHM()
    Larcay.infinite_loop()
    Larcay.affichage_variable()
    main()
