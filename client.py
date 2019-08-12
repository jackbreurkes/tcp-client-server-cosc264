#!/usr/local/bin/python3
import math
import os
import sys
import socket


def main():
    args = sys.argv

    if len(args) != 4:
        sys.exit('usage: client.py [sever ip] [server port number] [file name]')

    try:
        addr = socket.getaddrinfo(args[1], args[2])
    except socket.gaierror:
        sys.exit('error getting address info.')

    try:
        portnum = int(args[2])
    except ValueError:
        sys.exit('invalid port number argument.')

    if not (1024 <= portnum <= 64000):
        sys.exit('port number must be between 1024 and 64000 (inclusive).')

    if os.path.exists(args[3]) and os.path.isfile(args[3]):
        sys.exit('a local file named {} already exists. please rename it or choose a different file.'.format(args[3]))

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        sys.exit('could not create a socket.')
    sock.settimeout(1)

    valids = [tup for tup in addr if tup[0] == socket.AddressFamily.AF_INET and tup[1] == socket.SocketKind.SOCK_STREAM]
    if len(valids) == 0:
        sock.close()
        sys.exit("the service {} at port {} does not support stream sockets via IPv4.")
    try:
        sock.connect(valids[0][4])
    except OSError as e:
        sock.close()
        sys.exit("could not connect to the file server.")

    message = createfilerequest(0x497E, 1, args[3])
    sock.send(message)
    readfileresponse(sock, args[3])


def createfilerequest(magic_num, type_num, filename):
    filename_bytes = filename.encode('utf-8')

    filename_bitlen = len(filename_bytes) * 8
    binary = int.from_bytes(filename_bytes, 'big')
    binary |= len(filename_bytes) << filename_bitlen
    binary |= type_num << (filename_bitlen + 16)
    binary |= magic_num << (filename_bitlen + 16 + 8)
    pkt = int.to_bytes(binary, 5 + len(filename_bytes), 'big')
    return pkt


def readfileresponse(conn, filename):
    try:
        pktheader = conn.recv(8)
    except socket.timeout:
        conn.close()
        sys.exit('timeout reading FileResponse header')

    if int.from_bytes(pktheader[0:2], 'big') != 0x497E:
        conn.close()
        sys.exit('FileResponse has invalid MagicNo field value.')
    if pktheader[2] != 2:
        conn.close()
        sys.exit('FileResponse has invalid Type field value.')

    if pktheader[3] not in [0, 1]:
        conn.close()
        sys.exit('FileResponse has invalid StatusCode field value.')
    if pktheader[3] == 0:
        conn.close()
        sys.exit('Requested file could not be retrieved by the server.')

    try:
        f = open(filename, 'w+')
    except IOError:
        conn.close()
        sys.exit('could not open {} locally.'.format(filename))

    filesize = int.from_bytes(pktheader[4:8], 'big')

    bytesread = 0
    filedata = bytes(1)
    while len(filedata) > 0:  # will read until the connection is closed from the server side or the socket times out
        try:
            filedata = conn.recv(4096)
        except socket.timeout:
            print('timeout while reading FileResponse body')
            conn.close()
            f.close()
            sys.exit()
        bytesread += len(filedata)
        try:
            f.write(filedata.decode('utf-8'))
        except IOError:
            conn.close()
            sys.exit('error while writing received data to local file.')

    if bytesread != filesize:
        conn.close()
        f.close()
        sys.exit("invalid number of bytes read: expected {}, got {}.".format(filesize, bytesread))

    print("file {} successfully written locally. {} bytes read in total.".format(filename, bytesread))
    f.close()
    conn.close()


if __name__ == '__main__':
    main()
