<script setup>
import { ref } from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import { AuthStore } from '../stores/main.js'
import fetchData from '../helper.js'
import { computed } from 'vue'
import router from '../router/index.js'
var s = AuthStore()
var userID = parseInt(useRoute().params.id?.toString())

var userData = ref({
    user:{},
    books:[],
    past:[],
    req:[]
})
var isAdmin = !isNaN(userID)
var fetchUrl = isNaN(userID)?'/api/user_info':('/api/user_info/' + userID.toString())

async function init(){
    fetchData(fetchUrl).then(data => {
        console.log(data)
        userData.value = data
    })
}
init()
function dt(date){
    return new Date(date).toLocaleDateString()
}

async function returnBook(book_id){
    var returnUrl = isNaN(userID)?`/api/book/${book_id}/return`:`/api/revoke/${userID}/${book_id}`
    fetchData(returnUrl).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}

async function cancelRequest(book_id){
    var returnUrl = isNaN(userID)?`/api/request/${book_id}/cancel`:`/api/request/${userID}/${book_id}/reject`
    fetchData(returnUrl).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}

async function approveRequest(book_id){
    var returnUrl =`/api/request/${userID}/${book_id}/approve`
    fetchData(returnUrl).then(data => {
        if(data["status"] == "success"){
            init()
        }
    })
}



</script>
<template>
    <div id="body">
  <div class="float-profile container">
    <div class="container d-flex flex-row justify-content-between info"  style="margin-bottom: 20px; font-size: large; flex-wrap: wrap;">
        <div>
            Name - <b>{{userData.user.fname}} {{userData.user.lname}}</b>
        </div>
        <div>
            Username - <b>{{userData.user.username}}</b>
        </div>
        <div>
            Email - <b>{{userData.user.email}}</b>
        </div>
        <div>
            Tier - <b>
                <template v-if="userData.user.tier == 0"> FREE </template>
                <template v-else> PAID </template>
            </b>
        </div>
        
    </div>
    <div class="container" style="margin-bottom: 50px;">
      <h1>Requested Books</h1>
      <table id="issueList" class="table table-hover">
          <thead>
              <th>S. No.</th>
              <th>Book Name</th>
              <th>Request Date</th>
              <th></th>
          </thead>
          <tbody>
              
              <tr v-if="userData.req.length == 0">
                  <td colspan="4" class="text-muted">No books queued for request.</td>
                </tr>
              

            <tr v-for="(book, index) in userData.req" @click='router.push({ path: `/book/${book.book1.id}` })'>
                <td>{{index+1}}.</td>
                <td>{{book.book1.title}}</td>
                <td>{{dt(book.created_at)}}</td>
                <td>
                    <div v-if="!isAdmin">
                        <button class="btn btn-dark" @click.stop="cancelRequest(book.book1.id)">Cancel</button>
                    </div>
                    <div v-else>
                  <button class="btn btn-dark" @click.stop="approveRequest(book.book1.id)">Approve</button>
                  <button class="btn btn-dark" @click.stop="cancelRequest(book.book1.id)">Reject</button>
                </div>
                </td>
                
            </tr>
            
          </tbody>
      </table>
      
  </div>

    <div class="container" style="margin-bottom: 50px;">
        <h1>Issued Books</h1>
        <table id="issueList" class="table table-hover">
            <thead>
                <th>S. No.</th>
                <th>Book Name</th>
                <th>Issue Date</th>
                <th>Due Date</th>
                <th></th>
                <th></th>
            </thead>
            <tbody>
              
              
                <tr v-if="userData.books.length == 0">
                  <td colspan="6" class="text-muted">No books currently issued.</td>
                </tr>
              
                
                
              <tr v-for="(book, index) in userData.books" @click='router.push({ path: `/book/${book.id}` })'>
                  <td>{{index+1}}.</td>
                  <td>{{book.title}}</td>
                  <td>{{dt(book.start)}}</td>
                  <td>{{dt(book.end)}}</td>
                  <td>
                    <div v-if="isAdmin">
                        <button class="btn btn-dark" @click.stop="returnBook(book.id)">Revoke</button>
                    </div>
                    <div v-else>
                        <button class="btn btn-dark" @click.stop="returnBook(book.id)">Return</button>
                    </div>
                    
                  </td>
                  
              </tr>
              
            </tbody>
        </table>
        
    </div>

    <div class="container" style="margin-bottom: 50px;">
      <h1>Past Books</h1>
      <table id="issueList" class="table table-hover">
          <thead>
              <th>S. No.</th>
              <th>Book Name</th>
              <th>Issue Date</th>
              <th>Return Date</th>
              <th></th>
              <th></th>
          </thead>
          <tbody>
            <tr v-if="userData.past.length == 0">
                  <td colspan="5" class="text-muted">No books completed yet.</td>
                </tr>
            
              
              <tr v-for="(book, index) in userData.past" @click='router.push({ path: `/book/${book.book1.id}` })'>
                  <td>{{index+1}}.</td>
                  <td>{{book.book1.title}}</td>
                  <td>{{dt(book.start)}}</td>
                  <td>{{dt(book.end)}}</td>
              </tr>
              
              
          </tbody>
      </table>
      
  </div>

  <div v-if="!isAdmin" class="container" style="margin-bottom: 50px;">
        <h2>Account Settings</h2>
        <div class="d-flex flex-row justify-content-between">
            <div>
                <button class="btn btn-dark" @click="router.push({ path: '/change_info' })">Change Info</button>
            </div>
            
        </div>
  </div>
	
</div>
</div>
<div style="height: 10px"></div>
</template>
<style scoped>
tr {
    cursor: pointer
}
button {
    margin: 0px 10px
}

.info div{
    margin: 10px 10px
}
</style>