<script setup>
import { RouterLink, RouterView } from 'vue-router'
var loggedin = false
import { AuthStore } from '../stores/main.js'
var s = AuthStore()

function logout() {
    s.logout()
}

</script>

<template>
<header class="hero d-flex align-items-center  bg-light">
    <div style="width: 100%;" class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <div>
          <img src="@/assets/arcanum.png" style="max-height:30px; margin-right: 0px;">
          <a class="navbar-brand" href="/" >rcanum</a>
        </div>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
          aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end navbar-nav" id="navbarNav">
            
          <RouterLink class="nav-link" to="/">Home</RouterLink>
          <RouterLink class="nav-link" to="/books_list">Search</RouterLink>
          
          <RouterLink class="nav-link" to="/sections_list">Sections</RouterLink>
          <a class="nav-link" href="/#popular">Popular</a>
          <a class="nav-link" href="/#latest">Latest</a>
          <!-- <a class="nav-link" href="#">Account</a> -->
          <div class="dropdown">
            <a class=" dropdown-toggle nav-link" href="#" data-bs-toggle="dropdown">
              Account
            </a>
            <ul class="dropdown-menu">
                <template v-if="s.loggedIn">
              
              <li>
                
                <RouterLink class="dropdown-item" to="/dashboard">Dashboard</RouterLink>
            </li>
              <li><a class="dropdown-item" href="#" :onclick="logout">Log Out</a></li>
                </template>
              <template v-else>
              <li><a class="dropdown-item" href="/login">Login</a></li>
              <li><a class="dropdown-item" href="{{url_for('register')}}">Register</a></li>
              
              </template>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>