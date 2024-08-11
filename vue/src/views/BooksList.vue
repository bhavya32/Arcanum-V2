<script setup>
import { ref } from 'vue'
import API_URL from '@/constants';
import { AuthStore } from '../stores/main.js'
import {useRoute, RouterLink} from 'vue-router'
import router from '../router/index.js'
import fetchData from '../helper.js'
var authorq = useRoute().query.author
var author = authorq?authorq:""
var s = AuthStore()
var sections = ref([])
var books_list = ref([])
async function fetchSections(){
    const response = await fetch(API_URL + '/api/sections')
    const data = await response.json()
    sections.value = data
}

async function deleteBook(x){
    console.log(x)
    fetchData(`/api/book/${x}/delete`).then(data => {
        if(data["status"] == "success"){
            fetchDataDirect(last)
        }
      })
}

var last = {
    sort: "id",
    book: "",
    author: author,
    section:""
}

async function fetchDataDirect(params){
    const response = await fetch(API_URL + '/api/search?'  + new URLSearchParams({
        ...params
    }))
    const data = await response.json()
    books_list.value = data
}

function search(form){
  fetchDataDirect({
        sort: form.target.elements.sort.value,
        book: form.target.elements.book.value,
        author: form.target.elements.author.value,
        section: form.target.elements.section.value
    })
}
fetchSections()
fetchDataDirect(last)
</script>

<template>
    <div class=" container mb-4" style="padding-top:20px">
      <div class="container body">


        <form @submit.prevent="search" >
          <div class="row">
            <div class="col">
              <label>Book Name</label>
              <input type="text" name="book" class="form-control" placeholder="Book name">
            </div>
            <div class="col">
              <label>Author Name</label>
              <input :value="author" type="text" name="author" class="form-control" placeholder="Author name">
            </div>
            <div class="col">
              <label>Section</label>
              <select name="section" class="form-select">
                <option value="">Any</option>
                <template v-for="section in sections">
                  <option :value="section.id">{{section.name}}</option>
                </template>
              </select>
            </div>
            <div class="col">
              <label>Sort By</label>
              <select name="sort" class="form-select">
                <option value="id" selected disabled>Select</option>
                <option value="title" >Book Name (Asc.)</option>
                <option value="rating" >Rating (Desc.)</option>
                <option value="reads">Total Reads (Desc.)</option>
              </select>
            </div>
            <div class="col" style="display: flex; align-items: flex-end;">
              <button type="submit" class="btn btn-dark"> Filter </button>
            </div>
          </div>
        </form>
      </div>
    </div>
    <div class="float-profile container">

      <div class="container body" style="margin-bottom: 50px;">
        <div class="d-flex flex-row justify-content-between">
          <h1>Books</h1>
          <div class="d-flex align-items-center">
            <RouterLink v-if="s.userInfo.role == 'librarian'" class="btn btn-dark" to="book_add"><i class="bi bi-upload"></i> Upload</RouterLink>
            
          </div>
        </div>
        <table id="issueList" class="table table-hover">
          <thead>
            <th>S. No.</th>
            <th>Book Name</th>
            <th>Author Name</th>
            <th>Rating</th>
            <th>Total Reads</th>
            <th></th>

          </thead>
          <tbody>
            
            <tr v-if="books_list.length == 0">
              <td colspan="6" class="text-muted">No results available.</td>
            </tr>
            
            <tr v-for="(book, index) in books_list" @click='router.push({ path: `/book/${book.id}` })'>
              <td>{{index+1}}.</td>
              <td>{{book.title}}</td>
              <td>{{book.authors}}</td>
              <td>{{book.rating}}</td>
              <td>{{book.reads}}</td>
              <td v-if="s.userInfo.role == 'librarian'">
                <div>
                    <i class="bi bi-trash" style="font-size: x-large;" @click.stop="deleteBook(book.id)"></i>
                  
                    
                </div>
              </td>
            </tr>
            
          </tbody>
        </table>

      </div>

    </div>
</template>
<style scoped>
tr {
    cursor: pointer;
    font-size: large;
}
td {
  padding: 10px;
}
</style>