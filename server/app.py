from copy import deepcopy
import os
import random
from flask import Flask, jsonify, request
import pymongo
from pymongo.collection import ReturnDocument
import json
import bson
from bson.objectid import ObjectId
import string

app = Flask(__name__)
# TODO maybe add server info
mongo_hostname = os.environ.get('MONGODB_HOSTNAME', 'localhost')
mongo_client = pymongo.MongoClient(mongo_hostname)
db = mongo_client.game_database

PLAYER_ID_SIZE = 6  # bytes
PLAYER_COOKIE_SIZE = 20  # bytes
GAME_ID_LEN = 4
GAME_ID_LETTERS = string.ascii_uppercase


def random_hex_str(count):
    return os.urandom(count).hex()


def deid_obj(object: dict):
    object_copy = deepcopy(object)
    object_copy["id"] = str(object_copy.pop("game_id"))
    return object_copy


# TODO remove on production?
@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type'
    # Other headers can be added here if required
    return response

# TODO remove later on, this is for debugging


def jsonified_game_info(game: dict):
    return jsonify({
        "game_id": game["game_id"],
        "state": game["state"],
        "current_question": len(game["questions"])-1 if game["questions"] else None,
        "players": [
            {
                "id": p["id"],
                "name": p["name"],
                "game_status": p["game_status"],
            }
            for p in game["players"]
        ]
    })


@app.route("/game", methods=["GET"])
def get_games():
    games = db.games.find({})
    return {
        "games": [jsonified_game_info(g) for g in games]
    }


@app.route("/game", methods=["POST"])
def create_game():
    game = {
        "game_id": "".join(random.choice(GAME_ID_LETTERS) for _ in range(GAME_ID_LEN)),
        "state": "lobby",
        "questions": [],
        "old_questions": [],
        "players": [],
    }

    db.games.insert_one(game).inserted_id
    return jsonified_game_info(game)


@app.route("/game/<game_id>", methods=["GET"])
def get_game_info(game_id):
    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    return jsonified_game_info(game)


@app.route("/game/<game_id>/start", methods=["POST"])
def start_game(game_id):
    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    if game["state"] != "lobby":
        return {"error": f"Game in state '{game['state']}', should be 'lobby'"}, 409

    chosen_player = random.choice(game["players"])
    game = db.games.find_one_and_update(
        {"game_id": game["game_id"]},
        {"$set": {"state": "ask", "chosen_player_id": chosen_player["id"]}},
        return_document=ReturnDocument.AFTER
    )

    return jsonified_game_info(game)


@app.route("/game/<game_id>/reset", methods=["POST"])
def reset_game(game_id):
    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    if game["state"] != "ask":
        return {"error": f"Game in state '{game['state']}', should be 'ask'"}, 409

    chosen_player = random.choice(game["players"])
    game = db.games.find_one_and_update(
        {"game_id": game["game_id"]},
        {"$set": {
            "chosen_player_id": chosen_player["id"],
            "players.$[].game_status": "in",
            "old_questions": game["old_questions"] + game["questions"],
            "questions": []
        }},
        return_document=ReturnDocument.AFTER
    )

    return jsonified_game_info(game)


@app.route("/game/<game_id>/question", methods=["GET"])
def get_questions(game_id):
    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    return jsonify(game["questions"])


@app.route("/game/<game_id>/question", methods=["POST"])
def ask_question(game_id):
    if request.json is None:
        return {"error": "Invalid request format, expected json"}, 400

    if "title" not in request.json:
        return {"error": "Missing question title in request"}, 400

    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    if game["state"] != "ask":
        return {"error": f"Game in state '{game['state']}', should be 'ask'"}, 409

    new_question = {
        "title": request.json["title"],
        "answers": {p["id"]: None for p in game["players"]},
        "correct_answer": None
    }

    # Set the status of each player once the new question had been asked
    if game["questions"]:
        def new_status(p):
            if p["game_status"] == "in" and last_question["answers"][p["id"]] == correct_answer:
                return "in"
            return "out"

        last_question = game["questions"][-1]
        correct_answer = last_question["answers"][game["chosen_player_id"]]
        db.games.update_one(
            {"game_id": game_id},
            {
                "$set": {
                    f"players.{i}.game_status": new_status(p)
                    for i, p in enumerate(game["players"])
                }
            }
        )

    db.games.update_one(
        {"game_id": game_id},
        {
            "$push": {
                "questions": new_question
            },
            "$set": {
                "state": "answer"
            }
        }
    )

    return new_question


@app.route("/game/<game_id>/question/<int:question_id>", methods=["POST"])
def answer_question(game_id, question_id):
    if request.json is None:
        return {"error": "Invalid request format, expected json"}, 400

    if "answer" not in request.json or\
       "cookie" not in request.json:
        return {"error": "Missing answer and/or secret in request"}, 400

    if request.json["answer"] not in ["yes", "no"]:
        return {"error": "Invalid answer"}, 400

    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    if not 0 <= question_id < len(game["questions"]):
        return {"error": "Invalid question ID"}, 404

    if game["state"] != "answer":
        return {"error": f"Game in state '{game['state']}', should be 'answer'"}, 409

    for player in game["players"]:
        if player["cookie"] == request.json["cookie"]:
            break
    else:
        return {"error": "Unable to locate user based on secret"}, 400

    # NOTE This can potentially be re-answered after the fact... So be it for now :)
    db.games.update_one(
        {"game_id": game_id},
        {
            "$set": {f"questions.{question_id}.answers.{player['id']}": request.json["answer"]}
        }
    )

    game = db.games.find_one({"game_id": game_id})
    assert game is not None

    current_question = game["questions"][question_id]
    # After we answer, we check to see if we were the last answer. We do it after to _reduce_ race conditions
    if game["state"] == "answer" and all(answer is not None for answer in current_question["answers"].values()):
        correct_answer = current_question["answers"][game["chosen_player_id"]]
        db.games.update_one(
            {"game_id": game_id, "state": "answer"},
            {"$set": {"state": "ask", f"questions.{question_id}.correct_answer": correct_answer}}
        )

    return jsonify({"answer": request.json["answer"]})


@ app.route("/game/<game_id>/question/<int:question_id>", methods=["GET"])
def get_question_info(game_id, question_id):
    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    if not 0 <= question_id < len(game["questions"]):
        return {"error": "Invalid question ID"}, 404

    question = game["questions"][question_id]
    return jsonify({
        "title": question["title"],
        "answers": {
            player_id: answer for (player_id, answer) in question["answers"].items()
        },
        "correct_answer": question["correct_answer"]
    })


@ app.route("/game/<game_id>/join", methods=["POST"])
def join_game(game_id):
    if request.json is None:
        return {"error": "Invalid request format, expected json"}, 400

    if "name" not in request.json:
        return {"error": "Missing user name in request"}, 400

    player_id = random_hex_str(PLAYER_ID_SIZE)
    cookie = random_hex_str(PLAYER_COOKIE_SIZE)
    game = db.games.find_one({"game_id": game_id})
    if game is None:
        return {"error": "Game not found"}, 404

    if game["state"] != "lobby":
        return {"error": "Game doesn't accept players"}, 409

    game = db.games.find_one_and_update(
        {"game_id": game_id, "state": "lobby"},
        {
            "$push": {
                "players": {
                    "id": player_id,
                    "name": request.json["name"],
                    "cookie": cookie,
                    "game_status": "in",
                }
            }
        },
        return_document=ReturnDocument.AFTER
    )

    if game is None:
        return {"error": "Game doesn't accept players"}, 409

    return jsonify({
        "game_id": str(game_id),
        "player_id": player_id,
        "name": request.json["name"],
        "cookie": cookie
    })
