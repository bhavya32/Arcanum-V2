<script setup>
import { ref } from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import { AuthStore } from '@/stores/main.js'
import fetchData from '@/helper.js'
import { computed } from 'vue'
import router from '@/router/index.js'

var issued = ref([])

async function init(){
    fetchData('/api/issued').then(data => {
        issued.value = data
        console.log(data)
    })
}
init()
function dt(date){
    return new Date(date).toLocaleDateString()
}

async function revokeBook(userID, bookID){
    fetchData(`/api/revoke/${userID}/${bookID}`).then(data => {
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
          <h1>Issued Books</h1>
        </div>
        <table id="issueList" class="table table-hover">
          <thead>
            <th>S. No.</th>
            <th>Username</th>
            <th>Book</th>
            <th>Date Issued</th>
            <th>End Date</th>
            <th></th>

          </thead>
          <tbody>
            <tr v-if="issued.length == 0">
              <td colspan="5" class="text-muted">No books currently issued to any user.</td>
            </tr>
            
            <tr v-for="(r, index) in issued">
              <td>{{index + 1}}.</td>
              <td><RouterLink :to="`/user/${r.user_id}`" class="hidel">{{r.username}}</RouterLink></td>
              <td><RouterLink :to="`/book/${r.book_id}`" class="hidel">{{r.book_name}}</RouterLink></td>
              <td>{{dt(r.start)}}</td>
              <td>{{dt(r.end)}}</td>
              <td>
                <div>

                  <button @click="revokeBook(r.user_id, r.book_id)" class="btn btn-dark">Revoke</button>

                </div>
              </td>
            </tr>
            
          </tbody>
        </table>

      </div>

    </div>
  </div>
</template>