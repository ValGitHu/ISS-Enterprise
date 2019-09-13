#!/usr/bin/python
# coding: utf-8

import pygame
from pygame.locals import *
import os
import sys
from time import sleep
from helpers import *
from RPi import GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

import serial
import pynmea2
import string

# ----- GPS ----- #
class GPS(object):
	def __init__(self, path):
		try:
			self.gps = serial.Serial(path, 4800)
			self.gps.readline() # On se place au début d'une trame
		except serial.SerialException: # Le GPS n'est pas connecté
			self.gps = None

		self.data = None

	def __del__(self):
		if self.gps is not None:
			self.gps.close()

	def getInfos(self):
		if self.gps is not None:
			while self.gps.in_waiting > 0:
				serialBuffer = self.gps.readline()
				if serialBuffer[0:6] == "$GPGGA":
					self.data = pynmea2.parse(serialBuffer)

			return self.data
		else:
			return None

# ----- Rotor ----- #
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
gps = GPS("/dev/ttyUSB0")

# Rotor initialization
rotor = Rotor("/dev/ttyUSB1")

# Vérin initialization
verin = Verin(10, 8, 12)

# Check if executed with root access
if not "SUDO_UID" in os.environ.keys():
	print("Veuillez exécuter ce programme avec les droits root : sudo ./parabole.py")
	sys.exit(1)

# Colors
WHITE = (255, 255, 255)

# Screen setup
os.putenv("SDL_FBDEV", "/dev/fb1")
os.putenv("SDL_MOUSEDRV", "TSLIB")
os.putenv("SDL_MOUSEDEV", "/dev/input/touchscreen")

# Pygame initialization and configuration
pygame.init()
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
lcd = pygame.display.set_mode((480, 320)) # Taille de la fenêtre
lcd.fill((229, 50, 46))                   # Couleur d'arrière-plan
pygame.display.update()
font = pygame.font.Font(None, 30)

# Format des boutons : "Label": ((x, y), (w, h), TaillePolice, callback())
buttonsDef = {
	("^",    (340, 110), (70, 70), 100),
	(">",    (410, 180), (70, 70), 100),
	("v",    (340, 250), (70, 70), 100),
	("<",    (270, 180), (70, 70), 100),
	("Auto", (350, 190), (50, 50), 30),
}

buttons = []
for button in buttonsDef:
	btn = makeButton(button)
	buttons.append(btn)
	lcd.blit(btn[0], btn[1])

# GPS informations
gpsInfosLabel = pygame.font.Font(None, 30).render("Informations GPS", True, WHITE)
lcd.blit(gpsInfosLabel, gpsInfosLabel.get_rect().move((10, 10)))
gpsInfosSurface = pygame.Surface((320, 70))

# Antenna's position and signal strength
antennaPosLabel = pygame.font.Font(None, 30).render("Position parabole", True, WHITE)
lcd.blit(antennaPosLabel, antennaPosLabel.get_rect().move((10, 120)))
antennaPosSurface = pygame.Surface((250, 70))

# Compass
compassLabel = pygame.font.Font(None, 30).render("Boussole", True, WHITE)
lcd.blit(compassLabel, compassLabel.get_rect().move((10, 230)))
compassSurface = pygame.Surface((250, 30))

# Logo
logo = pygame.image.load("images/StrategicTelecom.png").convert_alpha()
logo = pygame.transform.scale(logo, (76, 76))
rect = logo.get_rect()
rect = rect.move((405, 0))
lcd.blit(logo, rect)

# Zone
zone = pygame.image.load("images/zoneInconnue.png").convert_alpha()
zoneRect = zone.get_rect()
zoneRect = zoneRect.move((340, 10))
lcd.blit(zone, zoneRect)

pygame.display.update()

zone2 = 0
timer = 0
showZone = False

def positionnementAuto():
	rotor.tourner(90)
	print("Tourner rotor à 90 deg")
	while rotor.angle() < 85: pass
	verin.monter()
	print("Monter verin 20s")
	sleep(20)
	verin.descendre()
	print("Descendre verin 10s")
	sleep(10)
	verin.monter()
	print("Monter verin 7s")
	sleep(7)
	verin.descendre()
	print("Descendre verin 5s")
	sleep(5)
	verin.monter()
	print("Monter verin 2s")
	sleep(2)
	verin.descendre()
	print("Descendre verin 1s")
	sleep(1)
	verin.monter()
	sleep(1)
	verin.descendre()
	sleep(0.8)
	verin.monter()
	sleep(0.5)
	verin.arreter()
	print("Termine")

while True:
	clock.tick(5)
	timer = timer + 1

	gpsData = gps.getInfos()

	# Zone image
	if (zone2 == 0):
		if timer % 5 == 0:
			if showZone:
				showZone = False
				pygame.draw.rect(lcd, (229, 50, 46), zoneRect)
			else:
				showZone = True
				lcd.blit(zone, zoneRect)

			if gpsData is not None: # Debug
				print("Lat : " + "%02do%02d'%07.4f\"" % (gpsData.latitude, gpsData.latitude_minutes, gpsData.latitude_seconds))
				print("Lon : " + "%02do%02d'%07.4f\"" % (gpsData.longitude, gpsData.longitude_minutes, gpsData.longitude_seconds))
				print("Fix" if gpsData.gps_qual else "No fix")
				print("Sats : " + gpsData.num_sats)

	# Get GPS informations
	gpsData = gps.getInfos()
	if gpsData is not None:
		gpsInfosSurface.fill((127, 0, 0))

		gpsInfosText = font.render("Nombre de satellites : " + gpsData.num_sats, True, WHITE)
		gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect())
		if gpsData.gps_qual:
			gpsInfosText = font.render("Latitude : %02d deg %02d' %07.4f\"" % (gpsData.latitude, gpsData.latitude_minutes, gpsData.latitude_seconds), True, WHITE)
			gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect().move((0, 20)))
			gpsInfosText = font.render("Longitude : %02d deg %02d' %07.4f\"" % (gpsData.longitude, gpsData.longitude_minutes, gpsData.longitude_seconds), True, WHITE);
			gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect().move((0, 40)))
		else:
			gpsInfosText = font.render("Pas de fix", True, WHITE)
			gpsInfosSurface.blit(gpsInfosText, gpsInfosText.get_rect().move((0, 30)))

		gpsInfosRect = gpsInfosSurface.get_rect().move((10, 40))
		lcd.blit(gpsInfosSurface, gpsInfosRect)

	pygame.display.update()


	# Antenna informations
        antennaPosSurface.fill((127, 0, 0))
        antennaPosText = font.render("Azimut : {} deg".format(rotor.angle()), True, WHITE)
        antennaPosSurface.blit(antennaPosText, antennaPosText.get_rect())
        antennaPosText = font.render("Elevation : {}".format(verin.compteur / 10.0), True, WHITE)
        antennaPosSurface.blit(antennaPosText, antennaPosText.get_rect().move((0, 20)))
	antennaPosText = font.render("Puissance signal : N/A".format(-12), True, WHITE)
	antennaPosSurface.blit(antennaPosText, antennaPosText.get_rect().move((0, 40)))

        lcd.blit(antennaPosSurface, antennaPosSurface.get_rect().move((10, 150)))

	# Compass informations
	compassSurface.fill((127, 0, 0))
	compassText = font.render("Cap : {} deg".format(183), True, WHITE)
	compassSurface.blit(compassText, compassText.get_rect())

	lcd.blit(compassSurface, compassSurface.get_rect().move((10, 260)))

	# Scan touchscreen events
	for event in pygame.event.get():
		if event.type is MOUSEBUTTONDOWN or event.type is MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()

			for button in buttons:
				if button[1].collidepoint(pos):
					if button[2] == "<": # Tourner rotor sens anti-horaire
						if event.type is MOUSEBUTTONDOWN:
							print("tourner")
							rotor.tournerAntiHoraire()
						elif event.type is MOUSEBUTTONUP:
							print("stop")
							rotor.stop()

					if button[2] == ">": # Tourner rotor sens horaire
						if event.type is MOUSEBUTTONDOWN:
							rotor.tournerHoraire()
						elif event.type is MOUSEBUTTONUP:
							rotor.stop()

					if button[2] == "^": # Monter parabole (sortir vérin)
						if event.type is MOUSEBUTTONDOWN:
							verin.monter()
							print("Monter")
						elif event.type is MOUSEBUTTONUP:
							verin.arreter()
							print("Stop")

					if button[2] == "v": # Descendre parabole (rentrer vérin)
						if event.type is MOUSEBUTTONDOWN:
							verin.descendre()
						elif event.type is MOUSEBUTTONUP:
							verin.arreter()

					if button[2] == "Auto": # Lancement de la procédure de positionnement automatique
						if event.type is MOUSEBUTTONDOWN:
							positionnementAuto()
						elif event.type is MOUSEBUTTONUP:
							pass
