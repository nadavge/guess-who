<template>
  <div class="app">
    <div style="margin-bottom: 10px" v-if="gameId && playerId">
      <button @click="leaveGame()">Leave game</button>
    </div>
    <GameChoice v-if="gameId == null" @joinGame="joinGame($event)" />
    <GameView :gameId="gameId" v-if="gameId != null && !admin" />
    <GameScreen :gameId="gameId" v-if="gameId != null && admin" />
  </div>
</template>

<script>
import GameScreen from "./components/GameScreen.vue";
import GameView from "./components/GameView.vue";
import GameChoice from "./components/GameChoice.vue";
import { useCookies } from "vue3-cookies";

export default {
  name: "App",
  components: {
    GameChoice,
    GameScreen,
    GameView,
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  data() {
    return {
      gameId: null,
      playerId: null,
      playerName: null,
      playerCookie: null,
      admin: false,
    };
  },
  mounted() {
    if (this.cookies.get("gameId") != null) {
      this.gameId = this.cookies.get("gameId");
      this.playerId = this.cookies.get("playerId");
      this.playerName = this.cookies.get("playerName");
      this.playerCookie = this.cookies.get("playerCookie");
    }
  },
  methods: {
    joinGame(e) {
      this.gameId = e.gameId;
      if (e.playerId == "admin") {
        this.admin = true;
        console.log(`admin: ${this.admin}, gameId: ${this.gameId}`);
        return;
      }

      this.playerId = e.playerId;
      this.playerName = e.playerName;
      this.playerCookie = e.cookie;

      this.cookies.set("playerCookie", e.cookie, "1Y");
      this.cookies.set("playerId", e.playerId, "1Y");
      this.cookies.set("playerName", e.playerName, "1Y");
      this.cookies.set("gameId", e.gameId, "1Y");
    },
    leaveGame() {
      if (
        confirm(
          "Are you sure you want to leave?\nYou can't come back and the game will be broken!"
        )
      ) {
        this.cookies.keys().forEach((cookie) => this.cookies.remove(cookie));
        this.gameId = null;
      }
    },
  },
};
</script>

<style>
#app {
  font-family: Arial, Helvetica, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1a1b1b;
}

.app {
  margin: auto;
  text-align: center;
}
</style>
