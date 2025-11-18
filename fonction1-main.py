# Imports go at the top
from microbit import *
import audio
import radio

#envoyer un message sous forme "code|long|contenu"

radio.on()
radio.config(channel=2)
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

def agite(mouvement,bruit):
    if is_awake(mouvement):
        
        if is_awake(mouvement) >=10 and
def melodie(bruit,mouvement):
    if shout(bruit) == True and is_awake(mouvement) == True:
        #mettre music
    elif shout(bruit) == False and is_awake(mouvement) == True:
        
    
        
    
    
    
            
            
        

            
            
    
    
    
messageTLV = "2|5|Hello"
while True:
    radio.send(messageTLV)