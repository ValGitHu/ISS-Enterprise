#!/bin/bash

# Mises a jour initiales
sudo apt-get update
sudo apt-get -y --force-yes upgrade

# Installation de Python et Pip
sudo apt-get -y --force-yes install python-pip
sudo apt-get -y --force-yes install python-pygame

# Dependances pour le bon fonctionnement de l'ecran tactile avec Pygame
# Activation des sources de paquets Wheezy
echo "deb http://archive.raspbian.org/raspbian wheezy main
" > /etc/apt/sources.list.d/wheezy.list
 
# Reglage de la source des paquets par defaut comme wheezy
echo "APT::Default-release \"oldstable\";
" > /etc/apt/apt.conf.d/10defaultRelease
 
# Reglage de la priorite de libsdl wheezy superieure a celle du paquet jessie
echo "Package: libsdl1.2debian
Pin: release n=jessie
Pin-Priority: -10
Package: libsdl1.2debian
Pin: release n=wheezy
Pin-Priority: 900
" > /etc/apt/preferences.d/libsdl
 
# Installation de SDL 1.2
apt-get update
apt-get -y --force-yes install libsdl1.2debian/wheezy

# Installation de la bibliotheque Python PySerial (communication avec le GPS & l'ERC V4)
sudo python -m pip install pyserial
# Installation de la bibliotheque Python Pynmea2 (exploitation des trames GPS)
sudo pip install pynmea2
# Installation de la bibliotheque Python bitstring (conversion des valeurs de la boussole)
sudo pip install bitstring
# Installation de la bibliotheque Python smbus2 (communication avec la boussole)
sudo pip install smbus2

# Installation de la bibliotheque Python GUI PGU
wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/pgu/pgu-0.18.zip
sudo pip install pgu-0.18.zip

# Nettoyage
rm pgu-0.18.zip