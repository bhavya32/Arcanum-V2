<script setup>
import {ref, toRef, watch, defineEmits} from 'vue'
import fetchData from '../helper.js'
const props = defineProps({
  rating: Number,
  book_id: Number
})
const emit = defineEmits(['rating-update'])

var userRatingRef = toRef(props, "rating")
var userRating = ref(userRatingRef.value)
watch(userRatingRef, (val) => {
    userRating.value = val
})


async function updateRating(num) {
    var old = userRating.value
    userRating.value = num
    console.log(userRating.value)
    var res = await fetchData('/api/rate/book/' + props.book_id.toString() + '?' + new URLSearchParams({
        rating: num
    }))
    console.log(res)

    if (res["status"] == "success" ){
        console.log("Rating Updated")
        emit('rating-update');
    } else {
        userRating.value = old
    }
}
</script>
<template>
      <div class="rating">
        <svg
          v-for="num in 5"
          
          :class="{active: userRating >= num}"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 19.481 19.481"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          enable-background="new 0 0 19.481 19.481"
          @click="updateRating(num)"
        >
          <g>
            <path d="m10.201,.758l2.478,5.865 6.344,.545c0.44,0.038 0.619,0.587 0.285,0.876l-4.812,4.169 1.442,6.202c0.1,0.431-0.367,0.77-0.745,0.541l-5.452-3.288-5.452,3.288c-0.379,0.228-0.845-0.111-0.745-0.541l1.442-6.202-4.813-4.17c-0.334-0.289-0.156-0.838 0.285-0.876l6.344-.545 2.478-5.864c0.172-0.408 0.749-0.408 0.921,0z" />
          </g>
        </svg>
      </div>
  </template>

  <style scoped >
    svg.active {
      fill: #e4b90c;
    }
  
    svg {
      fill: #9cacbd
    }
  
    .rating {
        display:flex;
        flex-direction: row;
        min-width: 150px;
    }
  </style>