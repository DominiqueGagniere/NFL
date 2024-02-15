from flask import Flask, render_template, request, redirect, flash, session
import socket, requests, time, json
from tcp_latency import measure_latency
import platform, subprocess, time, threading
import nmap # Utile ? 
import sys
import random # Pour les tests Docker
import urllib.request # Pour l'ip externe (Standard Library)

app = Flask(__name__)  # Instance de la classe Flask

## Logique de lancement nmap 
# Lecture du JSON
with open('scan_result.json', 'r') as json_file:
  data = json.load(json_file)
num_connected_hosts = data["connected_hosts"]
hosts_and_ports = {}
ports_status = {}
for host, info in data["hosts"].items():
  hosts_and_ports[host] = info["open_ports"]  # Add 'ip' : [ports]
  ports_status[host] = 'yes' if info["open_ports"] else 'no'

# Lancement périodique (10 min) du script d'écriture du JSON 
def scan_network():
  while True:
    subprocess.run(["python", "./client/ping_nmap.py"], bufsize=0)
    time.sleep(600)

# Lancement d'un thread pour l'écriture du JSON
def start_scan_network():
  thread_scan_network = threading.Thread(target=scan_network)
  thread_scan_network.start()

# Destination 
url_nester = 'http://127.0.0.1:5000/envoyer-client-info'
url_nester_details = 'http://127.0.0.1:5000/envoyer-client-details'

## Récupération et traitement des données  
# Donnée pour API
def refresh_fp_data(random_port):
  hostname = socket.gethostname()
  try:
    hostname_search, _, ip_addresses_list = socket.gethostbyname_ex(hostname)
  except socket.gaierror:
    ip_addresses_list = 'Unavailable'
  count_ip_address = len(ip_addresses_list)
  external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
  statut = 'Connected'
  request_time = time.time()
  agent_version = "0.1"
  latency_result = measure_latency(host='epsi.fr')
  latency_wan = int(latency_result[0]) if latency_result else None
  # Random port est récupérer dans la fonction
  
  data_fp = {
    'hostname': hostname,
    'ip_address_list': ip_addresses_list, 
    'statut': statut,
    'request_time': request_time,
    'agent_version': agent_version,
    'host_ip': ip_addresses_list,
    'external_ip': external_ip, 
    'random_port': random_port,
    'count_ip_address': count_ip_address,
    'latency_wan': latency_wan
  }
  
  return data_fp

def refresh_details_data():
  hostname = socket.gethostname()
  try:
    host_ip = ', '.join(socket.gethostbyname_ex(hostname)[2])
  except socket.gaierror:
    host_ip = 'Unavailable'
  os_v = platform.platform()
  statut = 'Connected'
  agent_version = "0.1"
  latency_result = measure_latency(host='epsi.fr')
  latency_wan = latency_result[0] if latency_result else None
  ip_adresses = list(hosts_and_ports.keys())
  open_ports = list(hosts_and_ports.values())
  machines_number = len(ip_adresses)
  
  data_details = {
    'hostname': hostname,
    'host_ip': host_ip,
    'os_v': os_v,
    'statut': statut,
    'latency_wan': latency_wan,
    'ip_adresses': ip_adresses,
    'open_ports': open_ports,
    'machines_number': machines_number,
    'agent_version': agent_version
    
  }
  
  return data_details

# Envoie des requêtes vers la frontpage
def put_to_nester_fp(url_nester, random_port):
  while True:
    data_fp = refresh_fp_data(random_port)
    try:
      response = requests.put(url_nester, json=data_fp)
      print(response.text)
    except Exception as e:
        print(f"""
[ERREUR] Emplacement : {sys.argv[0]} : {sys.exc_info()[2].tb_lineno}
Nom de la fonction: {sys._getframe().f_code.co_name}
Description de l'erreur : {type(e).__name__}
            """)
    
    time.sleep(30)

# Envoi des requêtes vers la page détails du nester 
def put_to_nester_details(url_nester_details):
    while True:
      data_details = refresh_details_data()
      try:
        response = requests.put(url_nester_details, json=data_details)
        print(response.text)
      except Exception as e:
        print(f"""
[ERREUR] Emplacement : {sys.argv[0]} : {sys.exc_info()[2].tb_lineno}
Nom de la fonction: {sys._getframe().f_code.co_name}
Description de l'erreur : {type(e).__name__}
            """)
      
      time.sleep(30)
      


# Thread de l'envoi périodique des données sur la page d'accueil du Nester 
def start_put_to_nester_fp(url_nester, random_port):
  thread_scan_network = threading.Thread(target=put_to_nester_fp,args=(url_nester,random_port))
  thread_scan_network.start()

# Thread de l'envoi périodique des données sur la page de détail du Nester 
def start_put_to_nester_details(url_nester_details):
  thread_scan_network = threading.Thread(target=put_to_nester_details,args=(url_nester_details,))
  thread_scan_network.start()


@app.route('/')
def connexion():
  if request.method == 'POST':
    # Si la requète est "POST" (envoie de donnée)
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "nfl":
      session['logged_in'] = True
      print("Connexion réussie")
      return redirect('/dashboard')
    else:
      flash('Connexion refusée. Merci de réessayer votre mot de passe !')
      print("Connexion échouée")
  return render_template('connexion.html', hostname=socket.gethostname())


@app.route('/dashboard')
def dashboard():
  data_details = refresh_details_data()
  return render_template('clientdb.html', data_details=data_details) 

if __name__ == '__main__':
  #start_scan_network()
  random_port = random.randrange(4000, 4900)
  start_put_to_nester_fp(url_nester, random_port)
  start_put_to_nester_details(url_nester_details)
  print("Attention t'es dans la branche css bg, pense au PR")
  app.run(debug=True, host='0.0.0.0', port=random_port)
