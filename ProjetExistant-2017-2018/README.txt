Installation
============

Sur un ordinateur *nix
----------------------

Flasher le système d'exploitation sur la carte microSD du Raspberry Pi (Raspbian Jessie Lite pour PiTFT 3,5" https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install) :
sudo dd if=2016-11-08-pitft-35r.img of=/dev/diskX bs=1M

Pour utiliser la connexion SSH, créer un fichier « ssh » à la racine de la partition « boot » créée :
touch ssh

Alimenter le Raspberry Pi

Mettre les fichiers « dependances.sh » et « parabole.py » sur le Raspberry Pi, par exemple en utilisant la connexion SSH avec l'adresse IP de Raspberry Pi 192.168.2.3 :
scp dependances.sh parabole.py pi@192.168.2.3:~/

Mot de passe par défaut : raspberry


Sur le Raspberry Pi (en SSH ou en direct)
-----------------------------------------
sudo raspi-config
« Expand filesystem »

sudo chmod +x dependances.sh
sudo ./dependances.sh

Éditer le fichier "/etc/rc.local"
nano /etc/rc.local
Ajouter les lignes suivantes à la fin du fichier
cd /home/pi
sudo python /home/pi/parabole.py &

Pour calibrer l'écran tactile :
sudo TSLIB_FBDEVICE=/dev/fb1 TSLIB_TSDEVICE=/dev/input/touchscreen ts_calibrate

Pour tester la calibration de l'écran tactile :
sudo TSLIB_FBDEVICE=/dev/fb1 TSLIB_TSDEVICE=/dev/input/touchscreen ts_test


Utilisation
===========

Exécution du script :
sudo ./parabole.py