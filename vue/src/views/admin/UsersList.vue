<script setup>
import { ref } from 'vue'

import router from '../../router/index.js'
import fetchData from '../../helper.js'


var users_list = ref([])

async function deleteUser(x){
    console.log("delete user",x)
    var r = await fetchData(`/api/user/${x}/delete`)
    if(r["status"] == "success"){
        fetchUsers(last)
    }
}

async function fetchUsers(params){
    const data = await fetchData('/api/users?'  + new URLSearchParams({
        ...params
    }))
    users_list.value = data
}
var last = {
    username: "",
    tier: "-1"
}
function search(form){
    last = {
        username: form.target.elements.username.value,
        tier: form.target.elements.tier.value,
    }
    fetchUsers(last)
}

async function flipTier(id){
    var r = await fetchData(`/api/user/${id}/flipTier`)
    if(r["status"] == "success"){
        fetchUsers(last)
    }
}

fetchUsers(last)
</script>

<template>
<div id="body">
    <div class=" container mb-4">
      <div class="container body">


        <form @submit.prevent="search">
          <div class="row">
            <div class="col">
              <label>Username</label>
              <input type="text" name="username" class="form-control" placeholder="Username">
            </div>
            <div class="col">
              <label>Downloads</label>
              <select name="tier" class="form-select">
                <option selected value="-1">-</option>
                <option value="0">Allowed</option>
                <option value="1">Not Allowed</option>
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
        <div>
          <h1>Active Users</h1>
        </div>
        <table id="userList" class="table table-hover">
          <thead>
            <th>S. No.</th>
            <th>Username</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Created At</th>
            <th>Downloads</th>
            
            <th></th>

          </thead>
          <tbody>
            <tr v-if="users_list.length == 0">
              <td colspan="6" class="text-muted">No results available.</td>
            </tr>
            
            <tr v-for="(r, ind) in users_list" @click='router.push({ path: `/user/${r.id}` })'>
              <td>{{ind+1}}.</td>
              <td>{{r.username}}</td>
              <td>{{r.fname}}</td>
              <td>{{r.lname}}</td>
              <td>{{(new Date(r.created_at)).toLocaleDateString()}}</td>
              <td v-if="r.tier == 0"> <i class="bi bi-x-square" title="Not Allowed"></i> </td>
                <td v-else> <i class="bi bi-check-square" title="Allowed"></i> </td>
              
              <td>
                <div>
                <i class="bi bi-trash" @click.stop="deleteUser(r.id)" title="Delete User"></i>
                <i class="bi bi-arrow-down-up" @click.stop="flipTier(r.id)" title="Change Tier"></i>
                  <!-- <button class="btn btn-dark" @click.stop="flipTier(r.id)">Change Tier</button> -->

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
i {
  margin:5px;
  font-size: x-large;
}
</style>