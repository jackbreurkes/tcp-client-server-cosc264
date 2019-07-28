#!/usr/local/bin/python3

import sys
import socket

MIN_PORT = 1024
MAX_PORT = 64000


def get_port_from_args(args):
    if len(args) != 2:
        print("usage: server.py.py [port number]")
        sys.exit(1)
    port_str = args[1]

    try:
        port_number = int(port_str)
    except ValueError as e:
        print("please enter an integer as a port number")
        sys.exit(2)

    if port_number not in range(MIN_PORT, MAX_PORT + 1):
        print("please enter a port number between {} and {}".format(MIN_PORT, MAX_PORT))
        sys.exit(3)

    return port_number


def main():
    if len(sys.argv) == 1:
        # DEBUG
        args = ['', '10234']
    else:
        args = sys.argv

    port = get_port_from_args(args)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        print("Error creating socket:", e)
        sys.exit(4)
        
    try:
        sock.bind(('localhost', port))
    except OSError as e:
        print(e)
        sys.exit(5)

    sock.listen()
    connection, client_addr = sock.accept()
    data = sock.recv(200)
    print(data.decode())
    print("conn & done")
    sock.close()


if __name__ == '__main__':
    main()
