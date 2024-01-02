# Importation des modules (pip install -r requirement.txt)
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # Instance de la classe Flask 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdd.db' #URI de la bdd qui va être crée  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Pas de suivi des modifications (bdd de test)
app.secret_key = "nfl"
db = SQLAlchemy(app) # Instance de SQLAlchemy 

# Génération d'un modèle pour la db avec ID / Hostname / IP
class Data(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    statut = db.Column(db.String(10), nullable=True)

    def __repr__(self): # ?? 
        return f'<MyData {self.hostname}>'

# Création de la forme de la db 
def create_tables():
    db.create_all()

def setup():
    create_tables()

#Pour utiliser cette partie, executer : client.py 
@app.route('/envoyer-client-info', methods=['PUT'])
def client_info():
    data = request.get_json()
    statut = data.get('statut')
    hostname = data.get('hostname')
    ip_address = data.get('ip_address')
    
    if not hostname or not ip_address or not statut :
        return jsonify({'error' : 'hostname/IP/Statut est absent'}), 400 
    
    data_search = Data.query.filter_by(hostname=hostname).first()
       
    if data_search: 
        data_search.ip_address = ip_address
        data_search.statut = statut 
    else:
        new_data = Data(hostname=hostname, ip_address=ip_address, statut=statut)
        db.session.add(new_data)
    
    
    
    db.session.commit()
    return jsonify({'message': 'Hostname et IP enregistrés ou mis à jour avec succès dans la DB'}), 200

@app.route('/', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == "admin" and password == "nfl":
            session['logged_in'] = True
            print("Connexion réussie")
            return redirect('/voir-client-info')
        else:
            flash('Connexion refusée. Merci de réessayer votre mot de passe !')
            print("Connexion échouée")
    return render_template('connexion.html')


#Voir les infos des clients
@app.route('/voir-client-info')
def view_client_info():
    all_data = Data.query.all()      # Récupère tous les enregistrements
    return render_template('hostname.html', hostnames=all_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

