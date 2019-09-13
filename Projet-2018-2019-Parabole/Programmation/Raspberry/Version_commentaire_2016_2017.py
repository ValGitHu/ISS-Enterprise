#!/usr/bin/python
# coding: utf-8

import pygame  # librairie de l'interface
from pygame.locals import *  # import de toutes les variables de la librairie pygame et les associe au current name space deconseillé(interface graphique)
import os  #
import sys  #
from time import sleep  # importe la classe sleep de la libraire time
from helpers import *  # import de toutes les variables de la librairie helpers est les associe au current name space deconseillé(libraire pour dev des applis externe)
from RPi import GPIO  # gestion des gpio
from math import * #pour le posi auto


GPIO.setwarnings(False)  # supprime les warnings sur les gpio
GPIO.setmode(GPIO.BOARD)  # utilisation de la numérotation de serigraphie et pas celle electronique

import serial  # acquisition des trames
import pynmea2  # librairie de lecture des trames
import string  # importation des chaines de caractères


# ----- GPS ----- #
class GPS(object):  # Création de la classe GPS
    def __init__(self, path):  # Argument pour les fonctions utilisés par la class GPS (constructeur)
        try:
            self.gps = serial.Serial(path, 4800)  # Liason 4800 bauds série
            self.gps.readline()  # On se place au début  de la ligne d'une trame pour lire
        except serial.SerialException:  # Le GPS n'est pas connecté
            self.gps = None  # donc gps n'est pas connecté alors on retourne rien

        self.data = None  # Si gps n'est pas connecté aucune data trouvé donc aucun retour

    def __del__(self):  # creation de la destruction ( destructeur)
        if self.gps is not None:  # Si gps  est connecté alors on ferme le fichier gps
            self.gps.close()  # fermeture de la trame gps

    def getInfos(self):  # récuperation les informations dans la chaine de carctère
        if self.gps is not None:  # Gps connecté
            while self.gps.in_waiting > 0:  # Tant que le gps  est en attente il lis la trame
                serialBuffer = self.gps.readline()  # La mémoire série = à la chaine de caractère lu sur la ligne
                if serialBuffer[0:6] == "$GPGGA":  # compare la trame au la chaine de cractère constitué de 7 caractères ($GPPGA la trame interpreté par pynmea2)
                    self.data = pynmea2.parse(serialBuffer)  # pynmea2 gère les trames ,parse = analyser la mémoire ( serial Buffer)

            return self.data  # return les valeurs chaines de caractères
        else:
            return None  # retourne rien si l'objet gps retourne rien


# ----- Rotor ----- #
class Rotor:
    def __init__(self, chemin):  # constructeur avec comme argument chemin
        try:
            self.ser = serial.Serial(chemin)  # Création  de l'objet type serial
            self.config()
        except serial.SerialException:  # L'Easy Rotor Control n'est pas connecté
            self.ser = None  # la liason prend la valeur rien

    def tourner(self, angle):  # argument angle degré
        if self.ser is not None:  # Si la liason retourne quelque chose autre que rien alors
            angle = int( angle)  # Calcul de l'angle en fonction des valeurs d'axes (angle=atan2(x,y)*180/pi+180) voir code source fichier boussole
            commande = "M0" + repr(angle) + "\r\n"  # commande =  caractère MO +réprésentation  sous chaine de l'angle grace à repr/ + retour en debut ligne et saut ligne (code ascii)
            print(commande)  # affiche la commande
            self.ser.write( commande.encode('latin-1'))  # encode un string sous (latin -1 meme chose que l'UTF-8 c'est du typage)

    def angle(self):
        if self.ser is not None:  # Si la liason retourne quelque chose autre que rien alors
            self.ser.write(b'C\r')
            return int(self.ser.readline())  # retourne un entier

    def tournerHoraire(self):
        if self.ser is not None:
            self.ser.write(b'R\r\n')  # fais tourner en sens horaire le rotor = R

    def tournerAntiHoraire(self):
        if self.ser is not None:
            self.ser.write(b'L\r\n')  # fais tourner en sens antiHoraire = L

    def stop(self):
        if self.ser is not None:
            self.ser.write(b'S\r\n')  # fais stop le rotor = R

    def calibrationDroite(self):
        if self.ser is not None:
            self.ser.write(b'sCAR0360\r\n')  # fais la calibration à 360 degré = sCAR0360

    def calibrationGauche(self):
        if self.ser is not None:
            self.ser.write(b'sCAL0000\r\n')  # fais la calibration à 0 degré = sCAL0000

    def config(self):
        if self.ser is not None:
            self.ser.write(b'sSPA0000\r')  # initialise la calibration à 0 degré
            self.ser.write(b'sSPL0003\r')  # initialise la vitesse de l'angle
            self.ser.write(b'sSPH0003\r')


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


# ----- Programme principal ----- #
# GPS initialization
gps = GPS("/dev/ttyUSB0")  # Port TTY USB0 ou est connecté le raspberry

# Rotor initialization
rotor = Rotor("/dev/ttyUSB1")  # Port TTY USB1 ou est connecté le raspbery

# Vérin initialization
verin = Verin(10, 8, 12)

# Check if executed with root access
if not "SUDO_UID" in os.environ.keys():
    print("Veuillez exécuter ce programme avec les droits root : sudo ./parabole.py")
    sys.exit(1)  # sortie du système de raspberry

# Colors
WHITE = (255, 255, 255)  # definition de la couleur avec le mode RGB

# Screen setup
os.putenv("SDL_FBDEV", "/dev/fb1")  # importation de la (sdl = libraire sur l'interface graphique) et changement du phéripherique à utilisé
os.putenv("SDL_MOUSEDRV", "TSLIB")  # importation de la sdl avec comme péripherique tactile ELO
os.putenv("SDL_MOUSEDEV","/dev/input/touchscreen")  # importation de la sdl et définition du périphérique tactile  à utilisé sur linux

# Pygame initialization and configuration
pygame.init()#initialisation de pygame
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
lcd = pygame.display.set_mode((480, 320))  # Taille de la fenêtre
lcd.fill((229, 50, 46))  # Couleur d'arrière-plan
pygame.display.update()
font = pygame.font.Font(None, 30)  # police de pygame

# Format des boutons : "Label": ((x, y), (w, h), TaillePolice, callback())
buttonsDef = {
    ("^", (340, 110), (70, 70), 100),  # Creation du bouton deplacement vers le haut
    (">", (410, 180), (70, 70), 100),  # Creation du bouton deplacement coté droit
    ("v", (340, 250), (70, 70), 100),  # Creation du bouton deplacment vers le bas
    ("<", (270, 180), (70, 70), 100),  # Creation du bouton deplacement coté gauche
    ("Auto", (350, 190), (50, 50), 30),  # Creation du bouton placement automatique
}

buttons = []  # Création d'une liste buttons
for button in buttonsDef:
    btn = makeButton(button)  # Crée un bouton
    buttons.append(btn)  # ajjout dans la liste de btn
    lcd.blit(btn[0], btn[1])  # Change la couleur des pixels des boutons construit

# GPS informations
gpsInfosLabel = pygame.font.Font(None, 30).render("Informations GPS", True, WHITE)  # les infos du gps une police d'ecriture blanche nommé informations GPS
lcd.blit(gpsInfosLabel, gpsInfosLabel.get_rect().move((10, 10)))  # Modifie les boutons
gpsInfosSurface = pygame.Surface((320, 70))  # definition de la taille en pixel 320 et longeur en X et 70 en hauteur Y

# Antenna's position and signal strength
antennaPosLabel = pygame.font.Font(None, 30).render("Position parabole", True,
                                                    WHITE)  # affectation d'une police blanche
lcd.blit(antennaPosLabel, antennaPosLabel.get_rect().move((10, 120)))  # antennaPos
antennaPosSurface = pygame.Surface(
    (250, 70))  # création d'une zone dans l'interface graphique pour la puissance du signal

# Compass
compassLabel = pygame.font.Font(None, 30).render("Boussole", True, WHITE)  # création d'une police pour l'objet compassLabel
lcd.blit(compassLabel,compassLabel.get_rect().move((10, 230)))  # associe l'ecriture de compassLabel au rectangle en placé au 10,230
compassSurface = pygame.Surface((250, 30))  # création d'une surface de 250 et 30 pixel

# Logo
logo = pygame.image.load("images/StrategicTelecom.png").convert_alpha()  # logo est une image png chargé
logo = pygame.transform.scale(logo, (76, 76))  # echelle 76 pixels sur 76pixels
rect = logo.get_rect()  # créer un rectangle
rect = rect.move((405, 0))  # deplacment du retangle au pixel 405 et 0
lcd.blit(logo, rect)  # copie le graphique d'une image dans une autre donc logo va dans rect.

# Zone
zone = pygame.image.load("images/zoneInconnue.png").convert_alpha()  # chargement dde l'image png zone inconnue
zoneRect = zone.get_rect()  # création d'un rectangle zoneRect
zoneRect = zoneRect.move((340, 10))  # triangle deplacé en 340 , 10
lcd.blit(zone, zoneRect)  # copie le graphique d'une image dans une autre donc zone va dans zoneRect

pygame.display.update()  # met à jour l'écran

zone2 = 0
timer = 0
showZone = False


def positionnementAuto():  # a changer

lat = gpsData.latitude
longi = gpsData.longitude

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

verin.monter()
verin.descendre()
rotor.monter()
rotor.arreter()




while True:
    clock.tick(5)
    timer = timer + 1

    gpsData = gps.getInfos() #prend les donnés du gps pour les stocké dans une variable data utilisé pour pygame

    # Zone image
    if (zone2 == 0):
        if timer % 5 == 0:
            if showZone:
                showZone = False
                pygame.draw.rect(lcd, (229, 50, 46), zoneRect)
            else:
                showZone = True
                lcd.blit(zone, zoneRect)

            if gpsData is not None:  # Debug
                print("Lat : " + "%02do%02d'%07.4f\"" % (gpsData.latitude, gpsData.latitude_minutes, gpsData.latitude_seconds))
                print("Lon : " + "%02do%02d'%07.4f\"" % (gpsData.longitude, gpsData.longitude_minutes, gpsData.longitude_seconds))
                print("Fix" if gpsData.gps_qual else "No fix")
                print("Sats : " + gpsData.num_sats)

    # Get GPS informations et affichage sur PY
    gpsData = gps.getInfos()
    if gpsData is not None:
        gpsInfosSurface.fill((127, 0, 0))

        gpsInfosText = font.render("Nombre de satellites : " + gpsData.num_sats, True, WHITE)
        gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect())
        if gpsData.gps_qual:
            gpsInfosText = font.render("Latitude : %02d deg %02d' %07.4f\"" % (
            gpsData.latitude, gpsData.latitude_minutes, gpsData.latitude_seconds), True, WHITE)
            gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect().move((0, 20)))
            gpsInfosText = font.render("Longitude : %02d deg %02d' %07.4f\"" % (
            gpsData.longitude, gpsData.longitude_minutes, gpsData.longitude_seconds), True, WHITE);
            gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect().move((0, 40)))
        else:
            gpsInfosText = font.render("Pas de fix", True, WHITE)
            gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect().move((0, 30)))

        gpsInfosRect = gpsInfosSurface.get_rect().move((10, 40))
        lcd.blit(gpsInfosSurface, gpsInfosRect)

    pygame.display.update() #Mise à jour de l'ecran PYgame

    # Antenna informations pour l'affichage sur PY
    antennaPosSurface.fill((127, 0, 0))
    antennaPosText = font.render("Azimut : {} deg".format(rotor.angle()), True, WHITE)
    antennaPosSurface.blit(antennaPosText, antennaPosText.get_rect())
    antennaPosText = font.render("Elevation : {}".format(verin.compteur / 10.0), True, WHITE)
    antennaPosSurface.blit(antennaPosText, antennaPosText.get_rect().move((0, 20)))
    antennaPosText = font.render("Puissance signal : N/A".format(-12), True, WHITE)
    antennaPosSurface.blit(antennaPosText, antennaPosText.get_rect().move((0, 40)))

    lcd.blit(antennaPosSurface, antennaPosSurface.get_rect().move((10, 150)))

    # Compass informations pour l'affichage sur PY
    compassSurface.fill((127, 0, 0))
    compassText = font.render("Cap : {} deg".format(183), True, WHITE)
    compassSurface.blit(compassText, compassText.get_rect())

    lcd.blit(compassSurface, compassSurface.get_rect().move((10, 260)))

    # Scan touchscreen events
    for event in pygame.event.get():  # si il y'a un evenement dans la librairie de l'interface graphique Pygame
        if event.type is MOUSEBUTTONDOWN or event.type is MOUSEBUTTONUP:  # Si c'est un click droit ou gauche alors
            pos = pygame.mouse.get_pos()  # la variable pos prend la valeur des cordonnés la ou à eu lieu l'event

            for button in buttons:  # pour la variable button dans la liste buttons
                if button[1].collidepoint(pos):  # Si la variable [1] de la liste buttons est
                    if button[2] == "<":  # Tourner rotor sens anti-horaire
                        if event.type is MOUSEBUTTONDOWN:
                            print("tourner")  # afficher tourner sur l'écran
                            rotor.tournerAntiHoraire()  # rotor tourne dans le sens anti horaire
                        elif event.type is MOUSEBUTTONUP:
                            print("stop")
                            rotor.stop()

                    if button[2] == ">":  # Tourner rotor sens horaire
                        if event.type is MOUSEBUTTONDOWN:
                            rotor.tournerHoraire()
                        elif event.type is MOUSEBUTTONUP:
                            rotor.stop()

                    if button[2] == "^":  # Monter parabole (sortir vérin)
                        if event.type is MOUSEBUTTONDOWN:
                            verin.monter()
                            print("Monter")
                        elif event.type is MOUSEBUTTONUP:
                            verin.arreter()
                            print("Stop")

                    if button[2] == "v":  # Descendre parabole (rentrer vérin)
                        if event.type is MOUSEBUTTONDOWN:
                            verin.descendre()
                        elif event.type is MOUSEBUTTONUP:
                            verin.arreter()

                    if button[2] == "Auto":  # Lancement de la procédure de positionnement automatique
                        if event.type is MOUSEBUTTONDOWN:
                            positionnementAuto()
                        elif event.type is MOUSEBUTTONUP:
                            pass

