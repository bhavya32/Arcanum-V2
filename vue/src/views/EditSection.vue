<script setup>
import { useRoute, RouterLink } from 'vue-router'
import { ref } from 'vue'
import API_URL from '../constants.js'
import fetchData from '../helper.js'
import { postData } from '../helper.js'
import router from '../router/index.js'
var section_id = useRoute().params.id
var s = ref({
    "date_created": "...",
    "description": "...",
    "id": section_id,
    "name": "..."
})

fetchData('/api/section/' + section_id.toString()).then(data => {
    console.log(data)
    s.value = data["section"]
})

function editSection(form){
    console.log(form.target)
    var formData = new FormData()
    formData.append('section_name', form.target.section_name.value)
    formData.append('section_desc', form.target.section_desc.value)
    if (form.target.section_img.files.length > 0) {
        formData.append('section_img', form.target.section_img.files[0])
    }
    postData('/api/section/' + section_id.toString() + '/edit', formData).then(res => {
        router.push('/section/' + section_id.toString())
    })
}

</script>


<template>
    <div id="body">
    <div class="float-login container">
      <h3 class="mb-3 text-center">Edit Section ID - {{s.id}}</h3>
      <!-- standard bootstrap login with validation -->
      <form enctype="multipart/form-data" id="createSection" @submit.prevent="editSection">


        <div class="mb-3">
          <label class="text-muted mb-2" for="username-input">Section Name</label>
          <input maxlength="50" :value="s.name" class="form-control" type="text" name="section_name" id="secname-input" required>
        </div>

        <div class="text-muted mb-4">
          <label for="section_desc">Section Description</label>
          <br><textarea maxlength="300" class="form-control" name="section_desc" form="createSection" required>{{s.description}}</textarea>
        </div>
        <div class="text-muted mb-4">
          <label for="myfile">Base Image (200px * 250px)</label>
          <input type="file" id="myfile" name="section_img" accept="image/png, image/jpeg">
        </div>
        <div class="mb-4" style="width: 100%;">
            <p>Note: Image will remain the same if not chosen, not removed.</p>
          <button type="submit" class="btn btn-dark" style="width: 100%;"> Update </button>
        </div>
      </form>
    </div>

  </div>
</template>