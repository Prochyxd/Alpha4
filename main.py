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
"""
1. UDP discovery

Po startu začne peer provádět periodické hledání protějšků pomocí “UDP discovery”. Každých pět sekund pošle do sítě UDP broadcast na port 9876 a čeká na odpovědi (těch pět sekund než ho pošle znovu). Ke komunikaci je použit protokol na bázi JSON. Co řádek, to buď dotaz nebo odpověď. Řádky končí buď CR-LF nebo jen LF.

Q=dotaz, A=odpověď

Q: {"command":"hello","peer_id":"molic-peer1"}
A: {"status":"ok","peer_id":"molic-peer1"}
A: {"status":"ok","peer_id":"molic-peer2"}
A: {"status":"ok","peer_id":"molic-peer3"}

Zde “molic-peer1” poslal UDP dotaz do sítě (představil se) a ozvali se mu tři protějšky. Pozor, peer odpoví také sám sobě, nutno ignorovat. Čili protějšky jsou pouze dva. Součástí odpovědi je IP adresa protějšků. Díky ní lze pak s nimi navázat TCP spojení."""

def UDPdiscovery(ipv4, port, mask, peerid):
    """
    Perform UDP discovery by sending a hello message to the specified IPv4 address and port,
    and receiving a response from the peer.

    Args:
        ipv4 (str): The IPv4 address to send the hello message to.
        port (int): The port number to send the hello message to.
        mask: Unused parameter.
        peerid (str): The peer ID to include in the hello message.

    Returns:
        dict: A dictionary containing the response received from the peer. The dictionary
        has the following format: {"status": "ok", "peer_id": <peer_id>}.
    """
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind((ipv4, port))
    # 5 second timeout
    s.settimeout(5)
    # send a message
    message = {"command": "hello", "peer_id": peerid}
    message = json.dumps(message)
    s.sendto(message.encode(), (ipv4, port))
    # receive a message
    data, addr = s.recvfrom(1024)
    data = data.decode()
    data = json.loads(data)
    # close socket
    s.close()
    return data

#filter data from UDPdiscovery
def filter_data(data, peerid):
    """
    Filters the data based on the given peerid.

    Args:
        data (dict): The data to be filtered.
        peerid (str): The peerid to filter the data with.

    Returns:
        str or None: The filtered peer_id if the data's status is 'ok', otherwise None.
    """
    if data['peerid'] == peerid:
        return None
    if data['status'] == 'ok':
        return data['peer_id']
    else:
        return None
    
#TCP Protocol (peer tp peer communication)
"""
S každým nově nalezeným peerem se naváže trvalé TCP spojení na port 9876. Komunikace probíhá podobným protokolem jako při UDP discovery, na bázi JSON.

Nejprve je nutno se opět představit, protože protějšek jinak neví kdo se k němu připojuje. V odpovědi na tento “handshake” protějšek pošle celou svou historii zpráv chatu.

Q: {"command":"hello","peer_id":"molic-peer1"}
A: {“status”:”ok”, “messages”:{"1707243010934"=>{"peer_id"=>"molic-peer3", "message"=>"pokus"}, "1707243028143"=>{"peer_id"=>"molic-peer3", "message"=>"pokus2"}, "1707243101261"=>{"peer_id"=>"molic-peer1", "message"=>"blablabla"}}

Toto se provede s každým nalezeným protějškem. Je možné, že tytéž zprávy má více protějšků. Peer proto musí sloučit všechny zprávy, které od všech obdržel, do jediné historie. Provede to jednoduše: každá zpráva má své ID, díky němuž lze ignorovat duplicitní zprávy.

Po “handshake” se toto již otevřené TCP spojení použije k posílání zpráv (směrem “k protějšku”). Novou zprávu peer pošle tak, že vygeneruje její ID (timestamp - viz níže) a pak ji rozešle všem peerům:

peeru 1:

Q: {“command”:”new_message”,”message_id”:"1707243010934","message":”pokus"}
A: {“status”:”ok”}

peeru 2:

Q: {“command”:”new_message”,”message_id”:"1707243010934","message":”pokus"}
A: {“status”:”ok”}
atd..

Protějšky uloží zprávu do svých historií chatu včetně peer_id (toho, kdo zprávu poslal). Tato historie je uložena pouze jako pole (kolekce, apod.) v paměti RAM.

Naopak od protějšků jsou zprávy akceptovány pomocí TCP spojení, která vytvořili směrem k peeru. Peer tedy implementuje jak TCP klienty (směrem ven), tak TCP server (směr dovnitř). Ve výsledku mezi dvěma peery vzniknou dvě TCP spojení.
"""
"""
Komunikace může vypadat takto:
Q: {"command":"hello","peer_id":"molic-peer1"}
A: {“status”:”ok”, “messages”:{"1707243010934"=>{"peer_id"=>"molic-peer3", "message"=>"pokus"}, "1707243028143"=>{"peer_id"=>"molic-peer3", "message"=>"pokus2"}, "1707243101261"=>{"peer_id"=>"molic-peer1", "message"=>"blablabla"}}
Q: {“command”:”new_message”,”message_id”:"1707243010934","message":"prvni zprava"}
A: {“status”:”ok”}
Q: {“command”:”new_message”,”message_id”:"1707243010935","message":”druha zprava"}
A: {“status”:”ok”}
Q: {“command”:”new_message”,”message_id”:"1707243010940","message":”treti zprava"}
A: {“status”:”ok”}
"""
def TCPprotocol(ipv4, port, peerid, messages):
    """
    Establishes a TCP connection with the specified IPv4 address and port,
    sends a hello message with the peer ID, and then sends a series of messages.
    Returns the response received from the server.

    :param ipv4: The IPv4 address to connect to.
    :param port: The port number to connect to.
    :param peerid: The peer ID to include in the hello message.
    :param messages: A list of messages to send to the server.
    :return: The response received from the server.
    """
    #create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ipv4, port))
    #send a message
    message = {"command":"hello","peer_id":peerid}
    message = json.dumps(message)
    s.send(message.encode())
    #receive a message
    data = s.recv(1024)
    data = data.decode()
    data = json.loads(data)
    #send messages
    for message in messages:
        message = {"command":"new_message","message_id":message['message_id'],"message":message['message']}
        message = json.dumps(message)
        s.send(message.encode())
        #receive a message
        data = s.recv(1024)
        data = data.decode()
        data = json.loads(data)
    #close socket
    s.close()
    return data

#filter data from TCPprotocol
def filter_data(data, peerid):
    """
    Filters the data based on the given peerid.

    Parameters:
    - data (dict): The data to be filtered.
    - peerid (str): The peerid to filter the data with.

    Returns:
    - str or None: The filtered peer_id if the data's status is 'ok', otherwise None.
    """
    if data['peerid'] == peerid:
        return None
    if data['status'] == 'ok':
        return data['peer_id']
    else:
        return None
    
#TCP server
def TCPserver(ipv4, port, peerid, messages):
    """
    TCP server function that listens for incoming connections, receives and sends messages.

    Args:
        ipv4 (str): The IPv4 address to bind the server socket to.
        port (int): The port number to bind the server socket to.
        peerid (str): The identifier of the peer.
        messages (list): List of messages to be sent as a response.

    Returns:
        dict: The received data as a dictionary.

    Raises:
        None

    """
    #create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ipv4, port))
    s.listen(1)
    conn, addr = s.accept()
    #receive a message
    data = conn.recv(1024)
    data = data.decode()
    data = json.loads(data)
    #send a message
    message = {"status":"ok","messages":messages}
    message = json.dumps(message)
    conn.send(message.encode())
    #receive messages
    while True:
        data = conn.recv(1024)
        data = data.decode()
        data = json.loads(data)
        #send a message
        message = {"status":"ok"}
        message = json.dumps(message)
        conn.send(message.encode())
    #close socket
    conn.close()
    s.close()
    return data

#filter data from TCPserver
def filter_data(data, peerid):
    """
    Filters the given data based on the peerid.

    Args:
        data (dict): The data to be filtered.
        peerid (str): The peerid to filter the data with.

    Returns:
        str or None: The filtered peer_id if the status is 'ok', otherwise None.
    """
    if data['peerid'] == peerid:
        return None
    if data['status'] == 'ok':
        return data['peer_id']
    else:
        return None
    
#TCP client
def TCPclient(ipv4, port, peerid, messages):
    """
    Connects to a TCP server at the specified IPv4 address and port,
    sends a hello message with the peer ID, and then sends a series of
    messages to the server. Finally, it receives a response from the server
    and returns it.

    Args:
        ipv4 (str): The IPv4 address of the server.
        port (int): The port number of the server.
        peerid (str): The ID of the peer.
        messages (list): A list of messages to be sent to the server.

    Returns:
        dict: The response received from the server.

    """
    #create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ipv4, port))
    #send a message
    message = {"command":"hello","peer_id":peerid}
    message = json.dumps(message)
    s.send(message.encode())
    #receive a message
    data = s.recv(1024)
    data = data.decode()
    data = json.loads(data)
    #send messages
    for message in messages:
        message = {"command":"new_message","message_id":message['message_id'],"message":message['message']}
        message = json.dumps(message)
        s.send(message.encode())
        #receive a message
        data = s.recv(1024)
        data = data.decode()
        data = json.loads(data)
    #close socket
    s.close()
    return data

#filter data from TCPclient
def filter_data(data, peerid):
    """
    Filters the given data based on the peerid.

    Args:
        data (dict): The data to be filtered.
        peerid (str): The peerid to filter the data with.

    Returns:
        str or None: The filtered peer_id if the status is 'ok', otherwise None.
    """
    if data['peerid'] == peerid:
        return None
    if data['status'] == 'ok':
        return data['peer_id']
    else:
        return None
    


#main    
if __name__ == "__main__":
    #load data from config.json
    data = load_config()
    ipv4 = data['ipv4']
    port = data['port']
    mask = data['mask']
    peerid = data['peerid']
    #UDP discovery
    data = UDPdiscovery(ipv4, port, mask, peerid)
    peerid = filter_data(data, peerid)
    #TCP protocol
    messages = [{"message_id": "1707243010934", "message": "pokus"},
                {"message_id": "1707243028143", "message": "pokus2"},
                {"message_id": "1707243101261", "message": "blablabla"}]
    data = TCPprotocol(ipv4, port, peerid, messages)
    peerid = filter_data(data, peerid)
    #TCP server
    messages = {"1707243010934": {"peer_id": "molic-peer3", "message": "pokus"},
                "1707243028143": {"peer_id": "molic-peer3", "message": "pokus2"},
                "1707243101261": {"peer_id": "molic-peer1", "message": "blablabla"}}
    data = TCPserver(ipv4, port, peerid, messages)
    peerid = filter_data(data, peerid)
    #TCP client
    messages = [{"message_id": "1707243010934", "message": "prvni zprava"},
                {"message_id": "1707243010935", "message": "druha zprava"},
                {"message_id": "1707243010940", "message": "treti zprava"}]
    data = TCPclient(ipv4, port, peerid, messages)
    peerid = filter_data(data, peerid)
    print(peerid)
    print("End of program.")

