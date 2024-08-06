<script setup>
import {ref, toRef, watch} from 'vue'
const props = defineProps({
  showOverlay: Boolean,
})
var showOverlay = toRef(props, "showOverlay")
</script>

<template>
    <div class="overlay" v-if="showOverlay">
      <div class="overlay-content">
        
        <slot></slot>
      </div>
    </div>
  </template>
  
  <style scoped>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .overlay-content {
    background-color: white;
    padding: 40px;
    border-radius: 10px;
    max-width:80%;
    max-height: 50%;
  }
  </style>