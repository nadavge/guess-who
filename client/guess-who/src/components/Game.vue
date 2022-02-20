<template>
  <div class="hello">
    YO
    <PlayerList :players="players" answer="yes" />
    <PlayerList :players="players" answer="no" />
  </div>
</template>

<script>
import PlayerList from "./PlayerList.vue";

export default {
  name: "Game",
  components: { PlayerList },
  props: {},
  data() {
    return {
      players: [],
    };
  },
  mounted() {
    var that = this;
    function fetchData() {
      // I prefer to use fetch
      // you can use use axios as an alternative
      fetch("http://127.0.0.1:5000/game/620a570626057c1a44731b8b")
        .then((res) => {
          console.log(res);
          // a non-200 response code
          if (!res.ok) {
            // create error instance with HTTP status text
            throw Error(`${res.status} ${res.statusText}`);
          }

          return res.json();
        })
        .then((json) => {
          // set the response data
          that.players = json.players;
        })
        .catch((err) => {
          console.log("Nabaz2", err);
        })
        .then(() => {
          console.log("Nabaz");
        });
    }

    fetchData();
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
