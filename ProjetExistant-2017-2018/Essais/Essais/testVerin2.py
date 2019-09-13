from RPi import GPIO
from time import *
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
gpio1 = 8
gpio2 = 10
gpio3 = 12
gpio4 = 16
GPIO.setup(gpio1,GPIO.OUT)
GPIO.setup(gpio2,GPIO.OUT)
GPIO.setup(gpio3,GPIO.OUT)
GPIO.setup(gpio4, GPIO.OUT)

while True:
	GPIO.output(gpio1, GPIO.LOW)
	GPIO.output(gpio2, GPIO.LOW)
	GPIO.output(gpio3, GPIO.LOW)
	GPIO.output(gpio4, GPIO.LOW)
	sleep(1)
	GPIO.output(gpio1, GPIO.HIGH)
	sleep (1)
	GPIO.output(gpio1, GPIO.LOW)
	GPIO.output(gpio2, GPIO.HIGH)
	sleep(1)
	GPIO.output(gpio1, GPIO.HIGH)
	sleep(1)
	GPIO.output(gpio1, GPIO.LOW)
	GPIO.output(gpio2, GPIO.LOW)
	GPIO.output(gpio3, GPIO.HIGH)
	GPIO.output(gpio4, GPIO.HIGH)
	sleep(1)
	GPIO.output(gpio1, GPIO.HIGH)
	sleep(1)
	GPIO.output(gpio1, GPIO.LOW)
	GPIO.output(gpio2, GPIO.HIGH)
	sleep(1)
	GPIO.output(gpio1, GPIO.HIGH)
	sleep(1)


def monte():
    GPIO.output(mont,GPIO.HIGH)
    GPIO.output(desc,GPIO.LOW)

def descendre():
    GPIO.output(mont,GPIO.LOW)
    GPIO.output(desc,GPIO.HIGH)

def arret():
    GPIO.output(mont,GPIO.LOW)
    GPIO.output(desc,GPIO.LOW)

#while True:
    
#    descendre()
#    time.sleep(3)
#    arret()
#    time.sleep(3)
