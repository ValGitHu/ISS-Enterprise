import smbus #Librairie pour communication I2C
import time
from math import atan2 #pemet d'utiliser la fonction atan2
pi=3.14159265359
bus = smbus.SMBus(1)
boussole = 0x0d #adresse de la boussole 

#Initialisation de la boussole
bus.write_byte_data(boussole,0x0B,0x01)
time.sleep(0.010)
bus.write_byte_data(boussole,0x09,0x11)
time.sleep(1)

while 1:
    
    xlo=bus.read_byte_data(boussole, 0x00)#LSB X
    xhi=bus.read_byte_data(boussole, 0x01)#MSB X            
    x=(xhi << 8) + xlo
    if(x>(2**15)-1) :
        x=x-2**16    #transformer en non signé
                        
    ylo=bus.read_byte_data(boussole, 0x02)#LSB Y
    yhi=bus.read_byte_data(boussole, 0x03)#MSB Y            
    y=(yhi << 8) + ylo    
    if (y>(2**15-1)): 
        y=y-2**16   #transformer en non signé    
        
    #Calcul de l'angle en fonction des valeurs d'axes
    angle=atan2(x,y)*180/pi+180
    #Afficher les valeurs
    print("x=",x)
    print("y=",y)
    print("angle :",angle)
    time.sleep(1)