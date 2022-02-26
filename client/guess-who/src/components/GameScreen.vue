<template>
  <div v-text="error" style="color: red" v-if="error" />
  <div style="margin-bottom: 10px">
    <button class="reset" @click="resetGame">Reset game</button>
  </div>
  <div class="question" v-if="currentQuestion != null">
    {{ currentQuestion.title }}
  </div>
  <div v-if="gameState == 'ask'">
    <input v-model="nextQuestionTitle" style="min-width: 50%" />
    <button style="width: 50px" @click="askQuestion">Ask!</button>
  </div>
  <div v-if="gameState == 'lobby'">
    <button style="width: 50px" @click="startGame">Start!</button>
  </div>

  <div class="playerRow headers">
    <div class="playerCol">
      <h2>Yes</h2>
    </div>
    <div class="playerCol">
      <h2>Waiting</h2>
    </div>
    <div class="playerCol">
      <h2>No</h2>
    </div>
  </div>
  <div class="playerRow">
    <div class="playerCol">
      <PlayerList
        :players="playersInYes"
        answer="yes"
        :class="[currentQuestion?.correct_answer == 'yes' ? 'correct' : '']"
      />
    </div>
    <div class="playerCol">
      <PlayerList :players="playersInUnknown" answer="unknown" />
    </div>
    <div class="playerCol">
      <PlayerList
        :players="playersInNo"
        answer="no"
        :class="[currentQuestion?.correct_answer == 'no' ? 'correct' : '']"
      />
    </div>
  </div>
  <hr />
  <div class="playerRow">
    <div class="playerCol">
      <PlayerList :players="playersOutYes" answer="yes" />
    </div>
    <div class="playerCol">
      <PlayerList :players="playersOutUnknown" answer="unknown" />
    </div>
    <div class="playerCol">
      <PlayerList :players="playersOutNo" answer="no" />
    </div>
  </div>
</template>

<script>
import PlayerList from "./PlayerList.vue";

function playersByAnswer(players, question, answer) {
  // If there isn't a question, all players' answers are considered unknown
  if (question == null) {
    return answer == null ? players : [];
  }

  return players.filter((p) => question.answers[p.id] == answer);
}

export default {
  name: "GameScreen",
  components: { PlayerList },
  props: {
    gameId: String,
  },
  inject: ["api_url"],
  data() {
    return {
      players: [],
      gameState: null,
      currentQuestionId: null,
      currentQuestion: null,
      fetchGameTimer: null,
      fetchAnswersTimer: null,
      nextQuestionTitle: "",
      error: "",
    };
  },
  computed: {
    playersIn: function () {
      return this.players.filter((p) => p.game_status == "in");
    },
    playersOut: function () {
      return this.players.filter((p) => p.game_status == "out");
    },
    playersInYes: function () {
      return playersByAnswer(this.playersIn, this.currentQuestion, "yes");
    },
    playersInUnknown: function () {
      return playersByAnswer(this.playersIn, this.currentQuestion, null);
    },
    playersInNo: function () {
      return playersByAnswer(this.playersIn, this.currentQuestion, "no");
    },
    playersOutYes: function () {
      return playersByAnswer(this.playersOut, this.currentQuestion, "yes");
    },
    playersOutUnknown: function () {
      return playersByAnswer(this.playersOut, this.currentQuestion, null);
    },
    playersOutNo: function () {
      return playersByAnswer(this.playersOut, this.currentQuestion, "no");
    },
  },
  mounted() {
    this.fetchGameTimer = setInterval(() => this.fetchGameState(), 2000);
    this.fetchGameState();
  },
  unmounted() {
    clearInterval(this.fetchGameTimer);
    if (this.fetchAnswersTimer !== null) {
      clearInterval(this.fetchAnswersTimer);
    }
  },
  methods: {
    postRequest(rel_url, body, handler) {
      return fetch(this.api_url + rel_url, {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      })
        .then(async (res) => {
          if (!res.ok) {
            const error = await res.json();
            throw Error(error.error);
          }
          return res.json();
        })
        .then(handler)
        .catch((err) => {
          this.error = err.message;
        });
    },
    getRequest(rel_url, handler) {
      return fetch(this.api_url + rel_url)
        .then((res) => res.json())
        .then(handler)
        .catch((err) => {
          this.error = err.message;
        });
    },
    gameInfoHandler(gameInfo) {
      this.players = gameInfo.players;
      this.gameState = gameInfo.state;
      this.currentQuestionId = gameInfo.current_question;
    },
    fetchGameState() {
      this.getRequest("/game/" + this.gameId, this.gameInfoHandler);
    },
    fetchQuestionInfo() {
      if (this.currentQuestionId == null) {
        this.currentQuestion = null;
        return;
      }
      console.log("Fetching question info");
      fetch(
        this.api_url +
          "/game/" +
          this.gameId +
          "/question/" +
          this.currentQuestionId
      )
        .then((res) => res.json())
        .then((data) => {
          this.currentQuestion = data;
        })
        .catch((err) => {
          console.log("Failed retrieving question info...", err);
        });
    },
    askQuestion() {
      this.postRequest(
        "/game/" + this.gameId + "/question",
        {
          title: this.nextQuestionTitle,
        },
        (data) => {
          this.currentQuestionId++;
          this.currentQuestion = data;
          this.nextQuestionTitle = "";
        }
      );
    },
    startGame() {
      this.postRequest(
        "/game/" + this.gameId + "/start",
        {},
        this.gameInfoHandler
      );
    },
    resetGame() {
      if (confirm("Sure you want to reset the game?")) {
        this.postRequest(
          "/game/" + this.gameId + "/reset",
          {},
          this.gameInfoHandler
        );
      }
    },
  },
  watch: {
    currentQuestionId: function () {
      this.fetchQuestionInfo();
    },
    gameState: function (newValue) {
      if (newValue == "answer") {
        this.fetchAnswersTimer = setInterval(
          () => this.fetchQuestionInfo(),
          1000
        );
      } else {
        clearInterval(this.fetchAnswersTimer);
        this.fetchAnswersTimer = null;
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
div.question {
  margin: auto;
  text-align: center;
  font-size: 32px;
  font-weight: bold;
}
div.playerRow {
  margin: auto;
  text-align: center;
}

div.playerRow.headers {
  color: rgb(110, 110, 110);
}

div.playerCol {
  display: inline-block;
  width: 20%;
}

button.reset {
  border: 1px solid #640000;
  padding: 5px 10px 5px 10px;
  border-radius: 5px;
  color: white;
  background-color: #a30000;
}

.correct {
  background-color: rgb(228, 246, 255);
}
</style>
