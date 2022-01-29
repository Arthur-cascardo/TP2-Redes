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
        eprint("Wrong argument for 'analysis' parameter")


def analise_1(games_info):
    f = open("output.csv", "w")
    auth_ids = []
    idsAndSunkShips = []
    games_out = {}
    games_out_list = []
    for games in games_info:  # pega todos os sags
        auth_ids.append(games['game_stats']['auth'])  # array com os sag de todos os jogadores do top 100
        idsAndSunkShips.append(games['game_stats']['auth'])
        idsAndSunkShips.append(games['game_stats']['score']['sunk_ships'])
    for x in auth_ids:  # ve numero de repeticoes dos sags
        aux2 = 0
        aux3 = 0
        numOfGames = 0
        sumOfSunk = 0
        while aux2 < 100:
            if x == auth_ids[aux2]:
                numOfGames = numOfGames + 1
            aux2 = aux2 + 1
        while aux3 < 200:
            aux3 = aux3 + 1
            if x == idsAndSunkShips[aux3-1]:
                sumOfSunk = sumOfSunk + idsAndSunkShips[aux3]
            aux3 = aux3 + 1
        avrgSunk = sumOfSunk/numOfGames
        games_out['SAG'] = x
        games_out['num_of_games'] = numOfGames
        games_out['avrg_sunk'] = avrgSunk
        games_out_list.insert(0, games_out)
        games_out = {}
    games_out_list = sorted(games_out_list, key=lambda y: y['avrg_sunk'], reverse=True)
    for game in games_out_list:
        print(game['SAG'], ",", game['num_of_games'], ",", round(game['avrg_sunk'], 2), file=f)
    f.close()
    return games_out_list


def funct(sets):
    return sets['avrg_sunk']


def analise_2(game_info):
    f = open("output.csv", "w")
    cannon_pos = {}
    normalized_cannons = []
    aux_list = []
    median_escaped = {}
    for game in game_info:  # Percorre as informações dos top 100 jogos e normaliza o posicionamento dos canhões
        normalized_cannons.insert(0, normalizeCannons(
            game["game_stats"]["cannons"]))
        try:
            cannon_pos[normalized_cannons[0]].append(game["game_stats"]["score"]["escaped_ships"])
        except KeyError:
            aux_list.insert(0, game["game_stats"]["score"]["escaped_ships"])
            cannon_pos[normalized_cannons[0]] = aux_list  # Lista com todos os valores de navio escapados associados a um posicionamento normalizado
        aux_list = []
    normalized_cannons = list(dict.fromkeys(normalized_cannons))  # Dicionario ordenado cuja chave é a normalização dos canhões e o valor associado à chave, o numero de navios escapados
    for normals in normalized_cannons:
        median_escaped[normals] = float(statistics.median(cannon_pos[normals]))  # Tira a média dos navios escapados
    for key in median_escaped:
        print(key, ",", median_escaped[key], file=f)
    f.close()
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
        req = ""
        eprint("Wrong argument for analysis")
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


arguments = sys.argv
arguments.pop(0)
print(parse_input(arguments))
# eof
