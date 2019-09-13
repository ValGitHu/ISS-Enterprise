import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
#GPIO.setup(12, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.output(8, GPIO.LOW)
GPIO.output(10, GPIO.LOW)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
from time import sleep

compteur = 0
increment = 1
stop = False
def impulsion(channel):
	global compteur, increment, stop
	compteur += increment
	print("Impulsion {}".format(compteur))
	if compteur == 100:
		stop = True

GPIO.add_event_detect(12, GPIO.FALLING, callback=impulsion, bouncetime=100)

try:
	GPIO.output(8, GPIO.HIGH)
	while not stop:
		pass
		"""increment = 1
		GPIO.output(8, GPIO.HIGH)
		sleep(1)
		GPIO.output(8, GPIO.LOW)
		sleep (1)
		increment = -1
		GPIO.output(10, GPIO.HIGH)
		sleep(1)
		GPIO.output(10, GPIO.LOW)
		sleep(1)"""


except KeyboardInterrupt:
	GPIO.cleanup()
GPIO.cleanup()
