import random
import time
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext


def sim_course_infini (context, slave_id=0x00) :
    en_course=True
    #met en place les positions
    for i in range(1,21) :
        context[slave_id].setValues(4, 80+1, [i])
    #temps référence
    temps_moyen=84

    while(en_course):
        #proba crash
        valide,voiture_crash=aleatoire_voiture(0.05)
        if valide==1:crash(voiture_crash)

        temp=context[slave_id].getValues(4, 0, count=1)[0]
        temp+=1
        context[slave_id].setValues(4, 0, [temp])
        verif_temps_crash()
        verif_drapeaux()
        time.sleep(1)

def aleatoire_voiture(proba, slave_id=0x00):
    while (not sortir):
        voiture_touche_proba = random.randint(1,20)
        for i in range(20):
            temp = context[slave_id].getValues(2, 0, count=1)[0]
            if temp ==True:
                if i+1 == voiture_touche_proba: voiture_touche_proba = random.randint(1,20)
            else : sortir = True

    
    if random.random()<proba :
        return 1, voiture_touche_proba
    else : return 0,0

def crash(voiture, slave_id=0x00):
    temp=context[slave_id].getValues(4, 61, count=1)[0]
    context[slave_id].setValues(2, 0, [True])
    zone = random.randint(2, 3)
    if temp == 0 :
        context[slave_id].setValues(2, 40+zone, [True])
    elif temp == 1 :
        context[slave_id].setValues(2, 43+zone, [True])
    context[slave_id].setValues(4, 81, [temp+1])
    context[slave_id].setValues(2, voiture, [True])

def verif_temps_crash(slave_id=0x00):
    return 0

def verif_drapeaux():
    
    return 0

if __name__ =='__main__' :
    device = ModbusDeviceContext(ir=ModbusSequentialDataBlock(0, [0]*120), di=ModbusSequentialDataBlock(0, [0]*50))
# Contexte du serveur (1 slave par défaut, unit_id=1)
    context = ModbusServerContext(devices = device, single=True)

sim_thread = Thread(target=sim_course_infini, args=(context,))
sim_thread.daemon=True
sim_thread.start()

# Démarrer le serveur sur le port 5020
StartTcpServer(context=context, address=("0.0.0.0", 502))