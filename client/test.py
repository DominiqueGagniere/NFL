from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for #ajout jsonify dynamic button
import socket, requests, time, json, platform
import nmap
from tcp_latency import measure_latency

app = Flask(__name__)  # Instance de la classe Flask

# Donnée pour API
hostname = socket.gethostname()
host_ip = socket.gethostbyname_ex(hostname)
statut = "Connected"
request_time = time.time()
agent_version = "1.0"
url = 'http://localhost:5000/envoyer-client-info'


# Fonction de scan network
def scan_network(network):
  nm = nmap.PortScanner()
  nm.scan(hosts=network)
  connected_hosts = nm.all_hosts()
  result = {"connected_hosts": len(connected_hosts), "hosts": {}}
  for host in connected_hosts:
      open_ports = [int(port) for port in nm[host]['tcp'].keys() if nm[host]['tcp'][port]['state'] == 'open']
      result["hosts"][host] = {"open_ports": open_ports}
  
  return result

# Fonction pour stocker les scans en local
def save_to_json(data, filename):
  with open(filename, 'w') as json_file:
      json.dump(data, json_file, indent=4)
    





# Donnée pour le dashboard
def get_nmap_data(network_to_scan = '172.20.10.0/24'):
  scan_result = scan_network(network_to_scan)

  hosts_and_ports = {}
  for host, info in data["hosts"].items():
    hosts_and_ports[host] = info["open_ports"]
    
  ip_adresses = list(hosts_and_ports.keys())
  open_ports = list(hosts_and_ports.values())
  machines_number = len(ip_adresses)

  return ip_adresses, open_ports, machines_number

ip_adresses, open_ports, machines_number = get_nmap_data()

os_v = platform.platform()
latency_wan = measure_latency(host='epsi.fr')


data = {
    'hostname': hostname,
    'ip_address': host_ip,  #FIXME!
    'statut': statut,
    'request_time': request_time,
    'agent_version': agent_version,
    'host_ip': host_ip
}


@app.route('/')
def connexion():
  if request.method == 'POST':
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
  return render_template('dashboard.html',
    machines_number=machines_number,
    open_ports=open_ports,
    ip_adresses=ip_adresses,
    hostname=hostname,
    host_ip=host_ip,
    latency_wan=latency_wan,
    statut=statut,
    os_v=os_v,
    agent_version=agent_version)


@app.route('/refresh_nmap')
def run_script():
  ip_adresses,open_ports,machines_number = get_nmap_data()
  redirect(url_for('dashboard'), ip_adresses=ip_adresses, open_ports=open_ports, machine_numbers=machines_number)


if __name__ == '__main__':
  app.run(debug=True, host='127.0.0.1', port=5000)
  while True:
    response = requests.put(url, json=data)
    print(response.text)
    time.sleep(30)
