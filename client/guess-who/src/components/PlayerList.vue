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
ul {
  list-style: none;
  font-size: 16px;
  font-weight: 600;
}

ul.unknown li {
  color: rgb(80, 80, 80);
}

ul.no li {
  color: rgb(124, 17, 17);
}

ul.yes li {
  color: rgb(26 126 26);
}
</style>