# Importation des modules (pip install -r requirement.txt)
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
import threading
import json

app = Flask(__name__) # Instance de la classe Flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdd.db' #URI de la bdd qui va être crée  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Pas de suivi des modifications (bdd de test)
app.secret_key = "nfl" # inutile pour l'instant 
db = SQLAlchemy(app) # Instance de SQLAlchemy 

# Génération d'un modèle pour la table du Dashboard avec ID / Hostname / IP / Statut / Request_time
class Data(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    statut = db.Column(db.String(10), nullable=True)
    hostname = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    last_request = db.Column(db.String(15), nullable=False)

# Génération d'un modèle pour la table des détails 
class HarvesterDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_number = db.Column(db.Integer)
    open_ports = db.Column(db.String)  # Peut-être stocker comme JSON ou séparé par des virgules
    ip_addresses = db.Column(db.String)  # Idem, selon le nombre d'adresses
    hostname = db.Column(db.String(120))
    host_ip = db.Column(db.String(120))
    latency_wan = db.Column(db.Float)
    statut = db.Column(db.String(50))
    os_v = db.Column(db.String(120))
    agent_version = db.Column(db.String(50))

# Création de la forme de la db 
def create_tables():
    db.create_all()

def setup():
    create_tables()

# Modification des status en fonction de la dernière requête 
def manage_status_v1():
    while True:
        now = time.time()
        try:
            hostname, search = db.session.query(
                Data.hostname, 
                db.func.min(Data.last_request)
            ).group_by(Data.hostname).order_by(db.func.min(Data.last_request)).first() # Le modèle de la bdd Data, requête, spécifie que nous voulons une entitée, minimal 
            search = float(search)      
            print(search)
            time.sleep(10)
        except Exception as e:
            if search == None:
                    search = 1
            print(e)
            time.sleep(10)
            
        delta = now - search 
        if delta > 60:
            update_request = Data.query.filter_by(hostname=hostname).first() # Instance de SQLAlch, requete dans la table Data, filtrer si par si hostname la variable est égale a hostname la value, premier résultat 
            if update_request:
                update_request.statut = 'Déconnecté'
                db.session.commit()
                    
def manage_status_v2():
    with app.app_context():
        while True: 
            all_client = Data.query.all()
            now = time.time()
            try:
                for client in all_client:
                    search_id = client.id
                    print(f"Je fais un tour pour {client.hostname}")
                    time.sleep(1)
                    if now - float(client.last_request) > 60 and now - float(client.last_request) < 600:
                        client.statut = "Disconnected"
                    elif now - float(client.last_request) > 600:
                        del_client = db.session.query(Data).filter_by(id=client.id).first()
                        db.session.delete(del_client)
            except Exception as e: 
                print(f"Euh.. erreur dans le process {e}")
            db.session.commit()
            
def auto_delete_hostname():
    with app.app_context():
        while True: 
            all_client = Data.query.all()
            
                

# Lancement d'un thread en parallèle de l'exécution de Flask    
# check_statut = threading.Thread(target=manage_status_v2)
# check_statut.start()

# Pour utiliser cette partie, executer : client.py ou le stack de client avec 'docker-compose up' 
# Cette route n'accepte que les requêtes PUT (Création et mise à jour)
@app.route('/envoyer-client-info', methods=['PUT'])
def client_info():
    data = request.get_json() # Récupére le JSON envoyé par client.py 
    statut = data.get('statut') # Assigne des variables aux éléments du PUT 
    hostname = data.get('hostname') 
    ip_address = data.get('ip_address')
    last_request = data.get('request_time')
    
    if not hostname or not ip_address or not statut or not last_request : # Vérifie la pertinence des données et en cas de d'incohérence renvoie un code 400 
        return jsonify({'error' : 'hostname/IP/Statut est absent'}), 400 # Bad Request 
    
    data_search = Data.query.filter_by(hostname=hostname).first() # Ne créer pas une nouvelle entrée si une avec la même IP existe 
    if data_search: 
        data_search.ip_address = ip_address
        data_search.statut = statut 
    else: # Sinon le fait 
        new_data = Data(hostname=hostname, ip_address=ip_address, statut=statut, last_request=last_request)
        db.session.add(new_data)
    
    db.session.commit() # Commit les data retravaillé à la DB 
    return jsonify({'message': 'Hostname et IP enregistrés ou mis à jour avec succès dans la DB'}), 200 # Envoie une confirmation 

@app.route('/envoyer-client-details', methods=['PUT'])
def client_details():
    data_details = request.get_json()
    
    # Vérifiez si une entrée avec ce hostname existe déjà
    existing_detail = HarvesterDetails.query.filter_by(hostname=data_details.get('hostname')).first()
    
    if existing_detail:
        # Mettre à jour les champs existants
        existing_detail.machine_number = int(data_details.get('machine_number', 0))
        existing_detail.open_ports = json.dumps(data_details.get('open_ports'))
        existing_detail.ip_addresses = json.dumps(data_details.get('ip_addresses'))
        existing_detail.host_ip = data_details.get('host_ip')
        existing_detail.latency_wan = data_details.get('latency_wan')[0] if isinstance(data_details.get('latency_wan'), list) else data_details.get('latency_wan')
        existing_detail.statut = data_details.get('statut')
        existing_detail.os_v = data_details.get('os_v')
        existing_detail.agent_version = data_details.get('agent_version')
    else:
        # Créez une nouvelle instance et ajoutez-la si aucune entrée existante n'a été trouvée
        new_data_details = HarvesterDetails(
            machine_number = int(data_details.get('machine_number', 0)),
            open_ports = json.dumps(data_details.get('open_ports')),
            ip_addresses = json.dumps(data_details.get('ip_addresses')),
            hostname = data_details.get('hostname'),
            host_ip = data_details.get('host_ip'),
            latency_wan = data_details.get('latency_wan')[0] if isinstance(data_details.get('latency_wan'), list) else data_details.get('latency_wan'),
            statut = data_details.get('statut'),
            os_v = data_details.get('os_v'),
            agent_version = data_details.get('agent_version')
        )
        db.session.add(new_data_details)
    
    db.session.commit()
    return jsonify({'message': f'Détails mis à jour ou ajoutés avec succès {new_data_details}'}), 200

@app.route('/', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST': # Si la requète est "POST" (envoie de donnée) 
        username = request.form['username']
        password = request.form['password']
        
        if username == "admin" and password == "nfl":
            session['logged_in'] = True
            print("Connexion réussie")
            return redirect('/voir-client-info')
        else:
            flash('Connexion refusée. Merci de réessayer votre mot de passe !')
            print("Connexion échouée")
    return render_template('connexion.html') # Si la requète est "GET" (récupération de donnée )


#Voir les infos des clients
@app.route('/voir-client-info')
def view_client_info():
    all_data = Data.query.all()      # Récupère tous les enregistrements
    return render_template('hostname.html', hostnames=all_data)

#voir les détails
@app.route('/voir-client-info/<hostname>')
def details(hostname):
    data_details = HarvesterDetails.query.filter_by(hostname=hostname).first()
    if data_details: 
        return render_template('clientdb.html', data_details=data_details)
    else: 
        return "Aucune information trouvée pour le hostname spécifié.", 404

if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
    check_statut = threading.Thread(target=manage_status_v2)
    check_statut.start()
    app.run(debug=True, host='0.0.0.0', port=5000)

