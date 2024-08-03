<script setup>
import { ref } from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import fetchData from '../helper.js'
import API_URL from '../constants.js'
import { AuthStore } from '../stores/main.js'
import { computed } from 'vue'
import Rating from '../components/Rating.vue'
import router from '../router/index.js'
var s = AuthStore()
var book_id = parseInt(useRoute().params.id.toString())
var book = ref({
    "authors": [],
    "desc": "",
    "id": book_id,
    "rating": 100,
    "reads": 1,
    "title": "",
    "sections": []
})
var tier = ref(0)
var issued = ref(false)
var requested = ref(false)
var score = ref(0)
var allratings = ref([])
var sections = ref([])
var isStudent = computed(() => s.userInfo.role == "student")
function init(){
fetchData('/api/book/' + book_id.toString()).then(data => {
    console.log(data)
    book.value = data["book"]
    issued.value = data["issued"]
    requested.value = data["requested"]
    score.value = data["score"]
    allratings.value = data["allratings"]
    tier.value = data["tier"]
})}
init()

fetchData('/api/sections').then(data => {
    sections.value = data
})

async function removeBookFromSection(section_id){
    fetchData(`/api/book/${book_id}/section/${section_id}/remove`).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}
async function addBookToSection(section_id){
    fetchData(`/api/book/${book_id}/section/${section_id}/add`).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}
async function request(){
    var result = await fetchData('/api/book/' + book_id.toString() + '/request')
    if(result["status"] == "success"){
        requested.value = true
    }
}

</script>
<template>
     <div id="body">

<div id="section-info" class="container mb-4 d-flex">
  <img class="img-thumbnail thumbnail" :onerror="`this.src='${API_URL}/static/200x250.svg';`" alt="Image not Set"
    :src="`${API_URL}/static/books/${book_id}`">
  <div class="d-flex flex-column justify-content-around">
    <div>
      <h2 class="mb-2">{{book.title}}</h2>
      <p style="color: rgba(0,0,0,.55);">{{book.desc}}</p>
    </div>
    <div>
      <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Authors: <template v-for="(auth, index) in book.authors"><template v-if="index!=0">,</template><RouterLink :to="{ name: 'books_list', query: { author: auth.name } }" class="hidel" >{{auth.name}}</RouterLink></template></p>
      <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Avg. Rating: {{book.rating}}/5</p>
      <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Total Reads: {{book.reads}}</p>
      <div class="d-flex flex-row ">
        <p style="margin: 0; margin-right: 5px; padding: 4px;" class="text-muted">Sections:</p>
        
        <div v-for="section in book.sections" class="dropdown" style="margin-right: 5px;">
          <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown"
            aria-expanded="false">
            {{section.name}}
          </button>
          <ul class="dropdown-menu ">
            <li><RouterLink class="dropdown-item" :to="`/section/${section.id}`">View</RouterLink></li>
            <li v-if="s.userInfo.role!='student'"><button class="dropdown-item" @click="removeBookFromSection(section.id)" href="/book/{{book.id}}/sections/remove?sid={{section.id}}">Remove</button></li>
            
          </ul>
        </div>
        
      </div>
      <div class="d-flex flex-row mb-2 text-muted">
            
            <p style="margin: 0; margin-right: 5px; padding: 4px;" class="text-muted">Your Rating:</p>
            <Rating @rating-update="init" :rating="score" :book_id="book_id"></Rating>
            
          </div>
      <div v-if="isStudent" class="mb-2">
        
        <template v-if="!issued">
        <button v-if="requested" disabled class="btn btn-dark">Requested on {{(new Date(requested.created_at)).toLocaleDateString()}}</button>
        <a v-else href="/book/{{book.id}}/request" class="btn btn-dark">Request</a>
        </template>
        
        <template v-else>
        
        <a href="./{{book.id}}/read" class="btn btn-dark">Read</a>
        <a v-if="tier==1" href="/static/pdfs/{{book.id}}.pdf" download="{{book.title}}" class="btn btn-dark">Download</a>
        
    </template>

      </div>
      
      <div v-else class="d-flex flex-row">
        <form method="get" action="/book/{{book.id}}/sections/add">
          <div class="d-flex flex-row">
            <select class="form-select" id="secsel" name="sid" @change='addBookToSection($event.target.value)'>
              <option selected disabled>Select Section</option>
              <option v-for="sec in sections" :value="sec.id">{{sec.name}}</option>
              
            </select>
          </div>
        </form>
        <a  style="margin-left: 5px;" href="/static/pdfs/{{book.id}}.pdf" target="_blank" class="btn btn-dark">View PDF</a>
        <RouterLink :to="`/book/${book_id}/edit`" class="btn btn-dark">Edit</RouterLink>
        <a  style="margin-left: 5px;" href="/book/{{book.id}}/delete" class="btn btn-dark">Delete</a>
      </div>
      
    </div>
  </div>

</div>
<div class="float-profile container">

  <div class="container body" style="margin-bottom: 50px;">
    <h1>User Ratings</h1>
    <table id="issueList" class="table table-hover">
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
          <td>{{index + 1}}.</td>
          <td>{{i.user}}</td>
          <td>{{i.score}}</td>
        </tr>
        
      </tbody>
    </table>

  </div>

</div>
</div>
</template>