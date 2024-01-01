import socket
import requests
import time

# Obtenir le nom d'hôte, l'ip et le statut 
hostname = socket.gethostname()
ip = socket.gethostbyname('localhost')
statut = "Connecté"
# hostname en face de la colonne hostname
data = {'hostname': hostname, 'ip_address': ip, 'statut': statut}

# URL de l'API
url = 'http://localhost:5000/envoyer-client-info'  

while True:
    response = requests.post(url, json=data)
    print(response.text)
    time.sleep(30)