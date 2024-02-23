"""
Alpha 4
"""
#load data from config.json - ipv4, port, mask, peerid
import json
import os
import socket
import time

def load_config():
    with open('config.json') as f:
        data = json.load(f)
        return data
    
#UDP discovery
def UDPdiscovery(ipv4, port, mask, peerid):
    #Q: {"command":"hello","peer_id":"molic-peer1"}
    #A: {"status":"ok","peer_id":"molic-peer1"}
    #A: {"status":"ok","peer_id":"molic-peer2"}
    #A: {"status":"ok","peer_id":"molic-peer3"}

    #create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind((ipv4, port))
    #5 second timeout
    s.settimeout(5)
    #send a message
    message = {"command":"hello","peer_id":peerid}
    message = json.dumps(message)
    s.sendto(message.encode(), (ipv4, port))
    #receive a message
    data, addr = s.recvfrom(1024)
    data = data.decode()
    data = json.loads(data)
    #close socket
    s.close()
    return data

#filter data from UDPdiscovery
def filter_data(data, peerid):
    if data['peerid'] == peerid:
        return None
    if data['status'] == 'ok':
        return data['peer_id']
    else:
        return None


    
if __name__ == "__main__":
    config = load_config()
    print(config)
    ip = config['ipv4']
    port = config['port']
    mask = config['mask']
    peerid = config['peerid']
    print(UDPdiscovery(ip, port, mask, peerid))