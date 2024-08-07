<script setup>
import { ref } from 'vue'
import {useRoute,  RouterLink} from 'vue-router'
import { AuthStore } from '../stores/main.js'
import fetchData from '../helper.js'
import { computed } from 'vue'
import router from '../router/index.js'
import API_URL from '../constants.js'
var s = AuthStore()
var msg = ref("")
var username = ref("")
var usernameStatus = ref("")

var userData = ref({
    user:{},
    books:[],
    past:[],
    req:[]
})

async function init(){
    fetchData("/api/user_info").then(data => {
        console.log(data)
        userData.value = data
    })
}
init()


async function update(form){
    var data = {
        password: form.target.elements.password.value,
        fname: form.target.elements.fname.value,
        lname: form.target.elements.lname.value,
        email: form.target.elements.email.value
    }
    console.log(data)
    var response = await fetch(API_URL + '/api/change_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${s.authToken}`,
        },
        body: JSON.stringify(data),
    })
    var data = await response.json()
    if(data["status"] == "success"){
        s.logout()
        var user_info = {name: data["name"], role: data["role"], username: data["username"], id: data["id"]}
        s.login(data["access_token"], user_info)
        router.replace({ path: '/dashboard' })
    }else{
        msg.value = r["msg"]
    }
}

</script>
<template>
    <div id="body">
    <div class="float-login container">
      <h3 class="mb-3 text-center">Update Info</h3>
      <p v-show="msg!=''" class="err-msg">{{msg}}</p>
      <form method="POST" @submit.prevent="update">

        <div class="mb-3">
          <label class="text-muted" for="fname-input">First Name</label>
          <input :value="userData.user.fname" maxlength="20" class="form-control" type="text" name="fname" id="fname-input" required autofocus>
        </div>

        <div class="mb-3">
          <label class="text-muted" for="lname-input">Last Name</label>
          <input :value="userData.user.lname" maxlength="20" class="form-control" type="text" name="lname" id="lname-input" required autofocus>
        </div>

        <div class="mb-3">
          <label class="text-muted" for="email-input">Email</label>
          <input :value="userData.user.email" class="form-control" type="email" name="email" id="email-input" required>
        </div>

        <div class="mb-3">
            <div class="d-flex flex-row" style="justify-content: space-between; align-items: baseline">
          <label class="text-muted" for="username-input"  >Username</label>
          </div>
          <input :value="userData.user.username" disabled maxlength="20" class="form-control" type="text" name="username" id="username-input">  
          
        </div>

        <div class="text-muted mb-4">
          <label for="password-input">Password</label>
          <input maxlength="20" class="form-control" type="password" name="password" id="password-input">
          <p> *Leaving password blank won't change your password</p>
        </div>
        <div class="mb-4" style="width: 100%;">
          <button type="submit" class="btn btn-dark" style="width: 100%;"> Update </button>
        </div>
      </form>
    </div>

  </div>
</template>
<style scoped>
span {
    font-size:large;
}
</style>