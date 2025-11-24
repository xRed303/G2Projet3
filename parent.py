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
def respond_to_connexion_request(key):
    """
    Réponse au challenge initial de connection avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                   Clé de chiffrement
	:return (srt) challenge_response:   Réponse au challenge
    """
    packet = radio.receive()
    if not packet:
        return ""

    challenge_recu = receive_packet(packet, key)

    if challenge_recu[0] != "CHALLENGE":
        return ""
    response = calculate_challenge_response(challenge_recu[2])
    send_packet(key, "RESPONSE", response)
    return response
    
#################################################################################
# Fonctions doses de laits

# On commence avec 0 dose de lait
etat = {"doses": 0}

# Affiche la dose sur les LEDs
def show_value(val):
    if val < 10:    
        display.show(str(val)) # Affiche la dose sur les LEDs et ne va pas au-dessus de 9
    else:  
        # Scroll qui se fait a l infini et sans blocker le programme pour les nombres a 2 chiffres
         display.scroll(str(val), wait=False, loop=True)

# Affiche 0 dès le démarrage et la derniere dose si on eteint pas le microbits
show_value(etat["doses"])

def add_doses(e):
    # Si on appuie sur le bouton B 
    if button_b.was_pressed():   
        if e["doses"] < 99: # limite de doses a donner
            e["doses"] += 1  # On augmente le compteur
            show_value(e["doses"])
        else:
            display.scroll("Stop c'est quoi ton probleme de lui donner autant de dose")    # si on dépasse les 99 doses MSG D AVERTISSEMENT
            show_value(e["doses"])

def delete_doses(e):
    # Si on appuie sur le bouton A
    if button_a.was_pressed():
        if e["doses"] > 0:  # On ne peut pas descendre en dessous de 0
            e["doses"] -= 1   # On diminue le compteur
        show_value(e["doses"])

def reset_doses(e):
    # Si on appuie sur les deux boutons en même temps
    if button_a.is_pressed() and button_b.is_pressed():
        e["doses"] = 0  # On remet à zéro
        show_value(e["doses"])  

# Envoyer le nombre de doses be:bi’ enfant
def send_doses(e):
    if pin_logo.is_touched():
        display.scroll(str(e["doses"]))
        radio.send(str(e["doses"]))



################################################################################################

display.show(Image.SQUARE)
radio.on()
radio.config(channel=2)

def main():
    while True:
        respond_to_connexion_request("MIMOSA")
        packet_received = radio.receive()
        receive_packet(packet_received, "MIMOSA")

        """add_doses(etat)
        delete_doses(etat)
        reset_doses(etat)
        send_doses(etat)
        """
        
