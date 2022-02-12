from copy import deepcopy
from flask import Flask, request
from pymongo import MongoClient
import json
import bson
from bson.objectid import ObjectId

app = Flask(__name__)
# TODO maybe add server info
mongo_client = MongoClient()
game_db = mongo_client.game_database


def deid(object: dict):
    object_copy = deepcopy(object)
    object_copy["id"] = str(object_copy.pop("_id"))
    return object_copy


@app.route("/games", methods=["POST"])
def create_game():
    game = {
        "state": "lobby"
    }


@app.route("/games/<game_id>", methods=["GET"])
def get_game_info(game_id):
    try:
        game_id = ObjectId(game_id)
    except bson.errors.InvalidId:
        return {"error": "Unknown or invalid Game ID"}, 400

    game = game_db.games.find_one({"_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    return {
        "state": game["state"],
        "questions": game["questions"],
        "players": [
            {
                p["id"],
                p["name"]
            }
            for p in game["players"]
        ]
    }
