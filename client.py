import socket
import json
import sys


def eprint(args):
    print(args, file=sys.stderr)


# arguments = sys.argv
arguments = ["localhost" + ":" + "80", "1"]
ip_port = arguments.pop(0).split(":")
ip_port[1] = int(ip_port[1])
analysis = arguments.pop(0)
while True:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(tuple(ip_port))
    message = "Client: " + input()
    client_socket.send(bytearray(message, "ascii"))
    data = client_socket.recv(1024)
    print(data.decode("ascii"))

