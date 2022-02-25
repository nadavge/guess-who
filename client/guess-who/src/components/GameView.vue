<template>
  Hello player!<br />
  {{ waiting }}
  <template v-if="currentQuestionId != null">
    {{ questionTitle }}
  </template>
  <button
    :class="myAnswer == 'yes' ? ['selected'] : []"
    :disabled="gameState != 'answer'"
    @click="answer('yes')"
  >
    Yes
  </button>
  <button
    :class="myAnswer == 'no' ? ['selected'] : []"
    :disabled="gameState != 'answer'"
    @click="answer('no')"
  >
    No
  </button>
  State: {{ gameState }}
</template>

<script>
import { useCookies } from "vue3-cookies";

export default {
  name: "GameView",
  components: {},
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  props: {
    gameId: String,
  },
  inject: ["api_url"],
  data() {
    return {
      gameState: null,
      myAnswer: null,
      currentQuestionId: null,
      questionTitle: null,
      waiting: 0,
      fetchTimer: null,
    };
  },
  mounted() {
    this.fetchTimer = setInterval(() => this.fetchGameState(), 2000);
    this.fetchGameState();
  },
  unmounted() {
    clearInterval(this.fetchTimer);
    alert("Destroyed");
  },
  watch: {
    currentQuestionId: function () {
      this.fetchQuestionInfo();
    },
  },
  methods: {
    fetchGameState() {
      this.waiting++;
      fetch(this.api_url + "/game/" + this.gameId)
        .then((res) => {
          return res.json();
        })
        .then((data) => {
          this.gameState = data.state;
          this.currentQuestionId = data.current_question;
          this.waiting--;
        })
        .catch((err) => {
          this.waiting--;
          console.log("Failed retrieving game state...", err);
        });
    },
    fetchQuestionInfo() {
      this.waiting++;
      fetch(
        this.api_url +
          "/game/" +
          this.gameId +
          "/question/" +
          this.currentQuestionId
      )
        .then((res) => res.json())
        .then((data) => {
          let playerId = this.cookies.get("playerId");
          this.myAnswer = data.answers[playerId];
          this.questionTitle = data.title;
          this.waiting--;
        })
        .catch((err) => {
          this.waiting--;
          console.log("Failed retrieving question info...", err);
        });
    },
    answer(value) {
      this.waiting++;
      fetch(
        this.api_url +
          "/game/" +
          this.gameId +
          "/question/" +
          this.currentQuestionId,
        {
          method: "post",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            answer: value,
            cookie: this.cookies.get("playerCookie"),
          }),
        }
      )
        .then(async (res) => {
          if (!res.ok) {
            const error = await res.json();
            throw Error(error.error);
          }
          return res.json();
        })
        .then(() => {
          this.myAnswer = value;
          this.waiting--;
        })
        .catch((err) => {
          this.waiting--;
          this.error =
            "Something was wrong with the parameters perhaps.. " + err.message;
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
button.selected {
  background-color: #89b3eb;
}
</style>
