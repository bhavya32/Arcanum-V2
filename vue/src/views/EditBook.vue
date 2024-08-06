<script setup>
import { useRoute, RouterLink } from 'vue-router'
import { ref } from 'vue'
import API_URL from '../constants.js'
import fetchData from '../helper.js'
import { postData } from '../helper.js'
import router from '../router/index.js'
var book_id = useRoute().params.id
var sections = ref([])
var book = ref({
  "authors": [],
  "desc": "",
  "id": book_id,
  "rating": 100,
  "reads": 1,
  "title": "",
  "sections": []
})

var authors = ref([])
var authorInput = ref("")
fetchData('/api/book/' + book_id.toString()).then(data => {
    console.log(data)
    book.value = data["book"]
    authors.value = data["book"]["authors"]

  })

fetchData('/api/sections').then(data => {
  sections.value = data
})


function addAuthor(){
    if(authorInput.value.trim() != "" ){
        authors.value.push({"name": authorInput.value.trim()})
        authorInput.value = ""
    }
}

function editBook(form){
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
    formData.entries().forEach(x => console.log(x))
    postData('/api/book/' + book_id.toString() + '/edit', formData).then(res => {
        router.push('/book/' + book_id.toString())
    })
}

function removeBookFromSection(section_id, index) {
    fetchData(`/api/book/${book_id}/section/${section_id}/remove`).then(data => {
        if (data["status"] == "success") {
            book.value.sections.splice(index, 1)
        }
    })

}

function addBookToSection(section_id, section_name) {
  if (book.value.sections.find(x => x.id == section_id)) {return}
    fetchData(`/api/book/${book_id}/section/${section_id}/add`).then(data => {
        if (data["status"] == "success") {
            book.value.sections.push({"id": section_id, "name": sections.value.find(x => x.id == section_id).name})
        }
    })
}

</script>
<template>
<div id="body">
    <div class="float-login container">
      <h3 class="mb-3 text-center">Editing Book ID - {{book_id}}</h3>
      <form enctype="multipart/form-data" id="editBook" @submit.prevent="editBook">


        <div class="mb-3">
          <label class="text-muted mb-2" for="username-input">Book Name</label>
          <input  maxlength="60" :value="book.title" class="form-control" type="text" name="book_name" id="secname-input" required >
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
            <!-- <button
              onclick="document.getElementById('author_input').insertAdjacentHTML('beforeend', `<input maxlength='60' list='authors' class='form-control' name='author_name'>`); return false;">Add
              Author</button> -->
              <button style="margin-left: 10px" @click.prevent="addAuthor()">Add Author</button>
          </div>
          <input maxlength="60" list="authors" class="form-control" name="author_name" onmousedown="value = '';" v-model="authorInput">
          <datalist id="authors"></datalist>
        </div>

        <div class="text-muted mb-4">
          <label for="book_desc">Book Description</label>
          <br><textarea maxlength="500" class="form-control" name="book_desc" form="editBook" required>{{book.desc}}</textarea>
        </div>
        <div class="text-muted mb-4">
          <div class="d-flex flex-row" style="align-items: center">
            <p style="margin-right: 10px; text-align: center;">Authors:
              
            </p>
            <div class="d-flex flex-wrap authors">
              <template v-for="(section, index) in book.sections">
                <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown"
                aria-expanded="false">
                {{ section.name }}
              </button>
              <ul class="dropdown-menu ">
                <li>
                  <button class="dropdown-item" @click.prevent="removeBookFromSection(section.id, index)">Remove</button></li>
                  
              </ul>
              </template>
              <select class="form-select" id="secsel" name="sid"
                @change='addBookToSection($event.target.value); $event.target.value = -1;'>
                <option value='-1' selected disabled>Add Section</option>
                <option v-for="sec in sections" :value="sec.id">{{ sec.name }}</option>

              </select>
            </div>
          </div>
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
          <button type="submit" class="btn btn-dark" style="width: 100%;"> Update </button>
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