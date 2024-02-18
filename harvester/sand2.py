import threading



def refresh_nmap(network):
  thread_nmap = threading.Thread(target=refresh_details_scan_network, args=(network,))
  thread_nmap.start()

network = "192.168.1.0/24"
data_details_nmap = refresh_nmap(network)
$



          {% for i in range(0,data_details_nmap.num_connected_hosts|default(0)) %}
          <tr>
            <th scope="row">{{i+1}}</th>
            <td>{{data_details_nmap.ip_adresses[i]}}</td>
            <td>{{data_details_nmap.open_ports[i]}}</td>
          </tr>
          {% endfor %}