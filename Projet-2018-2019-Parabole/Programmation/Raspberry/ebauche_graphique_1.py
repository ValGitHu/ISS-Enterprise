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
			commande = "M0" + repr(angle) + "\r\n"
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

rotor=Rotor("/dev/ttyUSB0")

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
        self.textes = [["Positionement de l'Antenne",WHITE, self.big,0,10],
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
        self.verin_baisse = Button(self.fond, "  verin baisse ", ORANGE, self.small, 100, 50)
        self.verin_hausse = Button(self.fond, " verin hausse ", ORANGE, self.small,100 , 150)
        self.rotor_horaire  = Button(self.fond, "   rotor horaire ", ORANGE, self.small,20,100 )
        self.rotor_antihoraire = Button(self.fond, " rotor antihoraire",ORANGE, self.small,185,100)
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
        self.auto = Button(self.fond, " AUTO  ", RED, self.small, 100,100)


    def display_text(self, text, color, font, dx, dy):
        '''Ajout d'un texte sur fond. Décalage dx, dy par rapport au centre.
        '''
        mytext = font.render(text, True, color)  # True pour antialiasing
        textpos = mytext.get_rect()
        textpos.centerx = self.fond.get_rect().centerx + dx
        textpos.centery = dy
        self.fond.blit(mytext, textpos)

    def affichage_variable(self):
        angle_afficher = afficher()
        myfont = pygame.font.SysFont("Helvetica", 35)
        angle_screen = myfont.render(str(angle_afficher), 1, (255,255,0))
        self.screen.blit(angle_screen, (100, 100))

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

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.rotor_horaire.update_button(self.fond, action=rotorhor)
                    self.rotor_antihoraire.update_button(self.fond, action=rotorant)
                    self.verin_baisse.update_button(self.fond, action=baisserverin)
                    self.verin_hausse.update_button(self.fond, action=monterverin)
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
                    self.auto.update_button(self.fond, action=auto)


            self.update_textes()
            self.rect()
            self.image()
            for text in self.textes:
                self.display_text(text[0], text[1], text[2],text[3],text[4])

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


garder =  []

def nouveau():
    del garder[0:100]
    return garder

def saisie(para):
    garder.append(para)
    print (garder)
    return garder

def numero0():
    a = 0
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
    saisie=(d)

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

def afficher():
     total = []
     total = saisie("")
     total.append("")
     total.append("")
     total.append("")
     premier_chiffre = total[0]
     second_chiffre = total[1]
     troisieme_chiffre= total[2]
     Angle = premier_chiffre+second_chiffre+troisieme_chiffre
     print(Angle)
     return Angle
def auto():
    auto_angle = afficher()
    rotor.tourner(auto_angle)




def Quitter():
    print("Quit")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    Larcay = IHM()
    Larcay.infinite_loop()
    Larcay.affichage_variable()
    main()
