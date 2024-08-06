<script setup>

import { ref } from 'vue'
import API_URL from '../constants.js'
import router from '../router/index.js'

import { AuthStore } from '../stores/main.js'
var s = AuthStore()
var loginBlocked = ref(false)
var msg = ""

console.log(s.authToken)
async function login(form){
    msg = ""
    loginBlocked.value = true
    var username = form.target.elements.username.value
    var password = form.target.elements.password.value
    var role = form.target.elements.userType.value
    
    fetch(API_URL + '/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password,
            userType: role
        })
    }).then(response => {
        if(response.status!==200){
          throw new Error(response.status.toString())
        }
        return response.json()
    }).then(data => {
        console.log(data)
        var user_info = {name: data["name"], role: data["role"], username: data["username"], id: data["id"]}
        s.login(data["access_token"], user_info)
        router.replace({ path: '/dashboard' })
    }).catch(err => {
        console.log(err)
        msg = "Invalid Credentials"
        loginBlocked.value = false
    })
}
</script>

<template>
    <div id = "body">
    <div class="float-login container">
			<h3 class="mb-3 text-center">Login</h3>
			<p v-show="msg!=''" class="err-msg">{{msg}}</p>
			
			<form method="POST" @submit.prevent="login" >
				<div class="mb-3 customRadio">
					<input type="radio" name="userType" id="userType1" value="student" checked>
					<label class="" for="userType1">Student</label>
					<input type="radio" name="userType" id="userType2" value="librarian">
					<label class="" for="userType2">Librarian</label>
				</div>

				<div class="mb-3">
					<label class="text-muted mb-2" for="username-input">Username</label>
					<input maxlength="20" class="form-control" type="text" name="username" id="username-input" required autofocus>
				</div>

				<div class="text-muted mb-4">
					<label for="password-input">Password</label>
					<input maxlength="20" class="form-control" type="password" name="password" id="password-input" required>
				</div>
				<div class="mb-4" style="width: 100%;">
					<button type="submit" class="btn btn-dark" style="width: 100%;" :disabled="loginBlocked"> Login </button>
				</div>
			</form>
			<div class=".d-flex">
				<div>
					<a href="/register" class="link-dark"> Create a new Account?</a>
				</div>

			</div>
		</div>
    </div>
</template>