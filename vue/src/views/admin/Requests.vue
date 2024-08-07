<script setup>
import { ref } from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import { AuthStore } from '@/stores/main.js'
import fetchData from '@/helper.js'
import { computed } from 'vue'
import router from '@/router/index.js'

var requests = ref([])

async function init(){
    fetchData('/api/requests').then(data => {
        requests.value = data
        console.log(data)
    })
}
init()
function dt(date){
    return new Date(date).toLocaleDateString()
}

async function reject(userID, bookID){
    fetchData(`/api/request/${userID}/${bookID}/reject`).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}
async function approve(userID, bookID){
    fetchData(`/api/request/${userID}/${bookID}/approve`).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}


</script>

<template>
    <div id="body">
    <div class="float-profile container">

      <div class="container body" style="margin-bottom: 50px;">
        <div>
          <h1>Issue Requests</h1>
        </div>
        <table id="issueList" class="table table-hover">
          <thead>
            <th>S. No.</th>
            <th>User</th>
            <th>Book</th>
            <th>Date Requested</th>
            <th></th>

          </thead>
          <tbody>
            <tr v-if="requests.length == 0">
              <td colspan="5" class="text-muted">No pending requests.</td>
            </tr>
            
            <tr v-for="(r, index) in requests">
              <td>{{index + 1}}.</td>
              <td><RouterLink :to="`/user/${r.user_id}`" class="hidel">{{r.username}}</RouterLink></td>
              <td><RouterLink :to="`/book/${r.book_id}`" class="hidel">{{r.book_name}}</RouterLink></td>
              <td>{{dt(r.created_at)}}</td>
              <td>
                <div>

                  <button @click="approve(r.user_id, r.book_id)" class="btn btn-dark">Approve</button>
                  <button @click="reject(r.user_id, r.book_id)" class="btn btn-dark">Reject</button>

                </div>
              </td>
            </tr>
            
          </tbody>
        </table>

      </div>

    </div>
  </div>
</template>