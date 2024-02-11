#import sys
#print(sys.version)
#print(sys.executable)
#print(sys.path)
try:
    import nmap
except Exception as e:
    print(e)
import json

def scan_network(network = '172.20.10.0/24'):
    nm = nmap.PortScanner()
    nm.scan(hosts=network)

    connected_hosts = nm.all_hosts()
    result = {"connected_hosts": len(connected_hosts), "hosts": {}}

    for host in connected_hosts:
        open_ports = [int(port) for port in nm[host]['tcp'].keys() if nm[host]['tcp'][port]['state'] == 'open']
        result["hosts"][host] = {"open_ports": open_ports}

    return result

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    network_to_scan = '172.20.10/24'
    scan_result = scan_network()
    save_to_json(scan_result, 'scan_result.json')