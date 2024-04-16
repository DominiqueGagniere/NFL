# Importation des modules (pip install -r requirement.txt)
from flask import Flask, jsonify, render_template, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import time
import threading
import datetime
import socket

app = Flask(__name__) # Instance de la classe Flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:1234@172.18.0.33/nester' #URI de la bdd postgres 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # Test de la fonction True 
app.secret_key = 'H,ObpL+jx0(nAu9j!seY[9B39-y<khl76'
db = SQLAlchemy(app) # Instance de SQLAlchemy 
migrate = Migrate(app, db) # Instance de Flask-Migrate 

# Génération d'un modèle pour la table du Dashboard avec ID / Hostname / IP / Statut / Request_time
class NesterFrontpage(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    statut = db.Column(db.String(10), nullable=True)
    hostname = db.Column(db.String(50), nullable=False)
    random_port = db.Column(db.Integer)
    ip_address_list = db.Column(db.PickleType)
    os_v = db.Column(db.String(120))
    count_ip_address = db.Column(db.Integer)
    external_ip = db.Column(db.String(15), nullable=False)
    latency_wan = db.Column(db.Float)
    last_request = db.Column(db.String(15), nullable=False)

# Génération d'un modèle pour la table des détails 
class NesterDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machines_number = db.Column(db.Integer)
    open_ports = db.Column(db.PickleType) 
    ip_adresses = db.Column(db.PickleType)  
    hostname = db.Column(db.String(120))
    host_ip = db.Column(db.PickleType)
    latency_wan = db.Column(db.Float)
    statut = db.Column(db.String(50))
    os_v = db.Column(db.String(120))
    agent_version = db.Column(db.String(50))
                    
def manage_status_of_host():
    with app.app_context():
        while True: 
            all_client = NesterFrontpage.query.all()
            now = time.time()
            try:
                for client in all_client:
                    #search_id = client.id
                    print(f"[NESTER][INFO] Checking the status of : {client.hostname}")
                    time.sleep(3)
                    if now - float(client.last_request) > 20 and now - float(client.last_request) < 350:
                        print(now)
                        print(float(client.last_request))
                        print(now - float(client.last_request))
                        client.statut = "Disconnected"
                    elif now - float(client.last_request) > 600: # Cette partie du code peut rendre une erreur en essayant de détruire une entité déjà inexistante
                        del_client = db.session.query(NesterFrontpage).filter_by(id=client.id).first()
                        if del_client is not None: # Vérification du statut de l'entité avant .delete 
                            db.session.delete(del_client)
            except Exception as e: 
                print(f"[NESTER][STATUT_MANAGER][ERROR] {e}")
            db.session.commit()


# Pour utiliser cette partie, executer : harvester.py ou le stack de client avec 'docker-compose up' 
# Cette route n'accepte que les requêtes PUT (Création et mise à jour)
@app.route('/envoyer-client-info', methods=['PUT'])
def client_info():
    data = request.get_json() # Récupére le JSON envoyé par client.py 
    statut = data.get('statut') # Assigne des variables aux éléments du PUT 
    hostname = data.get('hostname')
    ip_address_list = data.get('ip_address_list')
    os_v = data.get('os_v')
    count_ip_address = data.get('count_ip_address')
    random_port = data.get('random_port')
    external_ip = data.get('external_ip')
    latency_wan = data.get('latency_wan') if isinstance(data.get('latency_wan'), list) else data.get('latency_wan')
    last_request = data.get('request_time')

    if not hostname or not ip_address_list or not statut or not last_request : # Vérifie la pertinence des données et en cas de d'incohérence renvoie un code 400 
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return jsonify({'status' : 'error',
                        'timestamp': timestamp,
                        'data': [statut, hostname, ip_address_list, count_ip_address, os_v, random_port, latency_wan, last_request],
                        'message': "Invalid Value"
                        
        }), 400 # Bad Request 
    
    data_search = NesterFrontpage.query.filter_by(hostname=hostname).first() # Ne créer pas une nouvelle entrée si une avec la même IP existe 
    if data_search:
        data_search.ip_address_list = ip_address_list
        data_search.statut = statut
        data_search.count_ip_address = count_ip_address
        data_search.external_ip = external_ip
        data_search.os_v = os_v
        data_search.random_port = random_port
        data_search.latency_wan = latency_wan
        data_search.last_request = last_request
    else: # Sinon le fait 
        new_data = NesterFrontpage(hostname=hostname, ip_address_list=ip_address_list, statut=statut, os_v=os_v, count_ip_address=count_ip_address, external_ip=external_ip, random_port=random_port, last_request=last_request)
        db.session.add(new_data)
    
    db.session.commit() # Commit les data retravaillé à la DB
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return jsonify({
        'status': 'Success',
        'timestamp': timestamp,
        'data': [statut, hostname, ip_address_list, count_ip_address, random_port, latency_wan, last_request],
        'message': 'The data for the Nester dashboard was received successfully',
}), 200 # Envoie une confirmation 

@app.route('/envoyer-client-details', methods=['PUT'])
def client_details():
    data_details = request.get_json()
    
    # Vérifiez si une entrée avec ce hostname existe déjà
    existing_detail = NesterDetails.query.filter_by(hostname=data_details.get('hostname')).first()
    
    if existing_detail:
        # Mettre à jour les champs existants
        existing_detail.open_ports = data_details.get('open_ports')
        existing_detail.ip_adresses = data_details.get('ip_adresses')
        existing_detail.host_ip = data_details.get('host_ip')
        existing_detail.latency_wan = data_details.get('latency_wan')[0] if isinstance(data_details.get('latency_wan'), list) else data_details.get('latency_wan')
        existing_detail.statut = data_details.get('statut')
        existing_detail.os_v = data_details.get('os_v')
        existing_detail.agent_version = data_details.get('agent_version')
    else:
        # Créez une nouvelle instance et ajoutez-la si aucune entrée existante n'a été trouvée
        new_data_details = NesterDetails(
            machines_number = int(data_details.get('machines_number')),
            open_ports = data_details.get('open_ports')[0],
            ip_adresses = data_details.get('ip_adresses'),
            hostname = data_details.get('hostname'),
            host_ip = data_details.get('host_ip'),
            latency_wan = data_details.get('latency_wan')[0] if isinstance(data_details.get('latency_wan'), list) else data_details.get('latency_wan'),
            statut = data_details.get('statut'),
            os_v = data_details.get('os_v'),
            agent_version = data_details.get('agent_version')
        )
        db.session.add(new_data_details)
        
    db.session.commit()
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return jsonify({
        'status': 'Success',
        'timestamp': timestamp,
        'data': [data_details],
        'message': 'The data for the Nester details was received successfully',
}), 200 # Envoie une confirmation

@app.route('/', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST': # Si la requète est "POST" (envoie de donnée) 
        username = request.form['username']
        password = request.form['password']
        
        if username == "admin" and password == "nfl@admin":
            print("Connexion réussie")
            return redirect('/voir-client-info')
        else:
            flash("Connexion refusée. Merci de réessayer votre nom d'utilisateur ou votre mot de passe !")
            return redirect('/')
    if request.method == 'GET': ##
        return render_template('login.html', hostname=socket.gethostname()) # Si la requète est "GET" (récupération de donnée )


#Voir les infos des clients
@app.route('/voir-client-info')
def view_client_info():
    data_fp = NesterFrontpage.query.all()      # Récupère tous les enregistrements FIXME
    return render_template('dashboard.html', data_fp=data_fp)

#voir les détails
@app.route('/voir-client-info/<hostname>')
def details(hostname):
    data_details = NesterDetails.query.filter_by(hostname=hostname).first()
    if data_details: 
        return render_template('clientdb.html', data_details=data_details)
    else: 
        return "Aucune information trouvée pour le hostname spécifié.", 404

if __name__ == '__main__':
    ##try:
    ##    with app.app_context():
    ##      db.create_all()
    ##except Exception as e:
    ##    print(f"[NESTER][ERROR][DB GENERATION] {e}")
    check_statut = threading.Thread(target=manage_status_of_host)
    check_statut.start()
    app.run(debug=True, host='0.0.0.0', port=5000)

