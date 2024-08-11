<script setup>
import { ref, computed } from 'vue'
import API_URL from '@/constants';
import { AuthStore } from '../stores/main.js'
import {useRoute, RouterLink} from 'vue-router'
import router from '../router/index.js'
import fetchData from '../helper.js'
var s = AuthStore()
var sections = ref([])

async function fetchSections(){
    const response = await fetch(API_URL + '/api/sections')
    const data = await response.json()
    sections.value = data
}

async function deleteSection(id) {
    console.log("delete", id)
    fetchData(`/api/section/${id}/delete`).then(data => {
        if(data["status"] == "success"){
            fetchSections()
        }
    })
}

function match(a){
    return a.toLowerCase().includes(section_search.value.toLowerCase())
}

var section_search = ref("")
var filteredSections = computed(() => {
    return sections.value.filter(section => match(section.name))
})
fetchSections()

</script>

<template>
    <div id="body">
    <div class="float-profile container">

      <div class="container body" style="margin-bottom: 50px;">
        <div class="d-flex flex-row justify-content-between">
          <h1>Sections</h1>
          <input type="text" class="filterSection" placeholder="Search" v-model="section_search">
          
            
          <div v-if="s.userInfo.role=='librarian'" class="d-flex align-items-center">
            <RouterLink class="btn btn-dark" to="create_section"><i class="bi bi-folder-plus"></i> Create</RouterLink>
          
        </div>
        </div>
        <table id="issueList" class="table table-hover">
          <thead class="thead-dark">
            <th>S. No.</th>
            <th>Section Name</th>
            <th>Books</th>
            <th></th>

          </thead>
          <tbody>

            
            <tr v-for="(section, index) in filteredSections" @click='router.push({ path: `/section/${section.id}` })'>
              <td>{{index + 1}}.</td>
              <td>{{section.name}}</td>
              <td>{{section.books_count}}</td>
              <td v-if="s.userInfo.role == 'librarian'">
                <div>
                    <i class="bi bi-trash" style="font-size: x-large;" @click.stop="deleteSection(section.id)"></i>    
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
    cursor: pointer;
    font-size: large;
}
.filterSection {
    
  padding:10px;
  border-radius: 7px;
  font-size: 16px;
  border: 2px solid transparent;
  height: 40px;
  box-shadow: 0 0 0 1px #dddddd;
  :focus{
      border: 2px solid black;
      border-radius: 3px;
  }
                
}

td {
  padding: 10px;
}
</style>