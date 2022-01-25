import json
from flask import Flask
import asyncio
import socket


app = Flask(__name__)


@app.route("/api/game/<id>", methods=['GET'])
def game(id):
    stats = "No games found in DataSet"
    for games in games_played:
        if games["id"] == id:
            stats = games
            break
        else:
            stats = "No game found for id: " + str(id)
    return {"game_id": id, "game_stats": stats}


@app.route("/api/rank/sunk?start=<index1>&end=<index2>", methods=['GET'])
def sunk(index1, index2):
    podium_sunk = {"ranking": "sunk"}
    if index1 > index2:
        return "End id must be greater than start id"
    else:
        podium_sunk["start"] = index1
        podium_sunk["end"] = index2
        scoreboard = getScore(games_played, 'sunk_ships')
        scoreboard_sorted = sorted(scoreboard, key=lambda i: i['sunk_ships'], reverse=True)
        podium_sunk['game_ids'] = getIdByScore(scoreboard_sorted, podium_sunk["start"], podium_sunk["end"], podium_sunk['ranking'])


@app.route("/api/rank/escaped?start=<index1>&end=<index2>", methods=['GET'])
def escaped(index1, index2):
    podium_sunk = {"ranking": "escaped"}
    if index1 > index2:
        return "End id must be greater than start id"
    else:
        podium_sunk["start"] = index1
        podium_sunk["end"] = index2
        scoreboard = getScore(games_played, 'escaped_ships')
        scoreboard_sorted = sorted(scoreboard, key=lambda i: i['escaped_ships'], reverse=True)
        podium_sunk['game_ids'] = getIdByScore(scoreboard_sorted, podium_sunk["start"], podium_sunk["end"], podium_sunk['ranking'])


def getScore(dataset, key):
    scores = []
    for games in dataset:
        if key in games['score']:
            scores.insert(0, games['score'])
    return scores


def getIdByScore(dataset, start, end, type):
    ids = []
    length = (end - start) + 1
    for scores in dataset:
        set = []
        for games in games_played:
            if scores == games['score']:
                ids.insert(0, games['id'])
        if len(ids) == length:
            if type == 'sunk':
                ids.reverse()
            return ids


fp = open("dataset.json", 'r')
games_played = json.load(fp)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 80))
server_socket.listen(5)
while True:
    (client_socket, address) = server_socket.accept()
    data = client_socket.recv(1024)
    print(data.decode("ascii"))
    message = "Server: " + input()
    client_socket.send(bytearray(message, "ascii"))


