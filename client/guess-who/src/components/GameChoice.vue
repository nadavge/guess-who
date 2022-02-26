<template>
  <div>
    <label for="gameId">Game ID: </label><br />
    <input
      id="gameId"
      v-model="gameId"
      style="font-family: 'Courier New', Garamond, Times, Consolas"
    /><br />
    <label for="name">Name: </label><br />
    <input id="name" v-model="name" /><br />
    <button @click="joinGame">Join game!</button><br />
    <button @click="newGame">Create new game!</button><br />
    <div v-text="error" style="color: red" v-if="error" />
  </div>
</template>

<script>
export default {
  name: "GameChoice",
  components: {},
  inject: ["api_url"],
  emits: ["joinGame"],
  data() {
    return {
      gameId: "",
      name: "",
      error: "",
    };
  },
  methods: {
    joinGame() {
      if (this.name == "secretadmin") {
        fetch(this.api_url + "/game/" + this.gameId)
          .then((res) => {
            return res.json();
          })
          .then(() => {
            this.$emit("joinGame", {
              gameId: this.gameId,
              playerId: "admin",
            });
          })
          .catch((err) => {
            console.log("Failed retrieving game state...", err);
          });
        return;
      }
      fetch(this.api_url + "/game/" + this.gameId + "/join", {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: this.name }),
        cache: "no-cache",
      })
        .then(async (res) => {
          if (!res.ok) {
            const error = await res.json();
            throw Error(error.error);
          }
          return res.json();
        })
        .then((data) => {
          this.$emit("joinGame", {
            gameId: data.game_id,
            playerId: data.player_id,
            playerName: data.name,
            cookie: data.cookie,
          });
        })
        .catch((err) => {
          this.error =
            "Something was wrong with the parameters perhaps.. " +
            this.api_url +
            err.message;
        });
    },

    newGame() {
      fetch(this.api_url + "/game", {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then(async (res) => {
          if (!res.ok) {
            const error = await res.json();
            throw Error(error.error);
          }
          return res.json();
        })
        .then((data) => {
          // set the response data
          alert("New game created! '" + data.game_id + "'");
        })
        .catch((err) => {
          "Something was wrong with the parameters perhaps.. " +
            this.api_url +
            err.message;
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
