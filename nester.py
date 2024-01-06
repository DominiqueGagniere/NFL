# Importation des modules (pip install -r requirement.txt)
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
import threading

app = Flask(__name__) # Instance de la classe Flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdd.db' #URI de la bdd qui va être crée  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Pas de suivi des modifications (bdd de test)
app.secret_key = "nfl" # inutile pour l'instant 
db = SQLAlchemy(app) # Instance de SQLAlchemy 

# Génération d'un modèle pour la db avec ID / Hostname / IP / Statut / Request_time
class Data(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    statut = db.Column(db.String(10), nullable=True)
    hostname = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    last_request = db.Column(db.String(15), nullable=False)

    def __repr__(self): # ?? 
        return f'<MyData {self.hostname}>'

# Création de la forme de la db 
def create_tables():
    db.create_all()

def setup():
    create_tables()

#data_search = Data.query.filter_by(hostname=hostname).first()
def manage_status_v1():
    with app.app_context():
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
            try:
                all_client = Data.query.all()
                print (all_client)
            except: 
                pass
            
check_statut = threading.Thread(target=manage_status_v2)
check_statut.start()

#Pour utiliser cette partie, executer : client.py 
# Cette route n'accepte que les requêtes PUT (Création et mise à jour)
@app.route('/envoyer-client-info', methods=['PUT'])
def client_info():
    data = request.get_json() # Récupére le JSON envoyé par client.py 
    statut = data.get('statut') # Assigne des variables aux éléments du PUT 
    hostname = data.get('hostname')
    ip_address = data.get('ip_address')
    last_request = data.get('request_time')
    
    if not hostname or not ip_address or not statut or not last_request : # Vérifie la pertinence des données et en cas de d'incohérence renvoie un code 400 
        return jsonify({'error' : 'hostname/IP/Statut est absent'}), 400 
    
    data_search = Data.query.filter_by(hostname=hostname).first() # Ne créer pas une nouvelle entrée si une avec la même IP existe 
    if data_search: 
        data_search.ip_address = ip_address
        data_search.statut = statut 
    else: # Sinon le fait 
        new_data = Data(hostname=hostname, ip_address=ip_address, statut=statut, last_request=last_request)
        db.session.add(new_data)
    
    db.session.commit() # Commit les data retravaillé à la DB 
    return jsonify({'message': 'Hostname et IP enregistrés ou mis à jour avec succès dans la DB'}), 200 # Envoie une confirmation 

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

