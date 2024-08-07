<script setup>
import { useRoute, RouterLink } from 'vue-router'
import { ref } from 'vue'
import API_URL from '../constants.js'
import fetchData from '../helper.js'
import { postData } from '../helper.js'
import router from '../router/index.js'

var authors = ref([])
var authorInput = ref("")


function addAuthor(){
    if(authorInput.value.trim() != "" ){
        authors.value.push({"name": authorInput.value.trim()})
        authorInput.value = ""
    }
}

function addBook(form){
    console.log(form.target)
    var formData = new FormData()
    formData.append('book_name', form.target.book_name.value)
    formData.append('book_desc', form.target.book_desc.value)
    for (var i = 0; i < authors.value.length; i++) {
        formData.append('author_name', authors.value[i].name)
    }
    if (form.target.book_img.files.length > 0) {
        formData.append('book_img', form.target.book_img.files[0])
    }
    if (form.target.book_pdf.files.length > 0) {
        formData.append('book_pdf', form.target.book_pdf.files[0])
    }
    postData('/api/books', formData).then(res => {
        router.push('/book/' + res["id"].toString())
    })

}



</script>
<template>
<div id="body">
    <div class="float-login container">
      <h3 class="mb-3 text-center">Upload a new Book</h3>
      <form enctype="multipart/form-data" id="createBook" @submit.prevent="addBook">


        <div class="mb-3">
          <label class="text-muted mb-2" for="username-input">Book Name</label>
          <input  maxlength="60" class="form-control" type="text" name="book_name" id="book_name" required >
        </div>

        <div class="mb-3" id="author_input">
          <div>
            <div class="d-flex flex-row" style="align-items: center">
            <p style="margin-right: 10px">Authors:
              
            </p>
            <div class="d-flex flex-wrap authors">
              <template v-for="(author, index) in authors">
                <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown"
                aria-expanded="false">
                {{ author.name }}
              </button>
              <ul class="dropdown-menu ">
                <li>
                  <button class="dropdown-item" @click.prevent="authors.splice(index,1)">Remove</button></li>

              </ul>
              </template>
            </div>
          </div>
            <label class="text-muted mb-2" for="author-input">Author Name</label>
            <button style="margin-left: 10px" @click.prevent="addAuthor()">Add Author</button>
          </div>
          <input maxlength="60" class="form-control" name="author_name" v-model="authorInput">
          
        </div>

        <div class="text-muted mb-4">
          <label for="book_desc">Book Description</label>
          <br><textarea maxlength="500" class="form-control" name="book_desc" form="createBook" required></textarea>
        </div>
        
        <div class="text-muted mb-4">
          <label for="book_img">Update Base Image (200px * 250px)</label>
          <input type="file" id="book_img" name="book_img" accept="image/png, image/jpeg">
        </div>
        <div class="text-muted mb-4">
          <label for="book_pdf">Update PDF</label>
          <input type="file" id="book_pdf" name="book_pdf" accept="application/pdf">
        </div>
        <div class="mb-4" style="width: 100%;">
            <p>Note: Image/PDF will remain the same if not chosen, not removed.</p>
          <button type="submit" class="btn btn-dark" style="width: 100%;"> Create Book </button>
        </div>
      </form>
    </div>

  </div>
</template>
<style scoped>
.authors button {
  margin-right: 5px;
  margin-bottom: 5px;
}
.form-select {
  max-width: 150px;
}
</style>