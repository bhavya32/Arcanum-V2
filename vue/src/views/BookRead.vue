<script setup>
import { useRoute, RouterLink } from 'vue-router'
import API_URL from '../constants.js'
var book_id = useRoute().params.id


</script>

<template>
    <div id="body" style="width: 100%; height: 100%;">

<div id="pdf" style="width: 100%; height: 100%;">
  <iframe :src="`${API_URL}/static/pdfs/${book_id}.pdf#toolbar=0`" style="width: 100%; height: 100%;">
    <p>It appears your web browser doesn't support iframes.</p>
  </iframe>

</div>

</div>
</template>
