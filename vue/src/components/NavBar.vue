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
<header class="  hero d-flex align-items-center  bg-light">
    <div style="width: 100%; height:100%; background-color: white" class="navbar navbar-expand-lg navbar-light">
      <div class="container">
        <div>
          <img src="@/assets/arcanum.png" style="max-height:40px; margin-right: 0px;">
          <a class="navbar-brand" href="/" >rcanum</a>
        </div>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
          aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end navbar-nav" id="navbarNav">
            
          <RouterLink class="nav-link underline" to="/"><i class="bi bi-house"></i> Home</RouterLink>
          <RouterLink class="nav-link underline" to="/books_list"><i class="bi bi-book"></i> Books</RouterLink>
          
          <RouterLink class="nav-link underline" to="/sections_list"><i class="bi bi-folder"></i> Sections</RouterLink>
          <!-- <a class="nav-link underline" href="/#popular">Popular</a>
          <a class="nav-link underline" href="/#latest">Latest</a>
           -->
          <div class="dropdown">
            <a class=" dropdown-toggle nav-link" href="#" data-bs-toggle="dropdown">
              <i class="bi bi-person"></i> Account
            </a>
            <ul class="dropdown-menu">
                <template v-if="s.loggedIn">
              
              <li>
                
                <RouterLink class="dropdown-item" to="/dashboard"><i class="bi bi-columns-gap"></i> Dashboard</RouterLink>
            </li>
              <li><a class="dropdown-item" href="#" :onclick="logout"><i class="bi bi-box-arrow-right"></i> Log Out</a></li>
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

<style scoped>

.navbar-light {
  
  font-size:18px
}
.nav-link {
  color: rgb(0 0 0 / 80%) !important;
}
.underline {
  display: block;
}
.underline::after {
  content: '';
  width: 0px;
  height: 2px;
  display: block;
  background: black;
  transition: 500ms;
}

.underline:hover::after {
  width: 100%;
}
header {
  box-shadow: 0px -119px 115px 55px rgba(0,0,0,0.75);
  min-height:70px;
  position: fixed;
  top: 0;
  z-index: 2;
  width: 100%;
}
.dropdown-toggle:hover ~ .dropdown-menu {
  display: block; 
}
.dropdown-menu:hover {
  display: block;
}

</style>