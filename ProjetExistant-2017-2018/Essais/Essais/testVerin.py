from RPi import GPIO
from time import sleep
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
mont = 3
desc = 5
GPIO.setup(mont,GPIO.OUT)
GPIO.setup(desc,GPIO.OUT)
GPIO.output(mont,GPIO.LOW)
GPIO.output(desc,GPIO.LOW)

def monter():
	GPIO.output(mont,GPIO.HIGH)
	GPIO.output(desc,GPIO.LOW)

def descendre():
	GPIO.output(mont,GPIO.LOW)
	GPIO.output(desc,GPIO.HIGH)

def arreter():
	GPIO.output(mont,GPIO.LOW)
	GPIO.output(desc,GPIO.LOW)

while True:
	monter()
	sleep(1)
	descendre()
	sleep(1)
