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

def respond_to_connexion_request(key):
    t = running_time()
    while running_time() - t < 10000:
        packet = radio.receive()
        if packet:
            packet_type, packet_length, data = receive_packet(packet, key)
            if packet_type == "1":
                random.seed(int(data))  ####meme seed entre parent et bebe donc meme réponse
                challenge_resp = str(random.randint(100000, 999999))
                hashed = hashing(challenge_resp)
                send_packet(key, "2", hashed)
                return key + challenge_resp
    return ""

#################################################################################
# Fonctions doses de laits

# On commence avec 0 dose de lait
etat = {"doses": 0}

# Affiche la dose sur les LEDs
def show_value(val):    
    display.show(str(val)) # Affiche la dose sur les LEDs et ne va pas au-dessus de 9

# Affiche 0 dès le démarrage et la derniere dose si on eteint pas le microbits
show_value(etat["doses"])

def add_doses(e):
    def add_doses(e):
    if button_b.was_pressed():
        if e["doses"] < 10:
            e["doses"] += 1
            show_value(e["doses"])
            send_packet(session_key, "6", str(e["doses"]))

def delete_doses(e):
    # Si on appuie sur le bouton A
    if button_a.was_pressed():
        if e["doses"] > 0:  # On ne peut pas descendre en dessous de 0
            e["doses"] -= 1   # On diminue le compteur
        show_value(e["doses"])
         send_packet(session_key, "6", str(e["doses"]))

def reset_doses(e):
    # Si on appuie sur les deux boutons en même temps
    if button_a.is_pressed() and button_b.is_pressed():
        e["doses"] = 0
        show_value(e["doses"])
        send_packet(session_key, "6", str(e["doses"])) 


##############################################################################################
#partie environnement bébé

def Temperature1(data):
    t = data
    #display.show(Image.HAPPY)
    sleep(1000)
    display.scroll("t: " + str(t))
    sleep(250)
    
def Temperature2(data):
    #petite alerte ON ENVOIE EMOJI PAS TRISTE MAIS PAS JOYEUX COMME CA :/ et on envoie la t°
    t = data
    #audio.play(Sound.HAPPY)
    display.show(Image.SAD)
    sleep(1000)
    display.scroll("t: " + str(t))
    sleep(250)

def Temperature3(data):
    #grosse alerte C'EST LE :( + t°
    t = data
    #audio.play(Sound.SAD)
    for i in range(3):
        display.show(Image.ANGRY)
        sleep(1000)
        display.scroll("t: " + str(t))
        sleep(250)
    
    

################################################################################################

display.show(Image.SQUARE)
radio.on()
radio.config(channel=2)
nonce_list = []

def main():
    global session_key
    key = "MIMOSA"
    session_key = respond_to_connexion_request(key)
    if session_key != "":
        display.scroll("co OK")
    else:
        display.scroll("co FAIL")
        
    display.show(Image.SQUARE)
    sleep(1000)
    while True:
        
        message_received = radio.receive()
        if message_received != None:
            display.show(Image.ANGRY)
            sleep(1000)
            packet_type , packet_length, data = receive_packet(message_received, session_key)
            display.scroll(packet_type)
            sleep(1000)
            #verif packet type et data
        
        
        #################partie environnement
            if packet_type == "3":
                Temperature1(data)

            if packet_type == "4":
                Temperature2(data)

            if packet_type == "5":
                Temperature3(data)
            
        
        ##################partie biberon
        """add_doses(etat)
        delete_doses(etat)
        reset_doses(etat)
        """

main()
