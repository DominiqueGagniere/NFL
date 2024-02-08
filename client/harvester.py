from flask import Flask, render_template, request, redirect, flash, session
import socket, requests, time, json
from tcp_latency import measure_latency
import platform, subprocess, time, threading
import nmap
import sys

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

# Variable perdu 
url_nester = 'http://127.0.0.1:5000/envoyer-client-info'

## Récupération et traitement des données  
# Donnée pour API
def refresh_fp_data():
  hostname = socket.gethostname()
  host_ip = ', '.join(socket.gethostbyname_ex(hostname)[2])
  statut = 'Connected'
  request_time = time.time()
  agent_version = "0.1"
  
  data_fp = {
    'hostname': hostname,
    'ip_address': host_ip, 
    'statut': statut,
    'request_time': request_time,
    'agent_version': agent_version,
    'host_ip': host_ip
  }
  
  return data_fp
  

# Donnée pour le tableau de bord et l'url 
""" os_v = platform.platform()
latency_result = measure_latency(host='epsi.fr')
latency_wan = latency_result[0] if latency_result else None
ip_adresses = list(hosts_and_ports.keys())
open_ports = list(hosts_and_ports.values())
machines_number = len(ip_adresses)
url_nester_details = 'http://127.0.0.1:5000/envoyer-client-details' """

## Lot de donnée 
# Lot de donnée pour l'envoi au Nester  
#data_fp = {
# 'hostname': hostname,
#   'ip_address': host_ip, 
#   'statut': statut,
#   'request_time': request_time,
#   'agent_version': agent_version,
#   'host_ip': host_ip
#}

# Lot de donnée pour l'affichage local et l'envoi au Nester Details  
#data_details = {
#    'machines_number': machines_number,
#    'open_ports': open_ports,
"""    'ip_adresses': ip_adresses,
    'hostname': hostname,
    'host_ip': host_ip,
    'latency_wan':latency_wan,
    'statut':statut,
    'os_v':os_v,
    'agent_version':agent_version, 
}
 """
# Envoie des requêtes vers la frontpage
def put_to_nester_fp(url_nester):
  while True:
    data_fp = refresh_fp_data()
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
def put_to_nester_details(url_nester_details, data_details):
    while True:
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
def start_put_to_nester_fp(url_nester):
  thread_scan_network = threading.Thread(target=put_to_nester_fp,args=(url_nester,))
  thread_scan_network.start()

# Thread de l'envoi périodique des données sur la page de détail du Nester 
#def start_put_to_nester_details(url_nester_details,data_details):
  #thread_scan_network = threading.Thread(target=put_to_nester_details,args=(url_nester_details,data_details))
  #thread_scan_network.start()


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
  return render_template('connexion.html')


@app.route('/dashboard')
def dashboard():
  return render_template('clientdb.html', data_details = data_details) 

if __name__ == '__main__':
  #start_scan_network()
  start_put_to_nester_fp(url_nester)
  #start_put_to_nester_details(url_nester_details, data_details)
  app.run(debug=True, host='0.0.0.0', port=4000)
