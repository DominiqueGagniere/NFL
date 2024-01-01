![DALL·E 2023-12-30 12 38 31 - A minimalist banner representing an API for the NFL, featuring a monochromatic black design  The background is a deep, matte black, providing a stark ](https://github.com/DominiqueGagniere/NFL/assets/78609360/6b543220-b22d-4182-a9d2-2f9dcf040df9)
# NFL API - Projet EPSI ASRBD  
## Les fichiers du projets
- app.py 
- client.py

## Les fonctionnalités 
### App.py 
- Initialise une base de données SQLite temporaire avec trois colonnes (id, hostname, ip_address)
- Gère la réception des données via http://localhost/envoyer-client-info
- Créer une page http://localhost/voir-client-info qui affiche les données de la BDD. 

### Client.py 
- Envoie l'IP et l'Hostname de la machine hôte vers /envoyer-client-info 

## Erreur courante 
### File "C:\Users\user\Documents\GitHub\NFL\.venv\Lib\site-packages\sqlalchemy\engine\base.py", line 1969, in _exec_single_context
Supprimer le dossier "instance" qui contient la BDD 
