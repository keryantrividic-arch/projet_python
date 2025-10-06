import time
from pymodbus.client import ModbusTcpClient

def afficher_course():
    client = ModbusTcpClient('localhost', port=502)
    if not client.connect():
        print("Erreur: Impossible de se connecter au serveur Modbus")
        return
    
    print("Connecté au serveur Modbus")
    
    try:
        while True:
            time.sleep(1)
            
            print("\n" + "="*80)
            
            result = client.read_input_registers(address=0, count=1)
            if result.isError():
                print("Erreur de lecture du temps total")
                continue
            temps_total = result.registers[0]
            print(f"Temps total: {temps_total}s")
            
            result = client.read_discrete_inputs(address=0, count=1)
            if result.isError():
                print("Erreur de lecture du statut de course")
                continue
            course_en_cours = result.bits[0]
            print(f"Course en cours: {'Oui' if course_en_cours else 'Non'}")
            
            print("\n" + "-"*80)
            print("VOITURES:")
            print("-"*80)
            
            for i in range(1, 21):
                result_crash = client.read_discrete_inputs(address=i, count=1)
                result_stand = client.read_discrete_inputs(address=20 + i, count=1)
                result_temps = client.read_input_registers(address=40 + i, count=1)
                result_penalite = client.read_input_registers(address=i, count=1)
                
                if result_crash.isError() or result_stand.isError() or result_temps.isError() or result_penalite.isError():
                    print(f"Voiture {i:2d}: Erreur de lecture")
                    continue
                
                est_crash = result_crash.bits[0]
                est_stand = result_stand.bits[0]
                temps_voiture = result_temps.registers[0]
                nb_penalites = result_penalite.registers[0]
                
                print(f"Voiture {i:2d}: ", end="")
                
                if est_crash:
                    result_temps_crash = client.read_input_registers(address=20 + i, count=1)
                    if not result_temps_crash.isError():
                        temps_crash = result_temps_crash.registers[0]
                        print(f"CRASH depuis {temps_crash}s")
                elif est_stand:
                    print(f"AU STAND depuis {nb_penalites}s")
                else:
                    print(f"Temps: {temps_voiture}s", end="")
                    if nb_penalites > 0:
                        temps_penalite_total = nb_penalites * 5
                        print(f" (Pénalité: {nb_penalites}x5s = +{temps_penalite_total}s à ajouter)", end="")
                    print()
            
            print("\n" + "-"*80)
            print("DRAPEAUX:")
            print("-"*80)
            
            drapeau_jaune_actif = False
            for zone in range(1, 4):
                result_drapeau = client.read_discrete_inputs(address=46 + zone, count=1)
                if result_drapeau.isError():
                    continue
                    
                drapeau_jaune = result_drapeau.bits[0]
                if drapeau_jaune:
                    drapeau_jaune_actif = True
                    print(f"🟨 DRAPEAU JAUNE - Zone {zone}")
                    
                    voitures_crash_zone = []
                    for voiture in range(1, 21):
                        result_voiture = client.read_discrete_inputs(address=voiture, count=1)
                        if not result_voiture.isError() and result_voiture.bits[0]:
                            voitures_crash_zone.append(voiture)
                    
                    if voitures_crash_zone:
                        print(f"   Voiture(s): {', '.join(map(str, voitures_crash_zone))}")
            
            result_rouge = client.read_discrete_inputs(address=50, count=1)
            if not result_rouge.isError():
                drapeau_rouge = result_rouge.bits[0]
                if drapeau_rouge:
                    print("🟥 DRAPEAU ROUGE")
                    
                    voitures_crash = []
                    for voiture in range(1, 21):
                        result_voiture = client.read_discrete_inputs(address=voiture, count=1)
                        if not result_voiture.isError() and result_voiture.bits[0]:
                            voitures_crash.append(voiture)
                    
                    if voitures_crash:
                        print(f"   Voiture(s): {', '.join(map(str, voitures_crash))}")
                
                if not drapeau_jaune_actif and not drapeau_rouge:
                    print("✅ Aucun drapeau")
            
            print("="*80)
    
    except KeyboardInterrupt:
        print("\nArrêt de l'affichage")
    finally:
        client.close()


if __name__ == '__main__':
    afficher_course()