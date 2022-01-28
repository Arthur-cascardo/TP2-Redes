import socket
import json
import sys
import statistics


def eprint(args):
    print(args, file=sys.stderr)


def parse_input(arg):
    games: dict     # Remover warning da IDE
    ip_port = arg.pop(0).split(":")
    ip_port[1] = int(ip_port[1])
    analysis = arg.pop(0)
    if analysis == '1':
        games = httpRequest(ip_port, analysis, None)
        games_info = getTop100GamesInfo(ip_port, games["game_ids"])
        return analise_1(games_info)
    elif analysis == '2':
        games = httpRequest(ip_port, analysis, None)
        games_info = getTop100GamesInfo(ip_port, games["game_ids"])
        return analise_2(games_info)
    else:
        return "Error"


def analise_1(game_info):
    return "Ok"
    

def analise_2(game_info):
    cannon_pos = {}
    normalized_cannons = []
    aux_list = []
    median_escaped = {}
    game_info.reverse()  # Desnecessário
    for game in game_info:
        normalized_cannons.insert(0, normalizeCannons(
            game["game_stats"]["cannons"]))
        try:
            cannon_pos[normalized_cannons[0]].append(game["game_stats"]["score"]["escaped_ships"])
        except KeyError:
            aux_list.insert(0, game["game_stats"]["score"]["escaped_ships"])
            cannon_pos[normalized_cannons[0]] = aux_list
        aux_list = []
    normalized_cannons = list(dict.fromkeys(normalized_cannons))
    for normals in normalized_cannons:
        median_escaped[normals] = float(statistics.median(cannon_pos[normals]))
    return median_escaped
    

def normalizeCannons(cannons):
    normalized_string = ""
    normalized = [0] * 8
    for cannon in cannons:
        normalized = insertPlusOne(normalized, cannon[0])
    for num in normalized:
        normalized_string += str(num)
    return normalized_string


def insertPlusOne(lis, index):
    lis[index - 1] += 1
    return lis


def getTop100GamesInfo(ip_port, games_ids):
    analysis = '0'
    games_info = []
    for ids in games_ids:
        games_info.insert(0, httpRequest(ip_port, analysis, ids))
    games_info.reverse()
    return games_info


def httpRequest(ip_port, analysis, game_id):
    if analysis == '0':
        req = "/api/game/" + str(game_id)
    elif analysis == '1':
        req = "/api/rank/sunk?start=1&end=100"
    elif analysis == '2':
        req = "/api/rank/escaped?start=1&end=100"
    else:
        return "Error"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip_port[0], ip_port[1]))
    request = f"GET {req} HTTP/1.1\r\nHost: {ip_port[0]}:{ip_port[1]}\r\n\r\n".encode()
    response = ""
    client.sendall(request)
    while True:
        recv = client.recv(1024)
        if recv == b'':
            break
        response += recv.decode()
    json_obj = json.loads(response[response.find("{"):])
    return json_obj


# arguments = sys.argv
arguments = ["localhost" + ":" + "5000", "2"]
print(parse_input(arguments))
# eof
