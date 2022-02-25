<template>
  <GameChoice v-if="gameId == null" @joinGame="joinGame($event)" />
  <Game :gameId="gameId" v-if="gameId != null" />
</template>

<script>
import Game from "./components/Game.vue";
import GameChoice from "./components/GameChoice.vue";
import { useCookies } from "vue3-cookies";

export default {
  name: "App",
  components: {
    GameChoice,
    Game,
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  data() {
    return {
      gameId: null,
    };
  },
  methods: {
    joinGame(e) {
      alert("Event triggered" + e.gameId);
      this.gameId = e.gameId;
      this.playerId = e.playerId;
      this.playerName = e.playerName;
      this.cookie = e.cookie;

      this.cookies.set("playerCookie", e.cookie, "1Y");
      this.cookies.set("playerId", e.playerId, "1Y");
      this.cookies.set("playerName", e.playerName, "1Y");
      this.cookies.set("gameId", e.gameId, "1Y");
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
