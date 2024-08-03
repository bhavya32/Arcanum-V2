<script setup>
import API_URL from '../constants.js'
</script>
<script>
export default {
  data() {
    return { popular: [], latest: [], gs: [], loggedin: true }
  },
  created() {
    fetch(API_URL + '/api/home_books')
      .then(response => response.json())
      .then(data => {
        this.$data.popular = data["popular"];
        this.$data.latest = data["latest"];
        this.$data.gs = data["gs"];
      })
  }
}

  </script>
<template>
  
  <div class="container d-flex">
    <div class="container" style="display: flex; flex-direction: column; justify-content: center;">
      <h1>Embark on a Literary Odyssey: Your Next Favorite Book Awaits!</h1>
      <p>Every genre, every mood, right at your fingertips.</p>
    </div>
    <div>
      <img src="@/assets/edu.png" class="img-fluid" alt="Base image" style="max-height: 90vh;">
    </div>
  </div>
  <section class="categories my-5">

    <div id="category" class="container">
      <div class="d-flex flex-row justify-content-between mb-2">
        <h2>Browse by Category</h2>
        <div class="d-flex align-items-center">
          <a href="/sections" class="btn btn-dark">View All</a>
        </div>
      </div>
      <div id="categoryCarousel" class="carousel carousel-dark slide" data-bs-ride="carousel">
        <div class="carousel-inner">
          <div v-for="(sections, index) in gs" class="carousel-item" v-bind:class = "(index==0)?'active':''">
            
            <div  class="d-flex flex-row justify-content-evenly">
              
              <div v-for="s in sections" style="max-width: 208px; flex-wrap: wrap; align-content: center;"
                class="borderhover position-relative d-flex flex-column justify-content-center">
                <img style="margin: 2px;" class="thumbnail" :onerror="`this.src='${API_URL}/static/200x250.svg';`"
                  alt="Image not Set" :src="`${API_URL}/static/sections/${s.id}`">
                <div class="card-body">
                  <h5 class="card-title text-center">{{s.name}}</h5>
                  <a href="/section/{{s.id}}" class=" stretched-link hide-slink"></a>
                </div>
              </div>
              
            </div>
          </div>
          
          
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#categoryCarousel" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#categoryCarousel" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Next</span>
        </button>
      </div>
    </div>
  </section>

  <section class="popular my-5">
    <div id="popular" class="container">
      <h2>Most Popular E-Books</h2>
      <div  class="d-flex flex-row justify-content-evenly">
        
        <div v-for="s in popular" style="max-width: 208px; flex-wrap: wrap; align-content: center;"
          class="borderhover position-relative d-flex flex-column">
          <img style="margin: 2px;" class="thumbnail" :onerror="`this.src='${API_URL}/static/200x250.svg';`" alt="Image not Set"
            :src="`${API_URL}/static/books/${s.id}`">
          <div style="padding-top: 10px;">
            <h5 class="card-title text-center">{{s.title}}</h5>
            <a href="/book/{{s.id}}" class=" stretched-link hide-slink"></a>
          </div>
        </div>
        
      </div>
    </div>
  </section>

  <section class="latest my-5">
    <div id="latest" class="container">
      <h2>Latest Additions</h2>
      <div class="d-flex flex-row justify-content-evenly">
        <div v-for="s in latest" style="max-width: 208px; flex-wrap: wrap; align-content: center;"
          class="borderhover position-relative d-flex flex-column">
          <img style="margin: 2px;" class="thumbnail" :onerror="`this.src='${API_URL}/static/200x250.svg';`" alt="Image not Set"
          :src="`${API_URL}/static/books/${s.id}`">
          <div style="padding-top: 10px;">
            <h5 class="card-title text-center">{{s.title}}</h5>
            <a href="/book/{{s.id}}" class=" stretched-link hide-slink"></a>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section v-if="!loggedin" class="cta my-5">
    <div class="container text-center">
      <h2>Start Your Reading Journey Today</h2>
      <a href="/register" class="btn btn-lg btn-dark">Create a Free Account</a>
    </div>
  </section>

  <footer class="py-4 bg-light">
    <div class="container">
      <p class="text-center">Copyright &copy; Arcanum 2024</p>
    </div>
  </footer>

</template>
