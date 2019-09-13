#coding: utf-8
import time # manque le calcul du nombre d'impulsions necessaires                 
# enlever le seuil de déclenchement haut après le premier déclanchement                               
# voir pour les commandes et la polarité                                  
# s'assurer que ça ne va pas forcer en fin de course  
from RPi import GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
mont = 16
desc = 18
GPIO.setup(mont,GPIO.OUT)
GPIO.setup(desc,GPIO.OUT)
GPIO.output(mont,GPIO.LOW)
GPIO.output(desc,GPIO.LOW)

global polarity
arretverin=0
polarity = 1
Nb_mesures=0              	# nombre de mesures effectuées
delai_mesures=0.5           	# temps laissé au vérin entre deux mesures
mesure_qte=[]             	# tableau des valeurs de la qualité du signal
erreur=0.3                	# écart entre qte_min et qte_max satisfaisant

azimuth=171                 # valeur fournie par le code identification 
elevation=35                # valeur fournie par le code identification 

qte_max=0                   # init à une valeur qu'on est sûrs d'atteindre pour la première itération
qte_min=0                   # pour la première itération
qte=0                       # qualité mesurée
seuil=1                    # init à une valeur fixée pour la première itération
taille_provisoire=0
init=0

def monter():
  GPIO.output(mont,GPIO.HIGH)
  GPIO.output(desc,GPIO.LOW)
  polarity=1
  print("MONTEE")

def descendre():
  GPIO.output(mont,GPIO.LOW)
  GPIO.output(desc,GPIO.HIGH)
  polarity=0
  print("DESCENTE")
  
def arreter():
  GPIO.output(mont,GPIO.LOW)
  GPIO.output(desc,GPIO.LOW)
  print("ARRET")
  return (1)

#### Initialisation, départ en position basse ###

print("## Initialisation ##")
descendre()
time.sleep(3)
print("Fin de course basse ok")
monter()  
print("A commencé à monter")

#### Premier balayage #####

print("## Premier balayage ##")

while ((qte<seuil) or (init==0) and arretverin==0):            # le vérin monte tant que le signal n'est pas correct
  qte=float(input("Entrer la qualité : "))
  if qte==42:
    arretverin=1
    
  mesure_qte.append(qte)                    # récupère la première valeur au dessus du seuil
  
  for p in range(len(mesure_qte)):         # cherche la valeur max trouvée
    if mesure_qte[p]>=qte_max:
      qte_max=mesure_qte[p]

  init=1

while qte>=qte_max/1.2 and arretverin==0:                  # marge hysteresis
  qte=float(input("Entrer la qualité : "))  # rentrée à la main mais lecture directe quand mise en commun du code
  if qte==42:
    arretverin = arreter()
  if qte>=qte_max:
    qte_max=qte
  mesure_qte.append(qte)                    # agrandissement du tableau au fur et à mesure
  time.sleep(delai_mesures)                 # temps entre chaque mesure
  derniere_valeur_seuil=mesure_qte[len(mesure_qte)-1]
   
  for w in range(len(mesure_qte)):
    if mesure_qte[w]>=qte_max:
      qte_max=mesure_qte[w]
  qte_min=derniere_valeur_seuil
  seuil=(qte_max+qte_min)/2
  
#### Début du fonctionnement normal #####

print("## Debut du fonctionnement normal  ##")


print("erreur actuelle "+str(qte_max-qte_min))


while (abs(qte_max-qte_min)>erreur) and arretverin==0:
  print("seuil : "+str(seuil))
  polarity=not polarity                       # le vérin va monter s'il descendait
  if polarity == 0:
    monter()
  else:
    descendre()
      
  print("Delai entre les mesures : " + str(round(delai_mesures, 3)) + " secondes")
  
  while qte<=seuil and arretverin==0:        	# le vérin monte tant que le signal n'est pas correct
    qte=float(input("#Entrer la qualité : "))
    if qte==42:
      arretverin=1
      break
    mesure_qte.append(qte)             	# récupère la première valeur au dessus du seuil
    time.sleep(delai_mesures)                 # temps entre chaque mesure
          
  while qte>=(qte_max+mesure_qte[len(mesure_qte)-1])/2 and arretverin==0:               	# marge hysteresis
    qte=float(input("#Entrer la qualité : "))	# rentrée à la main mais lecture directe quand mise en commun du code
    if qte==42:
      arretverin=1
      break
    mesure_qte.append(qte)              	# agrandissement du tableau au fur et à mesure  
    time.sleep(delai_mesures)           	# temps entre chaque mesure
    
    del mesure_qte[0]                     	# Efface l'ancienne donnée qui est en première position
    Nb_mesures=len(mesure_qte)             	# pour que les boucles itèrent autant de fois
      
    if qte>qte_max:                             # mise à jour de la valeur max si nécessaire
      qte_max=qte

        
    if len(mesure_qte)>0:                       # s'éxécute sauf erreur
      derniere_valeur_seuil=mesure_qte[len(mesure_qte)-1]
      qte_min=derniere_valeur_seuil             # mise à jour de la valeur min
      seuil=(qte_max+derniere_valeur_seuil)/2   # mise à jour du seuil
      
    delai_mesures=delai_mesures/1.1             # raccourcit le temps entre les mesures
    
    for m in range(Nb_mesures-1):       	# Efface toutes les valeurs du tableau sauf une
      mesure_qte.pop()                          # pour n'avoir que les mesures de la prochaine boucle

    
if len(mesure_qte)>0:    
  if(abs(mesure_qte[0]-seuil)<=erreur and arretverin==0):       # dernier positionnement // erreur 
    while(qte<seuil):
      polarity=not polarity
      if polarity == 0:
        monter()
      else:
        descendre()


## if(abs(mesure_qte[0]-seuil)<2*erreur):     # en cas d'erreur


arretverin = arreter()      ## on arrête le vérin quand le positionnement est fini
