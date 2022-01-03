import time
import socket
import json
import sys

#Algoritmo de retransmissão:
#O algoritimo manda a requisição com o timeout definido como
#a latencia medida pelo comando "ping" do prompt do windows
#ao enviar 32 bytes de dados ao servidor.
#Caso a requisição não obtenha uma resposta do servidor
#o tempo de timeout é o tempo de latencia multiplicado por n
#sendo n definido pelo numero de vezes em que não houve resposta
#esse algoritimo e observado nos metodos authReq e sendData

def authReq(json_req):
    start = time.time()
    tiem = 0
    count = 0
    not_connected = [52221, 52222, 52223, 52224]
    client_socket.sendto(bytearray(json_req, "ascii"), (hostname, not_connected[0]))
    while len(not_connected) != 0:
        for addr in not_connected:
            try:
                writeSendFileAuthReq(json_req, addr - 52220)
                data, server = client_socket.recvfrom(1024)
                json_recv = writeReceivedFileAuthRes(data, server[1] - 52220)
                if json_recv["status"] == 1:
                    print("Invalid SAG on request to server port " + str(server[1]) + ", please try again")
                    return False
                if int(server[1]) in not_connected:
                    client_socket.settimeout(0.15)
                    not_connected.remove(int(server[1]))
                count += 1
                break
            except socket.timeout:
                print("Request timed out for server port " + str(addr) + ", retrying connection attempt...")
                client_socket.sendto(bytearray(json_req, "ascii"), (hostname, addr))
                tiem += 0.05
                client_socket.settimeout(tiem)
                count += 1
    end = time.time()
    elapsed = end - start
    print("Connection Succeeded after: " + str(elapsed) + " seconds and " + str(count) + " requests sent")
    return True


def formatRequests(args):

    file = open(args[-1] + ".json")
    json_obj = json.load(file)
    for key in json_obj:
        json_obj[key] = args.pop(0)
    writeSendFile(json.dumps(json_obj))
    json_recv = sendData(json.dumps(json_obj))
    return json_recv

def checkHasAllBridges(bridges_list):
    bridges_num = [1, 2, 3, 4, 5, 6, 7, 8]
    try:
        for bridges in bridges_list:
            aux_json = bridges.decode("ascii")
            bridges_num.remove(json.loads(aux_json)["bridge"])
        return not bridges_num
    except ValueError:
        return False
    except KeyError:
        return True


def sendData(json_obj):

    data = bytearray("", "ascii")
    tiem = 0.10
    aux_data = []
    aux_river = {}
    if "getturn" in json_obj:
        while len(aux_river) < 4:
            river_sockets[len(aux_river)].sendto(bytearray(json_obj, "ascii"), (hostname, 52221 + len(aux_river)))
            river_sockets[len(aux_river)].settimeout(0.5)
            aux_data = []
            while len(aux_data) < 8:
                try:
                    writeSendFile(json_obj)
                    data, server = river_sockets[len(aux_river)].recvfrom(1024)
                    if bytearray("state", "ascii") not in data:
                        if bytearray("gameover", "ascii") in data:
                            writeReceivedFile(data)
                            return data
                        else:
                            continue
                    aux_data.insert(0, data)
                except socket.timeout:
                    break
            if not checkHasAllBridges(aux_data):
                continue
            else:
                aux_river.update({len(aux_river): aux_data})
        formatStateRes(aux_river)
        return data
    else:
        client_socket.sendto(bytearray(json_obj, "ascii"), (hostname, 52221))
        client_socket.settimeout(0.15)
        while len(aux_data) < 1:
            try:
                writeSendFile(json_obj)
                data, server = client_socket.recvfrom(1024)
                if bytearray("state", "ascii") in data:
                    break
                client_socket.settimeout(0.15)
                aux_data.insert(0, data)
            except socket.timeout:
                tiem += 0.05
                client_socket.settimeout(tiem)
                client_socket.sendto(bytearray(json_obj, "ascii"), (hostname, 52221))
        writeReceivedFile(data)
        return data


def writeSendFile(json_obj):
    json_obj = json.loads(json_obj)
    filename = json_obj["type"] + ".json"
    with open(filename, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4, sort_keys=True)


def writeReceivedFile(json_obj):

        aux_json = formatReceivedData(json_obj)
        filename = aux_json["type"] + ".json"
        with open(filename, 'w') as outfile:
            json.dump(aux_json, outfile, indent=4, sort_keys=True)
        return aux_json


def writeSendFileAuthReq(json_obj, server_num):

    json_obj = json.loads(json_obj)
    filename = "authreq" + str(server_num) + ".json"
    with open(filename, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4, sort_keys=True)


def writeReceivedFileAuthRes(json_obj, server_num):

    aux_json = formatReceivedData(json_obj)
    filename = "authresp" + str(server_num) + ".json"
    with open(filename, 'w') as outfile:
        json.dump(aux_json, outfile, indent=4, sort_keys=True)
    return aux_json


def formatReceivedData(json_obj):

    try:
        aux_json = json_obj.decode("ascii").replace("'", '"')
        data = json.loads(aux_json)
        return data
    except AttributeError:
        return json_obj


def formatStateRes(json_dict):

    try:
        type_name = formatReceivedData(json_dict[0][0])
    except IndexError:
        type_name = formatReceivedData(json_dict[0][1])
    if type_name["type"] == "gameover":
        filename = type_name["type"] + ".json"
        aux_json = formatReceivedData(json_dict[0])
        with open(filename, 'w') as outfile:
            try:
                json.dump(aux_json, outfile, indent=4, sort_keys=True)
            except TypeError:
                return aux_json
    else:
        for i in range(4):
            for objs in json_dict[i]:
                filename = "River" + str(i + 1) + type_name["type"] + str(json_dict[i].index(objs)) + ".json"
                with open(filename, 'w') as outfile:
                    aux_json = formatReceivedData(objs)
                    outfile.write(json.dumps(aux_json, indent=4, sort_keys=True))

def findCannon(ship_coord):

    cannon_coord = []
    if ship_coord[1] in [1, 2, 3]:
        for i in range(2):
            cannon_coord.insert(0, [ship_coord[0], ship_coord[1] - i])
        return cannon_coord
    else:
        return ship_coord


def parseCommand(command):
    parsed = []
    aux_list = []
    if "getcannons" in command:
        return command
    elif "getturn" in command:
        parsed.insert(0, int(command.pop(0)))
        parsed.insert(1, command.pop(0))
        return parsed
    elif "shot" in command:
        lis = str.split(command.pop(0), ",")
        for item in lis:
            aux_list.insert(lis.index(item), int(item))
        parsed.insert(0, lis)
        parsed.insert(1, int(command.pop(0)))
        parsed.insert(2, command.pop(0))
        return parsed
    elif "quit" in command:
        return command
    else:
        print("Wrong command type")

arguments = sys.argv
#arguments = ["bd20212.dcc023.2advanced.dev", "52221" ,"2018013968:1:1c9324306dd2f0c2e3bc8623dc9df0d9d9b90cc5e0557843073665d069ceed3d+5a9ba60f795949fac526fe359039e17ce52f6e58f0a4ba3f1a748c98e2ab04fc"]
try:
    hostname = arguments.pop(0)
    port = arguments.pop(0)
    auth = arguments.pop(0)
except IndexError:
    print("Wrong number of arguments")
json_req = {
            "type": "authreq",
            "auth": auth
          }
json_req = json.dumps(json_req, indent=4, sort_keys=True)
message = json_req
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(0.2)
river_sockets = []
for i in range(4):
    river_sockets.insert(0, socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
connection_success = authReq(json_req)
while True:
    if connection_success:
        print("Type the command separated by blank spaces in the format specified below (It's not necessary to type in the SAG):")
        print("getcannons: auth, type\ngetturn: auth, turn, type\nshot: auth, cannon, id, type\nquit: auth, type")
        arguments = parseCommand(str.split(input(), " "))
        arguments.insert(0, auth)
        response = formatRequests(arguments).decode()
        if "gameover" in response:
            print(json.dumps(json.loads(response), indent=4, sort_keys=True))
            break
        print(json.dumps(json.loads(response), indent=4, sort_keys=True))
    else:
        print("Connection failed, retrying...")
        connection_success = authReq(json_req)
    
#Argumentos na lista vão em ordem alfabetica:
#getcannons: auth, type
#getturn: auth, turn, type
#shot: auth, cannon, id, type
#quit: auth, type
#Algoritmo de execução automática
# p = 0
# while p < 100:
#     connection_success = authReq(json_req)
#     args = [auth, "getcannons"]
#     if connection_success:
#         formatRequests(args)
#         f = open("cannons.json")
#         cannons = json.load(f)
#         print(cannons["cannons"])
#         f.close()
#         cannon_dict = {}
#         for i in range(273):
#             shooting_range = []
#             for cannon in cannons["cannons"]:
#                 shooting_range.insert(0, cannon)
#             ships = []
#             print("Starting turn: " + str(i))
#             args = [auth, i, "getturn"]
#             formatRequests(args)
#             for i in range(1, 5):
#                 for j in range(8):
#                     f = open("River" + str(i) + "state" + str(j) + ".json")
#                     ship_position = json.load(f)
#                     if ship_position["ships"]:
#                          ships.insert(0, (ship_position["bridge"], i))
#                          ships.insert(0, boat["id"])
#                     f.close()
#             for i in range(1, len(ships), 2):
#                 for pos in shooting_range:
#                     lis = findCannon(ships[i])
#                     if isinstance(lis[0], int):
#                         if tuple(pos) == lis:
#                             args = [auth, tuple(pos), ships[i - 1], "shot"]
#                             print("Shot at: " + str(ships[i]) + " from cannon " + str(pos[0]) + "," + str(pos[1]) + " at ship id " + str(ships[i - 1]))
#                             shooting_range.remove(pos)
#                             formatRequests(args)
#                         else:
#                             args = []
#                     else:
#                         if pos == lis[0] or pos == lis[1]:
#                             args = [auth, tuple(pos), ships[i - 1], "shot"]
#                             print("Shot at: " + str(ships[i]) + " from cannon " + str(pos[0]) + "," + str(pos[1]) + " at ship id " + str(ships[i - 1]))
#                             shooting_range.remove(pos)
#                             formatRequests(args)
#                         else:
#                             args = []
#         p += 1
#         print(p)
#     else:
#         print("Connection failed, retrying connection...")
