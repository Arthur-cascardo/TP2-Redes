import json
import asyncio
import socket
from flask import request, Flask

app = Flask(__name__)


@app.route("/api/game/<id>")
def game(id):
    stats = "No games found in DataSet"
    for games in games_played:
        if games["id"] == int(id):
            stats = games
            break
        else:
            stats = "No game found for id: " + str(id)
    return {"game_id": id, "game_stats": stats}


@app.route("/api/rank/sunk")
def sunk():
    args = request.args.to_dict()
    start = int(args["start"])
    end = int(args["end"])
    podium_sunk = {"ranking": "sunk"}
    if start > end:
        return "End id must be greater than start id"
    else:
        podium_sunk["start"] = start
        podium_sunk["end"] = end
        scoreboard = getScore(games_played, 'sunk_ships')
        scoreboard_sorted = sorted(scoreboard, key=lambda i: i['sunk_ships'], reverse=True)
        podium_sunk['game_ids'] = getIdByScore(scoreboard_sorted, podium_sunk["start"], podium_sunk["end"], podium_sunk['ranking'])
        return podium_sunk


@app.route("/api/rank/escaped")
def escaped():
    args = request.args.to_dict()
    start = int(args["start"])
    end = int(args["end"])
    podium_escaped = {"ranking": "escaped"}
    if start > end:
        return "End id must be greater than start id"
    else:
        podium_escaped["start"] = start
        podium_escaped["end"] = end
        scoreboard = getScore(games_played, 'escaped_ships')
        scoreboard_sorted = sorted(scoreboard, key=lambda i: i['escaped_ships'], reverse=True)
        podium_escaped['game_ids'] = getIdByScore(scoreboard_sorted, podium_escaped["start"], podium_escaped["end"], podium_escaped['ranking'])
        return podium_escaped


def getScore(dataset, key):
    scores = []
    for games in dataset:
        if key in games['score']:
            scores.insert(0, games['score'])
    return scores


def getIdByScore(dataset, start, end, type):
    ids = []
    length = (end - start) + 1
    if length > len(dataset):
        return "Too many games!"
    for scores in dataset:
        for games in games_played:
            if scores == games['score']:
                ids.insert(0, games['id'])
        if len(ids) == length:
            if type == 'sunk':
                ids.reverse()
            return ids


fp = open("dataset.json", 'r')
games_played = json.load(fp)
app.run()
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind(("localhost", 8090))
#server_socket.listen(5)


#(client_socket, address) = server_socket.accept()
#data = client_socket.recv(1024)
#rcv_msg=(data.decode("ascii"))
#print(rcv_msg)
#return_msg = "Codigo de analise cadastrado"
#client_socket.send(bytearray(return_msg, "ascii"))

