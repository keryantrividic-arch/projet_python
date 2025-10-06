# Simulation de Course Automobile avec Modbus

## Description

Ce projet simule une course automobile avec 20 voitures en utilisant le protocole Modbus TCP. Le système est composé de deux programmes :
- Un **serveur** qui gère la simulation de la course en temps réel
- Un **client** qui affiche l'état de la course en continu

## Prérequis

- Python 3.7 ou supérieur
- Bibliothèque `pymodbus`

### Installation des dépendances

```bash
pip install pymodbus
```

## Architecture

### Serveur (`serveur.py`)

Le serveur simule une course infinie avec les événements suivants :
- **Crashes** : Probabilité de 5% par seconde
- **Arrêts au stand** : Probabilité de 50% par seconde
- **Pénalités** : Probabilité de 10% par seconde

Le serveur tourne sur le port **502** (port Modbus standard).

### Client (`client.py`)

Le client se connecte au serveur et affiche en temps réel :
- Le temps total de la course
- L'état de chaque voiture (en course, crashée, au stand)
- Les pénalités accumulées
- Les drapeaux actifs (jaune ou rouge)

## Registres Modbus

### Input Registers (IR)

| Adresse | Description |
|---------|-------------|
| IR 0 | Temps total de la course (en tours) |
| IR 1-20 | Nombre de pénalités de la voiture X (ou temps au stand si la voiture y est) |
| IR 21-40 | Temps de crash de la voiture X (en secondes) |
| IR 41-60 | Temps réalisé par la voiture X (84 ± 10 secondes de base) |
| IR 61 | Compteur de crashes total (0, 1 ou 2) |

### Discrete Inputs (DI)

| Adresse | Description |
|---------|-------------|
| DI 0 | Course en cours (True/False) |
| DI 1-20 | Voiture X crashée (True/False) |
| DI 21-40 | Voiture X au stand (True/False) |
| DI 41-43 | Crash dans la zone 1/2/3 (premier crash) |
| DI 44-46 | Crash dans la zone 1/2/3 (deuxième crash) |
| DI 47-49 | Drapeau jaune dans la zone 1/2/3 |
| DI 50 | Drapeau rouge |

## Règles de la Course

### Crashes
- Une voiture peut crasher dans l'une des 3 zones du circuit
- Temps de récupération après un crash : **40 secondes**
- Une voiture ne peut crasher qu'une seule fois à la fois
- Si **2 voitures différentes** sont crashées → **Drapeau rouge** (course en pause)
- Si **1 voiture** est crashée → **Drapeau jaune** dans sa zone

### Arrêts au Stand
- Durée d'un arrêt au stand : **10 secondes**
- Les pénalités sont appliquées lors de l'arrêt au stand
- Chaque pénalité ajoute **5 secondes** au temps total de la voiture
- Le compteur de pénalités est remis à zéro après l'arrêt

### Pénalités
- Une voiture peut recevoir plusieurs pénalités (1, 2, 3...)
- Affichage : nombre de pénalités × 5 secondes
  - 1 pénalité = +5s
  - 2 pénalités = +10s
  - 3 pénalités = +15s
- Les pénalités ne s'appliquent que lors du prochain arrêt au stand

### Drapeaux

#### 🟨 Drapeau Jaune
- Activé quand **1 voiture** est crashée
- Indique la zone du crash
- La course continue

#### 🟥 Drapeau Rouge
- Activé quand **2 voitures ou plus** sont crashées
- La course est **mise en pause** (DI 0 = False)
- **Toutes les voitures non crashées** vont automatiquement au stand
- La course reprend quand il ne reste plus qu'une ou aucune voiture crashée

## Utilisation

### Lancement du serveur

```bash
python serveur.py
```

Le serveur démarre et écoute sur le port 502.

### Lancement du client

Dans un autre terminal :

```bash
python client.py
```

Le client affiche les informations en temps réel, rafraîchies chaque seconde.

### Arrêt

- Pour arrêter le client : `Ctrl+C`
- Pour arrêter le serveur : `Ctrl+C`

## Exemple d'Affichage

```
================================================================================
Temps total: 125s
Course en cours: Oui

--------------------------------------------------------------------------------
VOITURES:
--------------------------------------------------------------------------------
Voiture  1: Temps: 87s
Voiture  2: Temps: 92s (Pénalité: 2x5s = +10s à ajouter)
Voiture  3: AU STAND depuis 3s
Voiture  4: CRASH depuis 15s
Voiture  5: Temps: 79s
...

--------------------------------------------------------------------------------
DRAPEAUX:
--------------------------------------------------------------------------------
🟨 DRAPEAU JAUNE - Zone 2
   Voiture(s): 4
================================================================================
```

## Structure du Code

### Serveur

Fonctions principales :
- `sim_course_infini()` : Boucle principale de simulation
- `aleatoire_voiture()` : Sélectionne une voiture aléatoire disponible
- `crash()` : Enregistre un crash
- `arret_stand()` : Gère l'arrêt au stand et applique les pénalités
- `appliquer_penalite()` : Ajoute une pénalité à une voiture
- `verif_temps_crash()` : Gère le temps de récupération après crash
- `verif_temps_stand()` : Gère le temps passé au stand
- `verif_drapeaux()` : Gère l'activation des drapeaux jaune/rouge
- `mettre_toutes_voitures_au_stand()` : Force toutes les voitures au stand (drapeau rouge)

### Client

Fonction principale :
- `afficher_course()` : Se connecte au serveur et affiche les informations en boucle

## Notes Techniques

- Le serveur utilise des threads pour gérer la simulation en parallèle du serveur Modbus
- Le temps de la course continue même si elle est en pause (drapeau rouge)
- Les temps des voitures varient aléatoirement entre 74 et 94 secondes (84 ± 10)
- Le client gère les erreurs de connexion et de lecture des registres

