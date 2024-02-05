from flask import Flask, render_template, request, redirect, flash, session
import socket, requests, time, json
from tcp_latency import measure_latency
import platform, subprocess, time, threading
import nmap

#import sys
#print(sys.version)
#print(sys.executable)
#print(sys.path)

app = Flask(__name__)  # Instance de la classe Flask

# Donnée pour API
hostname = socket.gethostname()
host_ip = ', '.join(socket.gethostbyname_ex(hostname)[2])
statut = "Connected"
request_time = time.time()
agent_version = "0.1"
url = 'http://127.0.0.1:5000/envoyer-client-info'

## Lecture du JSON
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

# Lancement d'un Thread pour l'écriture du JSON
def start_scan_network():
  thread_scan_network = threading.Thread(target=scan_network)
  thread_scan_network.start()
  
# Donnée pour le dashboard
os_v = platform.platform()
latency_wan = measure_latency(host='epsi.fr')
ip_adresses = list(hosts_and_ports.keys())
open_ports = list(hosts_and_ports.values())
machines_number = len(ip_adresses)

# hostname en face de la colonne hostname
data = {
    'hostname': hostname,
    'ip_address': host_ip, 
    'statut': statut,
    'request_time': request_time,
    'agent_version': agent_version,
    'host_ip': host_ip
}

# Envoie des requêtes
def put_to_nester(url, data):
  while True:
    response = requests.put(url, json=data)
    print(response.text)
    time.sleep(30)

def start_put_to_nester(url,data):
  thread_scan_network = threading.Thread(target=put_to_nester,args=(url,data))
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
  return render_template('connexion.html')


@app.route('/dashboard')
def dashboard():
  return render_template('clientdb.html',
    machines_number=machines_number,
    open_ports=open_ports,
    ip_adresses=ip_adresses,
    hostname=hostname,
    host_ip=host_ip,
    latency_wan=latency_wan,
    statut=statut,
    os_v=os_v,
    agent_version=agent_version) 

if __name__ == '__main__':
  #start_scan_network()
  start_put_to_nester(url, data)
  app.run(debug=True, host='0.0.0.0', port=4000)
