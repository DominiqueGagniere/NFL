from flask import Flask, render_template, request, redirect, flash, jsonify
import socket, requests, time, json
from tcp_latency import measure_latency
import platform, time, threading, os
import nmap3 # Indispensable au fonctionnement de nmap3
import sys 
import random # Pour éviter les conflits de Ports 
import urllib.request # Pour l'ip externe (Standard Library)
import argparse # Pour permettre les arguments CLI 

app = Flask(__name__)  # Instance de la classe Flask
app.secret_key = 'R29z7R.0msFaIEcoUg}SvX9Wxz!R]]n_:'
parser = argparse.ArgumentParser(description="Script pour récupérer des détails réseau") # Instance de argparse

# Ajoutez les arguments souhaités
parser.add_argument('--network', default='192.168.1.0/24',  help="Nom du réseau")
parser.add_argument('--url_nester_details', default='http://127.0.0.1:5000/envoyer-client-details',  help="URL des détails du réseau")
parser.add_argument('--url_nester', default='http://127.0.0.1:5000/envoyer-client-info',  help="URL du réseau")

# Args build
args = parser.parse_args()
# Destination & réseau à scanner
url_nester = args.url_nester
url_nester_details = args.url_nester_details
network = args.network

## Récupération et traitement des données  
# Donnée pour API
def refresh_fp_data(random_port):
  hostname = socket.gethostname()
  try:
    hostname_search, _, ip_addresses_list = socket.gethostbyname_ex(hostname)
  except socket.gaierror:
    ip_addresses_list = 'Unavailable'
  count_ip_address = len(ip_addresses_list)
  external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
  statut = 'Connected'
  request_time = int(time.time())
  agent_version = "1.2"
  os_v = platform.platform()
  #latency_result = measure_latency(host='epsi.fr')
  latency_wan = round(measure_latency(host='epsi.fr')[0] , 3)
  
  data_fp = {
    'hostname': hostname,
    'ip_address_list': ip_addresses_list, 
    'statut': statut,
    'request_time': request_time,
    'agent_version': agent_version,
    'host_ip': ip_addresses_list,
    'os_v': os_v,
    'external_ip': external_ip, 
    'random_port': random_port,
    'count_ip_address': count_ip_address,
    'latency_wan': latency_wan
  }

  return data_fp

#Donnée pour la page Détails 
def refresh_details_data():
  hostname = socket.gethostname()
  try:
    host_ip = ', '.join(socket.gethostbyname_ex(hostname)[2])
  except socket.gaierror:
    host_ip = 'Unavailable'
  os_v = platform.platform()
  statut = 'Connected'
  agent_version = "1.1"
  latency_result = measure_latency(host='epsi.fr')
  latency_wan = latency_result[0] if latency_result else None
  
  data_details = {
    'hostname': hostname,
    'host_ip': host_ip,
    'os_v': os_v,
    'statut': statut,
    'latency_wan': latency_wan,
    'agent_version': agent_version
    
  }
  
  return data_details

# Donnée pour le tableau nmap 
def refresh_details_scan_network(network):
    # La commande "nmap network -T5" comprend l'option -sS par défaut
    # On utilise le scan tcp syn
    print(f"[NMAP] [{network}] Lancement du scan")
    nmap_instance = nmap3.NmapScanTechniques()
    raw_scan_results = nmap_instance.nmap_syn_scan(network, args='-T5') 
    print(f"[NMAP] [{network}] Scan en cours")
    # On supprime les données qui ne sont pas des adresses ip pour le traitement des données
    for key in ['runtime','stats','task_results']:
      if key in raw_scan_results:
        del raw_scan_results[key]
    
    # On vérifie pour chaque adresse ip scannée si des ports sont ouverts
    # Dans ce cas on retiendra seulement les ports pour être le plus pertinent
    connected_hosts = {}
    for ip in raw_scan_results.keys():
        if raw_scan_results.get('error'):
          nmap_error_msg = raw_scan_results.get('msg', '')
          if 'root' in nmap_error_msg or 'administrator' in nmap_error_msg:
                print(f"""
[ERREUR] Emplacement : c:/Users/domin/NFL/harvester/harvester.py
Nom de la fonction : refresh_details_scan_network
Erreur : Nécessite des privilèges plus élevés pour continuer.
Message d'erreur complet : {nmap_error_msg}
                """)
        elif raw_scan_results[ip]['ports']:
            # Le contenu de la clé 'ports' est une liste de dictionnaires 
            # qu'on transforme en liste de strings : les ports ouverts en TCP SYN parmi les 1000 ports scannés
            open_ports_on_ip = []
            for port in raw_scan_results[ip]['ports']:
                open_ports_on_ip += [int(port['portid'])]
            connected_hosts[ip] =  {'open_ports' : open_ports_on_ip}

    result = {"connected_hosts": len(connected_hosts), "hosts": connected_hosts}
    
    # On finit de formater les données pour répondre au format que le harvester et le nester accueillent. Le format du JSON sera a revoir.
    num_connected_hosts = result["connected_hosts"]
    hosts_and_ports = {}
    ports_status = {}
    for host, info in result["hosts"].items():
      hosts_and_ports[host] = info["open_ports"]  # Add 'ip' : [ports]
      ports_status[host] = 'yes' if info["open_ports"] else 'no'
    
    ip_adresses = list(hosts_and_ports.keys())
    open_ports = list(hosts_and_ports.values())
    
    # Ajout de l'hostname pour permettre l'ajout dans la bonne ligne de la BDD.
    hostname = hostname=socket.gethostname()
    
    # Packaging 
    data_details_nmap = {
      'hostname': hostname,
      'num_connected_hosts': num_connected_hosts, 
      'ip_adresses': ip_adresses,
      'open_ports': open_ports
    }
    print(f"[NMAP] [{network}] Fin du scan")
    return data_details_nmap



## Envoie des requêtes vers la frontpage
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
      
def put_to_nester_nmap(url_nester_details, network):
      while True:
        data_nmap = refresh_details_scan_network(network)
        try:
          response = requests.put(url_nester_details, json=data_nmap)
          print(response.text)
        except Exception as e:
          print(f"""
  [ERREUR] Emplacement : {sys.argv[0]} : {sys.exc_info()[2].tb_lineno}
  Nom de la fonction: {sys._getframe().f_code.co_name}
  Description de l'erreur : {type(e).__name__}
              """)
        
        time.sleep(120)
      
      


# Thread de l'envoi périodique des données sur la page d'accueil du Nester 
def start_put_to_nester_fp(url_nester, random_port):
  thread_fp = threading.Thread(target=put_to_nester_fp,args=(url_nester,random_port))
  thread_fp.start()

# Thread de l'envoi périodique des données sur la page de détail du Nester 
def start_put_to_nester_details(url_nester_details):
  thread_details = threading.Thread(target=put_to_nester_details,args=(url_nester_details,))
  thread_details.start()
  
# Thread de l'envoi périodique des données sur la page de scan du Nester
def start_put_to_nester_nmap(url_nester_details, network):
  thread_nmap = threading.Thread(target=put_to_nester_nmap,args=(url_nester_details,network,))
  thread_nmap.start()


@app.route('/', methods=['GET', 'POST'])
def connexion():
  if request.method == 'POST':
    # Si la requète est "POST" (envoie de donnée)
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "nfl@admin":
      print("Connexion réussie")
      return redirect('/dashboard')
    else:
      flash("Connexion refusée. Merci de réessayer votre mot de passe !")
      redirect('/')
  if request.method == 'GET':
    return render_template('connexion.html', hostname=socket.gethostname())

data_details_nmap = None
@app.route('/dashboard/refresh_nmap', methods=['POST'])
def refresh_nmap():
  # Limite par le nmap netmask /24 
  # network = '172.18.0.0/24' test parsing pour faire 
  print(f"[NMAP] [{network}] Début d'un scan depuis la page refresh_nmap")
  data_details_nmap = refresh_details_scan_network(network)
  # Obtenir la date et l'heure actuelles formatées
  temps_format = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
  # Nom du fichier avec la date et l'heure formatées
  nom_fichier = f"scan_result_{temps_format}.json"
  # Écrire le dictionnaire dans le fichier JSON
  with open(nom_fichier, "w") as f:  
    json.dump(data_details_nmap, f)
  return jsonify({'data_details_nmap': data_details_nmap})

@app.route('/dashboard')
def dashboard():
  data_details = refresh_details_data()
  return render_template('clientdb.html', data_details=data_details, data_details_nmap=data_details_nmap) 

@app.route('/get_latency', methods=['POST'])
def get_latency():
  latency_wan = measure_latency(host='epsi.fr')
  return jsonify({'content': round(latency_wan[0], 3) })

@app.route('/receive_modal_data', methods=['POST'])
def receive_modal_data():
    # Récupérer les données du formulaire
    network = request.form['network']
    destination = request.form['destination']

    # Effectuer une action avec ces données
    print(f"Réseau: {network}, Destination: {destination}")

    # Retourner une réponse JSON ou rediriger
    return jsonify({'status': 'success', 'message': f'Données reçues: Réseau - {network}, Destination - {destination}'})


if __name__ == '__main__':
  if 'FLASK_RUN_PORT' not in os.environ:
      random_port = random.randrange(4000, 4900)
      os.environ['FLASK_RUN_PORT'] = str(random_port)
  else:
      random_port = int(os.environ['FLASK_RUN_PORT'])
  start_put_to_nester_fp(url_nester, random_port)
  start_put_to_nester_details(url_nester_details)
  # Limite pas le netmask /24
  network = '192.168.1.0/24'
  start_put_to_nester_nmap(url_nester_details, network)
  app.run(debug=True, host='0.0.0.0', port=random_port)
