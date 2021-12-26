import struct
import sys
import time
import socket


def errortreat(data):
    errors = [
    "INVALID_MESSAGE_CODE",
    "INCORRECT_MESSAGE_LENGTH",
    "INVALID_PARAMETER",
    "INVALID_SINGLE_TOKEN",
    "ASCII_DECODE_ERROR"]
    return print(errors[struct.unpack('!hh', data)[1]])


def getaddrandport(command):
    return command[0], command[1]

def formatSAA(i):
    if(i%2 == 0 or i%3 == 0) and i > 1:
        return "+"
    elif i < 1:
        return ""
    else:
        return ":"

##TODO: Generalizar codigo atraves de loops e arrays
def parsecommand(command):
    commands = ['rsaa', 'vsaa', 'rsag', 'vsag']

    addr = getaddrandport(command)
    command = command[2:]

    if command[0] == commands[0]:
        command[0] = 1
        formats.append("!hii")
        formatsreceive.append("!hii64s")
        return addr, struct.pack(formats.pop(0), *command)
    elif command[0] == commands[1]:
        command[0] = 3
        formats.append("!hii64s")
        formatsreceive.append("!hii64ss")
        for i in range(len(command)):
            if isinstance(command[i], str):
                command[i] = bytearray(command[i], "ascii")
        return addr, struct.pack(formats.pop(0), *command)
    elif command[0] == commands[2]:
        command[0] = 5
        format = "!hh"
        for i in range(command[1]):
            format += "ii64s"
        formats.append(format)
        formatsreceive.append(format+"64s")
        for i in range(len(command)):
            if isinstance(command[i], str):
                command[i] = bytearray(command[i], "ascii")
        return addr, struct.pack(formats.pop(0), *command)
    elif command[0] == commands[3]:
        command[0] = 7
        format = "!hh"
        for i in range(command[1]):
            format += "ii64s"
        formats.append(format+"64s")
        formatsreceive.append(format+"64ss")
        for i in range(len(command)):
            if isinstance(command[i], str):
                command[i] = bytearray(command[i], "ascii")
        return addr, struct.pack(formats.pop(0), *command)
    else:
        print("fuck")


def parseresponse(response):
    res = []
    for i in range(len(response)):
        if isinstance(response[i], bytes):
            if len(response[i]) < 2:
                continue
            res.insert(response.index(response[i]), formatSAA(i) + response[i].decode("ascii"))
        else:
            res.insert(i, formatSAA(i) + str(response[i]))
    if response[0] == 4 or response[0] == 8:
        res.append(str(struct.unpack('!b', response[len(response) - 1])[0]))
    return "".join(res)



lis = []
formats = []
formatsreceive = []
##lis.append(["auth20212.dcc023.2advanced.dev", 51212, "rsaa", 2018013968, 1])
##lis.append(["auth20212.dcc023.2advanced.dev", 51212, "vsaa", 2018013968, 1, "1c9324306dd2f0c2e3bc8623dc9df0d9d9b90cc5e0557843073665d069ceed3d"])
lis.append(["auth20212.dcc023.2advanced.dev", 51212, "rsag", 1, 2018013968, 1, "1c9324306dd2f0c2e3bc8623dc9df0d9d9b90cc5e0557843073665d069ceed3d"])
##lis.append(["auth20212.dcc023.2advanced.dev", 51212, "vsag",2,2018013968,1,"1c9324306dd2f0c2e3bc8623dc9df0d9d9b90cc5e0557843073665d069ceed3d",2018013969,1,"e842ce90368718e30918b15e3fa000500a2329a5a02df9ea03ba141541ec03ba","2a7f46e20ef4b8eb3aa4db27ddbeaf8a9ab1c1a9c62f23c85c933fc17d1fa868"])
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
start = time.time()
i = 0

addr, message = parsecommand(lis[0])
client_socket.sendto(message, addr)
try:
    data, server = client_socket.recvfrom(1024)
    end = time.time()
    elapsed = end - start
    if len(data) == 4:
        print(f'{errortreat(data)}')
    else:
        data = struct.unpack(formatsreceive.pop(0), data)
        print(f'{parseresponse(data)}')
except socket.timeout:
    print("Request timed out, retrying connection attempt...")
