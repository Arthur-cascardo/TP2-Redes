import socket
import json
import sys


def eprint(args):
    print(args, file=sys.stderr)


def analise1():
    return "Ok"
    

def analise2(top100_ids):
    return "Ok"
    

def normalizeCannons(cannons):
    #cannon_list = [[7, 3], [8, 2], [6, 1], [8, 0], [5, 0], [5, 1], [1, 1], [8, 4]]
    #Normalização 10002113
    normalized = [0] * 8
    for cannon in cannons:
        insertPlusOne(normalized, cannon[0])
    return normalized


def insertPlusOne(lis, index):
    lis[index] += 1
    return lis


lis = [[7, 3], [8, 2], [6, 1], [8, 0], [5, 0], [5, 1], [1, 1], [8, 4]]
#print(normalizeCannons(lis))
# arguments = sys.argv
arguments = ["localhost" + ":" + "5000", "1"]
ip_port = arguments.pop(0).split(":")
ip_port[1] = int(ip_port[1])
analysis = arguments.pop(0)



target_host = "localhost" 
target_port = 5000  
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
client.connect((target_host,target_port))  
request    = f"GET /api/game/3 HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n".encode()
response   = ""  
client.sendall(request)
while True:
    recv = client.recv(1024)
    if recv == b'':
        break
    response += recv.decode()
json_obj = json.loads(response[response.find("{"):])
print(json_obj['game_stats']['auth'])







