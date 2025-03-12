![DALL·E 2023-12-30 12 38 31 - A minimalist banner representing an API for the NFL, featuring a monochromatic black design  The background is a deep, matte black, providing a stark ](https://github.com/DominiqueGagniere/NFL/assets/78609360/6b543220-b22d-4182-a9d2-2f9dcf040df9)
# NFL API - Projet EPSI ASRBD  
## Captures
![Capture d'écran 2024-02-18 111439](https://github.com/user-attachments/assets/c6c4ccde-5a32-4347-aef2-dbad563bc64d)

## Les fichiers du projet et leurs rôles 
- nester.py 
    - Le serveur du projet, fonctionnant via une base de données PostgreSQL (nécessite une base de données PostgreSQL disponible)
- nester_SQLite.py 
    - Le serveur du projet avec la technologie de base de données SQLite (La base se créer au lancement du .py)
- harvester/harvester.py 
    - Le client de l'API (trois options de lancement : --url_nester_details, --url_nester, --network)


## Récupération du projet & installation des dépendances 
```
git clone https://github.com/DominiqueGagniere/NFL.git
cd NFL/
pip install -r requirements.txt
cd harvester/
pip install -r requirements.txt
```
## Les fonctionnalités 
### nester.py 
- Gère une page de login
- Initialise une base de données SQLite temporaire
- Ou se connecte à une base de donnée postgresql 
- Gère la réception des données via /envoyer-client-info & /envoyer-client-details
- Compare les données pour éviter les doublons dans l'interface
- Vérifie l'inactivité du client pour afficher les déconnections 
- Supprime les hosts ayant plus de dix minutes d'inactivité de l'interface
- Créer une page http://localhost/voir-client-info qui affiche les données de la BDD. 

### harvester.py 
- Envoi de la machine hôte vers /envoyer-client-info du Nester les infos pour la page d'accueil du Nester
- Envoi une copie de son interface locale via /envoyer-client-details
- Effectue des scans nmap du réseau et les envois à l'API en fonction de --network au lancement  

## Erreur courante 
##### File "C:\Users\user\Documents\GitHub\NFL\.venv\Lib\site-packages\sqlalchemy\engine\base.py", line 1969, in _exec_single_context
Supprimer le dossier "instance" qui contient la BDD (pour la version SQLite)
