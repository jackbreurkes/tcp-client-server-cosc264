#!/usr/local/bin/python3

import sys
import socket
import time
from datetime import datetime

MIN_PORT = 1024
MAX_PORT = 64000


def main():
    args = sys.argv

    port = get_port_from_args(args)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        sys.exit("Error creating socket.")

    try:
        sock.bind(('localhost', port))
    except OSError:
        sys.exit("Error binding socket to given port.")

    try:
        sock.listen()
    except OSError as e:
        sock.close()
        sys.exit("Could not set the socket to accept incoming connections.")

    while True:
        print('')
        connection, clientaddrinfo = sock.accept()
        connection.settimeout(1)
        print("connection accepted from", clientaddrinfo[0], "port", clientaddrinfo[1], "at", datetime.now())
        readfilerequest(connection)


def get_port_from_args(args):
    if len(args) != 2:
        sys.exit("usage: files.py [port number]")
    port_str = args[1]

    try:
        port_number = int(port_str)
    except ValueError as e:
        sys.exit("please enter an integer as a port number")

    if port_number not in range(MIN_PORT, MAX_PORT + 1):
        sys.exit("please enter a port number between {} and {}".format(MIN_PORT, MAX_PORT))

    return port_number


def readfilerequest(conn):
    try:
        pktheader = conn.recv(5)
    except socket.timeout:
        print('timeout reading FileRequest header')
        conn.close()
        return

    if int.from_bytes(pktheader[0:2], 'big') != 0x497E:
        print('FileRequest has invalid MagicNo field value.')
        conn.close()
        return
    if pktheader[2] != 1:
        print('FileRequest has invalid Type field value.')
        conn.close()
        return
    filenamelen = int.from_bytes(pktheader[3:5], 'big')
    if not (1 <= filenamelen <= 1024):
        print('FileRequest has invalid FilenameLen field value.')
        conn.close()
        return

    try:
        filename_bytes = conn.recv(filenamelen)
    except socket.timeout:
        print('timeout reading FileRequest Filename field value.')
        conn.close()
        return

    filename = "server_files/" + filename_bytes.decode('utf-8')
    try:
        f = open(filename)
    except IOError:
        res = createfileresponse(0x497E, 2, 0)
        conn.send(res)
        conn.close()
        print('{} does not exist or could not be opened.'.format(filename))
        return

    filedata = f.read().encode('utf-8')
    f.close()
    res = createfileresponse(0x497E, 2, 1, filedata)
    conn.send(res)
    conn.close()
    print('transfer of file {} completed. {} bytes transferred in total.'.format(filename, len(res)))


def createfileresponse(magic_num, type_num, status_code, filedata=bytes()):
    filedata_bitlen = len(filedata) * 8

    binary = int.from_bytes(filedata, 'big')
    binary |= len(filedata) << filedata_bitlen
    binary |= status_code << (filedata_bitlen + 32)
    binary |= type_num << (filedata_bitlen + 32 + 8)
    binary |= magic_num << (filedata_bitlen + 32 + 8 + 8)
    pkt = int.to_bytes(binary, 8 + len(filedata), 'big')
    return pkt


if __name__ == '__main__':
    main()
