# Imports go at the top
from microbit import *

import radio
#envoyer un message sous forme "code|long|contenu"

radio.on()
radio.config(channel=2)

messageTLV = "2|5|Hello"
while True:
    radio.send(messageTLV)



   
