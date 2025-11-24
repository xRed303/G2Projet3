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
        key_index = i % key_length
        if char.isalpha():
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else:
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
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

def establish_connexion(key):
    nonce = str(random.randint(100000, 999999))
    challenge = str(random.randint(100000, 999999))
    send_packet(key, "01", nonce + ":" + challenge)
    t = running_time()
    while running_time() - t < 10000:
        packet = radio.receive()
        if packet:
            packet_type, packet_length, nonce, data = receive_packet(packet, key)
            if packet_type == "02":
                local_resp = calculate_challenge_response(challenge)
                if hashing(local_resp) == data:
                    return key + local_resp
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
nonce_list = []

def main():
    key = "MIMOSA"
    session_key = establish_connexion(key)
    if session_key != "":
        display.scroll("co OK")
    else:
        display.scroll("co FAIL")
        
    while True:
        sleep(100)
        
        
        
        

main()
            
        
        
        

