<script setup>
//import router from '../router/index.js'
//router.replace({ path: '/' })
import userDash from '../components/userDash.vue'
import adminDash from '../components/adminDash.vue'
import { AuthStore } from '../stores/main.js'
import { ref } from 'vue'
import API_URL from '../constants.js'
var loginBlocked = ref(false)
var msg = ""
var s = AuthStore()
console.log(s.authToken)
var role = ""
</script>

<template>
    <template v-if="s.userInfo.role=='student'">
        <userDash />
    </template>
    <template v-else>
        <adminDash />
    </template> 
</template>