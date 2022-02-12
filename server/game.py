import os

PLAYER_ID_SIZE = 12
QUESTION_ID_SIZE = 12
COOKIE_ID_SIZE = 20


class Player:
    def __init__(self, name, pid=None, cookie=None):
        self.name = name
        self.pid = os.urandom(PLAYER_ID_SIZE).hex() if pid is None else pid
        self.cookie = os.urandom(COOKIE_ID_SIZE).hex() if cookie is None else cookie

    @classmethod
    def from_json(cls, s: dict):
        return Player(
            s["name"],
            s["pid"],
            s["cookie"]
        )

    def json(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "cookie": self.cookie
        }


class Question:
    def __init__(self, title, answers, qid=None):
        self.id = os.urandom(QUESTION_ID_SIZE).hex() if qid is None else qid
        self.title = title
        self.answers = answers

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "answers": self.answers
        }


class Game:
    def __init__(self, state="lobby", questions=None, players=None, chosen_player_id=None):
        self.state = state
        self.questions = [] if questions is None else questions
        self.players = [] if players is None else players
        self.chosen_player_id = chosen_player_id

    @classmethod
    def from_json(cls, game: dict):
        return Game(
            game["state"],
            game["questions"],
            [Player.from_json(s) for s in game["players"]]
        )

    def json(self):
        return {
            "state": self.state,
            "questions": [q.json() for q in self.questions],
            "players": [p.json() for p in self.players]
        }
