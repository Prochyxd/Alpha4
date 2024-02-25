# Alpha 4

## Overview

This script implements a peer-to-peer communication protocol utilizing UDP discovery and TCP connections. The communication involves sending and receiving messages between peers over a network.

## Requirements

- Python 3.x
- `config.json` file containing IPv4 address, port number, mask, and peer ID.

## Usage

1. Ensure `config.json` is properly configured.
2. Run the script.

## Components

### UDP Discovery

The script starts by performing UDP discovery to find peers on the network. It sends periodic broadcast messages and waits for responses from other peers.

#### Function: `UDPdiscovery(ipv4, port, mask, peerid)`

This function performs UDP discovery by sending hello messages to peers and receiving responses.

### TCP Protocol (Peer-to-Peer Communication)

Once peers are discovered, the script establishes permanent TCP connections with them. Communication occurs using a JSON-based protocol.

#### Function: `TCPprotocol(ipv4, port, peerid, messages)`

This function establishes a TCP connection with a peer, sends hello messages, and exchanges messages.

### TCP Server

The script acts as a TCP server, listening for incoming connections, receiving messages, and sending responses.

#### Function: `TCPserver(ipv4, port, peerid, messages)`

This function sets up a TCP server to handle incoming connections, receive messages, and send responses.

### TCP Client

The script acts as a TCP client, connecting to a server, sending messages, and receiving responses.

#### Function: `TCPclient(ipv4, port, peerid, messages)`

This function connects to a TCP server, sends messages, and receives responses.

## Running the Script

python script.py

## Configuration

Ensure config.json is properly configured with the following parameters:

{
  "ipv4": "your_ipv4_address",
  "port": "your_port_number",
  "mask": "your_mask",
  "peerid": "your_peer_id"
}

## Note

Peers may be identified by their peer IDs.
Ensure proper handling of received data to prevent errors.

## Conclusion

This script facilitates peer-to-peer communication over a network using UDP discovery and TCP connections. It provides a foundation for building distributed applications.

For more details, refer to the inline documentation within the script.