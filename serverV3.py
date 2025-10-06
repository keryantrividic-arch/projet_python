import random
import time
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext


def sim_course_infini(context, slave_id=0x00):  
    context[slave_id].setValues(4, 0, [0])
    
    course_en_cours = context[slave_id].getValues(2, 0, count=1)[0]
    if not course_en_cours:
        context[slave_id].setValues(2, 0, [True])
    
    while True:
        course_en_cours = context[slave_id].getValues(2, 0, count=1)[0]
        
        if course_en_cours:
            valide_crash, voiture_crash = aleatoire_voiture(context, 0.05)
            if valide_crash == 1:
                crash(context, voiture_crash)
            
            valide_stand, voiture_stand = aleatoire_voiture(context, 0.5)
            if valide_stand == 1:
                arret_stand(context, voiture_stand)
            
            for i in range(1, 21):
                temps_voiture = 84 + random.randint(-10, 10)
                context[slave_id].setValues(4, 40 + i, [temps_voiture])

            valide_penalite, voiture_penalite = aleatoire_voiture(context, 0.1)
            if valide_penalite == 1:
                appliquer_penalite(context, voiture_penalite)
        else:
            mettre_toutes_voitures_au_stand(context)
        
        temp = context[slave_id].getValues(4, 0, count=1)[0]
        temp += 1
        context[slave_id].setValues(4, 0, [temp])
        
        verif_temps_crash(context)
        verif_temps_stand(course_en_cours, context)
        verif_drapeaux(context)
        
        time.sleep(1)


def mettre_toutes_voitures_au_stand(context, slave_id=0x00):
    for i in range(1, 21):
        est_crash = context[slave_id].getValues(2, i, count=1)[0]
        est_stand = context[slave_id].getValues(2, 20 + i, count=1)[0]
        
        if not est_crash and not est_stand:
            context[slave_id].setValues(2, 20 + i, [True])
            context[slave_id].setValues(4, i, [0])


def aleatoire_voiture(context, proba, slave_id=0x00):
    voitures_disponibles = []
    
    for i in range(1, 21):
        est_crash = context[slave_id].getValues(2, i, count=1)[0]
        est_stand = context[slave_id].getValues(2, 20 + i, count=1)[0]
        
        if not est_crash and not est_stand:
            voitures_disponibles.append(i)
    
    if not voitures_disponibles:
        return 0, 0
    
    if random.random() < proba:
        voiture_choisie = random.choice(voitures_disponibles)
        return 1, voiture_choisie
    else:
        return 0, 0


def crash(context, voiture, slave_id=0x00):
    est_deja_crash = context[slave_id].getValues(2, voiture, count=1)[0]
    if est_deja_crash:
        return
    
    nb_crash = context[slave_id].getValues(4, 61, count=1)[0]
    zone = random.randint(1, 3)
    
    context[slave_id].setValues(2, voiture, [True])
    
    if nb_crash == 0:
        context[slave_id].setValues(2, 40 + zone, [True])
        context[slave_id].setValues(4, 61, [1])
    elif nb_crash == 1:
        context[slave_id].setValues(2, 43 + zone, [True])
        context[slave_id].setValues(4, 61, [2])


def arret_stand(context, voiture, slave_id=0x00):
    context[slave_id].setValues(2, 20 + voiture, [True])
    
    nb_penalites = context[slave_id].getValues(4, voiture, count=1)[0]
    temps_total_penalites = nb_penalites * 5
    temps_voiture = context[slave_id].getValues(4, 40 + voiture, count=1)[0]
    context[slave_id].setValues(4, 40 + voiture, [temps_voiture + temps_total_penalites])
    
    context[slave_id].setValues(4, voiture, [0])


def appliquer_penalite(context, voiture, slave_id=0x00):
    penalite_actuelle = context[slave_id].getValues(4, voiture, count=1)[0]
    context[slave_id].setValues(4, voiture, [penalite_actuelle + 1])


def verif_temps_crash(context, slave_id=0x00):
    for i in range(1, 21):
        est_crash = context[slave_id].getValues(2, i, count=1)[0]
        if est_crash:
            temps_penalite = context[slave_id].getValues(4, 20 + i, count=1)[0]
            temps_penalite += 1
            context[slave_id].setValues(4, 20 + i, [temps_penalite])
            
            if temps_penalite >= 40:
                context[slave_id].setValues(4, 20 + i, [0])
                context[slave_id].setValues(2, i, [False])


def verif_temps_stand(course_en_cours, context, slave_id=0x00):
    if course_en_cours==True:
        for i in range(1, 21):
            est_stand = context[slave_id].getValues(2, 20 + i, count=1)[0]
            if est_stand:
                temps_stand = context[slave_id].getValues(4, i, count=1)[0]
                temps_stand += 1
                context[slave_id].setValues(4, i, [temps_stand])
            
                if temps_stand >= 10:
                    context[slave_id].setValues(2, 20 + i, [False])
                    context[slave_id].setValues(4, i, [0])


def verif_drapeaux(context, slave_id=0x00):
    voitures_crash_actives = []
    for i in range(1, 21):
        if context[slave_id].getValues(2, i, count=1)[0]:
            voitures_crash_actives.append(i)
    
    nb_voitures_crash = len(voitures_crash_actives)
    
    if nb_voitures_crash == 0:
        for zone in range(1, 4):
            context[slave_id].setValues(2, 46 + zone, [False])
        context[slave_id].setValues(2, 49, [False])
        
        for zone in range(1, 4):
            context[slave_id].setValues(2, 40 + zone, [False])
            context[slave_id].setValues(2, 43 + zone, [False])
        
        context[slave_id].setValues(4, 61, [0])
        context[slave_id].setValues(2, 0, [True])
        
    elif nb_voitures_crash >= 2:
        context[slave_id].setValues(2, 50, [True])
        for zone in range(1, 4):
            context[slave_id].setValues(2, 46 + zone, [False])
        
        context[slave_id].setValues(2, 0, [False])
        
    else:
        context[slave_id].setValues(2, 50, [False])
        
        crashes_zone = {1: False, 2: False, 3: False}
        
        for zone in range(1, 4):
            if context[slave_id].getValues(2, 40 + zone, count=1)[0]:
                crashes_zone[zone] = True
        
        for zone in range(1, 4):
            if context[slave_id].getValues(2, 43 + zone, count=1)[0]:
                crashes_zone[zone] = True
        
        for zone in range(1, 4):
            if crashes_zone[zone]:
                context[slave_id].setValues(2, 46 + zone, [True])
            else:
                context[slave_id].setValues(2, 46 + zone, [False])
        
        context[slave_id].setValues(2, 0, [True])


if __name__ == '__main__':
    device = ModbusDeviceContext(
        ir=ModbusSequentialDataBlock(0, [0] * 120),
        di=ModbusSequentialDataBlock(0, [False] * 62)
    )
    
    context = ModbusServerContext(devices=device, single=True)
    
    sim_thread = Thread(target=sim_course_infini, args=(context,))
    sim_thread.daemon = True
    sim_thread.start()
    
    StartTcpServer(context=context, address=("0.0.0.0", 502))