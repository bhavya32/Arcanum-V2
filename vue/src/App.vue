<script setup>
import NavBar from './components/NavBar.vue'
import { RouterLink, RouterView } from 'vue-router'
var loggedin = false;

</script>

<template>
  <NavBar />
  
  <RouterView />
</template>