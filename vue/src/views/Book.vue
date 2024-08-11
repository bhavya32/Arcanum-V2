<script setup>
import { ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import fetchData from '../helper.js'
import API_URL from '../constants.js'
import { AuthStore } from '../stores/main.js'
import { computed } from 'vue'
import Rating from '../components/Rating.vue'
import Comments from '../components/Comments.vue'
import router from '../router/index.js'

import Swal from 'sweetalert2'
var s = AuthStore()
var book_id = parseInt(useRoute().params.id.toString())
var book = ref({
  "authors": [],
  "desc": "",
  "id": book_id,
  "rating": 100,
  "reads": 1,
  "title": "",
  "sections": [],
  "price": 200
})
var tier = ref(0)
var issued = ref(false)
var requested = ref(false)
var score = ref(0)
var allratings = ref([])
var sections = ref([])
var isStudent = computed(() => s.userInfo.role == "student")
var owned = ref(false)

var croppedDesc = computed(() => book.value.desc.length > 300 ? book.value.desc.slice(0, 300) + "..." : book.value.desc)
var isCropped = computed(() => book.value.desc.length > 300)
function init() {
  fetchData('/api/book/' + book_id.toString()).then(data => {
    console.log(data)
    book.value = data["book"]
    issued.value = data["issued"]
    requested.value = data["requested"]
    score.value = data["score"]
    allratings.value = data["allratings"]
    tier.value = data["tier"]
    owned.value = data["owned"]
  })
}
init()
var showOverlay = ref(false)

fetchData('/api/sections').then(data => {
  sections.value = data
})


async function request() {
  var result = await fetchData('/api/book/' + book_id.toString() + '/request')
  if (result["status"] == "success") {
    init()
  }
  else {
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: result["msg"],
    })
  }
}

async function deleteBook() {
  console.log("delete book", book_id)
  fetchData('/api/book/' + book_id.toString() + '/delete').then(data => {
    if (data["status"] == "success") {
      router.push('/books_list')
    }
  })
}

var purchaseOngoing = ref(false)
async function purchase() {
  purchaseOngoing.value = true
  var response = await fetch(API_URL + '/api/create_purchase_request', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${s.authToken}`,
    },
    body: JSON.stringify({
      book_id: book_id
    }),
  })
  var data = await response.json()
  var options = {
    "key": "rzp_test_jeV260FCDVkU47",
    "amount": book.price * 100,
    "currency": "INR",
    "name": "Arcanum",
    "description": "Purchase Book",
    "order_id": data["order_id"],
    "handler": async function (response) {
      console.log(response)
      const paymentData = {
        razorpay_payment_id: response.razorpay_payment_id,
        razorpay_order_id: response.razorpay_order_id,
        razorpay_signature: response.razorpay_signature
      };
      var res = await fetch(API_URL + '/api/verify_purchase', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${s.authToken}`,
        },
        body: JSON.stringify(paymentData),
      })
      var data = await res.json()
      if (data["status"] == "success") {
        init()
      }
    },
  }
  var rzp1 = new Razorpay(options);
  rzp1.open()
  rzp1.on('payment.failed', function (response) {
    console.log("failed", response.error.code);
  });
  rzp1.on('payment.success', function (response) {
    console.log("success", response)
  })
  purchaseOngoing.value = false
}
async function download() {
  var data = await fetchData(`/api/book/${book_id}/download`)
  var url = `${API_URL}/api/download?id=${data["id"]}`
  window.open(url, '_blank')
}
</script>
<template>
  <div id="body">

    <div id="section-info" class="container mb-4 d-flex">
      <img class="img-thumbnail thumbnail" :onerror="`this.src='${API_URL}/static/200x250.svg';`" alt="Image not Set"
        :src="`${API_URL}/static/books/${book_id}`">
      <div class="d-flex flex-column justify-content-around desc">
        <div>
          <h2 class="mb-2">{{ book.title }}</h2>
          <p style="color: rgba(0,0,0,.55);">
            {{ croppedDesc }}
            <template v-if="isCropped">
              <button @click="showOverlay = true" class="readmore text-muted">Read More</button>
            </template>
          </p>
          <div class="buttons">
            <template v-if="isStudent" class="mb-2">
              <template v-if="!owned">
                <template v-if="!issued">
                  <button v-if="requested" disabled class="btn btn-dark">Requested on {{ (new
                    Date(requested.created_at)).toLocaleDateString() }}</button>
                  <button v-else @click="request()" class="btn btn-dark"><i class="bi bi-file-earmark-plus"></i>
                    Request</button>
                  <button v-if="!owned" :disabled="purchaseOngoing" @click="purchase()" class="btn btn-dark"><i
                      class="bi bi-cart3"></i> Purchase</button>
                </template>
              


              <template v-else>

                <RouterLink :to="`${book.id}/read`" class="btn btn-dark"><i class="bi bi-journal"></i> Read</RouterLink>
                <!-- <a v-if="tier == 1" href="/static/pdfs/{{book.id}}.pdf" download="{{book.title}}"
                  class="btn btn-dark">Download</a> -->
                <button v-if="tier==1" class="btn btn-dark" @click='download()'><i class="bi bi-download"></i> Download</button>

              </template>
            </template>
              <template v-else>
                <button class="btn btn-dark" @click='download()'><i class="bi bi-download"></i> Download</button>
              </template>
            </template>

            <template v-else class="d-flex flex-row">



              <a :href="`${API_URL}/static/pdfs/${book_id}.pdf`" target="_blank" class="btn btn-dark">View PDF</a>
              <RouterLink :to="`/book/${book_id}/edit`" class="btn btn-dark">Edit</RouterLink>
              <button class="btn btn-dark" @click="deleteBook()">Delete</button>
            </template>
          </div>

        </div>
        <div class="overlay" v-show="showOverlay">
          <div class="overlay-content">
            <i class="bi bi-x-lg" @click="showOverlay = false" style="position: absolute; top: 20px; right: 20px;"></i>

            <h2 class="mb-2">{{ book.title }}</h2>
            <p style="color: rgba(0,0,0,.55);">{{ book.desc }}</p>
          </div>
        </div>
      </div>
      
        <div class="metadata">
          <div>
          <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Authors: <template
              v-for="(auth, index) in book.authors"><template v-if="index != 0">,</template>
              <RouterLink :to="{ name: 'books_list', query: { author: auth.name } }" class="hidel">{{ auth.name }}
              </RouterLink>
            </template>
          </p>
          
          <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Total Reads: {{ book.reads }}</p>
          <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Price: ₹{{ book.price }}</p>
          <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Sections: <template
              v-for="(section, index) in book.sections"><template v-if="index != 0">,</template>
              <RouterLink :to="`/section/${section.id}`" class="hidel">{{ section.name }}</RouterLink>
            </template>
          </p>
        </div>
        <div class="rating-stats">
          <!-- <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Avg. Rating: {{ book.rating }}/5  (from {{ allratings.length }} users)</p> -->
          <div class="d-flex flex-row mb-2 text-muted">

            <!-- <p style="margin: 0; margin-right: 5px; padding: 4px;" class="text-muted">Your Rating:</p> -->
            <div class="d-flex flex-column" style="align-items: center; margin-right: 25px">
              <h3 style="margin:0">{{book.rating}} / 5</h3>
              <p style="margin:0">by {{allratings.length}} users</p>
            </div>
            <Rating @rating-update="init" :rating="score" :book_id="book_id"></Rating>

          </div>
        </div>

        </div>
      

    </div>
    <div class="float-profile container">

      <div class="container body" style="margin-bottom: 50px;">
        <h1>User Reviews</h1>
        <Comments :book_id="book_id" :user="s.userInfo.username"></Comments>
        <!-- <table id="issueList" class="table table-hover">
          <thead>
            <th>S. No.</th>
            <th>User</th>
            <th>Score</th>

          </thead>
          <tbody>
            <tr v-if="allratings.length == 0">
              <td colspan="3" class="text-muted">No ratings yet.</td>
            </tr>


            <tr v-for="(i, index) in allratings">
              <td>{{ index + 1 }}.</td>
              <td>{{ i.user }}</td>
              <td>{{ i.score }}</td>
            </tr>

          </tbody>
        </table> -->

      </div>

    </div>
  </div>
</template>

<style scoped>
#section-info {
  justify-content: center;
  flex-wrap: wrap;
  align-items: center;
}

.desc {
  max-width: 570px;
  padding: 10px 0px;
  margin-right: 20px;
}

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
  max-width: 80%;
  max-height: 50%;
  position: relative;
  overflow-y: scroll
}

.readmore {
  background: none;
  border: none;
  text-decoration: underline;
}

.metadata {
  padding:30px;
  padding-bottom: 0;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  width: 100%;
}
.rating-stats {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  border: 2px solid #cecdcd;
  padding: 10px 15px;
  border-radius: 20px;
  box-shadow: 0px 6px 40px -32px rgba(0,0,0,0.75);
}
.buttons {
  display: flex;
  flex-direction: row;
}

.buttons .btn {
  margin-right: 10px;
  padding: 10px 15px;
  border: none;
}

::-webkit-scrollbar {
  width: 5px;
}

::-webkit-scrollbar-track {
  margin: 10px 30px;
}

/* Handle */
::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 20px
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>