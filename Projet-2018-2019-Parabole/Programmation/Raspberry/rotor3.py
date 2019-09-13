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
			if (angle <100):
				commande = "M0" + repr(angle) + "\r\n"

			else:
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
			input('Déplacez votre rotor dans le sens des aiguilles d\'une montre (360°)');
			self.ser.write(b'sCAR0360\r\n')

	def calibrationGauche(self):
		if self.ser is not None:
			input('Déplacez le rotator dans la position la plus anti-horaire (0°)')
			self.ser.write(b'sCAL0000\r\n')

	def config(self):
		if self.ser is not None:
			self.ser.write(b'P36\r\n')
			self.ser.write(b'sSPA0000\r\n')
			self.ser.write(b'sSPL0004\r\n')
			self.ser.write(b'sSPH0004\r\n')
			self.ser.write(b'sTOL002\r\n')
			self.ser.write(b'sAOF000\r\n')


rotor = Rotor("/dev/ttyUSB1")

rotor.config()
rotor.calibrationGauche()
rotor.calibrationDroite()

angle=input('Valeur en degrés :')

rotor.tourner(angle)
