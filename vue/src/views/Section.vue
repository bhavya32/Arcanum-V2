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
var section_id = parseInt(useRoute().params.id.toString())

var books = ref([])
var section = ref({
    "date_created": "...",
    "description": "...",
    "id": section_id,
    "name": "..."
})

var isStudent = computed(() => s.userInfo.role == "student")
async function init(){
fetchData('/api/section/' + section_id.toString()).then(data => {
    console.log(data)
    books.value = data["books"]
    section.value = data["section"]
})
}
init()

async function removeBookFromSection(book_id){
    //console.log("removing book", book_id, "from section", section_id)
    fetchData(`/api/book/${book_id}/section/${section_id}/remove`).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}

async function deleteSection(){
    console.log("deleting section", section_id)
}

</script>

<template>
    <div id="body">

<div id="section-info" class="container mb-4 d-flex">
  <img class="img-thumbnail thumbnail" :onerror="`this.src='${API_URL}/static/200x250.svg';`" alt="Image not Set"
  :src="`${API_URL}/static/sections/${section_id}`">
  <div class="d-flex flex-column justify-content-around">
    <div>
      <h2 class="mb-2">{{section.name}}</h2>
      <h5 style="color: rgba(0,0,0,.55);">{{section.description}}</h5>
    </div>
    <div>
      <p style="color: rgba(0,0,0,.55); margin-bottom: 0;">Date Created: {{(new Date(section.date_created)).toLocaleDateString()}}</p>
      <p style="color: rgba(0,0,0,.55);">Total Books: {{books.length}}</p>
      <div v-if="!isStudent" class="d-flex flex-row">
        <RouterLink :to="`/section/${section_id}/edit`" class="btn btn-dark">Edit</RouterLink>
        <button style="margin-left: 5px;" @click='deleteSection()' class="btn btn-dark">Delete</button>
      </div>
      
    </div>
    
  </div>

</div>
<div class="float-profile container">

  <div class="container body" style="margin-bottom: 50px;">
    <h1>Section Books</h1>
    <table id="issueList" class="table table-hover">
      <thead>
        <th>S. No.</th>
        <th>Book Name</th>
        <th>Reads</th>
        <th>Rating</th>
        <th></th>

      </thead>
      <tbody>
        
        <tr v-if="books.length == 0">
          <td colspan="5" class="text-muted">No books in this section yet.</td>
        </tr>
        
        
        <tr v-for="(book, index) in books" @click='router.push({ path: `/book/${book.id}` })'>
          <td>{{index + 1}}.</td>
          <td>{{book.title}}</td>
          <td>{{book.reads}}</td>
          <td>{{book.rating}}</td>
          <td v-if="s.userInfo.role == 'librarian'">
                <div>
                    <i class="bi bi-trash" style="font-size: x-large;" @click.stop="removeBookFromSection(book.id)"></i>
                </div>
          </td>
          
        </tr>
        
      </tbody>
    </table>

  </div>

</div>
</div>

</template>
<style scoped>
tr {
    cursor: pointer
}
</style>