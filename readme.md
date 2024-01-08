![DALL·E 2023-12-30 12 38 31 - A minimalist banner representing an API for the NFL, featuring a monochromatic black design  The background is a deep, matte black, providing a stark ](https://github.com/DominiqueGagniere/NFL/assets/78609360/6b543220-b22d-4182-a9d2-2f9dcf040df9)
# NFL API - Projet EPSI ASRBD  
## Les fichiers du projet
- nester.py 
- client.py

## Installation 
```
git clone https://github.com/DominiqueGagniere/NFL.git
cd NFL/
pip install -r requirements.txt
cd client/
pip install -r requirements.txt
```
## Les fonctionnalités 
### nester.py 
- Gère une page de login
- Initialise une base de données SQLite temporaire avec quatre colonnes (id, hostname, ip_address, last_request)
- Gère la réception des données via http://localhost/envoyer-client-info
- Compare les données pour éviter les doublons dans l'interface
- Supprime les hosts ayant plus de dix minutes d'inactivité de l'interface
- Créer une page http://localhost/voir-client-info qui affiche les données de la BDD. 

### client.py 
- Envoie de la machine hôte vers http://localhost/envoyer-client-info 

## Erreur courante 
##### File "C:\Users\user\Documents\GitHub\NFL\.venv\Lib\site-packages\sqlalchemy\engine\base.py", line 1969, in _exec_single_context
Supprimer le dossier "instance" qui contient la BDD 
