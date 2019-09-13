# -*- coding: utf-8 -*-

import serial
import pynmea2
from time import sleep

gps = serial.Serial('/dev/ttyUSB0', 4800)

class GPS(object):
	def __init__(self, path):
		self.path = path

		try:
			self.gps = serial.Serial(path, 4800)
			gps.readline() # On se place au début d'une trame
		except serial.SerialException:
			# Le GPS n'est pas connecté
			self.gps = None

	def __del__(self):
		if self.gps is not None:
			self.gps.close()

	def getInfos(self):
		if self.gps is not None:
			while self.gps.in_waiting > 0:
				trame = self.gps.readline()
				if trame[3:6] == "GGA":
					donnees = pynmea2.parse(trame)
					print(donnees.latitude)

while True:
	print(gps.readline())
