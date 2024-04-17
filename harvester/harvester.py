from flask import Flask, render_template, request, redirect, flash, session, jsonify
import socket, requests, time, json
from tcp_latency import measure_latency
import platform, time, threading, os
import nmap3 # Utile ? 
import sys
import random # Pour les tests Docker
import urllib.request # Pour l'ip externe (Standard Library)

app = Flask(__name__)  # Instance de la classe Flask
app.secret_key = 'R29z7R.0msFaIEcoUg}SvX9Wxz!R]]n_:'

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
  request_time = int(time.time())
  agent_version = "1.1"
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
        if raw_scan_results[ip]['ports']:
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
      flash('Connexion refusée. Merci de réessayer votre mot de passe !')
      redirect("/")
  if request.method == 'GET':
    return render_template('connexion.html', hostname=socket.gethostname())


@app.route('/dashboard')
def dashboard():
  data_details = refresh_details_data()
  return render_template('clientdb.html', data_details=data_details) 

@app.route('/dashboard/refresh_nmap', methods=['POST'])
def refresh_nmap():
  # Limite par le nmap netmask /24 
  network = '172.18.0.0/24'
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

@app.route('/get_latency', methods=['POST'])
def get_latency():
  latency_wan = measure_latency(host='epsi.fr')
  return jsonify({'content': round(latency_wan[0], 3) })


if __name__ == '__main__':
  if 'FLASK_RUN_PORT' not in os.environ:
      random_port = random.randrange(4000, 4900)
      os.environ['FLASK_RUN_PORT'] = str(random_port)
  else:
      random_port = int(os.environ['FLASK_RUN_PORT'])
  start_put_to_nester_fp(url_nester, random_port)
  start_put_to_nester_details(url_nester_details)
  # Limite pas le netmask /24
  network = '172.18.0.0/24'
  put_to_nester_nmap(url_nester_details, network)
  app.run(debug=True, host='0.0.0.0', port=random_port)
