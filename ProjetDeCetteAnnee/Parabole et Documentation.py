"""@package docstring
Documentation for this module.

More details.
"""

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# server_gui.py



import serial  # acquisition des trames
#from helpers import *  # import de toutes les variables de la librairie helpers est les associe au current name space deconseillé(libraire pour dev des applis externe)
from RPi import GPIO  # gestion des gpio# server_gui.py
GPIO.setwarnings(False)  # supprime les warnings sur les gpio
GPIO.setmode(GPIO.BOARD)  # utilisation de la numérotation de serigraphie et pas celle electronique
import pynmea2
import pygame
import sys
from time import sleep
from math import *
import string

pygame.init()
clock = pygame.time.Clock()
pygame.mouse.set_cursor(*pygame.cursors.diamond)


BLACK = 0, 0, 0
WHITE = 255, 255, 255
CIEL = 0, 200, 255
RED = 255, 0, 0
ORANGE = 227,119, 26
GREEN = 0, 255, 0
GREY = 158,158,158
ORANGETEST= 204,21,21
ORANGEFONCE= 179, 94, 37
GRISFONCE = 63, 63, 63
angleIHM = ""

PortUSBRotor = ("/dev/ttyUSB0")
PortUSBGPS = ("/dev/ttyUSB1")

## ----- Asservissement ----- ##
    
class Asservissement:
    """Classe pour l'asservissement du placement de la parabole"""

    def __init__(self, rotorSerial, verinSerial):
        """Création d'un objet d'asservissement"""
        if rotorSerial is not None:
            if verinSerial is not None:
                self.algo = 1
                self.puissance = 0
                self.bruit = 0
                self.objet = 'R'
                self.sensRotor = 'H'
                self.sensVerin = 'M'
                self.changementDeSens = 0
                self.changementObjet = 0
                self.angleRotor = 0
                self.finAlgo = 0
                print("Demarage de l'asservissement'")
            else:
                self.algo = None
                print("Algorithme non opérationel. Verin non connecté")
        else:
            self.algo = None
            print("Algorithme non opérationel. Rotor non connecté")

    def algorithme(self):
        """algo"""
        if self.algo is not None:
            self.angleRotor = afficher()
            newPuissance, bruit = getData()
            if bruit < 20:
                #Si c'est le Rotor qui doit bouger# 
                while self.finAlgo != 1 :
                    if self.objet == 'R':
                        if (self.puissance <= newPuissance and self.sensRotor == 'H') or (self.puissance > newPuissance and self.sensRotor == 'A'):
                            if self.sensRotor == 'H':
                                self.angleRotor = angleRotor - 1
                                self.sens = 'A'
                            else:                               
                                self.angleRotor = angleRotor + 1
                                self.sens = 'H'
                            self.changementDeSens = self.changementDeSens + 1


                        if self.angleRotor >= 360:
                            self.angleRotor == 0

                        if self.angleRotor < 0:
                            self.angleRotor == 360

                        rotor.tourner(self.angleRotor)
                        self.puissance = newPuissance

                    #Si c'est le Verin qui doit bouger#
                    if self.objet == 'V':
                        if (self.puissance <= newPuissance and self.sensVerin == 'M') or (self.puissance > newPuissance and self.sensVerin == 'D'):
                            if self.sensVerin == 'M':
                                verin.Descendre()
                                self.sensVerin = 'D'
                            else:
                                verin.Monter()
                                self.sensVerin = 'M'
                            self.changementDeSens = self.changementDeSens + 1
                        verin.Impulsion(1)
                        self.puissance = newPuissance
                    #Si il y a eu 4 changement de sens sur un objet, on change d'objet#
                    if self.ChangementDeSens == 4:
                        if self.objet == 'R':
                            self.objet = 'V'
                        else:
                            self.objet = 'R'
                        self.changementObjet = self.ChangementObjet + 1
                        self.changementDeSens = 0
                    #Si il y a eu 4 changement d'objet, on considére que la parabole est bien positionnée donc fin de l'algorithme#
                    if self.changementObjet == 4:
                        self.finAlgo = 1
                    else:
                        self.finAlgo = 0
                    #Tempo
                    time.sleep(1)
                print("Parabole parfaitement placée")

    def getFinAlgo(self):
        return self.finAlgo

## ----- Rotor ----- ##
class Rotor:
    def __init__(self, chemin):
        try:
            self.ser = serial.Serial(chemin)
            self.config()
        except serial.SerialException: # L'ERC n'est pas connecté
            print ("L'ERC n'est pas connecté")
            PortUSBRotor = ("/dev/ttyUSB1")
            PortUSBGPS = ("/dev/ttyUSB0") 
            self.ser = serial.Serial(PortUSBRotor)
            self.config()

    def tourner(self, angle):
        if self.ser is not None:
            angle = int(angle)
            if (angle < 100 & angle >10 ):
                commande = "M0" + repr(angle) + "\r\n"

            elif (angle >= 100):
                commande = "M" + repr(angle) + "\r\n"
            elif (angle < 10):
                commande = "M00" + repr(angle) + "\r\n"

            #print(commande)
            self.ser.write(commande.encode('latin-1'))

    def angle(self):
        if self.ser is not None:
            self.ser.write(b'C\r')
            return int(self.ser.readline())
        else:
            return None

    def tournerHoraire(self):
        if self.ser is not None:
            cmd = "R\r\n"
            self.ser.write(cmd.encode('latin-1'))

    
        
    def tournerAntiHoraire(self):
        angle = self.ser.write(b'C2\r\n')
        if self.ser is not None:
            print (angle)
            print ("Rotation commence")
            if(angle-5<0):
                rotor.tourner(0)
            else:
                rotor.tourner(angle-5)
            print ("fin de rotation")
            
##    def tournerAntiHoraire(self):
##        tournerAGauche(self.ser.write(b'C2\r\n'))
        
    def stop(self):
        if self.ser is not None:
            self.ser.write(b'S\r\n')

    def calibrationDroite(self):
        if self.ser is not None:
            #input('Deplacez le rotor dans la position la plus horaire (360°)')
            print ('Deplacez le rotor dans la position la plus horaire (360°)')
            sleep(3)
            self.ser.write(b'sCAR0360\r\n')
            print ('Calibration Droite Ok ')

    def calibrationGauche(self):
        if self.ser is not None:
            #input('Deplacez le rotator dans la position la plus anti-horaire (0°)')
            print ('Deplacez le rotor dans la position la plus horaire (0°)')
            sleep(3)
            self.ser.write(b'sCAL0000\r\n')
            print ('Calibration Gauche OK')

    def config(self):
        if self.ser is not None:
            self.ser.write(b'sSPA0000\r')
            self.ser.write(b'sSPL0003\r')
            self.ser.write(b'sSPH0003\r')

rotor=Rotor(PortUSBRotor)

## ----- Verin ----- ##
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
        self.compteur = 0
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
        print("arreter")

verin = Verin(10, 8, 12)

## ----- Button ----- ##
class Button:
    """cette classe permet de créer des boutons"""
    def __init__(self, fond, text,colortxt, color, font, dx, dy, visible):
        """On créé le bouton avec: la fenetre où il est créé, son texte, la couleur du texte, la couleur du fond, sa police d'écriture, sa position, et sa visibilité ou non"""
        self.fond = fond
        self.text = text
        self.color = color
        self.font = font
        self.dec = dx, dy
        self.etat = False
        self.state = visible  # enable or not
        self.title = self.font.render(self.text, True, colortxt)
        textpos = self.title.get_rect()
        textpos.centerx = self.fond.get_rect().centerx + self.dec[0]
        textpos.centery = self.dec[1]
        self.textpos = [textpos[0], textpos[1], textpos[2], textpos[3]]
        self.rect = pygame.draw.rect(self.fond, self.color, self.textpos)
        self.fond.blit(self.title, self.textpos)

    def update_button(self, fond, action=None):
        """effectue l'action lors de la pression du bouton et permet un retour visuel de l'appuis"""

        self.fond = fond
        mouse_xy = pygame.mouse.get_pos()
        over = self.rect.collidepoint(mouse_xy)
        if(self.state):

            if (over and not self.etat):
                action()
                self.etat = True
                if self.color == ORANGE:
                    self.color = ORANGEFONCE

                if self.color == BLACK:
                    self.color = RED

            # action()
            # à la bonne couleur
            else:
                if(self.etat):
                    action()
                self.etat = False
                #print(self.text, self.color, ORANGEFONCE, ORANGE)
                if self.color == ORANGEFONCE:
                    self.color = ORANGE


                if self.color == RED:
                    self.color = BLACK

            self.rect = pygame.draw.rect(self.fond, self.color, self.textpos)
            self.fond.blit(self.title, self.textpos)

    def display_button(self, fond):
        """dessine le bouton s'il est visisble"""
        if(self.state):
            self.fond = fond
            self.rect = pygame.draw.rect(self.fond, self.color, self.textpos)
            self.fond.blit(self.title, self.textpos)

    def destroy_button(self):
        """supprime le bouton"""
        self.text = ""
        self.state = False

## ----- IHM ----- ##
class IHM:
    """Classe permettant de gérer toute l'interface"""
    def __init__(self):
        self.screen = pygame.display.set_mode((720,480))#(720,480))
        self.loop = True
        #print(self.screen.get_size())
        self.mouse_cursor_visible = False
        # Définition de la police
        self.big = pygame.font.SysFont('Helvetica',45)
        self.small = pygame.font.SysFont('Helvetica',25)
        self.PoliceBouttons = pygame.font.SysFont('Helvetica',60)

        self.create_fond()
        self.create_button()
        azimPara, elevPara, lat, longi = GPS()
        self.azimPara = azimPara
        self.elevPara = elevPara
        self.lat = lat
        self.longi = longi
        #self.update_textes(self)
    def update_textes(self):
        #print angleIHM
        self.textes = [["Positionnement de l'Antenne",WHITE, self.big,0,15,True],
                        ["Azimuth de la parabole : " + str(int(self.azimPara)),WHITE, self.small,-200,60,True],
                        ["Elevation de la parabole : " + str(int(self.elevPara)),WHITE, self.small,-200,100,True],
                        ["Latitude : "+ str(int(self.lat)), WHITE, self.small,-280,140,True],
                        ["Longitude : "+ str(int(self.longi)),WHITE, self.small,-280,180,True],
                        ["Nord magnetique : "+angleIHM,WHITE,self.small,200,200,True],
                        ["Mettez le rotor a 0 degre",WHITE, self.big,0,100,False]]

    def create_fond(self):
        # Image de la taille de la fenêtre
        self.fond = pygame.Surface(self.screen.get_size())
        self.fond.fill(GREY)
    def image(self):
        strategic = pygame.image.load("/home/pi/Desktop/StrategicTelecom.png").convert_alpha()
        strategic = self.fond.blit(strategic, (650,0))
        pass
    def rect(self):
        if(self.textes[2][5]):  paraelev = pygame.draw.rect(self.fond,WHITE, [0,88,315,25],2)
        if(self.textes[1][5]):  paraazi  = pygame.draw.rect(self.fond,WHITE, [0,48,315,25],2)
        if(self.textes[4][5]):  satangle = pygame.draw.rect(self.fond,WHITE, [0,128,315,25],2)
        if(self.textes[3][5]):  satelev = pygame.draw.rect(self.fond,WHITE, [0,168,315,25],2)

    def create_button(self):
        self.verin_baisse = Button(self.fond, " ^ ",BLACK, ORANGE, self.PoliceBouttons,-260,330, True)
        self.verin_hausse = Button(self.fond, " v ", BLACK, ORANGE, self.PoliceBouttons,-260 , 450, True)
        self.rotor_horaire  = Button(self.fond, " < ", BLACK, ORANGE, self.PoliceBouttons,-325,390, True)
        self.rotor_antihoraire = Button(self.fond, " > ", BLACK,ORANGE, self.PoliceBouttons,-198,390, True)
        self.numero0 = Button(self.fond, " 0 ", BLACK, ORANGE, self.PoliceBouttons, 260 , 450, True)
        self.numero1 = Button(self.fond, " 1 ",  BLACK, ORANGE, self.PoliceBouttons, 200 , 270, True)
        self.numero2 = Button(self.fond, " 2 ",  BLACK, ORANGE, self.PoliceBouttons, 260 , 270, True)
        self.numero3 = Button(self.fond, " 3 ",  BLACK, ORANGE, self.PoliceBouttons, 320 , 270, True)
        self.numero4 = Button(self.fond, " 4 ",  BLACK, ORANGE, self.PoliceBouttons, 200 , 330, True)
        self.numero5 = Button(self.fond, " 5 ",  BLACK, ORANGE, self.PoliceBouttons, 260 , 330, True)
        self.numero6 = Button(self.fond, " 6 ",  BLACK, ORANGE, self.PoliceBouttons, 320 , 330, True)
        self.numero7 = Button(self.fond, " 7 ",  BLACK, ORANGE, self.PoliceBouttons, 200 , 390, True)
        self.numero8 = Button(self.fond, " 8 ",  BLACK, ORANGE, self.PoliceBouttons, 260 , 390, True)
        self.numero9 = Button(self.fond, " 9 ",  BLACK, ORANGE, self.PoliceBouttons, 320 , 390, True)
        self.valider = Button(self.fond, " V ",  BLACK, ORANGE, self.PoliceBouttons, 320 , 457, True)
        self.nouveau = Button(self.fond, " C ",  BLACK, ORANGE, self.PoliceBouttons, 200 , 457, True)
        self.quitter = Button(self.fond, " QUITTER ", WHITE, BLACK, self.big, 0, 450, True)
        self.auto = Button(self.fond, " AUTO ", WHITE, BLACK, self.big, 0,390, True)
        self.Calibration = Button(self.fond, " CALIBRATION ", WHITE, BLACK, self.big, 0,330, True)
        self.Valider = Button(self.fond, " VALIDER ", WHITE, BLACK, self.big, 0,250, False)
        #self.auto_verin = Button(self.fond, " AUTO VERIN  ", RED, self.small,100,200)


    def display_text(self, text, color, font, dx, dy, visible):
        '''Ajout d'un texte sur fond. Décalage dx, dy par rapport au centre.
        '''
        if(visible):
            mytext = font.render(text, True, color)  # True pour antialiasing
            textpos = mytext.get_rect()
            textpos.centerx = self.fond.get_rect().centerx + dx
            textpos.centery = dy
            self.fond.blit(mytext, textpos)

    def affichage_variable(self):
        angle_afficher = afficher()
        print (angle_afficher)
        #mettre angle sur ihm
        myfont = pygame.font.SysFont("Helvetica", 35)
        angle_screen = myfont.render(str(angle_afficher), 1, (255,255,0))
        self.screen.blit(angle_screen, (100, 100))

    def infinite_loop(self):
        self.update_textes()
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
            self.auto.display_button(self.fond)
            self.Calibration.display_button(self.fond)
            self.Valider.display_button(self.fond)
            #self.auto_verin.display_button(self.fond)

            for event in pygame.event.get():


                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.rotor_horaire.update_button(self.fond, action=rotorhor)
                    self.rotor_antihoraire.update_button(self.fond, action=rotorant)
                    self.verin_baisse.update_button(self.fond, action=monterverin)
                    self.verin_hausse.update_button(self.fond, action=baisserverin)
                    self.quitter.update_button(self.fond, action=Quitter)
                    self.valider.update_button(self.fond,action=auto)
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
                    self.auto.update_button(self.fond, action=Affinement)
                    self.Calibration.update_button(self.fond, action = calibrationRotor)
                    self.Valider.update_button(self.fond, action = valider)
                    #self.auto_verin.update_button(self.fond, action=auto_verin)
                    #self.affichage_variable()
                    #self.update_textes()

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.rotor_horaire.update_button(self.fond, action=stop )
                    self.rotor_antihoraire.update_button(self.fond, action=stop  )
                    self.verin_baisse.update_button(self.fond, action=stop  )
                    self.verin_hausse.update_button(self.fond, action=stop  )
                    self.quitter.update_button(self.fond, action=actionVide  )
                    self.valider.update_button(self.fond, action=actionVide )
                    self.nouveau.update_button(self.fond, action=actionVide  )
                    self.numero0.update_button(self.fond, action=actionVide  )
                    self.numero1.update_button(self.fond, action=actionVide  )
                    self.numero2.update_button(self.fond, action=actionVide  )
                    self.numero3.update_button(self.fond, action=actionVide  )
                    self.numero4.update_button(self.fond, action=actionVide  )
                    self.numero5.update_button(self.fond, action=actionVide  )
                    self.numero6.update_button(self.fond, action=actionVide  )
                    self.numero7.update_button(self.fond, action=actionVide  )
                    self.numero8.update_button(self.fond, action=actionVide  )
                    self.numero9.update_button(self.fond, action=actionVide  )
                    self.auto.update_button(self.fond, action=actionVide  )
                    self.Calibration.update_button(self.fond, action = actionVide)
                    self.Valider.update_button(self.fond, action = actionVide)

            #self.update_textes()
            #print azim

            self.rect()
            self.image()
            for text in self.textes:
                self.display_text(text[0], text[1], text[2],text[3],text[4],text[5])

            # Ajout du fond dans la fenêtre
            self.screen.blit(self.fond, (0, 0))
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
    
def calibrationRotor():
    #Larcay.create_fond()
    Larcay.Valider.display_button(Larcay.fond)
    Larcay.Valider.state = True


    Larcay.verin_baisse.destroy_button()
    Larcay.verin_hausse.destroy_button()
    #Larcay.rotor_horaire.destroy_button()
    #Larcay.rotor_antihoraire.destroy_button()
    Larcay.numero0.destroy_button()
    Larcay.numero1.destroy_button()
    Larcay.numero2.destroy_button()
    Larcay.numero3.destroy_button()
    Larcay.numero4.destroy_button()
    Larcay.numero5.destroy_button()
    Larcay.numero6.destroy_button()
    Larcay.numero7.destroy_button()
    Larcay.numero8.destroy_button()
    Larcay.numero9.destroy_button()
    Larcay.valider.destroy_button()
    Larcay.nouveau.destroy_button()
    Larcay.auto.destroy_button()
    Larcay.Calibration.destroy_button()

    Larcay.textes[0][0] = "Calibration du rotor"
    Larcay.textes[1][5] = False
    Larcay.textes[2][5] = False
    Larcay.textes[3][5] = False
    Larcay.textes[4][5] = False
    Larcay.textes[5][5] = False
    Larcay.textes[6][5] = True

    # rotor.config()
    # #effecer écran  afficher txt + boutton valider
    # while(Valider.etat):
    #     pass
    # #Appuie sur bouton
    # #Affichage du texte calibraion à 0
    # while(not Valider.etat):
    #     pass
    # rotor.calibrationGauche() #0
    # #Affichage du texte calibraion à 360
    # #Appuie sur bouton
    # while(Valider.etat):
    #     pass
    # while(not Valider.etat):
    #     pass
    # rotor.calibrationDroite() #360
    # #Remise de l'écran initial

garder =  []

def nouveau():
    global angleIHM
    del garder[0:100]
    #print("av reset", angleIHM)
    angleIHM=""
    print("reset", angleIHM)
    Larcay.update_textes()
    return garder

def saisie(para):
    global angleIHM
    garder.append(para)
    del garder[3:100000]
    print (garder)
    angleIHM = ""
    #print(len(garder))

    for i in garder:
        angleIHM += i
    print(angleIHM)
    Larcay.textes[5][0] = "Nord magnetique : "+angleIHM
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

def actionVide():
    pass

def afficher():#Recuperation du nord magnétique 
     total = []
     total = saisie("")
     total.append("")
     total.append("")
     total.append("")
     premier_chiffre = total[0]
     second_chiffre = total[1]
     troisieme_chiffre= total[2]
     Angle = premier_chiffre+second_chiffre+troisieme_chiffre
     #print(Angle)
     return float(Angle)+Larcay.azimPara #Angle GPS + Décalage Nord Magnétique
##
def auto():
    auto_angle = afficher()
    a,b,c,d = GPS()
    print (b)

    #============================================Placement Approximatif==============================================

    rotor.tourner(auto_angle)
    verin.descendre()
    sleep(90)
    print ("lancement verin")
    verin.compteur = 0
    while verin.compteur*0.057+10 <= Larcay.elevPara:
        verin.monter()
        print (verin.compteur)
    #sleep(1.5*b)
    verin.stop
    #================================================================================================================


def GPS():
    gps = serial.Serial(PortUSBGPS, 4800)#configuration du port serie avec un bauderate 4800
    nmea = gps.readline() #on  lis la ligne ou est present la trame NMEA

    print ("On rentre dans GPS")
    while nmea[0:6] != "$GPGGA": #On compare la trame GPGGA
        print ("Recherche de sinal GPS...")
        nmea = gps.readline()
    print ("Signal trouve")
    gpsData = pynmea2.parse(nmea) #On parcoure la trame qu'on affecte a une variable gpsDATA
    #global lata #Variable global utilisé pour l'algo suivant
    #global longitu #Variable longitude  utilise pour l'algo suivant
    lata = float(gpsData.latitude) #permet de retrouver  dans notre trame la latitude et la traduire
    longitu = float(gpsData.longitude)#permet de retrouver dans notre trame la latitude et la traduire
    print ('latitude = ' , lata)
    print ('longitude = ' , longitu)
    print("Fix" if gpsData.gps_qual else "No fix")
    print("Sats : " + gpsData.num_sats)
        #return lata,longitu #on retourne ces deux variables pour le futur programme
        #gps.close()
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
    print (lat)
    print (longi)
    print ("valeur azimuth pointer ",algoazimuth)
    print ("valeur  elevation ou pointer ",algoelevation)
    return algoazimuth,algoelevation,lat,longi

def auto_verin():
    total_verin = int(afficher())
    auto_verin = total_verin*1.5
    print (auto_verin)
    verin.descendre()
    sleep(90)
    verin.monter()
    sleep(auto_verin)
    print ("Verin monté")
    verin.arreter()


def Affinement() :
    asservissement =Asservissement(PortUSBRotor,PortUSBGPS)
    asservissement.algorithme()

def valider():
    if(Larcay.textes[6][0]=="Mettez le rotor a 0 degre"):
        rotor.calibrationGauche()
        Larcay.textes[6][0]="Mettez le rotor a 360 degre"
        print("0 fait")
    else:
        rotor.calibrationDroite()
        print("360 fait")
        Larcay.textes[6][5]=False
        Larcay.Valider.state = False
        Larcay.Valider.etat = False

        Larcay.textes[6][0]="Mettez le rotor a 0 degre"

        Larcay.verin_baisse.state = True
        Larcay.verin_hausse.state = True
        #Larcay.rotor_horaire.state = True
        #Larcay.rotor_antihoraire.state = True
        Larcay.numero0.state = True
        Larcay.numero1.state = True
        Larcay.numero2.state = True
        Larcay.numero3.state = True
        Larcay.numero4.state = True
        Larcay.numero5.state = True
        Larcay.numero6.state = True
        Larcay.numero7.state = True
        Larcay.numero8.state = True
        Larcay.numero9.state = True
        Larcay.valider.state = True
        Larcay.nouveau.state = True
        Larcay.auto.state = True
        Larcay.Calibration.state = False

        Larcay.textes[0][0] = "Positionnement de l'Antenne"
        Larcay.textes[1][5] = True
        Larcay.textes[2][5] = True
        Larcay.textes[3][5] = True
        Larcay.textes[4][5] = True
        Larcay.textes[5][5] = True
        Larcay.textes[6][5] = False

def Quitter():
    print("Quit")
    rotor.ser.write('M000\r\n')
##    verin.descendre()
##    sleep(90)
##    verin.stop()
    pygame.quit()
##    sys.exit()
def getData():
    data = []
    r = requests.get("http://192.168.100.1/index.cgi?page=modemStatusData")
    data = r.text.split("##")
    rxPower = data[14]
    rxSNR =data[11]
    return rxPower,rxSNR
if __name__ == '__main__':
    Larcay = IHM()
    Larcay.infinite_loop()
    print ("Affichage variable")
    Larcay.affichage_variable()
    main()

