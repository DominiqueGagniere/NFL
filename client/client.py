import socket
import requests
import time

# Obtenir le nom d'hôte, l'ip et le statut 
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
statut = "Connecté"
request_time = time.time()



# hostname en face de la colonne hostname
data = {'hostname': hostname, 'ip_address': ip, 'statut': statut, 'request_time': request_time}

# URL de l'API
url = 'http://192.168.1.9:5000/envoyer-client-info'  

while True:
    response = requests.put(url, json=data)
    print(response.text)
    time.sleep(30)