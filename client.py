#!/usr/local/bin/python3

import sys
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10234)
try:
    sock.connect(server_address)
except socket.timeout as e:
    print(e)
except OSError as e:
    print(e)
except ConnectionRefusedError as e:
    print(e)

message = 'testing the messaging capabilities of my TCP client server combo'
sock.send(message.encode('utf-8'))
