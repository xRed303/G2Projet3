#########################################################################################################
from microbit import *
import radio
import random
import music

def musique():
    tune = [
    "R:4", "C4:2","D:2","E:4", "C:2","R:2","C:2","D:2","E:4","C:2", "R:2",
    "C4:2","E:2","A#:4","A:4","G:4","G:4","F:4",
    "G#3:2","A#:2","B:4", "G#:2","R:2","G#:2","A#:2","B:4","G#:2", "R:2",
    "G#:2", "B:4", "D3:4", "G:4", #première partie
    ]

    music.play(tune)

def musique2():
    tune = [
    "G#3:2","A#:2","B:4", "G#:2","R:2","G#:2","A#:2","B:4","G#:2", "R:2",
    "G#:2", "B:2", "F4:2", "E:2", "C:2" #deuxième partie
    ]
    music.play(tune)
musique()
musique2()

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
    nonce = str(random.randint(100000, 999999))
    content = nonce + ":" + content
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
    if packet_type == None:
        return "", 0, ""
        
    if ":" not in packet_content:
        return "", 0, ""
    else:
        nonce, data = packet_content.split(":", 1)
        
    if nonce in nonce_list:
        return "", 0, ""
    else:
        nonce_list.append(nonce)
        
    return packet_type, packet_length, data

def calculate_challenge_response(challenge):
    random.seed(int(challenge))
    return str(random.randint(100000, 999999))

def establish_connexion(key):
    
    challenge = str(random.randint(100000, 999999))
    send_packet(key, "1", challenge)
    t = running_time()
    while running_time() - t < 10000:
        packet = radio.receive()
        if packet:
            packet_type, packet_length, data = receive_packet(packet, key)
            if packet_type == "2":
                local_resp = calculate_challenge_response(challenge)
                if hashing(local_resp) == data:
                    return key + local_resp
    return ""


#######################################################
#Fonctions sysytème surveillance etat bb

# état initial
etat = {"eveil": "ENDORMI"}  

# Fonction qui lit la force du mouvement via l'accéléromètre
def detect_mouvement():
    return accelerometer.get_strength()

# Fonction qui calcule l'état d'éveil à partir de la force mesurée via l accelerometre
def calculate_status(force):
    # Faible mouvement → endormi
    if force < 400: 
        return "ENDORMI"
    # Mouvement moyen → agité
    elif force < 1200:
        return "AGITE"
    # Fort mouvement ou chute → très agité 
    else:
        return "TRES_AGITE"

# Affiche un symbole selon l'état sur les leds
def show_status(e):
    if e == "ENDORMI":
        display.show("Z")   # Z = sommeil
    elif e == "AGITE":
        display.show("A")   # A = agité
    else:
        display.show("!")   # ! = très agité

# Joue un son selon l'état
def play_sound(e):
    if e == "ENDORMI":
        musique()  # son doux et apaisant
    elif e == "AGITE":
        musique2()    # son court et regulier
    else:
        music.play(music.BA_DING) # alarme sonore

# Envoie l'état au micobites parent
def send_status(e):
    radio.send(e)

# Fonction principale qui met à jour l’état si nécessaire
def update_status():
    force = detect_mouvement()        # mesure du mouvement
    nouvel_etat = calculate_status(force)  # conversion en état

    # Agit uniquement s'il y a un changement d'état
    if nouvel_etat != etat["eveil"]:
        etat["eveil"] = nouvel_etat
        show_status(nouvel_etat)
        send_status(nouvel_etat)
        play_sound(nouvel_etat)
        
# Affiche l'état initial au démarrage
show_status(etat["eveil"])
    
        
#############################################################################
#Fonctions pour le lait

def doses_total(data):
    if data:
        etat["doses_recu"] = int(data)
        display.scroll("Dose:" + str(etat["doses_recu"]))


########################################################################################################
#Fonction pour vérifier l'environnement durant le sommeil du bébé

#faire une interface pour avoir les données de quand il dort
#donc un bouton qui montre la température, un le son et un la luminosité

def get_temperature():
    t = temperature()
    if 19 <= t <= 21:
        send_packet(session_key, "3", str(t))
            
    if 17 <= t <= 18 or 22 <= t <= 24:
        send_packet(session_key, "4", str(t))

    if t < 17 or t > 24:
        send_packet(session_key, "5", str(t))


###########################################################################################################
#toute la partie qui va faire en sorte que notre code fonctionne

display.show(Image.SQUARE_SMALL) #on affiche l'image pour identifier le be:bi parent
radio.on()
radio.config(channel=2)
nonce_list = []
############################################################################################################
#fonctions pour interface bb
def mode_lait(quantite,allume=True):
    display.show(quantite)
    sleep(3000)
def mode_temp(temp,allume=True):
    if allume:
        display.show(temp)
        sleep(3000)
def mode_eveil_bb(allume=True):
    if allume:
        display.show(Image('09999:''99990:''99900:''99990:''09999'))
        sleep(3000)
def main():
    global session_key
    key = "MIMOSA"
    session_key = establish_connexion(key)
    if session_key != "":
        display.scroll("co OK")
    else:
        display.scroll("co FAIL")


    while True:
        
        message_received = radio.receive()
        if message_received != None:
            display.show(Image.ANGRY)
            sleep(1000)
            packet_type , packet_length, data = receive_packet(message_received, session_key)
            display.scroll(packet_type)
            sleep(1000)
            
            if packet_type == "6":
                doses_total(data)  # Affiche la dose de lait reçue
    
        if button_a.was_pressed():
        
            mode_eveil_bb(True)
            if button_a.was_pressed():
                while not button_b.was_pressed():
                    show_status(calculate_status(detect_mouvement()))
            elif button_b.was_pressed():
                while not button_a.was_pressed():
                    send_status(calculate_status(detect_mouvement()))
                
            
    
        elif button_b.was_pressed():
            message = unpack_data(message,"MIMOSA")
            if message[0] == "LAIT":
                try:
                    quantite = unpack_data(message,"MIMOSA")[2]
                    mode_lait(quantite,allume=True)
                except:
                    display.scroll("ERROR")
            #il reçoit la quantité de lait du Be:Bi parent et l'affiche
        elif pin0.is_touched():
            temp = temperature()
            mode_temp(temp,True) #affiche temp
            

    


        
main()
            
        
        
        


