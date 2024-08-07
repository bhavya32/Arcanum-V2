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
async function register(form){
    var data = {
        username: form.target.elements.username.value,
        password: form.target.elements.password.value,
        fname: form.target.elements.fname.value,
        lname: form.target.elements.lname.value
    }
    var response = await fetch(API_URL + '/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    var data = await response.json()
    if(data["status"] == "success"){
        var user_info = {name: data["name"], role: data["role"], username: data["username"], id: data["id"]}
        s.login(data["access_token"], user_info)
        router.replace({ path: '/dashboard' })
    }else{
        msg.value = r["msg"]
    }
}

async function checkUsername() {
    if (username.value.trim() === '') {
    usernameStatus.value = "";
    return;
    }

    usernameStatus.value = 'checking';
    const data = await fetchData(`/api/usename_availability?username=${username.value}`);
    usernameStatus.value = data.available ? 'available' : 'taken';
}

</script>
<template>
    <div id="body">
    <div class="float-login container">
      <h3 class="mb-3 text-center">Register</h3>
      <p v-show="msg!=''" class="err-msg">{{msg}}</p>
      <form method="POST" @submit.prevent="register">

        <div class="mb-3">
          <label class="text-muted" for="fname-input">First Name</label>
          <input maxlength="20" class="form-control" type="text" name="fname" id="fname-input" required autofocus>
        </div>

        <div class="mb-3">
          <label class="text-muted" for="lname-input">Last Name</label>
          <input maxlength="20" class="form-control" type="text" name="lname" id="lname-input" required autofocus>
        </div>

        <div class="mb-3">
            <div class="d-flex flex-row" style="justify-content: space-between; align-items: baseline">
          <label class="text-muted" for="username-input"  >Username</label>
          <div style="text-align: center;margin-top: 5px">
            <span v-show="usernameStatus === 'checking'">Checking...</span>
            <span v-show="usernameStatus === 'available'"><i class="bi bi-check2-square"></i> Username is available</span>
            <span v-show="usernameStatus === 'taken'"><i class="bi bi-exclamation-square"></i> Username is already taken</span>
        </div></div>
          <input maxlength="20" class="form-control" type="text" name="username" id="username-input" required autofocus v-model="username" v-on:focusout="checkUsername">  
          
        </div>

        <div class="text-muted mb-4">
          <label for="password-input">Password</label>
          <input maxlength="20" class="form-control" type="password" name="password" id="password-input" required>
        </div>
        <div class="mb-4" style="width: 100%;">
          <button type="submit" class="btn btn-dark" style="width: 100%;"> Create Account </button>
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