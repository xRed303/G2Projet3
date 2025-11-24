#########################################################################################################
from microbit import *
import radio
import random
import music


def hashing(string):
    def to_32(value):
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
        if char.isalpha():
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else:
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        elif char.isdigit():
            key_index = i % key_length
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text

def send_packet(key, type, content):
    length = len(content)
    message = str(type) + "|" + str(length) + "|" + content
    crypted_message = vigenere(message, key, decryption=False)
    radio.send(crypted_message)

def unpack_data(crypted_message, key):
    message = vigenere(crypted_message, key, decryption = True)
    try:
        packet_type, packet_length, packet_content = message.split("|", 2)
        return packet_type, int(packet_length), packet_content
    except:
        return "", 0, ""

def receive_packet(packet_received, key):
    packet_type, packet_length, packet_content = unpack_data(packet_received, key)
    if packet_type == "":
        return "", 0, ""
    if ":" not in packet_content:
        return "", 0, ""
    nonce, data = packet_content.split(":", 1)
    if nonce in nonce_list:
        return "", 0, ""
    nonce_list.append(nonce)
    return packet_type, packet_length, nonce, data

def calculate_challenge_response(challenge):
    random.seed(int(challenge))
    return str(random.randint(100000, 999999))

def respond_to_connexion_request(key):
    t0 = running_time()
    while running_time() - t0 < 10000:
        packet = radio.receive()
        if packet:
            packet_type, packet_length, nonce, data = receive_packet(packet, key)
            if packet_type == "01":
                random.seed(int(data))  ####meme seed entre parent et bebe donc meme réponse
                challenge_resp = str(random.randint(100000, 999999))
                hashed = hashing(challenge_resp)
                nonce2 = str(random.randint(100000, 999999))
                send_packet(key, "02", nonce2 + ":" + hashed)
                return key + challenge_resp
    return ""



    
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
        display.show(Image.YES) # Affiche un petit symbole pour indiquer que le message est envoyé
        radio.send(str(e["doses"])) 
        sleep(750) 
        show_value(e["doses"])



################################################################################################

display.show(Image.SQUARE)
radio.on()
radio.config(channel=2)
nonce_list = []

def main():
    key = "MIMOSA"
    session_key = respond_to_connexion_request(key)
    if session_key != "":
        display.scroll("co OK")
    else:
        display.scroll("co FAIL")
        
    while True:
        sleep(100)

        """add_doses(etat)
        delete_doses(etat)
        reset_doses(etat)
        send_doses(etat)
        """

main()
