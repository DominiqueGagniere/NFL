import socket
import requests

# Obtenir le nom d'hôte
hostname = socket.gethostname()
ip = socket.gethostbyname('localhost')
# hostname en face de la colonne hostname
data = {'hostname': hostname, 'ip_address': ip}

# URL de l'API
url = 'http://localhost:5000/envoyer-client-info'  

# Envoyer les données à l'API
response = requests.post(url, json=data)

# Renvoie le code de la requête envoyé 
print(response.text)

