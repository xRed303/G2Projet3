#########################################################################################################
from microbit import *
import radio
import random
import music

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)

def hashing(string):
	"""
	Hachage d'une chaîne de caractères fournie en paramètre.
	Le résultat est une chaîne de caractères.
	Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.

	:param (str) string: la chaîne de caractères à hacher
	:return (str): le résultat du hachage
	"""
	def to_32(value):
		"""
		Fonction interne utilisée par hashing.
		Convertit une valeur en un entier signé de 32 bits.
		Si 'value' est un entier plus grand que 2 ** 31, il sera tronqué.

		:param (int) value: valeur du caractère transformé par la valeur de hachage de cette itération
		:return (int): entier signé de 32 bits représentant 'value'
		"""
		value = value % (2 ** 32)
		if value >= 2**31:
			value = value - 2 ** 32
		value = int(value)
		return value

	if string:
		x = ord(string[0]) << 7
		m = 1000003
		for c in string:
			x = to_32((x*m) ^ ord(c))
		x ^= len(string)
		if x == -1:
			x = -2
		return str(x)
	return ""
    
def vigenere(message, key, decryption=False):
    text = ""
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        key_index = i % key_length
        #Letters encryption/decryption
        if char.isalpha():
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else : 
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            #Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        #Digits encryption/decryption
        elif char.isdigit():
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:  
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text
    
def send_packet(key, type, content):
    """
    Envoie de données fournie en paramètres
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit

    :param (str) key:       Clé de chiffrement
           (str) type:      Type du paquet à envoyer
           (str) content:   Données à envoyer
	:return none
    """
    #Format message: type | long | message
    long = str(len(content))
    message = type + "|" + long + "|" + content
    message_hash = hashing(message)
    message += "|" + message_hash
    message_chiffre = vigenere(message,key,decryption=False)
    radio.send(message_chiffre)
    
#Decrypt and unpack the packet received and return the fields value
def unpack_data(encrypted_packet, key):
    """
    Déballe et déchiffre les paquets reçus via l'interface radio du micro:bit
    Cette fonction renvoit les différents champs du message passé en paramètre

    :param (str) encrypted_packet: Paquet reçu
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)lenght:           Longueur de la donnée en caractères
            (str) message:         Données reçues
    """
    message_dechiffre = vigenere(encrypted_packet,key,decryption=True)
    #message => 1|longueur|message|hash
    message_dechiffre = message_dechiffre.split("|")
    typePaquet = message_dechiffre[0]
    lenght = int(message_dechiffre[1])
    message = message_dechiffre[2]
    hash_message = message_dechiffre[3]
    return typePaquet,lenght,message,hash_message

#Unpack the packet, check the validity and return the type, length and content
def receive_packet(packet_received, key):
    """
    Traite les paquets reçue via l'interface radio du micro:bit
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit
    Si une erreur survient, les 3 champs sont retournés vides

    :param (str) packet_received: Paquet reçue
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)lenght:           Longueur de la donnée en caractère
            (str) message:         Données reçue
    """
    donnee = unpack_data(packet_received,key) #donnee = (T,L,M)
    #partie securite
    verif_hash = hashing(donnee[0]+"|"+str(donnee[1])+"|"+donnee[2])
    if verif_hash != donnee[3]:
        return "",0,""
    if len(donnee[2]) != donnee[1]:
        return "",0,"" 
    #fin partie securite
    return donnee[0],donnee[1],donnee[2]
    
#Calculate the challenge response
def calculate_challenge_response(challenge):
    """
    Calcule la réponse au challenge initial de connection avec l'autre micro:bit

    :param (str) challenge:            Challenge reçu
	:return (srt)challenge_response:   Réponse au challenge
    """
    #challenge = mot de passe
    return hashing(challenge[::-1])

#Ask for a new connection with a micro:bit of the same group
def establish_connexion(key):
    """
    Etablissement de la connexion avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                  Clé de chiffrement
	:return (srt)challenge_response:   Réponse au challenge
    """
    challenge = str(random.randint(1000,100000))
    send_packet(key,"CHALLENGE",challenge)
    finished = False
    while not finished:
         message_recu = radio.receive()
         data = receive_packet(message_recu,key)
         if data[0] == "CHALLENGE":
              expected = calculate_challenge_response(challenge)
              if data[2] == expected:
                   send_packet(key,"ACK","OK")
                   finished = True
                   return expected
              else:
                   return ""
                  

#######################################################
#Fonctions sysytème surveillance etat bb

def convert(millig):
    if millig >= 0:
        m_par_second_caree = millig/(10**-5)
    else:
        m_par_second_caree = -millig/(10**-5)
    return m_par_second_caree
    
def is_awake(mouvement):
    liste = []
    #mouvement = (accelerometer.get_x(),accelerometer.get_y(),accelerometer.get_z())
    for coor in mouvement:
        convert(coor)
        if coor > 5:
            liste.append("éveillé")
    if "éveillé" in liste:
        return True
    else:
        return False
        
def shout(bruit):
    """pre:
    bruit: est une instance de """
    speaker.on()
    #bruit = microphone.sound_level()
    if bruit > 200:
        return True
    else:
        return False

def melodie(bruit,mouvement):
    if shout(bruit) == True and is_awake(mouvement) == True: #très agité
        pass#à retirer c'est juste pour virer l'erreur
        #mettre music
    elif shout(bruit) == False and is_awake(mouvement) == True: #agité
        pass  #ici aussi c'est pour l'erreur
        
#############################################################################
#Fonctions pour le lait














########################################################################################################
#Fonction pour vérifier l'environnement durant le sommeil du bébé

#faire une interface pour avoir les données de quand il dort
#donc un bouton qui montre la température, un le son et un la luminosité

def get_temperature(code):
    if code == "Temperature":
        t = temperature()
        if 19 <= t <= 21:
            for i in range(3):
                display.show(Image.HAPPY)
                sleep(1000)
                display.scroll("t: " + str(temperature()))
                sleep(250)#c'est ce qui faudra faire sur le be:bi parent
            
        if 17 <= t <= 18 or 22 <= t <= 24:
            #petite alerte ON ENVOIE EMOJI PAS TRISTE MAIS PAS JOYEUX COMME CA :/ et on envoie la t°
            audio.play(Sound.HAPPY)
            for i in range(3):
                display.show(Image.SAD)
                sleep(1000)
                display.scroll("t: " + str(temperature()))
                sleep(250)
            
        if t < 17 or t > 24:
            #grosse alerte C'EST LE :( + t°
            audio.play(Sound.SAD)
            for i in range(3):
                display.show(Image.ANGRY)
                sleep(1000)
                display.scroll("t: " + str(temperature()))
                sleep(250)
            
    








###########################################################################################################
#toute la partie qui va faire en sorte que notre code fonctionne

display.show(Image.SQUARE_SMALL) #on affiche l'image pour identifier le be:bi parent
radio.on()
radio.config(channel=2)
radio.config(group=2)

def main():
    while True:
        establish_connexion("MIMOSA")
        packet_received = radio.receive()
        receive_packet(packet_received, "MIMOSA")
        
        

main()
            
        
        
        
