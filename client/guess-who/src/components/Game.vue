<template>
  <div class="hello">
    Playing in room {{ this.gameId }}
    <PlayerList :players="players" answer="yes" />
    <PlayerList :players="players" answer="no" />
  </div>
</template>

<script>
import PlayerList from "./PlayerList.vue";

export default {
  name: "Game",
  components: { PlayerList },
  props: {
    gameId: String,
  },
  inject: ["api_url"],
  data() {
    return {
      players: [],
    };
  },
  mounted() {
    this.fetchGameState();
  },
  methods: {
    fetchGameState() {
      fetch(this.api_url + "/game/" + this.gameId)
        .then((res) => res.json())
        .then((data) => {
          // set the response data
          this.players = data.players;
        })
        .catch((err) => {
          console.log("Failed retreiving game state...", err);
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
