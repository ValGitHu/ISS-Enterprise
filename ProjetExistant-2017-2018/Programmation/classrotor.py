import serial
import time

class rotor:
    def __init__(self,chemin):
        self.chemin = chemin
        self.ser = serial.Serial('/dev/ttyUSB0')

    def tourner(self,angle):
        angle = int(angle)
        commande="M"+repr(angle)+"\r\n"
        self.ser.write(commande.encode('latin-1'))

    def tournerdroite(self):
        self.ser.write(b'R\r\n')

    def tournergauche(self):
        self.ser.write(b'L\r\n')

    def stop(self):
        self.ser.write(b'S\r\n')
        
    def calibrationdroite(self):
        self.ser.write(b'sCAR0360\r\n')

    def calibrationgauche(self):
        self.ser.write(b'sCAL0000\r\n')
                
    def calibrationconfig(self):
        self.ser.write(b'sPRO0000')
        self.ser.write(b'sSPA0001')
        self.ser.write(b'sSPL0001')
        self.ser.write(b'sSPH0003')
