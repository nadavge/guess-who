<template>
  <div class="question" v-if="currentQuestion != null">
    {{ currentQuestion.title }}
  </div>
  <div class="playerRow">
    <div class="playerCol">
      <PlayerList :players="playersInYes" answer="yes" />
    </div>
    <div class="playerCol">
      <PlayerList :players="playersInUnknown" answer="unknown" />
    </div>
    <div class="playerCol">
      <PlayerList :players="playersInNo" answer="no" />
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
    fetchGameState() {
      fetch(this.api_url + "/game/" + this.gameId)
        .then((res) => res.json())
        .then((data) => {
          // set the response data
          this.players = data.players;
          this.gameState = data.state;
          this.currentQuestionId = data.current_question;
        })
        .catch((err) => {
          console.log("Failed retreiving game state...", err);
        });
    },
    fetchQuestionInfo() {
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
div.playerCol {
  display: inline-block;
  width: 20%;
}
</style>
