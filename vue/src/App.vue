<script setup>
import NavBar from './components/NavBar.vue'
import { RouterLink, RouterView } from 'vue-router'
var loggedin = false;

</script>

<template>
  <NavBar />
  <div class="body-margin">
  <RouterView />
</div>
</template>

<style scoped>
.body-margin{
  margin-top: 70px;
  height:90%;
}
</style>
