#creation interface pour bébé
from microbit import *
def mode_lait(quantite,allume=True):
    display.show(quantite)
    sleep(3000)
        
        

def mode_envi(allume=True):
    if allume:
        display.show("E")
        #implémenter temp de la pièce

def mode_eveil_bb(allume=True):
    if allume:
        display.show(Image('09999:''99990:''99900:''99990:''09999'))
        sleep(3000)
    
while True:
    display.show(Image.SQUARE)
    if button_a.was_pressed():
        
        mode_eveil_bb(allume=True)
        
            
    elif button_b.was_pressed():
        
        mode_lait("1",allume=True)
        #pas terminé
        
