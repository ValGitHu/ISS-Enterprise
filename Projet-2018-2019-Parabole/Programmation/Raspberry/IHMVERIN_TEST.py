#! /usr/bin/env python3
# -*- coding: utf-8 -*-



import serial  # acquisition des trames
#from helpers import *  # import de toutes les variables de la librairie helpers est les associe au current name space deconseillé(libraire pour dev des applis externe)
from RPi import GPIO  # gestion des gpio# server_gui.py
GPIO.setwarnings(False)  # supprime les warnings sur les gpio
GPIO.setmode(GPIO.BOARD)  # utilisation de la numérotation de serigraphie et pas celle electronique
import pygame
import sys
from math import *
#import requests
#from requests_toolbelt.utils import dump

from time import sleep

Register_A     = 0              #Address of Configuration register A
Register_B     = 0x01           #Address of configuration register B
Register_mode  = 0x02           #Address of mode register

X_axis_H    = 0x03              #Address of X-axis MSB data register
Z_axis_H    = 0x05              #Address of Z-axis MSB data register
Y_axis_H    = 0x07              #Address of Y-axis MSB data register
declination = 0.477522083#-0.00669          #define declination angle of location where measurement going to be done
pi


pygame.init()
clock = pygame.time.Clock()

BLACK = 0, 0, 0
WHITE = 255, 255, 255
CIEL = 0, 200, 255
RED = 255, 0, 0
ORANGE = 255,220, 0
GREEN = 0, 255, 0
GREY = 23,23,23
ORANGETEST= 204,21,21


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
        self.big = pygame.font.SysFont('freesans', 25)
        self.small = pygame.font.SysFont('freesans', 15)

        self.create_fond()
        self.create_button()

    def update_textes(self):
     self.textes = [["Positionement de l'Antenne",WHITE, self.big,0,10],
                            ["Azimuth de la parabole : ",WHITE, self.small,-170,50],
                            ["Elevation de la parabole : ",WHITE, self.small,-165,80],
                            ["Angle du satellite :", WHITE, self.small,-185,110],
                            ["Elevation du satellite :",WHITE, self.small,-180,140]]
    def image(self):
        strategic = pygame.image.load("StrategicTelecom.png").convert_alpha()
        strategic = self.fond.blit(strategic, (200,200))
    def rect(self):
        paraelev = pygame.draw.rect(self.fond,WHITE, [0,70,200,20],2)
        paraazi  = pygame.draw.rect(self.fond,WHITE, [0,40,200,20],2)
        satangle = pygame.draw.rect(self.fond,WHITE, [0,100,200,20],2)
        satelev = pygame.draw.rect(self.fond,WHITE, [0,130,200,20],2)

    def create_fond(self):
        # Image de la taille de la fenêtre
        self.fond = pygame.Surface(self.screen.get_size())
        # En bleu
        self.fond.fill(ORANGETEST)

    def create_button(self):

        self.verin_baisse = Button(self.fond, "  verin baisse ", ORANGE, self.small, 100, 50)
        self.verin_hausse = Button(self.fond, " verin hausse ", ORANGE, self.small,100 , 150)
        self.rotor_horaire  = Button(self.fond, "   rotor horaire ", ORANGE, self.small,20,100 )
        self.rotor_antihoraire = Button(self.fond, " rotor antihoraire",ORANGE, self.small,185,100)
        self.quitter = Button(self.fond, " QUITTER  ", RED, self.small, 200, 300)

    def display_text(self, text, color, font, dx, dy):
        '''Ajout d'un texte sur fond. Décalage dx, dy par rapport au centre.
        '''
        mytext = font.render(text, True, color)  # True pour antialiasing
        textpos = mytext.get_rect()
        textpos.centerx = self.fond.get_rect().centerx + dx
        textpos.centery = dy
        self.fond.blit(mytext, textpos)

    def infinite_loop(self):
        while self.loop:
            self.create_fond()

            # Boutons
            self.verin_baisse.display_button(self.fond)
            self.verin_hausse.display_button(self.fond)
            self.rotor_horaire.display_button(self.fond)
            self.rotor_antihoraire.display_button(self.fond)
            self.quitter.display_button(self.fond)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                        self.rotor_horaire.update_button(self.fond, action=rotorhor)
                        self.rotor_antihoraire.update_button(self.fond, action=rotorant)
                        self.verin_baisse.update_button(self.fond, action=baisserverin)
                        self.verin_hausse.update_button(self.fond, action=monterverin)

                if event.type == pygame.MOUSEBUTTONUP:
                    self.rotor_horaire.update_button(self.fond,action=stoprotor)
                    self.rotor_antihoraire.update_button(self.fond,action=stoprotor)
                    self.verin_baisse.update_button(self.fond, action= stopverin)
                    self.verin_hausse.update_button(self.fond, action= stopverin)
                    self.quitter.update_button(self.fond, action=Quitter)


            self.update_textes()
            self.rect()
            self.image()
            for text in self.textes:
                self.display_text(text[0], text[1], text[2],text[3], text[4])

            # Ajout du fond dans la fenêtre
            self.screen.blit(self.fond, (0, 0))
            # Actualisation de l'affichage
            pygame.display.update()
            # 10 fps
            clock.tick(10)

#----ROTOR CLASSE---
class Rotor:
    def __init__(self, chemin):  # constructeur avec comme argument chemin
        try:
            self.ser = serial.Serial(chemin)  # Création  de l'objet type serial
            self.config()
        except serial.SerialException:  # L'Easy Rotor Control n'est pas connecté
            self.ser = None  # la liason prend la valeur rienx

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


def stopverin():
    print("stop verin")

def stoprotor():
    print("stop rotor")

def rotorhor():
    print("rotor horaire")
    tournerhoraire()

def rotorant():
    print("rotor antihoraire")

def baisserverin():
    print("baisser verin")

def monterverin():
    print("monter verin")
    monter()

def Quitter():
    print("Quit")
    pygame.quit()
    sys.exit()




if __name__ == '__main__':
    Larcay = IHM()
    Larcay.infinite_loop()
    main()
