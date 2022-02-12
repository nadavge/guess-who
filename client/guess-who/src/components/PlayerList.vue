<template>
  <ul :class="[answer]">
    <li v-for="player in players" :key="player.id">{{ player.name }}</li>
  </ul>
</template>

<script>
export default {
  name: "PlayerList",
  props: {
    answer: String,
    players: Array,
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul.unknown li {
  color: gray;
}

ul.no li {
  color: red;
}

ul.yes li {
  color: green;
}
</style>