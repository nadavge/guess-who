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
      players: [
        {
          id: 1,
          name: "Player1",
        },
        {
          id: 2,
          name: "Player2",
        },
      ],
    };
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
