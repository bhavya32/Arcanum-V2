<script setup>
import { ref } from 'vue'
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

fetchSections()

</script>

<template>
    <div id="body">
    <div class="float-profile container">

      <div class="container body" style="margin-bottom: 50px;">
        <div class="d-flex flex-row justify-content-between">
          <h1>Sections</h1>
          
          <div v-if="s.userInfo.role=='librarian'" class="d-flex align-items-center">
            <RouterLink class="btn btn-dark" to="create_section">Create New</RouterLink>
          </div>
          
        </div>
        <table id="issueList" class="table table-hover">
          <thead>
            <th>S. No.</th>
            <th>Section Name</th>
            <th>Books</th>
            <th></th>

          </thead>
          <tbody>

            
            <tr v-for="(section, index) in sections" @click='router.push({ path: `/section/${section.id}` })'>
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
    cursor: pointer
}
</style>