#########################################################################################################
from microbit import *
import radio
import random
import music

def musiqueZ():
    tune = [
    "R:4", "C4:2","D:2","E:4", "C:2","R:2","C:2","D:2","E:4","C:2", "R:2",
    "C4:2","E:2","A#:4","A:4","G:4","G:4","F:4",
    "G#3:2","A#:2","B:4", "G#:2","R:2","G#:2","A#:2","B:4","G#:2", "R:2",
    "G#:2", "B:4", "D3:4", "G:4","G#3:2","A#:2","B:4", "G#:2","R:2","G#:2","A#:2","B:4","G#:2", "R:2",
    "G#:2", "B:2", "F4:2", "E:2", "C:2"
    ]

    music.play(tune)
def musiqueA():
    tune = [
    "R:4", "C4:4", "E4:4", "G4:4", "C5:4", "R:4", 
    "E4:4", "G4:4", "C5:4", "R:4", 
    "C4:4", "G4:4", "E4:4", "C5:4", "R:4",
    "C4:4", "E4:4", "G4:4", "C5:4", "R:4",
    "E4:4", "G4:4", "C5:4", "R:4",
    "R:4", "C4:4", "E4:4", "G4:4", "C5:4", "R:4",
    "E4:4", "G4:4", "C5:4", "R:4", 
    "C4:4", "G4:4", "E4:4", "C5:4", "R:4"
    ]


    music.play(tune)



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

# État initial
etat = "ENDORMI"
timer = running_time()
force_b = []
Time = 3000  # 3 secondes 

# Fonctions
def detect_mouvement():
    return accelerometer.get_strength()

def calculate_status(force):
    if force >= 1800:
        return "TRES_AGITE"
    elif force >= 1200:
        return "AGITE"
    else:
        return "ENDORMI"

def show_status(e):
    if e == "ENDORMI":
        display.show("Z")
    elif e == "AGITE":
        display.show("A")
    elif e == "TRES AGITE":
        display.show("!")
    else:
        display.show("C")

def play_sound(e):
    if e == "ENDORMI":
        musiqueZ()
    elif e == "AGITE":
        musiqueA()
    elif e == "TRES AGITE":
        music.play(music.BA_DING)
    else:
        music.play(music.WAWAWAWAA)

def send_status(status, force):
    global session_key
    if session_key == "":
        return
    if status == "ENDORMI":
        send_packet(session_key, "7", status)
    elif status == "AGITE":
        send_packet(session_key, "8", status)
    elif status == "TRES_AGITE":
        send_packet(session_key, "9", status)
    if force >= 3200:  # alerte chute
        send_packet(session_key, "10", "CHUTE")

# Mise à jour de l'état
def update_status():
    global etat, timer, force_b
    force = detect_mouvement()
    
    # Chute 
    if force >= 3200:
        if etat != "TRES_AGITE":
            etat = "CHUTE"
            show_status(etat)
            send_status(etat, force)
            play_sound(etat)  
        timer = running_time()
        force_b.clear()  # reset observation
        return

    # Ajouter force au b pour moyenne sur 3 secondes
    if len(force_b) <= 100:
        force_b.append(force)

    # Si le temps d'observation atteint 3 sec
    if running_time() - timer >= Time:
        # Calculer moyenne
        avg_force = sum(force_b) / len(force_b)
        
        # Détermine l'état selon la moyenne
        etat_calcule = calculate_status(avg_force)
        # Met à jour l état et affiche/son
        if etat != etat_calcule:
            etat = etat_calcule
            show_status(etat)
            send_status(etat, detect_mouvement())
            play_sound(etat)
        # Réinitialiser timer et b pour la prochaine observation
        timer = running_time()
        force_b.clear()


#############################################################################
#Fonctions pour le lait
etat_bb = {}
def doses_total(data):
    etat_bb["doses_recu"] = int(data)
    return etat_bb["doses_recu"]


########################################################################################################
#Fonction pour vérifier la température durant le sommeil du bébé


def get_temperature():
    t = temperature()
    if 19 <= t <= 21:
        send_packet(session_key, "3", str(t))
        a = 1   #a c'est une variable que j'utilise pour l'interface
        return a, t
            
    if 17 <= t <= 18 or 22 <= t <= 24:
        send_packet(session_key, "4", str(t))
        a = 2
        return a, t
        
    if t < 17 or t > 24:
        send_packet(session_key, "5", str(t))
        a = 3
        return a, t


###########################################################################################################
#toute la partie qui va faire en sorte que notre code fonctionne


radio.on()
radio.config(channel=2)
nonce_list = []

def main():
    display.show(Image.SQUARE_SMALL)
    global session_key
    key = "MIMOSA"
    doses = 0
    
    session_key = establish_connexion(key)
    if session_key != "":
        display.scroll("co OK")
    else:
        display.scroll("co FAIL")
    

    while True:
        display.show(Image.SQUARE_SMALL)
        update_status()   #je les mets ici ET dans l'interface pour les éventuelles alarmes
        force = detect_mouvement()
        if etat == "TRES_AGITE":
            send_status(etat,force)
        if etat == "AGITE":
            send_status(etat,force)
        message_received = radio.receive()
        
        if message_received != None:
            packet_type , packet_length, data = receive_packet(message_received, session_key)
            if packet_type == "6":
                doses = doses_total(data)

        
        ########pour le sommeil
        if button_a.was_pressed():
            
            while not pin_logo.is_touched():
                
                
                display.show(Image('09999:''99990:''99900:''99990:''09999'))
                play_sound(etat)
                if button_a.was_pressed():
                    show_status("ENDORMI")
                    
                    while not pin_logo.is_touched():
                        update_status()

        
        #####pour le lait
        elif button_b.was_pressed():
            while not pin_logo.is_touched():
                display.show("L")
                if button_b.was_pressed():
                    while not pin_logo.is_touched():
                        message_received = radio.receive()
                        if message_received != None:
                            packet_type , packet_length, data = receive_packet(message_received, session_key)
                            if packet_type == "6":
                                doses = doses_total(data)
                        display.show(str(doses))

        
        ########pour la température
        elif pin0.is_touched():
            while not pin_logo.is_touched():
                display.show("T")
                if pin1.is_touched():
                     while not pin_logo.is_touched():
                        a, t = get_temperature()
                        if a == 1:
                            display.show(Image.HAPPY)
                            sleep(750)
                            display.scroll("t:" + str(temperature()))
                            
                            
                        if a == 2:
                            display.show(Image.SAD)
                            sleep(750)
                            display.scroll("t:" + str(t))

                        if a == 3:
                            display.show(Image.ANGRY)
                            sleep(750)
                            display.scroll("t:" + str(t))


main()
